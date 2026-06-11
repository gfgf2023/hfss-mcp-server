# HFSS MCP Server - 后处理工具
from typing import Optional, List, Dict
from ..hfss_connection import HFSSManager
import logging

logger = logging.getLogger(__name__)


def register_results_tools(mcp):
    """注册后处理相关的 MCP tools"""
    
    @mcp.tool()
    def get_s_parameters(
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
        port_i: int = 1,
        port_j: int = 1,
        output_format: str = "dB",
    ) -> str:
        """
        获取 S 参数
        
        Args:
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            port_i: 端口 i
            port_j: 端口 j
            output_format: 输出格式 (dB/real_imag/magnitude_phase)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            expression = f"S({port_i},{port_j})"
            
            # 获取 S 参数数据
            data = hfss.post.get_solution_data(
                expressions=expression,
                setup_sweep_name=f"{setup_name} : {sweep_name}",
            )
            
            if data is None:
                return f"❌ 未找到 S 参数数据"
            
            frequencies = data.primary_sweep_values
            values = data.data_real()
            
            if output_format == "dB":
                import numpy as np
                values_db = 20 * np.log10(np.abs(values))
                
                result = f"📈 S({port_i},{port_j}) 参数 (dB):\n"
                result += f"{'频率 (GHz)':<15} {'S参数 (dB)':<15}\n"
                result += "-" * 30 + "\n"
                
                # 采样显示
                step = max(1, len(frequencies) // 20)
                for i in range(0, len(frequencies), step):
                    freq = float(frequencies[i])
                    result += f"{freq:<15.3f} {values_db[i]:<15.3f}\n"
                
                # 找谐振点
                min_idx = np.argmin(values_db)
                result += f"\n🎯 谐振频率: {float(frequencies[min_idx]):.3f} GHz\n"
                result += f"   最小回波损耗: {values_db[min_idx]:.3f} dB\n"
                
                return result
            else:
                return f"✅ 获取 S({port_i},{port_j}) 数据成功\n数据点数: {len(frequencies)}"
                
        except Exception as e:
            return f"❌ 获取 S 参数失败: {str(e)}"
    
    @mcp.tool()
    def get_return_loss(
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
        port: int = 1,
    ) -> str:
        """
        获取回波损耗 (S11)
        
        Args:
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            port: 端口号
        """
        return get_s_parameters(setup_name, sweep_name, port, port, "dB")
    
    @mcp.tool()
    def get_insertion_loss(
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
        port_i: int = 1,
        port_j: int = 2,
    ) -> str:
        """
        获取插入损耗 (S21)
        
        Args:
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            port_i: 输入端口
            port_j: 输出端口
        """
        return get_s_parameters(setup_name, sweep_name, port_i, port_j, "dB")
    
    @mcp.tool()
    def get_antenna_parameters(
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
        frequency_ghz: Optional[float] = None,
    ) -> str:
        """
        获取天线参数
        
        Args:
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            frequency_ghz: 频率 (GHz)，留空则返回谐振频率处的参数
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 获取回波损耗
            s11_data = hfss.post.get_solution_data(
                expressions="S(1,1)",
                setup_sweep_name=f"{setup_name} : {sweep_name}",
            )
            
            if s11_data is None:
                return "❌ 未找到天线数据"
            
            import numpy as np
            
            frequencies = s11_data.primary_sweep_values
            s11_values = s11_data.data_real()
            s11_db = 20 * np.log10(np.abs(s11_values))
            
            # 找谐振频率
            min_idx = np.argmin(s11_db)
            resonant_freq = float(frequencies[min_idx])
            min_s11 = s11_db[min_idx]
            
            # 计算带宽（-10dB 带宽）
            threshold = -10.0
            bandwidth_indices = np.where(s11_db < threshold)[0]
            
            if len(bandwidth_indices) > 0:
                bw_start = float(frequencies[bandwidth_indices[0]])
                bw_stop = float(frequencies[bandwidth_indices[-1]])
                bandwidth = bw_stop - bw_start
                fractional_bw = bandwidth / resonant_freq * 100
            else:
                bw_start = bw_stop = bandwidth = fractional_bw = 0
            
            # 获取增益（如果有远场数据）
            try:
                gain_data = hfss.post.get_solution_data(
                    expressions="GainTotal",
                    setup_sweep_name=f"{setup_name} : {sweep_name}",
                )
                if gain_data:
                    gain_values = gain_data.data_real()
                    max_gain = np.max(gain_values)
                    gain_str = f"{max_gain:.2f} dB"
                else:
                    gain_str = "未计算"
            except:
                gain_str = "未计算"
            
            result = f"""📊 天线参数汇总

🎯 谐振频率: {resonant_freq:.3f} GHz
📉 回波损耗: {min_s11:.3f} dB

📈 带宽 (-10dB):
  起始频率: {bw_start:.3f} GHz
  终止频率: {bw_stop:.3f} GHz
  绝对带宽: {bandwidth:.3f} GHz
  相对带宽: {fractional_bw:.2f}%

📡 增益: {gain_str}
"""
            return result
            
        except Exception as e:
            return f"❌ 获取天线参数失败: {str(e)}"
    
    @mcp.tool()
    def get_impedance(
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
        port: int = 1,
    ) -> str:
        """
        获取端口阻抗
        
        Args:
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            port: 端口号
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 获取 Z 参数
            z_data = hfss.post.get_solution_data(
                expressions=f"Z({port},{port})",
                setup_sweep_name=f"{setup_name} : {sweep_name}",
            )
            
            if z_data is None:
                return "❌ 未找到阻抗数据"
            
            import numpy as np
            
            frequencies = z_data.primary_sweep_values
            z_values = z_data.data_complex()
            
            result = f"📈 端口 {port} 阻抗:\n"
            result += f"{'频率 (GHz)':<15} {'实部 (Ω)':<15} {'虚部 (Ω)':<15} {'幅值 (Ω)':<15}\n"
            result += "-" * 60 + "\n"
            
            step = max(1, len(frequencies) // 20)
            for i in range(0, len(frequencies), step):
                freq = float(frequencies[i])
                z_real = np.real(z_values[i])
                z_imag = np.imag(z_values[i])
                z_mag = np.abs(z_values[i])
                result += f"{freq:<15.3f} {z_real:<15.3f} {z_imag:<15.3f} {z_mag:<15.3f}\n"
            
            # 找 50Ω 匹配点
            z_mag_all = np.abs(z_values)
            match_idx = np.argmin(np.abs(z_mag_all - 50))
            result += f"\n🎯 最佳匹配频率: {float(frequencies[match_idx]):.3f} GHz\n"
            result += f"   阻抗: {z_mag_all[match_idx]:.3f} Ω\n"
            
            return result
            
        except Exception as e:
            return f"❌ 获取阻抗失败: {str(e)}"
    
    @mcp.tool()
    def get_vswr(
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
        port: int = 1,
    ) -> str:
        """
        获取电压驻波比 (VSWR)
        
        Args:
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            port: 端口号
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            vswr_data = hfss.post.get_solution_data(
                expressions=f"VSWR({port})",
                setup_sweep_name=f"{setup_name} : {sweep_name}",
            )
            
            if vswr_data is None:
                return "❌ 未找到 VSWR 数据"
            
            import numpy as np
            
            frequencies = vswr_data.primary_sweep_values
            vswr_values = vswr_data.data_real()
            
            result = f"📈 端口 {port} VSWR:\n"
            result += f"{'频率 (GHz)':<15} {'VSWR':<15}\n"
            result += "-" * 30 + "\n"
            
            step = max(1, len(frequencies) // 20)
            for i in range(0, len(frequencies), step):
                freq = float(frequencies[i])
                result += f"{freq:<15.3f} {vswr_values[i]:<15.3f}\n"
            
            # 找最小 VSWR
            min_idx = np.argmin(vswr_values)
            result += f"\n🎯 最小 VSWR: {vswr_values[min_idx]:.3f} @ {float(frequencies[min_idx]):.3f} GHz\n"
            
            # 计算 VSWR < 2 的带宽
            threshold = 2.0
            bw_indices = np.where(vswr_values < threshold)[0]
            if len(bw_indices) > 0:
                bw_start = float(frequencies[bw_indices[0]])
                bw_stop = float(frequencies[bw_indices[-1]])
                result += f"📏 VSWR < {threshold} 带宽: {bw_start:.3f} - {bw_stop:.3f} GHz\n"
            
            return result
            
        except Exception as e:
            return f"❌ 获取 VSWR 失败: {str(e)}"
    
    @mcp.tool()
    def get_far_field(
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
        frequency_ghz: Optional[float] = None,
        phi_cut: float = 0.0,
    ) -> str:
        """
        获取远场方向图
        
        Args:
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            frequency_ghz: 频率 (GHz)
            phi_cut: Phi 切割角度 (度)
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 创建远场设置
            far_field = hfss.insert_infinite_sphere(
                definition="3D",
            )
            
            # 获取远场数据
            gain_data = hfss.post.get_solution_data(
                expressions="GainTotal",
                setup_sweep_name=f"{setup_name} : {sweep_name}",
                domain="Infinite Sphere1",
            )
            
            if gain_data is None:
                return "❌ 未找到远场数据"
            
            import numpy as np
            
            theta = gain_data.primary_sweep_values
            gain = gain_data.data_real()
            gain_db = 10 * np.log10(gain)
            
            # 找最大增益和方向
            max_idx = np.argmax(gain_db)
            max_gain = gain_db[max_idx]
            max_theta = float(theta[max_idx])
            
            result = f"""📊 远场方向图 (Phi={phi_cut}°)

📡 最大增益: {max_gain:.2f} dB
📍 最大方向: Theta = {max_theta:.1f}°

📈 增益 vs Theta:
"""
            step = max(1, len(theta) // 20)
            for i in range(0, len(theta), step):
                t = float(theta[i])
                g = gain_db[i]
                bar = "█" * int(max(0, (g + 20) / 2))
                result += f"  {t:>6.1f}°: {g:>8.2f} dB {bar}\n"
            
            # 计算半功率波束宽度
            half_power = max_gain - 3
            above_half = np.where(gain_db > half_power)[0]
            if len(above_half) > 0:
                hpbw = float(theta[above_half[-1]]) - float(theta[above_half[0]])
                result += f"\n📏 半功率波束宽度 (HPBW): {hpbw:.1f}°\n"
            
            return result
            
        except Exception as e:
            return f"❌ 获取远场数据失败: {str(e)}"
    
    @mcp.tool()
    def export_touchstone(
        filename: str = "results.s2p",
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
    ) -> str:
        """
        导出 Touchstone 文件
        
        Args:
            filename: 输出文件名 (.s1p/.s2p/.snp)
            setup_name: 求解设置名称
            sweep_name: 扫描名称
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            hfss.export_touchstone(
                filename=filename,
                setup_name=setup_name,
                sweep_name=sweep_name,
            )
            
            return f"✅ 导出 Touchstone 文件成功\n文件: {filename}"
        except Exception as e:
            return f"❌ 导出 Touchstone 失败: {str(e)}"
    
    @mcp.tool()
    def export_field_plot(
        quantity: str = "GainTotal",
        output_file: str = "field_plot.svf",
        setup_name: str = "Setup1",
    ) -> str:
        """
        导出场分布图
        
        Args:
            quantity: 场量名称 (GainTotal/E_Field/H_Field 等)
            output_file: 输出文件路径
            setup_name: 求解设置名称
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            # 创建场图
            hfss.post.create_fieldplot_cutplane(
                quantity=quantity,
                setup_name=setup_name,
            )
            
            return f"✅ 创建场图成功\n场量: {quantity}"
        except Exception as e:
            return f"❌ 导出场图失败: {str(e)}"
    
    @mcp.tool()
    def generate_report(
        report_type: str = "s_parameters",
        setup_name: str = "Setup1",
        sweep_name: str = "Sweep1",
        output_file: Optional[str] = None,
    ) -> str:
        """
        生成仿真报告
        
        Args:
            report_type: 报告类型 (s_parameters/antenna/impedance/vswr)
            setup_name: 求解设置名称
            sweep_name: 扫描名称
            output_file: 输出文件路径
        """
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            if report_type == "s_parameters":
                report = get_s_parameters(setup_name, sweep_name, 1, 1, "dB")
                report += "\n" + get_s_parameters(setup_name, sweep_name, 2, 1, "dB")
            elif report_type == "antenna":
                report = get_antenna_parameters(setup_name, sweep_name)
                report += "\n" + get_vswr(setup_name, sweep_name)
            elif report_type == "impedance":
                report = get_impedance(setup_name, sweep_name)
            elif report_type == "vswr":
                report = get_vswr(setup_name, sweep_name)
            else:
                return f"❌ 不支持的报告类型: {report_type}"
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                return f"✅ 报告已保存到: {output_file}\n\n{report}"
            
            return report
            
        except Exception as e:
            return f"❌ 生成报告失败: {str(e)}"
