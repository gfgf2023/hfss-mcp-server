#!/usr/bin/env python3
"""
HFSS MCP Server - Ansys HFSS 的模型上下文协议服务器
用于天线设计仿真和 PCB 仿真
"""

import argparse
import logging
import sys
from typing import Optional

from fastmcp import FastMCP

from .tools import (
    register_project_tools,
    register_geometry_tools,
    register_material_tools,
    register_antenna_tools,
    register_pcb_tools,
    register_setup_tools,
    register_results_tools,
    register_script_tools,
)
from .resources import register_resources
from .hfss_connection import HFSSManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_server(name: str = "HFSS-MCP-Server") -> FastMCP:
    """
    创建 HFSS MCP 服务器实例
    
    Args:
        name: 服务器名称
        
    Returns:
        FastMCP 服务器实例
    """
    # 创建 MCP 服务器
    mcp = FastMCP(
        name=name,
        instructions="""
        HFSS MCP Server - 用于 Ansys HFSS 电磁仿真
        
        这个服务器提供了以下功能：
        
        1. 项目管理
           - 连接/断开 HFSS
           - 保存/关闭项目
           - 列出项目信息
        
        2. 几何建模
           - 创建基本几何体（长方体、圆柱、球体等）
           - 创建 2D 对象（矩形、圆形、多边形）
           - 布尔运算（合并、减去）
           - 对象操作（移动、旋转、复制）
        
        3. 材料管理
           - 设置材料属性
           - 创建自定义材料
           - 材料库查询
        
        4. 天线设计
           - 创建常用天线（贴片、偶极子、喇叭）
           - 创建天线阵列
           - 波端口和集总端口
           - 天线仿真设置
        
        5. PCB 仿真
           - 创建 PCB 叠层
           - 走线、过孔、焊盘
           - 接地平面
           - 差分对
           - 导入 BRD/ODB 文件
        
        6. 求解设置
           - 创建求解配置
           - 频率扫描
           - 网格设置
           - 运行仿真
        
        7. 后处理
           - S 参数分析
           - 天线参数（增益、带宽、VSWR）
           - 远场方向图
           - 阻抗分析
           - 导出 Touchstone 文件
        """,
    )
    
    # 注册所有工具
    logger.info("Registering project tools...")
    register_project_tools(mcp)
    
    logger.info("Registering geometry tools...")
    register_geometry_tools(mcp)
    
    logger.info("Registering material tools...")
    register_material_tools(mcp)
    
    logger.info("Registering antenna tools...")
    register_antenna_tools(mcp)
    
    logger.info("Registering PCB tools...")
    register_pcb_tools(mcp)
    
    logger.info("Registering setup tools...")
    register_setup_tools(mcp)
    
    logger.info("Registering results tools...")
    register_results_tools(mcp)
    
    logger.info("Registering script tools...")
    register_script_tools(mcp)
    
    # 注册资源
    logger.info("Registering resources...")
    register_resources(mcp)
    
    logger.info(f"Server '{name}' created with all tools and resources")
    
    return mcp


def main(
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8765,
    name: str = "HFSS-MCP-Server",
):
    """
    启动 HFSS MCP 服务器
    
    Args:
        transport: 传输方式 (stdio/http/sse)
        host: HTTP 监听地址
        port: HTTP 监听端口
        name: 服务器名称
    """
    logger.info(f"Starting HFSS MCP Server...")
    logger.info(f"Transport: {transport}")
    
    # 记录传输模式，用于脚本执行安全检查
    HFSSManager.set_transport_mode(transport)
    
    if transport in ("http", "sse"):
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
    
    # 创建服务器
    mcp = create_server(name)
    
    # 启动服务器
    try:
        if transport == "stdio":
            logger.info("Starting STDIO transport...")
            mcp.run(transport="stdio")
        elif transport == "http":
            logger.info(f"Starting HTTP transport on {host}:{port}...")
            mcp.run(transport="http", host=host, port=port)
        elif transport == "sse":
            logger.info(f"Starting SSE transport on {host}:{port}...")
            mcp.run(transport="sse", host=host, port=port)
        else:
            logger.error(f"Unknown transport: {transport}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


def cli():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="HFSS MCP Server - Ansys HFSS 的模型上下文协议服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 STDIO 传输（默认）
  python -m src.server
  
  # 使用 HTTP 传输
  python -m src.server --transport http --port 8765
  
  # 使用 SSE 传输
  python -m src.server --transport sse --port 8765
        """,
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="传输方式 (默认: stdio)",
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP/SSE 监听地址 (默认: 127.0.0.1)",
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="HTTP/SSE 监听端口 (默认: 8765)",
    )
    
    parser.add_argument(
        "--name",
        default="HFSS-MCP-Server",
        help="服务器名称 (默认: HFSS-MCP-Server)",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式",
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 启动服务器
    main(
        transport=args.transport,
        host=args.host,
        port=args.port,
        name=args.name,
    )


if __name__ == "__main__":
    cli()
