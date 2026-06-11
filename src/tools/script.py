# HFSS MCP Server - 脚本执行工具
# 核心能力：让 AI 生成并执行任意 PyAEDT 脚本

from typing import Optional, Dict, Any
from ..hfss_connection import HFSSManager
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


def register_script_tools(mcp):
    """注册脚本执行相关的 MCP tools"""
    
    @mcp.tool()
    def run_pyaedt_script(
        script: str,
        description: str = "",
    ) -> str:
        """
        执行 PyAEDT Python 脚本
        
        这是最强大的工具 - 可以执行任意 PyAEDT 代码来创建任意天线/PCB 结构。
        
        脚本中可以使用以下变量:
        - hfss: 已连接的 HFSS 实例 (pyaedt.Hfss)
        - modeler: 几何建模器 (hfss.modeler)
        - materials: 材料库 (hfss.materials)
        
        示例脚本:
        ```python
        # 创建螺旋天线
        import numpy as np
        
        turns = 3
        r_inner = 2.0  # mm
        r_outer = 10.0  # mm
        
        points = []
        for theta in np.linspace(0, turns * 2 * np.pi, 360):
            r = r_inner + (r_outer - r_inner) * theta / (turns * 2 * np.pi)
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            points.append([x, y])
        
        # 创建螺旋线
        hfss.modeler.create_polyline(
            points=points,
            name="spiral",
            material="copper",
        )
        ```
        
        Args:
            script: PyAEDT Python 脚本
            description: 脚本功能描述（用于日志）
            
        Returns:
            脚本执行结果
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 准备执行环境
            exec_globals = {
                'hfss': hfss,
                'modeler': hfss.modeler,
                'materials': hfss.materials,
                'np': __import__('numpy'),
                'math': __import__('math'),
            }
            
            # 捕获输出
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            try:
                # 执行脚本
                exec(script, exec_globals)
                output = buffer.getvalue()
            finally:
                sys.stdout = old_stdout
            
            result = f"✅ 脚本执行成功"
            if description:
                result += f"\n描述: {description}"
            if output:
                result += f"\n输出:\n{output}"
            
            return result
            
        except Exception as e:
            return f"❌ 脚本执行失败: {str(e)}\n\n请检查脚本语法和 PyAEDT API 调用"
    
    @mcp.tool()
    def run_hfss_script_file(
        script_path: str,
    ) -> str:
        """
        执行外部 PyAEDT 脚本文件
        
        Args:
            script_path: 脚本文件路径 (.py)
            
        Returns:
            脚本执行结果
        """
        try:
            if not os.path.exists(script_path):
                return f"❌ 脚本文件不存在: {script_path}"
            
            with open(script_path, 'r', encoding='utf-8') as f:
                script = f.read()
            
            return run_pyaedt_script(
                script=script,
                description=f"执行文件: {script_path}",
            )
            
        except Exception as e:
            return f"❌ 读取脚本文件失败: {str(e)}"
    
    @mcp.tool()
    def generate_antenna_script(
        antenna_type: str,
        parameters: Dict[str, Any],
    ) -> str:
        """
        生成天线建模脚本
        
        支持的天线类型:
        - archimedean_spiral: 阿基米德螺旋天线
        - log_spiral: 对数螺旋天线
        - vivaldi: Vivaldi 渐变缝隙天线
        - yagi: 八木天线
        - helix: 螺旋天线
        - slot: 缝隙天线
        - monopole: 单极子天线
        - loop: 环形天线
        - custom: 自定义（需要提供 points/curves）
        
        Args:
            antenna_type: 天线类型
            parameters: 天线参数字典
            
        Returns:
            生成的 PyAEDT 脚本
        """
        
        scripts = {
            "archimedean_spiral": _gen_archimedean_spiral,
            "log_spiral": _gen_log_spiral,
            "vivaldi": _gen_vivaldi,
            "yagi": _gen_yagi,
            "helix": _gen_helix,
            "slot": _gen_slot,
            "monopole": _gen_monopole,
            "loop": _gen_loop,
        }
        
        if antenna_type not in scripts:
            available = ", ".join(scripts.keys())
            return f"❌ 不支持的天线类型: {antenna_type}\n可用类型: {available}"
        
        try:
            script = scripts[antenna_type](parameters)
            return f"""✅ 生成 {antenna_type} 天线脚本

