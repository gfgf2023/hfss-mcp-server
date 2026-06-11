#!/usr/bin/env python3
"""
天线建模演示 - 多种建模方式
"""

# ============================================================
# 方式 1：基本几何体组合 - 微带贴片天线
# ============================================================
def patch_antenna_demo():
    """
    微带贴片天线建模
    特点：使用基本几何体（长方体、圆柱）组合
    """
    script = """
import numpy as np

# 参数
freq_ghz = 2.4
er = 4.4  # FR4 介电常数
h = 1.6   # 基板厚度 mm
c = 3e8

# 自动计算贴片尺寸
wavelength = c / (freq_ghz * 1e9) * 1000
W = c / (2 * freq_ghz * 1e9) * (2 / (er + 1))**0.5 * 1000
er_eff = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * h / W)**-0.5
L = c / (2 * freq_ghz * 1e9 * er_eff**0.5) * 1000 - 0.824 * h * (er_eff + 0.3) * (W / h + 0.264) / ((er_eff - 0.258) * (W / h + 0.8))

# 基板
hfss.modeler.create_box(
    origin=[-W/2 - 10, -W/2 - 10, 0],
    sizes=[W + 20, W + 20, h],
    name="substrate",
    material="FR4_epoxy",
)

# 接地面
hfss.modeler.create_box(
    origin=[-W/2 - 10, -W/2 - 10, -0.035],
    sizes=[W + 20, W + 20, 0.035],
    name="ground",
    material="copper",
)

# 贴片
hfss.modeler.create_box(
    origin=[-L/2, -W/2, h],
    sizes=[L, W, 0.035],
    name="patch",
    material="copper",
)

# 馈线
hfss.modeler.create_box(
    origin=[-1, -W/2 - 10, h],
    sizes=[2, 10 + W/2, 0.035],
    name="feed",
    material="copper",
)

# 合并金属部分
hfss.modeler.unite(["patch", "feed"], new_name="radiator")

print(f"贴片天线建模完成: L={L:.2f}mm, W={W:.2f}mm, f={freq_ghz}GHz")
"""
    return script


# ============================================================
# 方式 2：曲线建模 - 阿基米德螺旋天线
# ============================================================
def spiral_antenna_demo():
    """
    阿基米德螺旋天线建模
    特点：使用 polyline 创建复杂曲线
    """
    script = """
import numpy as np

# 参数
turns = 3
r_inner = 2.0   # mm
r_outer = 10.0  # mm
wire_radius = 0.5  # mm

# 生成螺旋点
num_points = 360 * turns
theta = np.linspace(0, turns * 2 * np.pi, num_points)
r = r_inner + (r_outer - r_inner) * theta / (turns * 2 * np.pi)

points = []
for i in range(len(theta)):
    x = r[i] * np.cos(theta[i])
    y = r[i] * np.sin(theta[i])
    points.append([x, y, 0])

# 创建螺旋线
hfss.modeler.create_polyline(
    points=points,
    name="spiral_arm1",
    material="copper",
    xsection_type="Circle",
    xsection_width=wire_radius,
)

# 第二条臂（旋转 180 度）
points_arm2 = [[-p[0], -p[1], p[2]] for p in points]
hfss.modeler.create_polyline(
    points=points_arm2,
    name="spiral_arm2",
    material="copper",
    xsection_type="Circle",
    xsection_width=wire_radius,
)

# 接地板
hfss.modeler.create_cylinder(
    origin=[0, 0, -2],
    radius=r_outer + 5,
    height=2,
    orientation="Z",
    name="ground",
    material="pec",
)

print(f"阿基米德螺旋天线建模完成: {turns}圈, 内径{r_inner}mm, 外径{r_outer}mm")
"""
    return script


# ============================================================
# 方式 3：参数化曲面 - 喇叭天线
# ============================================================
def horn_antenna_demo():
    """
    喇叭天线建模
    特点：参数化渐变截面
    """
    script = """
import numpy as np

# 参数
freq_ghz = 10.0
a_wg = 22.86   # 波导宽边 mm
b_wg = 10.16   # 波导窄边 mm
a_horn = 50.0  # 喇叭口面宽边 mm
b_horn = 40.0  # 喇叭口面窄边 mm
L_horn = 50.0  # 喇叭长度 mm
L_wg = 50.0    # 波导长度 mm

# 创建波导段
hfss.modeler.create_box(
    origin=[-a_wg/2, -b_wg/2, 0],
    sizes=[a_wg, b_wg, L_wg],
    name="waveguide",
    material="vacuum",
)

# 创建喇叭段（分段近似）
num_segments = 20
for i in range(num_segments):
    t = i / num_segments
    a = a_wg + (a_horn - a_wg) * t
    b = b_wg + (b_horn - b_wg) * t
    z = L_wg + L_horn * t
    dz = L_horn / num_segments
    
    hfss.modeler.create_box(
        origin=[-a/2, -b/2, z],
        sizes=[a, b, dz],
        name=f"horn_seg_{i}",
        material="vacuum",
    )

# 合并所有段
seg_names = ["waveguide"] + [f"horn_seg_{i}" for i in range(num_segments)]
hfss.modeler.unite(seg_names, new_name="horn_body")

# 创建外壁
wall = 2.0
hfss.modeler.create_box(
    origin=[-(a_horn + 2*wall)/2, -(b_horn + 2*wall)/2, L_wg],
    sizes=[a_horn + 2*wall, b_horn + 2*wall, L_horn],
    name="horn_outer",
    material="pec",
)

# 挖空内部
hfss.modeler.create_box(
    origin=[-a_horn/2, -b_horn/2, L_wg - 0.01],
    sizes=[a_horn, b_horn, L_horn + 0.02],
    name="horn_inner",
    material="vacuum",
)

hfss.modeler.subtract("horn_outer", ["horn_inner"], keep_originals=False)
hfss.modeler.subtract("horn_outer", ["horn_body"], keep_originals=True)

print(f"喇叭天线建模完成: {a_horn}x{b_horn}mm口面, 频率{freq_ghz}GHz")
"""
    return script


