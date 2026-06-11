#!/usr/bin/env python3
"""
HFSS MCP Server - AEDT 2022 版本连接示例

针对 AEDT 2022 R1/R2 的特殊配置
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def connect_2022_r1():
    """
    连接 AEDT 2022 R1 (仅 Windows, COM 接口)
    
    注意: 2022 R1 不支持 gRPC，只能在 Windows 上使用 COM 接口
    """
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 连接到 AEDT 2022 R1
            result = await session.call_tool(
                "connect_hfss",
                arguments={
                    "design_name": "HFSSDesign1",
                    "solution_type": "DrivenModal",
                    "desktop_version": "2022.1",  # 指定 2022 R1
                    "non_graphical": False,
                    "new_session": True,  # 启动新会话
                },
            )
            print(result.content[0].text)


async def connect_2022_r2():
    """
    连接 AEDT 2022 R2 (支持 gRPC, Windows/Linux)
    
    推荐使用 gRPC 接口，性能更好
    """
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.server"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 连接到 AEDT 2022 R2
            result = await session.call_tool(
                "connect_hfss",
                arguments={
                    "design_name": "HFSSDesign1",
                    "solution_type": "DrivenModal",
                    "desktop_version": "2022.2",  # 指定 2022 R2
                    "non_graphical": False,
                },
            )
            print(result.content[0].text)


async def connect_remote_2022_r2():
    """
    通过 gRPC 远程连接 AEDT 2022 R2
    
    需要在远程机器上启动 AEDT gRPC 服务
    """
    from pyaedt import Desktop
    
    # 远程连接配置
    desktop = Desktop(
        version="2022.2",
        non_graphical=True,
        new_desktop_session=False,
        # 远程连接参数
        # hostname="remote-server-ip",
        # port=50051,
    )
    
    # 然后创建 HFSS 实例
    from pyaedt import Hfss
    
    hfss = Hfss(
        designname="HFSSDesign1",
        solution_type="DrivenModal",
        specified_version="2022.2",
        non_graphical=True,
    )
    
    print(f"Connected to remote AEDT: {hfss.project_name}")


async def main():
    """示例主函数"""
    
    print("=" * 60)
    print("AEDT 2022 版本连接示例")
    print("=" * 60)
    
    print("""
请选择连接方式:

1. AEDT 2022 R1 (仅 Windows, COM 接口)
2. AEDT 2022 R2 (推荐, gRPC 接口)
3. 远程连接 AEDT 2022 R2

注意事项:
- 2022 R1 只能在 Windows 上使用
- 2022 R2 推荐使用 gRPC 接口
- 远程连接需要在服务器上启动 gRPC 服务
    """)
    
    choice = input("请选择 (1/2/3): ").strip()
    
    if choice == "1":
        await connect_2022_r1()
    elif choice == "2":
        await connect_2022_r2()
    elif choice == "3":
        await connect_remote_2022_r2()
    else:
        print("无效选择")


if __name__ == "__main__":
    asyncio.run(main())