```python
{script}
```

使用方法:
1. 直接执行: run_pyaedt_script(script=...)
2. 保存文件后执行: run_hfss_script_file(script_path=...)
"""
        except Exception as e:
            return f"❌ 生成脚本失败: {str(e)}"


def _gen_archimedean_spiral(params: Dict) -> str:
    """生成阿基米德螺旋天线脚本"""
    turns = params.get("turns", 3)
    r_inner = params.get("r_inner_mm", 2.0)
    r_outer = params.get("r_outer_mm", 10.0)
    wire_radius = params.get("wire_radius_mm", 0.5)
    material = params.get("material", "copper")
    name = params.get("name", "archimedean_spiral")
    
    return f"""import numpy as np

# 阿基米德螺旋天线参数
turns = {turns}
r_inner = {r_inner}  # mm
r_outer = {r_outer}  # mm
wire_radius = {wire_radius}  # mm
material = "{material}"
name = "{name}"

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
    name=name,
    material=material,
    xsection_type="Circle",
    xsection_width=wire_radius,
)

# 创建接地板（可选）
ground_size = r_outer * 2 + 10
hfss.modeler.create_cylinder(
    origin=[0, 0, -2],
    radius=ground_size / 2,
    height=2,
    orientation="Z",
    name=f"{{name}}_ground",
    material="pec",
)

print(f"创建阿基米德螺旋天线: {{turns}} 圈, 内径 {{r_inner}}mm, 外径 {{r_outer}}mm")
"""


def _gen_log_spiral(params: Dict) -> str:
    """生成对数螺旋天线脚本"""
    turns = params.get("turns", 3)
    r_inner = params.get("r_inner_mm", 2.0)
    r_outer = params.get("r_outer_mm", 15.0)
    growth_rate = params.get("growth_rate", 0.1)
    material = params.get("material", "copper")
    name = params.get("name", "log_spiral")
    
    return f"""import numpy as np

# 对数螺旋天线参数
turns = {turns}
r_inner = {r_inner}  # mm
r_outer = {r_outer}  # mm
a = {growth_rate}  # 增长率
material = "{material}"
name = "{name}"

# 生成对数螺旋点
num_points = 360 * turns
theta = np.linspace(0, turns * 2 * np.pi, num_points)
r = r_inner * np.exp(a * theta)
r = np.clip(r, r_inner, r_outer)

points = []
for i in range(len(theta)):
    x = r[i] * np.cos(theta[i])
    y = r[i] * np.sin(theta[i])
    points.append([x, y, 0])

# 创建螺旋臂 1
hfss.modeler.create_polyline(
    points=points,
    name=f"{{name}}_arm1",
    material=material,
)

# 创建螺旋臂 2（旋转 180 度）
points_arm2 = []
for p in points:
    points_arm2.append([-p[0], -p[1], p[2]])

hfss.modeler.create_polyline(
    points=points_arm2,
    name=f"{{name}}_arm2",
    material=material,
)

print(f"创建对数螺旋天线: {{turns}} 圈, 增长率 {{a}}")
"""


def _gen_vivaldi(params: Dict) -> str:
    """生成 Vivaldi 渐变缝隙天线脚本"""
    length = params.get("length_mm", 30.0)
    width = params.get("width_mm", 20.0)
    slot_width_start = params.get("slot_width_start_mm", 0.2)
    slot_width_end = params.get("slot_width_end_mm", 10.0)
    substrate_material = params.get("substrate_material", "Rogers4003")
    substrate_height = params.get("substrate_height_mm", 0.508)
    name = params.get("name", "vivaldi")
    
    return f"""import numpy as np