# ============================================================
# 方式 4：布尔运算 - Vivaldi 天线
# ============================================================
def vivaldi_demo():
    """
    Vivaldi 渐变缝隙天线建模
    特点：布尔运算创建复杂形状
    """
    script = """
import numpy as np

# 参数
length = 30.0   # mm
width = 20.0    # mm
slot_start = 0.2  # mm
slot_end = 10.0   # mm
h = 0.508       # mm (Rogers4003)

# 创建基板
hfss.modeler.create_box(
    origin=[-width/2, 0, 0],
    sizes=[width, length, h],
    name="substrate",
    material="Rogers4003",
)

# 创建金属层
hfss.modeler.create_box(
    origin=[-width/2, 0, h],
    sizes=[width, length, 0.035],
    name="metal",
    material="copper",
)

# 创建渐变缝隙形状（指数渐变）
num_points = 100
t = np.linspace(0, 1, num_points)
slot_width = slot_start * (slot_end / slot_start) ** t

# 上边缘
upper = []
for i in range(num_points):
    y = t[i] * length
    x = slot_width[i] / 2
    upper.append([x, y, h + 0.02])

# 下边缘
lower = []
for i in range(num_points):
    y = t[i] * length
    x = -slot_width[i] / 2
    lower.append([x, y, h + 0.02])

# 创建缝隙形状（闭合多边形）
slot_points = upper + lower[::-1]
hfss.modeler.create_polyline(
    points=slot_points,
    close=True,
    name="slot_shape",
)

# 拉伸成实体
hfss.modeler.sweep_along_vector(
    "slot_shape",
    vector=[0, 0, 0.08],
)

# 布尔减法
hfss.modeler.subtract("metal", ["slot_shape"], keep_originals=False)

print(f"Vivaldi 天线建模完成: 长度{length}mm, 缝宽{slot_start}-{slot_end}mm")
"""
    return script


# ============================================================
# 方式 5：旋转体 - 圆锥天线/单极子
# ============================================================
def cone_monopole_demo():
    """
    锥形单极子天线建模
    特点：旋转体建模
    """
    script = """
import numpy as np

# 参数
freq_ghz = 2.4
c = 3e8
wavelength = c / (freq_ghz * 1e9) * 1000

# 锥体参数
height = wavelength / 4  # mm
r_bottom = 10.0  # mm 底部半径
r_top = 2.0      # mm 顶部半径

# 创建锥体（用多段圆柱近似）
num_segments = 20
for i in range(num_segments):
    t = i / num_segments
    r = r_bottom + (r_top - r_bottom) * t
    z = height * t
    dz = height / num_segments
    
    hfss.modeler.create_cylinder(
        origin=[0, 0, z],
        radius=r,
        height=dz,
        orientation="Z",
        name=f"cone_seg_{i}",
        material="copper",
    )

# 合并所有段
seg_names = [f"cone_seg_{i}" for i in range(num_segments)]
hfss.modeler.unite(seg_names, new_name="cone")

# 接地板
hfss.modeler.create_cylinder(
    origin=[0, 0, -0.035],
    radius=30,
    height=0.035,
    orientation="Z",
    name="ground",
    material="copper",
)

print(f"锥形单极子建模完成: 高度{height:.1f}mm, 底径{r_bottom}mm, 顶径{r_top}mm")
"""
    return script


