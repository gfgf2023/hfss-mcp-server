# HFSS MCP Server - 天线设计专用工具
from typing import List, Optional
from ..hfss_connection import HFSSManager
import logging

logger = logging.getLogger(__name__)


def register_antenna_tools(mcp):
    """注册天线设计相关的 MCP tools"""
    
    @mcp.tool()
    def create_patch_antenna(
        name: str = "PatchAntenna",
        frequency_ghz: float = 2.4,
        substrate_material: str = "FR4_epoxy",
        substrate_height_mm: float = 1.6,
        ground_size_mm: Optional[List[float]] = None,
        patch_size_mm: Optional[List[float]] = None,
        feed_offset_mm: float = 0.0,
        feed_width_mm: float = 2.0,
    ) -> str:
        """
        创建矩形微带贴片天线
        
        Args:
            name: 天线名称
            frequency_ghz: 工作频率 (GHz)
            substrate_material: 基板材料
            substrate_height_mm: 基板厚度 (mm)
            ground_size_mm: 接地平面尺寸 [长, 宽] (mm)，留空自动计算
            patch_size_mm: 贴片尺寸 [长, 宽] (mm)，留空自动计算
            feed_offset_mm: 馈电点偏移 (mm)
            feed_width_mm: 馈线宽度 (mm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 自动计算贴片尺寸（基于传输线模型）
            c = 3e8  # 光速
            freq = frequency_ghz * 1e9
            wavelength = c / freq  # 自由空间波长
            
            # 获取基板有效介电常数
            if substrate_material == "FR4_epoxy":
                er = 4.4
            elif "Rogers" in substrate_material:
                er = 3.55  # Rogers4003
            else:
                er = 4.4  # 默认值
            
            # 贴片宽度
            W = c / (2 * freq) * (2 / (er + 1))**0.5 * 1000  # mm
            
            # 有效介电常数
            er_eff = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * substrate_height_mm / W)**-0.5
            
            # 贴片长度
            L_eff = c / (2 * freq * er_eff**0.5) * 1000  # mm
            delta_L = 0.412 * substrate_height_mm * (er_eff + 0.3) * (W / substrate_height_mm + 0.264) / ((er_eff - 0.258) * (W / substrate_height_mm + 0.8))
            L = (L_eff - 2 * delta_L)  # mm
            
            if patch_size_mm:
                L, W = patch_size_mm
            
            # 接地平面尺寸（通常比贴片大 6h）
            ground_L = L + 6 * substrate_height_mm
            ground_W = W + 6 * substrate_height_mm
            if ground_size_mm:
                ground_L, ground_W = ground_size_mm
            
            # 创建基板
            substrate_origin = [-ground_L / 2, -ground_W / 2, 0]
            hfss.modeler.create_box(
                origin=substrate_origin,
                sizes=[ground_L, ground_W, substrate_height_mm],
                name=f"{name}_substrate",
                material=substrate_material,
            )
            
            # 创建接地面
            gnd_origin = [-ground_L / 2, -ground_W / 2, -0.035]  # 铜箔厚度
            hfss.modeler.create_box(
                origin=gnd_origin,
                sizes=[ground_L, ground_W, 0.035],
                name=f"{name}_ground",
                material="copper",
            )
            
            # 创建贴片
            patch_origin = [-L / 2, -W / 2, substrate_height_mm]
            hfss.modeler.create_box(
                origin=patch_origin,
                sizes=[L, W, 0.035],
                name=f"{name}_patch",
                material="copper",
            )
            
            # 创建馈线
            feed_origin = [-feed_width_mm / 2, -W / 2 - 10, substrate_height_mm]
            hfss.modeler.create_box(
                origin=feed_origin,
                sizes=[feed_width_mm, 10 + feed_offset_mm, 0.035],
                name=f"{name}_feed",
                material="copper",
            )
            
            # 合并金属部分
            hfss.modeler.unite(
                [f"{name}_patch", f"{name}_feed"],
                new_name=f"{name}_radiator",
            )
            
            # 创建空气盒（用于辐射边界）
            air_padding = wavelength * 1000 / 4  # 四分之一波长
            air_origin = [-ground_L / 2 - air_padding, -ground_W / 2 - air_padding, -air_padding]
            air_size = [ground_L + 2 * air_padding, ground_W + 2 * air_padding, substrate_height_mm + 2 * air_padding]
            hfss.modeler.create_box(
                origin=air_origin,
                sizes=air_size,
                name=f"{name}_airbox",
                material="vacuum",
            )
            
            # 设置辐射边界
            hfss.assign_radiation_boundary_to_objects(
                f"{name}_airbox",
                f"{name}_radiation",
            )
            
            return f"""✅ 创建贴片天线 '{name}' 成功

