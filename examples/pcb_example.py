#!/usr/bin/env python3
"""
HFSS MCP Server - PCB 仿真示例

这个示例展示如何使用 HFSS MCP Server 进行 PCB 信号完整性仿真
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """运行 PCB 仿真示例"""
    
    # 服务器参数
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"],
    )
    
    print("=" * 60)
    print("HFSS MCP Server - PCB 仿真示例")
    print("=" * 60)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            
            print("\n1. 连接到 HFSS (DrivenTerminal 模式)...")
            result = await session.call_tool(
                "connect_hfss",
                arguments={
                    "design_name": "PCB_Design",
                    "solution_type": "DrivenTerminal",
                    "non_graphical": False,
                },
            )
            print(result.content[0].text)
            
            print("\n2. 创建 4 层 PCB 叠层...")
            result = await session.call_tool(
                "create_pcb_stackup",
                arguments={
                    "name": "PCB",
                    "layers": [
                        {"name": "TOP", "type": "signal", "thickness_mm": 0.035, "material": "copper"},
                        {"name": "PREPREG", "type": "dielectric", "thickness_mm": 0.2, "material": "FR4_epoxy"},
                        {"name": "GND", "type": "ground", "thickness_mm": 0.035, "material": "copper"},
                        {"name": "CORE", "type": "dielectric", "thickness_mm": 1.0, "material": "FR4_epoxy"},
                        {"name": "PWR", "type": "power", "thickness_mm": 0.035, "material": "copper"},
                        {"name": "PREPREG2", "type": "dielectric", "thickness_mm": 0.2, "material": "FR4_epoxy"},
                        {"name": "BOTTOM", "type": "signal", "thickness_mm": 0.035, "material": "copper"},
                    ],
                    "board_width_mm": 100.0,
                    "board_length_mm": 100.0,
                },
            )
            print(result.content[0].text)
            
            print("\n3. 创建信号走线...")
            # 差分对走线
            result = await session.call_tool(
                "create_trace",
                arguments={
                    "name": "Signal_P",
                    "layer": "TOP",
                    "start_point": [-40.0, 0.0],
                    "end_point": [40.0, 0.0],
                    "width_mm": 0.15,
                },
            )
            print(result.content[0].text)
            
            result = await session.call_tool(
                "create_trace",
                arguments={
                    "name": "Signal_N",
                    "layer": "TOP",
                    "start_point": [-40.0, 0.3],
                    "end_point": [40.0, 0.3],
                    "width_mm": 0.15,
                },
            )
            print(result.content[0].text)
            
            print("\n4. 创建过孔...")
            result = await session.call_tool(
                "create_via",
                arguments={
                    "name": "Via1",
                    "position": [-40.0, 0.0],
                    "drill_diameter_mm": 0.3,
                    "pad_diameter_mm": 0.6,
                    "start_layer": "TOP",
                    "end_layer": "BOTTOM",
                },
            )
            print(result.content[0].text)
            
            result = await session.call_tool(
                "create_via",
                arguments={
                    "name": "Via2",
                    "position": [40.0, 0.0],
                    "drill_diameter_mm": 0.3,
                    "pad_diameter_mm": 0.6,
                    "start_layer": "TOP",
                    "end_layer": "BOTTOM",
                },
            )
            print(result.content[0].text)
            
            print("\n5. 创建差分对...")
            result = await session.call_tool(
                "create_diff_pair",
                arguments={
                    "name": "DiffPair1",
                    "positive_trace": "Signal_P",
                    "negative_trace": "Signal_N",
                    "impedance": 100.0,
                },
            )
            print(result.content[0].text)
            
            print("\n6. 创建 PCB 端口...")
            result = await session.call_tool(
                "create_pcb_port",
                arguments={
                    "signal_name": "Signal_P",
                    "ground_name": "PCB_GND",
                    "port_name": "Port1",
                    "impedance": 50.0,
                    "port_type": "wave",
                },
            )
            print(result.content[0].text)
            
            result = await session.call_tool(
                "create_pcb_port",
                arguments={
                    "signal_name": "Signal_N",
                    "ground_name": "PCB_GND",
                    "port_name": "Port2",
                    "impedance": 50.0,
                    "port_type": "wave",
                },
            )
            print(result.content[0].text)
            
            print("\n7. 创建求解设置...")
            result = await session.call_tool(
                "create_pcb_setup",
                arguments={
                    "setup_name": "PCB_Setup",
                    "frequency_ghz": 5.0,
                    "max_passes": 20,
                    "max_delta_s": 0.02,
                    "sweep_start_ghz": 0.1,
                    "sweep_stop_ghz": 10.0,
                    "sweep_type": "Interpolating",
                },
            )
            print(result.content[0].text)
            
            print("\n8. 运行仿真...")
            result = await session.call_tool(
                "run_simulation",
                arguments={
                    "setup_name": "PCB_Setup",
                },
            )
            print(result.content[0].text)
            
            print("\n9. 获取 S 参数...")
            # 差分 S 参数
            result = await session.call_tool(
                "get_s_parameters",
                arguments={
                    "setup_name": "PCB_Setup",
                    "sweep_name": "PCB_Setup_sweep",
                    "port_i": 1,
                    "port_j": 1,
                    "output_format": "dB",
                },
            )
            print(result.content[0].text)
            
            print("\n10. 获取插入损耗...")
            result = await session.call_tool(
                "get_insertion_loss",
                arguments={
                    "setup_name": "PCB_Setup",
                    "sweep_name": "PCB_Setup_sweep",
                    "port_i": 1,
                    "port_j": 2,
                },
            )
            print(result.content[0].text)
            
            print("\n11. 获取阻抗...")
            result = await session.call_tool(
                "get_impedance",
                arguments={
                    "setup_name": "PCB_Setup",
                    "sweep_name": "PCB_Setup_sweep",
                    "port": 1,
                },
            )
            print(result.content[0].text)
            
            print("\n12. 导出 Touchstone 文件...")
            result = await session.call_tool(
                "export_touchstone",
                arguments={
                    "filename": "pcb_design.s2p",
                    "setup_name": "PCB_Setup",
                    "sweep_name": "PCB_Setup_sweep",
                },
            )
            print(result.content[0].text)
            
            print("\n13. 保存项目...")
            result = await session.call_tool(
                "save_project",
                arguments={},
            )
            print(result.content[0].text)
            
            print("\n14. 断开连接...")
            result = await session.call_tool(
                "disconnect_hfss",
                arguments={},
            )
            print(result.content[0].text)
    
    print("\n" + "=" * 60)
    print("示例完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