# Vivaldi 天线参数
length = {length}  # mm
width = {width}  # mm
slot_width_start = {slot_width_start}  # mm
slot_width_end = {slot_width_end}  # mm
substrate_material = "{substrate_material}"
substrate_height = {substrate_height}  # mm
name = "{name}"

# 创建基板
hfss.modeler.create_box(
    origin=[-width/2, 0, 0],
    sizes=[width, length, substrate_height],
    name=f"{{name}}_substrate",
    material=substrate_material,
)

# 创建渐变缝隙（指数渐变）
num_points = 100
t = np.linspace(0, 1, num_points)
slot_width = slot_width_start * (slot_width_end / slot_width_start) ** t

# 上边缘
upper_edge = []
for i in range(num_points):
    y = t[i] * length
    x = slot_width[i] / 2
    upper_edge.append([x, y, substrate_height])

# 下边缘
lower_edge = []
for i in range(num_points):
    y = t[i] * length
    x = -slot_width[i] / 2
    lower_edge.append([x, y, substrate_height])

# 创建金属层（上表面减去缝隙）
hfss.modeler.create_box(
    origin=[-width/2, 0, substrate_height],
    sizes=[width, length, 0.035],
    name=f"{{name}}_metal",
    material="copper",
)

# 创建缝隙形状
slot_points = upper_edge + lower_edge[::-1]
hfss.modeler.create_polyline(
    points=slot_points,
    close=True,
    name=f"{{name}}_slot_shape",
)

print(f"创建 Vivaldi 天线: 长度 {{length}}mm, 缝宽 {{slot_width_start}}-{{slot_width_end}}mm")
"""


def _gen_yagi(params: Dict) -> str:
    """生成八木天线脚本"""
    frequency_ghz = params.get("frequency_ghz", 2.4)
    num_directors = params.get("num_directors", 3)
    element_radius = params.get("element_radius_mm", 1.0)
    material = params.get("material", "copper")
    name = params.get("name", "yagi")
    
    return f"""import numpy as np

# 八木天线参数
frequency = {frequency_ghz}e9  # Hz
c = 3e8
wavelength = c / frequency * 1000  # mm
num_directors = {num_directors}
element_radius = {element_radius}  # mm
material = "{material}"
name = "{name}"

# 元素长度计算
reflector_length = wavelength * 0.525
driven_length = wavelength * 0.48
director_length = wavelength * 0.44

# 元素间距
reflector_spacing = wavelength * 0.2
director_spacing = wavelength * 0.3

# 创建反射器
hfss.modeler.create_cylinder(
    origin=[-reflector_spacing, -reflector_length/2, 0],
    radius=element_radius,
    height=reflector_length,
    orientation="Y",
    name=f"{{name}}_reflector",
    material=material,
)

# 创建驱动振子
hfss.modeler.create_cylinder(
    origin=[0, -driven_length/2, 0],
    radius=element_radius,
    height=driven_length,
    orientation="Y",
    name=f"{{name}}_driven",
    material=material,
)

# 创建引向器
for i in range(num_directors):
    x = (i + 1) * director_spacing
    hfss.modeler.create_cylinder(
        origin=[x, -director_length/2, 0],
        radius=element_radius,
        height=director_length,
        orientation="Y",
        name=f"{{name}}_director_{{i}}",
        material=material,
    )

# 创建馈电缝隙
gap = 2.0  # mm
hfss.modeler.create_box(
    origin=[-1, -gap/2, -element_radius],
    sizes=[2, gap, element_radius*2],
    name=f"{{name}}_feed_gap",
    material="vacuum",
)