📊 天线参数:
工作频率: {frequency_ghz} GHz
波长: {wavelength*1000:.2f} mm
基板: {substrate_material} (εr={er})
基板厚度: {substrate_height_mm} mm

📐 贴片尺寸:
长度 L: {L:.2f} mm
宽度 W: {W:.2f} mm

📏 接地平面: {ground_L:.2f} x {ground_W:.2f} mm
馈线宽度: {feed_width_mm} mm
馈电偏移: {feed_offset_mm} mm

⚠️ 下一步:
1. 使用 create_wave_port 设置馈电端口
2. 使用 create_setup 设置求解参数
3. 使用 run_simulation 运行仿真
"""
        except Exception as e:
            return f"❌ 创建贴片天线失败: {str(e)}"
    
    @mcp.tool()
    def create_dipole_antenna(
        name: str = "Dipole",
        frequency_ghz: float = 2.4,
        arm_length_mm: Optional[float] = None,
        arm_radius_mm: float = 1.0,
        gap_mm: float = 2.0,
    ) -> str:
        """
        创建半波偶极子天线
        
        Args:
            name: 天线名称
            frequency_ghz: 工作频率 (GHz)
            arm_length_mm: 臂长 (mm)，留空自动计算为 λ/4
            arm_radius_mm: 臂半径 (mm)
            gap_mm: 两臂间距 (mm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            c = 3e8
            wavelength = c / (frequency_ghz * 1e9) * 1000  # mm
            
            if arm_length_mm is None:
                arm_length_mm = wavelength / 4  # 半波偶极子
            
            # 创建上臂
            hfss.modeler.create_cylinder(
                origin=[0, 0, gap_mm / 2],
                radius=arm_radius_mm,
                height=arm_length_mm,
                orientation="Z",
                name=f"{name}_arm1",
                material="copper",
            )
            
            # 创建下臂
            hfss.modeler.create_cylinder(
                origin=[0, 0, -gap_mm / 2 - arm_length_mm],
                radius=arm_radius_mm,
                height=arm_length_mm,
                orientation="Z",
                name=f"{name}_arm2",
                material="copper",
            )
            
            # 创建空气盒
            air_radius = wavelength / 2
            air_height = arm_length_mm * 2 + gap_mm + wavelength / 2
            hfss.modeler.create_cylinder(
                origin=[0, 0, -arm_length_mm - gap_mm / 2 - wavelength / 4],
                radius=air_radius,
                height=air_height,
                orientation="Z",
                name=f"{name}_airbox",
                material="vacuum",
            )
            
            # 辐射边界
            hfss.assign_radiation_boundary_to_objects(
                f"{name}_airbox",
                f"{name}_radiation",
            )
            
            return f"""✅ 创建偶极子天线 '{name}' 成功

📊 天线参数:
工作频率: {frequency_ghz} GHz
波长: {wavelength:.2f} mm
臂长: {arm_length_mm:.2f} mm (λ/4)
臂半径: {arm_radius_mm} mm
间距: {gap_mm} mm

⚠️ 下一步:
1. 使用 create_lumped_port 在间隙处创建馈电端口
2. 使用 create_setup 设置求解参数
3. 使用 run_simulation 运行仿真
"""
        except Exception as e:
            return f"❌ 创建偶极子天线失败: {str(e)}"
    
    @mcp.tool()
    def create_horn_antenna(
        name: str = "Horn",
        frequency_ghz: float = 10.0,
        waveguide_a_mm: float = 22.86,
        waveguide_b_mm: float = 10.16,
        horn_aperture_a_mm: float = 50.0,
        horn_aperture_b_mm: float = 40.0,
        horn_length_mm: float = 50.0,
    ) -> str:
        """
        创建喇叭天线
        
        Args:
            name: 天线名称
            frequency_ghz: 工作频率 (GHz)
            waveguide_a_mm: 波导宽边尺寸 (mm)
            waveguide_b_mm: 波导窄边尺寸 (mm)
            horn_aperture_a_mm: 喇叭口面宽边尺寸 (mm)
            horn_aperture_b_mm: 喇叭口面窄边尺寸 (mm)
            horn_length_mm: 喇叭长度 (mm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            wavelength = 3e8 / (frequency_ghz * 1e9) * 1000  # mm
            
            # 创建波导段
            waveguide_length = wavelength * 2
            hfss.modeler.create_box(
                origin=[-waveguide_a_mm / 2, -waveguide_b_mm / 2, 0],
                sizes=[waveguide_a_mm, waveguide_b_mm, waveguide_length],
                name=f"{name}_waveguide",
                material="vacuum",
            )
            
            # 创建喇叭段（使用 loft 或分段近似）
            # 这里使用简单的梯形近似
            horn_segments = 10
            for i in range(horn_segments):
                t = i / horn_segments
                a = waveguide_a_mm + (horn_aperture_a_mm - waveguide_a_mm) * t
                b = waveguide_b_mm + (horn_aperture_b_mm - waveguide_b_mm) * t
                z = waveguide_length + horn_length_mm * t
                dz = horn_length_mm / horn_segments
                
                hfss.modeler.create_box(
                    origin=[-a / 2, -b / 2, z],
                    sizes=[a, b, dz],
                    name=f"{name}_horn_seg{i}",
                    material="vacuum",
                )
            
            # 合并所有段
            seg_names = [f"{name}_waveguide"] + [f"{name}_horn_seg{i}" for i in range(horn_segments)]
            hfss.modeler.unite(seg_names, new_name=f"{name}_body")
            
            # 创建外壁（通过减去内部）
            wall_thickness = 2.0
            outer_a = horn_aperture_a_mm + 2 * wall_thickness
            outer_b = horn_aperture_b_mm + 2 * wall_thickness
            
            # 创建空气盒
            air_padding = wavelength
            total_length = waveguide_length + horn_length_mm
            hfss.modeler.create_box(
                origin=[-outer_a / 2 - air_padding, -outer_b / 2 - air_padding, -air_padding],
                sizes=[outer_a + 2 * air_padding, outer_b + 2 * air_padding, total_length + 2 * air_padding],
                name=f"{name}_airbox",
                material="vacuum",
            )
            
            # 辐射边界
            hfss.assign_radiation_boundary_to_objects(
                f"{name}_airbox",
                f"{name}_radiation",
            )
            
            return f"""✅ 创建喇叭天线 '{name}' 成功

📊 天线参数:
工作频率: {frequency_ghz} GHz
波长: {wavelength:.2f} mm

📐 波导尺寸: {waveguide_a_mm} x {waveguide_b_mm} mm
📐 口面尺寸: {horn_aperture_a_mm} x {horn_aperture_b_mm} mm
📏 喇叭长度: {horn_length_mm} mm

⚠️ 下一步:
1. 使用 create_wave_port 在波导口创建端口
2. 使用 create_setup 设置求解参数
3. 使用 run_simulation 运行仿真
"""
        except Exception as e:
            return f"❌ 创建喇叭天线失败: {str(e)}"
    
    @mcp.tool()
    def create_array_antenna(
        name: str = "AntennaArray",
        element_type: str = "patch",
        rows: int = 2,
        cols: int = 2,
        spacing_x_mm: float = 62.5,
        spacing_y_mm: float = 62.5,
        frequency_ghz: float = 2.4,
    ) -> str:
        """
        创建天线阵列
        
        Args:
            name: 阵列名称
            element_type: 单元类型 (patch/dipole)
            rows: 行数
            cols: 列数
            spacing_x_mm: X 方向间距 (mm)
            spacing_y_mm: Y 方向间距 (mm)
            frequency_ghz: 工作频率 (GHz)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 创建第一个单元
            if element_type == "patch":
                create_patch_antenna(
                    name=f"{name}_elem_0_0",
                    frequency_ghz=frequency_ghz,
                )
            elif element_type == "dipole":
                create_dipole_antenna(
                    name=f"{name}_elem_0_0",
                    frequency_ghz=frequency_ghz,
                )
            else:
                return f"❌ 不支持的单元类型: {element_type}"
            
            # 复制阵列
            for row in range(rows):
                for col in range(cols):
                    if row == 0 and col == 0:
                        continue
                    
                    dx = col * spacing_x_mm
                    dy = row * spacing_y_mm
                    
                    # 复制并移动
                    hfss.modeler.duplicate_along_line(
                        f"{name}_elem_0_0",
                        vector=[dx, dy, 0],
                        count=1,
                    )
                    
                    # 重命名复制的对象
                    # PyAEDT 会自动命名，需要获取最新创建的对象
                    objects = hfss.modeler.object_names
                    new_obj = objects[-1]  # 最后创建的对象
                    hfss.modeler.rename(new_obj, f"{name}_elem_{row}_{col}")
            
            return f"""✅ 创建天线阵列 '{name}' 成功

📊 阵列配置:
单元类型: {element_type}
阵列规模: {rows} x {cols} = {rows * cols} 元
X 间距: {spacing_x_mm} mm
Y 间距: {spacing_y_mm} mm
频率: {frequency_ghz} GHz

⚠️ 下一步:
1. 为每个单元创建端口
2. 设置求解和扫频参数
3. 运行仿真获取阵列方向图
"""
        except Exception as e:
            return f"❌ 创建天线阵列失败: {str(e)}"
    
    @mcp.tool()
    def create_wave_port(
        object_name: str,
        port_name: str = "WavePort1",
        axis: str = "Z",
        impedance: float = 50.0,
    ) -> str:
        """
        创建波端口（用于天线馈电）
        
        Args:
            object_name: 端口所在的对象名称
            port_name: 端口名称
            axis: 端口法向轴
            impedance: 特性阻抗 (Ohm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 获取对象的面
            faces = hfss.modeler.get_object_faces(object_name)
            if not faces:
                return f"❌ 对象 '{object_name}' 没有面"
            
            # 选择最小的面作为端口面（通常是馈电口）
            min_area = float('inf')
            port_face = None
            for face in faces:
                area = hfss.modeler.get_face_area(face)
                if area < min_area:
                    min_area = area
                    port_face = face
            
            # 创建波端口
            hfss.wave_port(
                assignment=port_face,
                name=port_name,
                impedance=impedance,
                renormalize=True,
            )
            
            return f"✅ 创建波端口 '{port_name}' 成功\n阻抗: {impedance} Ohm"
        except Exception as e:
            return f"❌ 创建波端口失败: {str(e)}"
    
    @mcp.tool()
    def create_lumped_port(
        object_name: str,
        port_name: str = "LumpedPort1",
        axis: str = "Z",
        impedance: float = 50.0,
        voltage_start: Optional[List[float]] = None,
        voltage_end: Optional[List[float]] = None,
    ) -> str:
        """
        创建集总端口（用于天线馈电）
        
        Args:
            object_name: 端口所在的对象名称
            port_name: 端口名称
            axis: 端口方向轴
            impedance: 特性阻抗 (Ohm)
            voltage_start: 电压积分线起点 [x, y, z] (mm)
            voltage_end: 电压积分线终点 [x, y, z] (mm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 获取对象的面
            faces = hfss.modeler.get_object_faces(object_name)
            if not faces:
                return f"❌ 对象 '{object_name}' 没有面"
            
            # 选择最小的面
            min_area = float('inf')
            port_face = None
            for face in faces:
                area = hfss.modeler.get_face_area(face)
                if area < min_area:
                    min_area = area
                    port_face = face
            
            # 创建集总端口
            hfss.lumped_port(
                assignment=port_face,
                name=port_name,
                impedance=impedance,
                renormalize=True,
            )
            
            return f"✅ 创建集总端口 '{port_name}' 成功\n阻抗: {impedance} Ohm"
        except Exception as e:
            return f"❌ 创建集总端口失败: {str(e)}"
    
    @mcp.tool()
    def create_antenna_setup(
        setup_name: str = "Setup1",
        frequency_ghz: float = 2.4,
        max_passes: int = 20,
        max_delta_s: float = 0.02,
        frequency_sweep_start_ghz: float = 1.0,
        frequency_sweep_stop_ghz: float = 4.0,
        sweep_type: str = "Interpolating",
        sweep_step_mhz: float = 10.0,
    ) -> str:
        """
        创建天线仿真求解设置
        
        Args:
            setup_name: 求解设置名称
            frequency_ghz: 求解频率 (GHz)
            max_passes: 最大迭代次数
            max_delta_s: S 参数收敛阈值
            frequency_sweep_start_ghz: 扫频起始频率 (GHz)
            frequency_sweep_stop_ghz: 扫频终止频率 (GHz)
            sweep_type: 扫频类型 (Fast/Interpolating/Discrete)
            sweep_step_mhz: 扫频步长 (MHz)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 创建求解设置
            setup = hfss.create_setup(
                name=setup_name,
                setup_type="DrivenModal",
            )
            
            setup.props["Frequency"] = f"{frequency_ghz}GHz"
            setup.props["MaximumPasses"] = max_passes
            setup.props["MaxDeltaS"] = max_delta_s
            
            # 创建频率扫描
            sweep_name = f"{setup_name}_sweep"
            hfss.create_linear_count_sweep(
                setup=setup_name,
                unit="GHz",
                start_frequency=frequency_sweep_start_ghz,
                stop_frequency=frequency_sweep_stop_ghz,
                num_of_freq_points=int((frequency_sweep_stop_ghz - frequency_sweep_start_ghz) * 1000 / sweep_step_mhz),
                sweep_type=sweep_type,
                name=sweep_name,
            )
            
            return f"""✅ 创建求解设置 '{setup_name}' 成功

📊 设置参数:
求解频率: {frequency_ghz} GHz
最大迭代: {max_passes} 次
收敛阈值: ΔS = {max_delta_s}

📈 频率扫描:
起始频率: {frequency_sweep_start_ghz} GHz
终止频率: {frequency_sweep_stop_ghz} GHz
扫频类型: {sweep_type}
步长: {sweep_step_mhz} MHz

⚠️ 下一步:
1. 使用 run_simulation 运行仿真
2. 使用 get_s_parameters 查看 S 参数
3. 使用 get_antenna_parameters 查看天线指标
"""
        except Exception as e:
            return f"❌ 创建求解设置失败: {str(e)}"