# ============================================================
# 方式 6：阵列复制 - 相控阵天线
# ============================================================
def phased_array_demo():
    """
    相控阵天线建模
    特点：参数化阵列复制
    """
    script = """
import numpy as np

# 参数
freq_ghz = 10.0
c = 3e8
wavelength = c / (freq_ghz * 1e9) * 1000
rows = 8
cols = 8
spacing = wavelength * 0.8  # 间距

# 创建单元（微带贴片）
patch_size = wavelength * 0.4
h = 1.0  # 基板厚度

# 创建第一个单元
hfss.modeler.create_box(
    origin=[-patch_size/2, -patch_size/2, h],
    sizes=[patch_size, patch_size, 0.035],
    name="elem_0_0",
    material="copper",
)

# 创建阵列
for row in range(rows):
    for col in range(cols):
        if row == 0 and col == 0:
            continue
        
        dx = col * spacing
        dy = row * spacing
        
        # 复制并移动
        hfss.modeler.duplicate_along_line(
            "elem_0_0",
            vector=[dx, dy, 0],
            count=1,
        )
        
        # 重命名
        new_obj = hfss.modeler.object_names[-1]
        hfss.modeler.rename(new_obj, f"elem_{row}_{col}")

# 创建公共基板
total_width = (cols - 1) * spacing + patch_size + 20
total_length = (rows - 1) * spacing + patch_size + 20

hfss.modeler.create_box(
    origin=[-total_width/2, -total_length/2, 0],
    sizes=[total_width, total_length, h],
    name="substrate",
    material="FR4_epoxy",
)

# 接地板
hfss.modeler.create_box(
    origin=[-total_width/2, -total_length/2, -0.035],
    sizes=[total_width, total_length, 0.035],
    name="ground",
    material="copper",
)

print(f"相控阵建模完成: {rows}x{cols}={rows*cols}单元, 间距{spacing:.2f}mm")
"""
    return script


# ============================================================
# 方式 7：导入 CAD + 修改
# ============================================================
def cad_import_demo():
    """
    CAD 导入 + 修改建模
    特点：导入外部模型后进行布尔运算
    """
    script = """
# 导入 STEP 文件
hfss.modeler.import_3d_cad("/path/to/antenna.step")

# 导入后可以进行布尔运算
# 例如：添加馈电结构
hfss.modeler.create_cylinder(
    origin=[0, 0, 0],
    radius=1.0,
    height=5.0,
    orientation="Z",
    name="feed_pin",
    material="copper",
)

# 减去馈电缝隙
hfss.modeler.create_cylinder(
    origin=[0, 0, -0.01],
    radius=0.5,
    height=0.06,
    orientation="Z",
    name="feed_gap",
    material="vacuum",
)

hfss.modeler.subtract("antenna_body", ["feed_gap"], keep_originals=False)

print("CAD 导入并修改完成")
"""
    return script


# ============================================================
# 方式 8：复杂曲面 - 介质谐振器天线
# ============================================================
def dra_demo():
    """
    介质谐振器天线 (DRA) 建模
    特点：圆柱形介质 + 馈电结构
    """
    script = """
import numpy as np

# 参数
freq_ghz = 5.8
c = 3e8
wavelength = c / (freq_ghz * 1e9) * 1000

# DRA 参数
er_dra = 10.0  # 介质谐振器介电常数
radius = wavelength / 4 * (er_dra)**0.5  # mm
height = radius * 1.2  # mm

# 创建介质谐振器
hfss.modeler.create_cylinder(
    origin=[0, 0, 0],
    radius=radius,
    height=height,
    orientation="Z",
    name="dra",
    material="custom_dra",
)

# 创建自定义材料
hfss.materials.add_material(
    name="custom_dra",
    properties={
        "permittivity": er_dra,
        "permeability": 1.0,
        "conductivity": 0.0,
        "dielectric_loss_tangent": 0.002,
    },
)

# 创建接地板
ground_size = radius * 4
hfss.modeler.create_box(
    origin=[-ground_size/2, -ground_size/2, -0.035],
    sizes=[ground_size, ground_size, 0.035],
    name="ground",
    material="copper",
)

# 创建微带馈线
feed_width = 1.5  # 50 欧姆线宽
feed_length = radius * 2

hfss.modeler.create_box(
    origin=[-feed_width/2, -feed_length/2, -0.035],
    sizes=[feed_width, feed_length, 0.035],
    name="feed_line",
    material="copper",
)

# 创建耦合缝隙
slot_width = 0.5
slot_length = radius * 0.8

hfss.modeler.create_box(
    origin=[-slot_width/2, -slot_length/2, -0.04],
    sizes=[slot_width, slot_length, 0.075],
    name="coupling_slot",
    material="vacuum",
)

hfss.modeler.subtract("ground", ["coupling_slot"], keep_originals=False)

print(f"DRA 建模完成: 半径{radius:.2f}mm, 高度{height:.2f}mm, εr={er_dra}")
"""
    return script


if __name__ == "__main__":
    print("=" * 60)
    print("天线建模演示 - 8 种建模方式")
    print("=" * 60)
    
    demos = [
        ("1. 基本几何体组合 - 微带贴片天线", patch_antenna_demo),
        ("2. 曲线建模 - 阿基米德螺旋天线", spiral_antenna_demo),
        ("3. 参数化曲面 - 喇叭天线", horn_antenna_demo),
        ("4. 布尔运算 - Vivaldi 天线", vivaldi_demo),
        ("5. 旋转体 - 锥形单极子", cone_monopole_demo),
        ("6. 阵列复制 - 相控阵天线", phased_array_demo),
        ("7. CAD 导入 + 修改", cad_import_demo),
        ("8. 复杂曲面 - 介质谐振器天线", dra_demo),
    ]
    
    for name, func in demos:
        print(f"\n{name}")
        print("-" * 40)
        script = func()
        print(script[:200] + "..." if len(script) > 200 else script)
