# HFSS MCP Server - PCB 仿真专用工具
from typing import List, Optional, Dict
from ..hfss_connection import HFSSManager
import logging

logger = logging.getLogger(__name__)


def register_pcb_tools(mcp):
    """注册 PCB 仿真相关的 MCP tools"""
    
    @mcp.tool()
    def create_pcb_stackup(
        name: str = "PCB",
        layers: List[Dict] = None,
        board_width_mm: float = 100.0,
        board_length_mm: float = 100.0,
    ) -> str:
        """
        创建 PCB 叠层结构
        
        Args:
            name: PCB 名称
            layers: 叠层定义列表，每层包含:
                - name: 层名
                - type: 类型 (signal/dielectric/ground/power)
                - thickness_mm: 厚度 (mm)
                - material: 材料
            board_width_mm: 板宽 (mm)
            board_length_mm: 板长 (mm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            if layers is None:
                # 默认 4 层板叠层
                layers = [
                    {"name": "TOP", "type": "signal", "thickness_mm": 0.035, "material": "copper"},
                    {"name": "PREPREG", "type": "dielectric", "thickness_mm": 0.2, "material": "FR4_epoxy"},
                    {"name": "GND", "type": "ground", "thickness_mm": 0.035, "material": "copper"},
                    {"name": "CORE", "type": "dielectric", "thickness_mm": 1.0, "material": "FR4_epoxy"},
                    {"name": "PWR", "type": "power", "thickness_mm": 0.035, "material": "copper"},
                    {"name": "PREPREG2", "type": "dielectric", "thickness_mm": 0.2, "material": "FR4_epoxy"},
                    {"name": "BOTTOM", "type": "signal", "thickness_mm": 0.035, "material": "copper"},
                ]
            
            z_offset = 0
            layer_objects = []
            
            for layer in layers:
                layer_name = f"{name}_{layer['name']}"
                
                if layer['type'] == 'dielectric':
                    # 介质层
                    hfss.modeler.create_box(
                        origin=[-board_width_mm / 2, -board_length_mm / 2, z_offset],
                        sizes=[board_width_mm, board_length_mm, layer['thickness_mm']],
                        name=layer_name,
                        material=layer['material'],
                    )
                else:
                    # 金属层
                    hfss.modeler.create_box(
                        origin=[-board_width_mm / 2, -board_length_mm / 2, z_offset],
                        sizes=[board_width_mm, board_length_mm, layer['thickness_mm']],
                        name=layer_name,
                        material=layer['material'],
                    )
                
                layer_objects.append(layer_name)
                z_offset += layer['thickness_mm']
            
            # 创建整体封装（可选）
            total_thickness = sum(l['thickness_mm'] for l in layers)
            
            return f"""✅ 创建 PCB 叠层 '{name}' 成功

📊 叠层配置:
总厚度: {total_thickness:.3f} mm
板尺寸: {board_width_mm} x {board_length_mm} mm
层数: {len(layers)}

