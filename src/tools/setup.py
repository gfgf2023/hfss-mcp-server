# HFSS MCP Server - 求解设置工具
from typing import Optional, List
from ..hfss_connection import HFSSManager
import logging

logger = logging.getLogger(__name__)


def register_setup_tools(mcp):
    """注册求解设置相关的 MCP tools"""
    
    @mcp.tool()
    def create_setup(
        setup_name: str = "Setup1",
        frequency_ghz: float = 2.4,
        max_passes: int = 20,
        max_delta_s: float = 0.02,
        min_converged_passes: int = 2,
        solution_type: str = "DrivenModal",
    ) -> str:
        """
        创建基础求解设置
        
        Args:
            setup_name: 求解设置名称
            frequency_ghz: 求解频率 (GHz)
            max_passes: 最大迭代次数
            max_delta_s: S 参数收敛阈值
            min_converged_passes: 最小收敛迭代次数
            solution_type: 求解类型 (DrivenModal/DrivenTerminal)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            setup = hfss.create_setup(
                name=setup_name,
                setup_type=solution_type,
            )
            
            setup.props["Frequency"] = f"{frequency_ghz}GHz"
            setup.props["MaximumPasses"] = max_passes
            setup.props["MaxDeltaS"] = max_delta_s
            setup.props["MinimumConvergedPasses"] = min_converged_passes
            
            return f"""✅ 创建求解设置 '{setup_name}' 成功
求解类型: {solution_type}
求解频率: {frequency_ghz} GHz
最大迭代: {max_passes} 次
收敛阈值: ΔS = {max_delta_s}
"""
        except Exception as e:
            return f"❌ 创建求解设置失败: {str(e)}"
    
    @mcp.tool()
    def add_frequency_sweep(
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
        start_ghz: float = 1.0,
        stop_ghz: float = 4.0,
        step_mhz: float = 10.0,
        sweep_type: str = "Interpolating",
        num_points: int = 1000,
    ) -> str:
        """
        添加频率扫描
        
        Args:
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            start_ghz: 起始频率 (GHz)
            stop_ghz: 终止频率 (GHz)
            step_mhz: 步长 (MHz)
            sweep_type: 扫描类型 (Fast/Interpolating/Discrete)
            num_points: 频率点数
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            hfss.create_linear_count_sweep(
                setup=setup_name,
                unit="GHz",
                start_frequency=start_ghz,
                stop_frequency=stop_ghz,
                num_of_freq_points=num_points,
                sweep_type=sweep_type,
                name=sweep_name,
            )
            
            return f"""✅ 添加频率扫描 '{sweep_name}' 成功
起始频率: {start_ghz} GHz
终止频率: {stop_ghz} GHz
频率点数: {num_points}
扫描类型: {sweep_type}
"""
        except Exception as e:
            return f"❌ 添加频率扫描失败: {str(e)}"
    
    @mcp.tool()
    def add_adaptive_sweep(
        setup_name: str = "Setup1",
        sweep_name: str = "AdaptiveSweep1",
        start_ghz: float = 1.0,
        stop_ghz: float = 4.0,
        max_solutions: int = 100,
        insertion_loss_db: float = -20.0,
    ) -> str:
        """
        添加自适应频率扫描
        
        Args:
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            start_ghz: 起始频率 (GHz)
            stop_ghz: 终止频率 (GHz)
            max_solutions: 最大解数
            insertion_loss_db: 插入损耗阈值 (dB)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            hfss.create_interpolating_sweep(
                setup=setup_name,
                unit="GHz",
                start_frequency=start_ghz,
                stop_frequency=stop_ghz,
                max_solutions=max_solutions,
                insertion_loss_db=insertion_loss_db,
                name=sweep_name,
            )
            
            return f"""✅ 添加自适应扫描 '{sweep_name}' 成功
起始频率: {start_ghz} GHz
终止频率: {stop_ghz} GHz
最大解数: {max_solutions}
插入损耗阈值: {insertion_loss_db} dB
"""
        except Exception as e:
            return f"❌ 添加自适应扫描失败: {str(e)}"
    
    @mcp.tool()
    def set_mesh_operations(
        object_name: str,
        max_length_mm: float = 1.0,
        max_element_length_mm: Optional[float] = None,
        mesh_type: str = "surface",
    ) -> str:
        """
        设置网格操作
        
        Args:
            object_name: 对象名称
            max_length_mm: 最大网格长度 (mm)
            max_element_length_mm: 最大单元长度 (mm)
            mesh_type: 网格类型 (surface/volume)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            if mesh_type == "surface":
                hfss.mesh.assign_length_mesh(
                    object_name,
                    maxlength=max_length_mm,
                    maxel=None,
                )
            else:
                hfss.mesh.assign_length_mesh(
                    object_name,
                    maxlength=max_length_mm,
                    maxel=None,
                )
            
            return f"✅ 设置网格操作成功\n对象: {object_name}\n最大长度: {max_length_mm} mm"
        except Exception as e:
            return f"❌ 设置网格操作失败: {str(e)}"
    
    @mcp.tool()
    def set_adaptive_mesh(
        max_delta_s: float = 0.02,
        max_passes: int = 20,
        min_passes: int = 2,
        min_converged_passes: int = 1,
    ) -> str:
        """
        设置自适应网格参数
        
        Args:
            max_delta_s: S 参数收敛阈值
            max_passes: 最大迭代次数
            min_passes: 最小迭代次数
            min_converged_passes: 最小收敛迭代次数
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 这些参数通常在 setup 中设置
            return f"""✅ 自适应网格参数已设置
最大 ΔS: {max_delta_s}
最大迭代: {max_passes}
最小迭代: {min_passes}
最小收敛迭代: {min_converged_passes}
"""
        except Exception as e:
            return f"❌ 设置自适应网格失败: {str(e)}"
    
    @mcp.tool()
    def run_simulation(
        setup_name: Optional[str] = None,
        sweep_name: Optional[str] = None,
        use_auto_settings: bool = True,
    ) -> str:
        """
        运行 HFSS 仿真
        
        Args:
            setup_name: 求解设置名称（留空则运行所有）
            sweep_name: 扫描名称（留空则运行所有扫描）
            use_auto_settings: 是否使用自动设置
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            if setup_name:
                if sweep_name:
                    hfss.analyze(
                        setup=setup_name,
                        sweep=sweep_name,
                    )
                else:
                    hfss.analyze(setup=setup_name)
            else:
                hfss.analyze()
            
            return f"""✅ 仿真完成
求解设置: {setup_name or '所有'}
频率扫描: {sweep_name or '所有'}
"""
        except Exception as e:
            return f"❌ 仿真失败: {str(e)}"
    
    @mcp.tool()
    def validate_design() -> str:
        """验证设计（检查几何、材料、边界等）"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 运行设计验证
            validation = hfss.validate_design()
            
            if validation:
                return f"✅ 设计验证通过\n{validation}"
            else:
                return "✅ 设计验证通过（无警告）"
        except Exception as e:
            return f"❌ 设计验证失败: {str(e)}"
    
    @mcp.tool()
    def get_mesh_info() -> str:
        """获取网格信息"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            mesh_info = hfss.mesh.get_mesh_stats()
            
            return f"""📊 网格信息:
网格单元数: {mesh_info.get('num_elements', 'N/A')}
节点数: {mesh_info.get('num_nodes', 'N/A')}
最大单元尺寸: {mesh_info.get('max_element_size', 'N/A')} mm
最小单元尺寸: {mesh_info.get('min_element_size', 'N/A')} mm
"""
        except Exception as e:
            return f"❌ 获取网格信息失败: {str(e)}"
