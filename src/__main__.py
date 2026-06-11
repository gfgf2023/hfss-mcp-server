#!/usr/bin/env python3
"""
HFSS MCP Server - 入口点
允许使用 python -m src.server 运行
"""

from .server import cli

if __name__ == "__main__":
    cli()
