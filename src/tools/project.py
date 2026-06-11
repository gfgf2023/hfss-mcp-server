# HFSS MCP Server - 项目管理工具
from typing import Optional
from ..hfss_connection import HFSSManager
import logging

logger = logging.getLogger(__name__)


def register_project_tools(mcp):
    """注册项目管理相关的 MCP tools"""
    
    @mcp.tool()
    def connect_hfss(
        project_path: Optional[str] = None,
        design_name: str = "HFSSDesign1",
        solution_type: str = "DrivenModal",
        desktop_version: str = "2022.2",
        non_graphical: bool = False,
        new_session: bool = False,
    ) -> str:
        """
        连接到 HFSS/AEDT 实例
        
        Args:
            project_path: 项目文件路径 (.aedt)，留空则创建新项目
            design_name: 设计名称
            solution_type: 求解类型 (DrivenModal/DrivenTerminal/Numeric)
            desktop_version: AEDT 版本号
            non_graphical: 是否无界面模式
            new_session: 是否启动新的 AEDT 会话
            
        Returns:
            连接状态信息
        """
        try:
            conn = HFSSManager.create_connection(
                project_path=project_path,
                design_name=design_name,
                solution_type=solution_type,
                desktop_version=desktop_version,
                non_graphical=non_graphical,
                new_session=new_session,
            )
            
            return f"""✅ 已连接到 HFSS
项目: {conn.hfss.project_name}
设计: {design_name}
求解类型: {solution_type}
版本: {desktop_version}
"""
        except Exception as e:
            return f"❌ 连接失败: {str(e)}"
    
    @mcp.tool()
    def disconnect_hfss() -> str:
        """断开与 HFSS 的连接"""
        try:
            HFSSManager.disconnect()
            return "✅ 已断开 HFSS 连接"
        except Exception as e:
            return f"❌ 断开失败: {str(e)}"
    
    @mcp.tool()
    def save_project(path: Optional[str] = None) -> str:
        """
        保存当前项目
        
        Args:
            path: 保存路径，留空则保存到当前位置
        """
        try:
            conn = HFSSManager.get_connection()
            conn.save_project(path)
            return f"✅ 项目已保存到: {path or conn.hfss.project_path}"
        except Exception as e:
            return f"❌ 保存失败: {str(e)}"
    
    @mcp.tool()
    def list_projects() -> str:
        """列出 AEDT 中打开的项目"""
        try:
            conn = HFSSManager.get_connection()
            projects = conn.hfss.project_list
            if not projects:
                return "没有打开的项目"
            
            result = "打开的项目:\n"
            for i, proj in enumerate(projects, 1):
                result += f"{i}. {proj}\n"
            return result
        except Exception as e:
            return f"❌ 获取项目列表失败: {str(e)}"
    
    @mcp.tool()
    def get_project_info() -> str:
        """获取当前项目信息"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            info = f"""📋 项目信息:
项目名称: {hfss.project_name}
项目路径: {hfss.project_path}
设计名称: {hfss.design_name}
求解类型: {hfss.solution_type}
网格类型: {hfss.mesh_type}
"""
            return info
        except Exception as e:
            return f"❌ 获取项目信息失败: {str(e)}"
