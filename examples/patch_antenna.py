#!/usr/bin/env python3
"""
HFSS MCP Server - 贴片天线设计示例

这个示例展示如何使用 HFSS MCP Server 设计一个 2.4GHz 贴片天线
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """运行贴片天线设计示例"""
    
    # 服务器参数
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"],
    )
    
    print("=" * 60)
    print("HFSS MCP Server - 贴片天线设计示例")
    print("=" * 60)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            
            print("\n1. 连接到 HFSS...")
            result = await session.call_tool(
                "connect_hfss",
                arguments={
                    "design_name": "PatchAntenna",
                    "solution_type": "DrivenModal",
                    "non_graphical": False,
                },
            )
            print(result.content[0].text)
            
            print("\n2. 创建 2.4GHz 贴片天线...")
            result = await session.call_tool(
                "create_patch_antenna",
                arguments={
                    "name": "Patch2G4",
                    "frequency_ghz": 2.4,
                    "substrate_material": "FR4_epoxy",
                    "substrate_height_mm": 1.6,
                    "feed_offset_mm": 5.0,
                    "feed_width_mm": 2.0,
                },
            )
            print(result.content[0].text)
            
            print("\n3. 创建波端口...")
            result = await session.call_tool(
                "create_wave_port",
                arguments={
                    "object_name": "Patch2G4_feed",
                    "port_name": "WavePort1",
                    "impedance": 50.0,
                },
            )
            print(result.content[0].text)
            
            print("\n4. 创建求解设置...")
            result = await session.call_tool(
                "create_antenna_setup",
                arguments={
                    "setup_name": "Setup1",
                    "frequency_ghz": 2.4,
                    "max_passes": 20,
                    "max_delta_s": 0.02,
                    "frequency_sweep_start_ghz": 1.5,
                    "frequency_sweep_stop_ghz": 3.5,
                    "sweep_type": "Interpolating",
                },
            )
            print(result.content[0].text)
            
            print("\n5. 运行仿真...")
            result = await session.call_tool(
                "run_simulation",
                arguments={
                    "setup_name": "Setup1",
                },
            )
            print(result.content[0].text)
            
            print("\n6. 获取 S 参数...")
            result = await session.call_tool(
                "get_return_loss",
                arguments={
                    "setup_name": "Setup1",
                    "sweep_name": "Setup1_sweep",
                    "port": 1,
                },
            )
            print(result.content[0].text)
            
            print("\n7. 获取天线参数...")
            result = await session.call_tool(
                "get_antenna_parameters",
                arguments={
                    "setup_name": "Setup1",
                    "sweep_name": "Setup1_sweep",
                },
            )
            print(result.content[0].text)
            
            print("\n8. 获取 VSWR...")
            result = await session.call_tool(
                "get_vswr",
                arguments={
                    "setup_name": "Setup1",
                    "sweep_name": "Setup1_sweep",
                    "port": 1,
                },
            )
            print(result.content[0].text)
            
            print("\n9. 获取远场方向图...")
            result = await session.call_tool(
                "get_far_field",
                arguments={
                    "setup_name": "Setup1",
                    "sweep_name": "Setup1_sweep",
                    "phi_cut": 0.0,
                },
            )
            print(result.content[0].text)
            
            print("\n10. 导出 Touchstone 文件...")
            result = await session.call_tool(
                "export_touchstone",
                arguments={
                    "filename": "patch_antenna.s1p",
                    "setup_name": "Setup1",
                    "sweep_name": "Setup1_sweep",
                },
            )
            print(result.content[0].text)
            
            print("\n11. 保存项目...")
            result = await session.call_tool(
                "save_project",
                arguments={},
            )
            print(result.content[0].text)
            
            print("\n12. 断开连接...")
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
