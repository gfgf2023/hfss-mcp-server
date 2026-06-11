# HFSS MCP Server - 几何建模工具
from typing import List, Optional, Tuple
from ..hfss_connection import HFSSManager
import logging

logger = logging.getLogger(__name__)


def register_geometry_tools(mcp):
    """注册几何建模相关的 MCP tools"""
    
    @mcp.tool()
    def create_box(
        name: str,
        origin: List[float],
        dimensions: List[float],
        material: str = "vacuum",
        color: Optional[List[int]] = None,
    ) -> str:
        """
        创建长方体
        
        Args:
            name: 对象名称
            origin: 起始坐标 [x, y, z] (mm)
            dimensions: 尺寸 [dx, dy, dz] (mm)
            material: 材料名称
            color: RGB 颜色 [r, g, b] (0-255)
        """
        try:
            conn = HFSSManager.get_connection()
            obj = conn.hfss.modeler.create_box(
                origin=origin,
                sizes=dimensions,
                name=name,
                material=material,
            )
            
            if color:
                conn.hfss.modeler.set_object_color(name, color)
            
            return f"✅ 创建长方体 '{name}' 成功\n坐标: {origin}\n尺寸: {dimensions}\n材料: {material}"
        except Exception as e:
            return f"❌ 创建长方体失败: {str(e)}"
    
    @mcp.tool()
    def create_cylinder(
        name: str,
        origin: List[float],
        radius: float,
        height: float,
        axis: str = "Z",
        material: str = "vacuum",
    ) -> str:
        """
        创建圆柱体
        
        Args:
            name: 对象名称
            origin: 底面圆心坐标 [x, y, z] (mm)
            radius: 半径 (mm)
            height: 高度 (mm)
            axis: 轴向 (X/Y/Z)
            material: 材料名称
        """
        try:
            conn = HFSSManager.get_connection()
            obj = conn.hfss.modeler.create_cylinder(
                origin=origin,
                radius=radius,
                height=height,
                orientation=axis,
                name=name,
                material=material,
            )
            return f"✅ 创建圆柱体 '{name}' 成功\n半径: {radius}mm\n高度: {height}mm\n材料: {material}"
        except Exception as e:
            return f"❌ 创建圆柱体失败: {str(e)}"
    
    @mcp.tool()
    def create_sphere(
        name: str,
        origin: List[float],
        radius: float,
        material: str = "vacuum",
    ) -> str:
        """
        创建球体
        
        Args:
            name: 对象名称
            origin: 球心坐标 [x, y, z] (mm)
            radius: 半径 (mm)
            material: 材料名称
        """
        try:
            conn = HFSSManager.get_connection()
            obj = conn.hfss.modeler.create_sphere(
                origin=origin,
                radius=radius,
                name=name,
                material=material,
            )
            return f"✅ 创建球体 '{name}' 成功\n半径: {radius}mm\n材料: {material}"
        except Exception as e:
            return f"❌ 创建球体失败: {str(e)}"
    
    @mcp.tool()
    def create_rectangle(
        name: str,
        origin: List[float],
        dimensions: List[float],
        axis: str = "Z",
        material: str = "vacuum",
    ) -> str:
        """
        创建矩形（2D 对象）
        
        Args:
            name: 对象名称
            origin: 起始坐标 [x, y, z] (mm)
            dimensions: 尺寸 [dx, dy] (mm)
            axis: 法向轴 (X/Y/Z)
            material: 材料名称
        """
        try:
            conn = HFSSManager.get_connection()
            obj = conn.hfss.modeler.create_rectangle(
                origin=origin,
                sizes=[dimensions[0], dimensions[1], 0],
                orientation=axis,
                name=name,
            )
            return f"✅ 创建矩形 '{name}' 成功\n尺寸: {dimensions[0]}mm x {dimensions[1]}mm"
        except Exception as e:
            return f"❌ 创建矩形失败: {str(e)}"
    
    @mcp.tool()
    def create_circle(
        name: str,
        origin: List[float],
        radius: float,
        axis: str = "Z",
    ) -> str:
        """
        创建圆形（2D 对象）
        
        Args:
            name: 对象名称
            origin: 圆心坐标 [x, y, z] (mm)
            radius: 半径 (mm)
            axis: 法向轴 (X/Y/Z)
        """
        try:
            conn = HFSSManager.get_connection()
            obj = conn.hfss.modeler.create_circle(
                origin=origin,
                radius=radius,
                orientation=axis,
                name=name,
            )
            return f"✅ 创建圆形 '{name}' 成功\n半径: {radius}mm"
        except Exception as e:
            return f"❌ 创建圆形失败: {str(e)}"
    
    @mcp.tool()
    def create_polygon(
        name: str,
        points: List[List[float]],
        axis: str = "Z",
        material: str = "vacuum",
    ) -> str:
        """
        创建多边形
        
        Args:
            name: 对象名称
            points: 顶点列表 [[x1,y1], [x2,y2], ...] (mm)
            axis: 法向轴 (X/Y/Z)
            material: 材料名称
        """
        try:
            conn = HFSSManager.get_connection()
            obj = conn.hfss.modeler.create_polygon(
                points=points,
                orientation=axis,
                name=name,
                material=material,
            )
            return f"✅ 创建多边形 '{name}' 成功\n顶点数: {len(points)}\n材料: {material}"
        except Exception as e:
            return f"❌ 创建多边形失败: {str(e)}"
    
    @mcp.tool()
    def subtract_objects(
        blank_name: str,
        tool_names: List[str],
        keep_originals: bool = False,
    ) -> str:
        """
        布尔减法操作
        
        Args:
            blank_name: 被减对象名称
            tool_names: 减去的对象名称列表
            keep_originals: 是否保留原始对象
        """
        try:
            conn = HFSSManager.get_connection()
            for tool_name in tool_names:
                conn.hfss.modeler.subtract(
                    blank_name=blank_name,
                    tool_names=[tool_name],
                    keep_originals=keep_originals,
                )
            return f"✅ 布尔减法完成: {blank_name} - {tool_names}"
        except Exception as e:
            return f"❌ 布尔减法失败: {str(e)}"
    
    @mcp.tool()
    def unite_objects(
        object_names: List[str],
        new_name: Optional[str] = None,
    ) -> str:
        """
        布尔合并操作
        
        Args:
            object_names: 要合并的对象名称列表
            new_name: 后对象的新名称（留空则使用第一个对象的名称）
        """
        try:
            conn = HFSSManager.get_connection()
            result = conn.hfss.modeler.unite(
                object_names,
                new_name=new_name or object_names[0],
            )
            return f"✅ 布尔合并完成: {object_names}"
        except Exception as e:
            return f"❌ 布尔合并失败: {str(e)}"
    
    @mcp.tool()
    def move_object(
        name: str,
        vector: List[float],
    ) -> str:
        """
        移动对象
        
        Args:
            name: 对象名称
            vector: 移动向量 [dx, dy, dz] (mm)
        """
        try:
            conn = HFSSManager.get_connection()
            conn.hfss.modeler.move(name, vector)
            return f"✅ 移动 '{name}' 完成: {vector}"
        except Exception as e:
            return f"❌ 移动失败: {str(e)}"
    
    @mcp.tool()
    def rotate_object(
        name: str,
        axis: str = "Z",
        angle: float = 90.0,
    ) -> str:
        """
        旋转对象
        
        Args:
            name: 对象名称
            axis: 旋转轴 (X/Y/Z)
            angle: 旋转角度 (度)
        """
        try:
            conn = HFSSManager.get_connection()
            conn.hfss.modeler.rotate(name, axis=axis, angle=angle)
            return f"✅ 旋转 '{name}' 完成: {angle}° 绕 {axis} 轴"
        except Exception as e:
            return f"❌ 旋转失败: {str(e)}"
    
    @mcp.tool()
    def duplicate_object(
        name: str,
        count: int = 2,
        vector: Optional[List[float]] = None,
        angle: Optional[float] = None,
        axis: Optional[str] = None,
    ) -> str:
        """
        复制对象
        
        Args:
            name: 对象名称
            count: 复制数量
            vector: 平移向量 [dx, dy, dz] (mm) - 线性阵列
            angle: 旋转角度 (度) - 旋转阵列
            axis: 旋转轴 (X/Y/Z) - 旋转阵列
        """
        try:
            conn = HFSSManager.get_connection()
            if vector:
                # 线性阵列
                result = conn.hfss.modeler.duplicate_along_line(
                    name, vector=vector, count=count,
                )
                return f"✅ 线性阵列复制完成: {name} x {count}"
            elif angle and axis:
                # 旋转阵列
                result = conn.hfss.modeler.duplicate_around_axis(
                    name, axis=axis, angle=angle, count=count,
                )
                return f"✅ 旋转阵列复制完成: {name} x {count}, {angle}°/{axis}"
            else:
                # 单纯复制
                result = conn.hfss.modeler.duplicate(name, count=count)
                return f"✅ 复制完成: {name} x {count}"
        except Exception as e:
            return f"❌ 复制失败: {str(e)}"
    
    @mcp.tool()
    def list_objects() -> str:
        """列出当前设计中的所有对象"""
        try:
            conn = HFSSManager.get_connection()
            objects = conn.hfss.modeler.object_names
            
            if not objects:
                return "当前设计中没有对象"
            
            result = "对象列表:\n"
            for i, obj in enumerate(objects, 1):
                result += f"{i}. {obj}\n"
            return result
        except Exception as e:
            return f"❌ 获取对象列表失败: {str(e)}"
    
    @mcp.tool()
    def get_object_info(name: str) -> str:
        """获取对象详细信息"""
        try:
            conn = HFSSManager.get_connection()
            obj = conn.hfss.modeler[name]
            
            info = f"""📋 对象信息:
名称: {name}
材料: {obj.material_name}
坐标范围: {obj.bounding_box}
体积: {obj.volume} mm³
面积: {obj.face_area} mm²
"""
            return info
        except Exception as e:
            return f"❌ 获取对象信息失败: {str(e)}"
