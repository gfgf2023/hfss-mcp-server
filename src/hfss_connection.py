# HFSS MCP Server - HFSS 连接管理
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class HFSSConnection:
    """管理与 HFSS/AEDT 的连接"""
    
    def __init__(
        self,
        project_path: Optional[str] = None,
        design_name: str = "HFSSDesign1",
        solution_type: str = "DrivenModal",
        desktop_version: str = "2022.2",
        non_graphical: bool = False,
        new_session: bool = False,
    ):
        self.project_path = project_path
        self.design_name = design_name
        self.solution_type = solution_type
        self.desktop_version = desktop_version
        self.non_graphical = non_graphical
        self.new_session = new_session
        self._hfss = None
        self._desktop = None
        
    def connect(self):
        """建立与 HFSS 的连接"""
        try:
            # 兼容 PyAEDT 0.x 和 1.x
            try:
                from ansys.aedt.core import Hfss
            except ImportError:
                from pyaedt import Hfss
            
            if self.project_path:
                self._hfss = Hfss(
                    projectname=self.project_path,
                    designname=self.design_name,
                    solution_type=self.solution_type,
                    specified_version=self.desktop_version,
                    non_graphical=self.non_graphical,
                    new_desktop_session=self.new_session,
                )
            else:
                # 创建新项目
                self._hfss = Hfss(
                    designname=self.design_name,
                    solution_type=self.solution_type,
                    specified_version=self.desktop_version,
                    non_graphical=self.non_graphical,
                    new_desktop_session=self.new_session,
                )
            
            logger.info(f"Connected to HFSS: {self._hfss.project_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to HFSS: {e}")
            return False
    
    @property
    def hfss(self):
        """获取 HFSS 实例"""
        if self._hfss is None:
            raise RuntimeError(
                "未连接到 HFSS。请先调用 connect_hfss() 建立连接。\n"
                "如果使用 MCP 客户端，请先调用 connect_hfss 工具。"
            )
        return self._hfss
    
    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._hfss is not None
    
    def disconnect(self):
        """断开连接"""
        if self._hfss:
            try:
                self._hfss.release_desktop()
            except:
                pass
            self._hfss = None
    
    def save_project(self, path: Optional[str] = None):
        """保存项目"""
        if path:
            self.hfss.save_project(path)
        else:
            self.hfss.save_project()
    
    def close_project(self):
        """关闭项目"""
        if self._hfss:
            self.hfss.close_project()
            self._hfss = None


class HFSSManager:
    """HFSS 连接管理器 - 单例模式"""
    
    _instance: Optional[HFSSConnection] = None
    _transport_mode: str = "stdio"  # 记录传输模式，用于安全检查
    
    @classmethod
    def get_connection(cls) -> HFSSConnection:
        """获取当前连接"""
        if cls._instance is None:
            cls._instance = HFSSConnection()
        if not cls._instance.is_connected:
            raise RuntimeError(
                "HFSS 连接尚未建立。请先调用 connect_hfss() 工具连接到 HFSS/AEDT。\n"
                "示例: connect_hfss(design_name=\"MyDesign\", solution_type=\"DrivenModal\")"
            )
        return cls._instance
    
    @classmethod
    def create_connection(
        cls,
        project_path: Optional[str] = None,
        design_name: str = "HFSSDesign1",
        solution_type: str = "DrivenModal",
        desktop_version: str = "2022.2",
        non_graphical: bool = False,
        new_session: bool = False,
    ) -> HFSSConnection:
        """创建新连接"""
        if cls._instance:
            cls._instance.disconnect()
        
        cls._instance = HFSSConnection(
            project_path=project_path,
            design_name=design_name,
            solution_type=solution_type,
            desktop_version=desktop_version,
            non_graphical=non_graphical,
            new_session=new_session,
        )
        success = cls._instance.connect()
        if not success:
            instance = cls._instance
            cls._instance = None
            raise RuntimeError(
                "无法连接到 HFSS/AEDT。请检查：\n"
                "1. Ansys AEDT 是否已安装并正在运行\n"
                "2. PyAEDT 是否已安装 (pip install pyaedt)\n"
                "3. AEDT 版本号是否正确 (当前: {desktop_version})\n"
                "4. 如果是 Linux，需要 AEDT 2022 R2+ 并使用 gRPC"
            )
        return cls._instance
    
    @classmethod
    def disconnect(cls):
        """断开当前连接"""
        if cls._instance:
            cls._instance.disconnect()
            cls._instance = None
    
    @classmethod
    def set_transport_mode(cls, mode: str):
        """设置传输模式（由 server.py 在启动时调用）"""
        cls._transport_mode = mode
    
    @classmethod
    def get_transport_mode(cls) -> str:
        """获取当前传输模式"""
        return cls._transport_mode