📋 叠层结构:
"""
            for i, layer in enumerate(layers):
                layer_type_cn = {
                    "signal": "信号层",
                    "dielectric": "介质层",
                    "ground": "接地层",
                    "power": "电源层",
                }.get(layer['type'], layer['type'])
                layer_info += f"  {i+1}. {layer['name']} ({layer_type_cn}) - {layer['thickness_mm']}mm {layer['material']}\n"
            
            return result + layer_info
            
        except Exception as e:
            return f"❌ 创建 PCB 叠层失败: {str(e)}"
    
    @mcp.tool()
    def create_trace(
        name: str,
        layer: str,
        start_point: List[float],
        end_point: List[float],
        width_mm: float = 0.2,
        height_mm: float = 0.035,
    ) -> str:
        """
        创建 PCB 走线
        
        Args:
            name: 走线名称
            layer: 所在层名
            start_point: 起点 [x, y] (mm)
            end_point: 终点 [x, y] (mm)
            width_mm: 线宽 (mm)
            height_mm: 铜箔厚度 (mm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 计算走线方向和长度
            dx = end_point[0] - start_point[0]
            dy = end_point[1] - start_point[1]
            
            # 创建走线矩形
            if abs(dx) > abs(dy):
                # 水平走线
                origin = [
                    min(start_point[0], end_point[0]),
                    start_point[1] - width_mm / 2,
                    0,  # Z 坐标由层决定
                ]
                sizes = [abs(dx), width_mm, height_mm]
            else:
                # 垂直走线
                origin = [
                    start_point[0] - width_mm / 2,
                    min(start_point[1], end_point[1]),
                    0,
                ]
                sizes = [width_mm, abs(dy), height_mm]
            
            hfss.modeler.create_box(
                origin=origin,
                sizes=sizes,
                name=name,
                material="copper",
            )
            
            return f"✅ 创建走线 '{name}' 成功\n层: {layer}\n线宽: {width_mm} mm\n长度: {(dx**2 + dy**2)**0.5:.2f} mm"
        except Exception as e:
            return f"❌ 创建走线失败: {str(e)}"
    
    @mcp.tool()
    def create_via(
        name: str,
        position: List[float],
        drill_diameter_mm: float = 0.3,
        pad_diameter_mm: float = 0.6,
        start_layer: str = "TOP",
        end_layer: str = "BOTTOM",
        antipad_diameter_mm: float = 0.8,
    ) -> str:
        """
        创建过孔
        
        Args:
            name: 过孔名称
            position: 位置 [x, y] (mm)
            drill_diameter_mm: 钻孔直径 (mm)
            pad_diameter_mm: 焊盘直径 (mm)
            start_layer: 起始层
            end_layer: 结束层
            antipad_diameter_mm: 反焊盘直径 (mm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 创建钻孔
            hfss.modeler.create_cylinder(
                origin=[position[0], position[1], 0],
                radius=drill_diameter_mm / 2,
                height=1.5,  # 总板厚，需要根据实际调整
                orientation="Z",
                name=f"{name}_drill",
                material="vacuum",
            )
            
            # 创建焊盘（顶层）
            hfss.modeler.create_cylinder(
                origin=[position[0], position[1], 0],
                radius=pad_diameter_mm / 2,
                height=0.035,
                orientation="Z",
                name=f"{name}_pad_top",
                material="copper",
            )
            
            # 创建焊盘（底层）
            hfss.modeler.create_cylinder(
                origin=[position[0], position[1], 1.465],
                radius=pad_diameter_mm / 2,
                height=0.035,
                orientation="Z",
                name=f"{name}_pad_bottom",
                material="copper",
            )
            
            # 创建过孔铜壁
            hfss.modeler.create_cylinder(
                origin=[position[0], position[1], 0],
                radius=drill_diameter_mm / 2,
                height=1.5,
                orientation="Z",
                name=f"{name}_barrel",
                material="copper",
            )
            hfss.modeler.subtract(
                f"{name}_barrel",
                [f"{name}_drill"],
                keep_originals=False,
            )
            
            # 合并铜部分
            hfss.modeler.unite(
                [f"{name}_pad_top", f"{name}_pad_bottom", f"{name}_barrel"],
                new_name=name,
            )
            
            return f"""✅ 创建过孔 '{name}' 成功
位置: ({position[0]}, {position[1]}) mm
钻孔直径: {drill_diameter_mm} mm
焊盘直径: {pad_diameter_mm} mm
连接层: {start_layer} -> {end_layer}
"""
        except Exception as e:
            return f"❌ 创建过孔失败: {str(e)}"
    
    @mcp.tool()
    def create_ground_plane(
        name: str = "GND",
        width_mm: float = 100.0,
        length_mm: float = 100.0,
        clearance_mm: float = 0.5,
        keepout_regions: Optional[List[Dict]] = None,
    ) -> str:
        """
        创建接地平面
        
        Args:
            name: 名称
            width_mm: 宽度 (mm)
            length_mm: 长度 (mm)
            clearance_mm: 边缘间隙 (mm)
            keepout_regions: 禁布区列表，每个包含:
                - center: [x, y] (mm)
                - width: 宽度 (mm)
                - length: 长度 (mm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 创建完整的接地平面
            hfss.modeler.create_box(
                origin=[-width_mm / 2, -length_mm / 2, 0],
                sizes=[width_mm, length_mm, 0.035],
                name=name,
                material="copper",
            )
            
            # 减去禁布区
            if keepout_regions:
                for i, region in enumerate(keepout_regions):
                    keepout_name = f"{name}_keepout_{i}"
                    center = region['center']
                    w = region['width']
                    l = region['length']
                    
                    hfss.modeler.create_box(
                        origin=[center[0] - w / 2, center[1] - l / 2, -0.01],
                        sizes=[w, l, 0.075],
                        name=keepout_name,
                        material="vacuum",
                    )
                    
                    hfss.modeler.subtract(
                        name,
                        [keepout_name],
                        keep_originals=False,
                    )
            
            return f"✅ 创建接地平面 '{name}' 成功\n尺寸: {width_mm} x {length_mm} mm"
        except Exception as e:
            return f"❌ 创建接地平面失败: {str(e)}"
    
    @mcp.tool()
    def create_component_pad(
        name: str,
        position: List[float],
        pad_width_mm: float = 1.0,
        pad_length_mm: float = 1.5,
        pad_height_mm: float = 0.035,
        layer: str = "TOP",
    ) -> str:
        """
        创建元件焊盘
        
        Args:
            name: 焊盘名称
            position: 位置 [x, y] (mm)
            pad_width_mm: 焊盘宽度 (mm)
            pad_length_mm: 焊盘长度 (mm)
            pad_height_mm: 铜箔厚度 (mm)
            layer: 所在层
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            hfss.modeler.create_box(
                origin=[position[0] - pad_width_mm / 2, position[1] - pad_length_mm / 2, 0],
                sizes=[pad_width_mm, pad_length_mm, pad_height_mm],
                name=name,
                material="copper",
            )
            
            return f"✅ 创建焊盘 '{name}' 成功\n位置: ({position[0]}, {position[1]}) mm\n尺寸: {pad_width_mm} x {pad_length_mm} mm"
        except Exception as e:
            return f"❌ 创建焊盘失败: {str(e)}"
    
    @mcp.tool()
    def create_pcb_port(
        signal_name: str,
        ground_name: str,
        port_name: str = "Port1",
        impedance: float = 50.0,
        port_type: str = "wave",
    ) -> str:
        """
        创建 PCB 端口（信号到参考平面）
        
        Args:
            signal_name: 信号对象名称
            ground_name: 参考地对象名称
            port_name: 端口名称
            impedance: 特性阻抗 (Ohm)
            port_type: 端口类型 (wave/lumped)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 获取信号对象的面
            signal_faces = hfss.modeler.get_object_faces(signal_name)
            if not signal_faces:
                return f"❌ 信号对象 '{signal_name}' 没有面"
            
            # 选择最小的面作为端口
            min_area = float('inf')
            port_face = None
            for face in signal_faces:
                area = hfss.modeler.get_face_area(face)
                if area < min_area:
                    min_area = area
                    port_face = face
            
            if port_type == "wave":
                hfss.wave_port(
                    assignment=port_face,
                    name=port_name,
                    impedance=impedance,
                    renormalize=True,
                )
            else:
                hfss.lumped_port(
                    assignment=port_face,
                    name=port_name,
                    impedance=impedance,
                    renormalize=True,
                )
            
            return f"✅ 创建 PCB 端口 '{port_name}' 成功\n类型: {port_type}\n阻抗: {impedance} Ohm"
        except Exception as e:
            return f"❌ 创建 PCB 端口失败: {str(e)}"
    
    @mcp.tool()
    def create_pcb_setup(
        setup_name: str = "PCB_Setup",
        frequency_ghz: float = 5.0,
        max_passes: int = 20,
        max_delta_s: float = 0.02,
        sweep_start_ghz: float = 0.1,
        sweep_stop_ghz: float = 10.0,
        sweep_type: str = "Interpolating",
    ) -> str:
        """
        创建 PCB 仿真求解设置
        
        Args:
            setup_name: 求解设置名称
            frequency_ghz: 求解频率 (GHz)
            max_passes: 最大迭代次数
            max_delta_s: S 参数收敛阈值
            sweep_start_ghz: 扫频起始频率 (GHz)
            sweep_stop_ghz: 扫频终止频率 (GHz)
            sweep_type: 扫频类型 (Fast/Interpolating/Discrete)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 创建求解设置
            setup = hfss.create_setup(
                name=setup_name,
                setup_type="DrivenTerminal",
            )
            
            setup.props["Frequency"] = f"{frequency_ghz}GHz"
            setup.props["MaximumPasses"] = max_passes
            setup.props["MaxDeltaS"] = max_delta_s
            
            # 创建频率扫描
            sweep_name = f"{setup_name}_sweep"
            hfss.create_linear_count_sweep(
                setup=setup_name,
                unit="GHz",
                start_frequency=sweep_start_ghz,
                stop_frequency=sweep_stop_ghz,
                num_of_freq_points=1000,
                sweep_type=sweep_type,
                name=sweep_name,
            )
            
            return f"""✅ 创建 PCB 求解设置 '{setup_name}' 成功

📊 设置参数:
求解频率: {frequency_ghz} GHz
最大迭代: {max_passes} 次
收敛阈值: ΔS = {max_delta_s}

📈 频率扫描:
起始频率: {sweep_start_ghz} GHz
终止频率: {sweep_stop_ghz} GHz
扫频类型: {sweep_type}
"""
        except Exception as e:
            return f"❌ 创建 PCB 求解设置失败: {str(e)}"
    
    @mcp.tool()
    def import_brd_file(
        brd_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        导入 Allegro BRD 文件到 HFSS
        
        Args:
            brd_path: BRD 文件路径
            output_path: 输出 AEDT 文件路径（留空则自动生成）
        """
        try:
            from pyaedt import Hfss3dLayout
            
            if output_path is None:
                output_path = brd_path.replace('.brd', '_hfss.aedt')
            
            # 使用 HFSS 3D Layout 导入
            hfss3d = Hfss3dLayout(
                projectname=brd_path,
                specified_version="2022.2",
            )
            
            return f"✅ 导入 BRD 文件成功\n输入: {brd_path}\n输出: {output_path}"
        except Exception as e:
            return f"❌ 导入 BRD 文件失败: {str(e)}"
    
    @mcp.tool()
    def import_odb_file(
        odb_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        导入 ODB++ 文件到 HFSS
        
        Args:
            odb_path: ODB++ 文件路径
            output_path: 输出 AEDT 文件路径（留空则自动生成）
        """
        try:
            from pyaedt import Hfss3dLayout
            
            if output_path is None:
                output_path = odb_path.replace('.tgz', '_hfss.aedt').replace('.zip', '_hfss.aedt')
            
            hfss3d = Hfss3dLayout(
                projectname=odb_path,
                specified_version="2022.2",
            )
            
            return f"✅ 导入 ODB++ 文件成功\n输入: {odb_path}\n输出: {output_path}"
        except Exception as e:
            return f"❌ 导入 ODB++ 文件失败: {str(e)}"
    
    @mcp.tool()
    def create_diff_pair(
        name: str,
        positive_trace: str,
        negative_trace: str,
        impedance: float = 100.0,
    ) -> str:
        """
        创建差分对
        
        Args:
            name: 差分对名称
            positive_trace: 正极走线名称
            negative_trace: 负极走线名称
            impedance: 差分阻抗 (Ohm)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 创建差分对定义
            hfss.set_differential_pair(
                positive=positive_trace,
                negative=negative_trace,
                name=name,
                common_name=f"{name}_CM",
            )
            
            return f"""✅ 创建差分对 '{name}' 成功
正极: {positive_trace}
负极: {negative_trace}
差分阻抗: {impedance} Ohm
"""
        except Exception as e:
            return f"❌ 创建差分对失败: {str(e)}"