print(f"创建八木天线: {{num_directors}} 个引向器, 频率 {{frequency_ghz}}GHz")
"""


def _gen_helix(params: Dict) -> str:
    """生成螺旋天线（轴向模）脚本"""
    frequency_ghz = params.get("frequency_ghz", 2.4)
    turns = params.get("turns", 5)
    radius = params.get("radius_mm", 15.0)
    pitch_angle = params.get("pitch_angle_deg", 14.0)
    wire_radius = params.get("wire_radius_mm", 1.0)
    material = params.get("material", "copper")
    name = params.get("name", "helix")
    
    return f"""import numpy as np

# 螺旋天线参数
frequency = {frequency_ghz}e9
c = 3e8
wavelength = c / frequency * 1000  # mm
turns = {turns}
radius = {radius}  # mm
pitch_angle = {pitch_angle} * np.pi / 180  # 弧度
wire_radius = {wire_radius}  # mm
material = "{material}"
name = "{name}"

# 螺距
pitch = 2 * np.pi * radius * np.tan(pitch_angle)

# 生成螺旋点
num_points = 360 * turns
theta = np.linspace(0, turns * 2 * np.pi, num_points)
z = pitch * theta / (2 * np.pi)

points = []
for i in range(len(theta)):
    x = radius * np.cos(theta[i])
    y = radius * np.sin(theta[i])
    points.append([x, y, z[i]])

# 创建螺旋
hfss.modeler.create_polyline(
    points=points,
    name=name,
    material=material,
    xsection_type="Circle",
    xsection_width=wire_radius,
)

# 创建接地板
ground_radius = radius * 1.5
hfss.modeler.create_cylinder(
    origin=[0, 0, -2],
    radius=ground_radius,
    height=2,
    orientation="Z",
    name=f"{{name}}_ground",
    material="pec",
)

# 创建馈电同轴线（简化）
hfss.modeler.create_cylinder(
    origin=[0, 0, 0],
    radius=wire_radius * 3,
    height=pitch * turns,
    orientation="Z",
    name=f"{{name}}_feed",
    material="vacuum",
)

print(f"创建螺旋天线: {{turns}} 圈, 半径 {{radius}}mm, 螺距角 {{pitch_angle*180/np.pi:.1f}}°")
"""


def _gen_slot(params: Dict) -> str:
    """生成缝隙天线脚本"""
    frequency_ghz = params.get("frequency_ghz", 10.0)
    slot_length = params.get("slot_length_mm", None)  # 自动计算
    slot_width = params.get("slot_width_mm", 2.0)
    ground_size = params.get("ground_size_mm", 30.0)
    substrate_material = params.get("substrate_material", "Rogers4003")
    substrate_height = params.get("substrate_height_mm", 0.508)
    feed_offset = params.get("feed_offset_mm", 0.0)
    name = params.get("name", "slot")
    
    return f"""import numpy as np

# 缝隙天线参数
frequency = {frequency_ghz}e9
c = 3e8
wavelength = c / frequency * 1000  # mm
slot_length = {slot_length or "wavelength / 2"}  # mm
slot_width = {slot_width}  # mm
ground_size = {ground_size}  # mm
substrate_material = "{substrate_material}"
substrate_height = {substrate_height}  # mm
name = "{name}"

# 创建基板
hfss.modeler.create_box(
    origin=[-ground_size/2, -ground_size/2, 0],
    sizes=[ground_size, ground_size, substrate_height],
    name=f"{{name}}_substrate",
    material=substrate_material,
)

# 创建接地面
hfss.modeler.create_box(
    origin=[-ground_size/2, -ground_size/2, substrate_height],
    sizes=[ground_size, ground_size, 0.035],
    name=f"{{name}}_ground",
    material="copper",
)

# 创建缝隙
hfss.modeler.create_box(
    origin=[-slot_length/2, -slot_width/2, substrate_height - 0.01],
    sizes=[slot_length, slot_width, 0.07],
    name=f"{{name}}_slot",
    material="vacuum",
)

# 布尔减法
hfss.modeler.subtract(
    f"{{name}}_ground",
    [f"{{name}}_slot"],
    keep_originals=False,
)

print(f"创建缝隙天线: 长度 {{slot_length}}mm, 宽度 {{slot_width}}mm, 频率 {{frequency_ghz}}GHz")
"""


def _gen_monopole(params: Dict) -> str:
    """生成单极子天线脚本"""
    frequency_ghz = params.get("frequency_ghz", 2.4)
    element_length = params.get("element_length_mm", None)  # 自动计算
    element_radius = params.get("element_radius_mm", 1.0)
    ground_size = params.get("ground_size_mm", 60.0)
    feed_gap = params.get("feed_gap_mm", 2.0)
    material = params.get("material", "copper")
    name = params.get("name", "monopole")
    
    return f"""import numpy as np

# 单极子天线参数
frequency = {frequency_ghz}e9
c = 3e8
wavelength = c / frequency * 1000  # mm
element_length = {element_length or "wavelength / 4"}  # mm (λ/4)
element_radius = {element_radius}  # mm
ground_size = {ground_size}  # mm
feed_gap = {feed_gap}  # mm
material = "{material}"
name = "{name}"

# 创建接地面
hfss.modeler.create_box(
    origin=[-ground_size/2, -ground_size/2, -0.035],
    sizes=[ground_size, ground_size, 0.035],
    name=f"{{name}}_ground",
    material=material,
)

# 创建辐射体
hfss.modeler.create_cylinder(
    origin=[0, 0, feed_gap],
    radius=element_radius,
    height=element_length,
    orientation="Z",
    name=f"{{name}}_element",
    material=material,
)

# 创建馈电间隙
hfss.modeler.create_cylinder(
    origin=[0, 0, 0],
    radius=element_radius,
    height=feed_gap,
    orientation="Z",
    name=f"{{name}}_feed_gap",
    material="vacuum",
)

print(f"创建单极子天线: 长度 {{element_length}}mm, 频率 {{frequency_ghz}}GHz")
"""


def _gen_loop(params: Dict) -> str:
    """生成环形天线脚本"""
    frequency_ghz = params.get("frequency_ghz", 2.4)
    loop_radius = params.get("loop_radius_mm", None)  # 自动计算
    wire_radius = params.get("wire_radius_mm", 1.0)
    material = params.get("material", "copper")
    name = params.get("name", "loop")
    
    return f"""import numpy as np

# 环形天线参数
frequency = {frequency_ghz}e9
c = 3e8
wavelength = c / frequency * 1000  # mm
loop_radius = {loop_radius or "wavelength / (2 * np.pi)"}  # mm (周长 = λ)
wire_radius = {wire_radius}  # mm
material = "{material}"
name = "{name}"

# 创建环
hfss.modeler.create_cylinder(
    origin=[0, 0, -wire_radius],
    radius=loop_radius,
    height=wire_radius * 2,
    orientation="Z",
    name=f"{{name}}_outer",
    material=material,
)

# 内部挖空
hfss.modeler.create_cylinder(
    origin=[0, 0, -wire_radius - 0.01],
    radius=loop_radius - wire_radius,
    height=wire_radius * 2 + 0.02,
    orientation="Z",
    name=f"{{name}}_inner",
    material="vacuum",
)

hfss.modeler.subtract(
    f"{{name}}_outer",
    [f"{{name}}_inner"],
    keep_originals=False,
)

# 创建馈电缝隙
hfss.modeler.create_box(
    origin=[-wire_radius, -0.5, -wire_radius - 0.01],
    sizes=[wire_radius * 2, 1, wire_radius * 2 + 0.02],
    name=f"{{name}}_gap",
    material="vacuum",
)

hfss.modeler.subtract(
    f"{{name}}_outer",
    [f"{{name}}_gap"],
    keep_originals=False,
)

print(f"创建环形天线: 半径 {{loop_radius}}mm, 频率 {{frequency_ghz}}GHz")
"""
