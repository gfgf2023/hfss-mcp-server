# HFSS MCP Server - 材料管理工具
from typing import Optional, Dict
from ..hfss_connection import HFSSManager
import logging

logger = logging.getLogger(__name__)


def register_material_tools(mcp):
    """注册材料管理相关的 MCP tools"""
    
    @mcp.tool()
    def set_material(
        object_name: str,
        material_name: str,
    ) -> str:
        """
        设置对象的材料
        
        Args:
            object_name: 对象名称
            material_name: 材料名称（如 copper, FR4_epoxy, Rogers4003 等）
        """
        try:
            conn = HFSSManager.get_connection()
            conn.hfss.modeler[object_name].material_name = material_name
            return f"✅ 已将 '{object_name}' 的材料设置为 '{material_name}'"
        except Exception as e:
            return f"❌ 设置材料失败: {str(e)}"
    
    @mcp.tool()
    def create_custom_material(
        name: str,
        permittivity: float = 1.0,
        permeability: float = 1.0,
        conductivity: float = 0.0,
        dielectric_loss_tangent: float = 0.0,
        magnetic_loss_tangent: float = 0.0,
    ) -> str:
        """
        创建自定义材料
        
        Args:
            name: 材料名称
            permittivity: 相对介电常数 εr
            permeability: 相对磁导率 μr
            conductivity: 电导率 (S/m)
            dielectric_loss_tangent: 介电损耗角正切
            magnetic_loss_tangent: 磁损耗角正切
        """
        try:
            conn = HFSSManager.get_connection()
            
            material_props = {
                "permittivity": permittivity,
                "permeability": permeability,
                "conductivity": conductivity,
                "dielectric_loss_tangent": dielectric_loss_tangent,
                "magnetic_loss_tangent": magnetic_loss_tangent,
            }
            
            conn.hfss.materials.add_material(
                name=name,
                properties=material_props,
            )
            
            return f"""✅ 创建材料 '{name}' 成功:
  介电常数 εr: {permittivity}
  磁导率 μr: {permeability}
  电导率: {conductivity} S/m
  介电损耗: {dielectric_loss_tangent}
"""
        except Exception as e:
            return f"❌ 创建材料失败: {str(e)}"
    
    @mcp.tool()
    def list_materials() -> str:
        """列出可用的材料库"""
        try:
            conn = HFSSManager.get_connection()
            materials = conn.hfss.materials.material_keys
            
            if not materials:
                return "材料库为空"
            
            result = "可用材料:\n"
            # 常用材料分类
            metals = []
            dielectrics = []
            others = []
            
            for mat in materials:
                mat_lower = mat.lower()
                if any(m in mat_lower for m in ["copper", "aluminum", "gold", "silver", "iron", "steel", "brass", "tin", "nickel"]):
                    metals.append(mat)
                elif any(m in mat_lower for m in ["fr4", "rogers", "duroid", "teflon", "glass", "ceramic", "rubber", "plastic"]):
                    dielectrics.append(mat)
                else:
                    others.append(mat)
            
            if metals:
                result += "\n🔩 金属:\n"
                for m in sorted(metals)[:20]:  # 限制显示数量
                    result += f"  - {m}\n"
            
            if dielectrics:
                result += "\n💎 介质:\n"
                for d in sorted(dielectrics)[:20]:
                    result += f"  - {d}\n"
            
            result += f"\n... 共 {len(materials)} 种材料"
            return result
        except Exception as e:
            return f"❌ 获取材料列表失败: {str(e)}"
    
    @mcp.tool()
    def get_material_properties(material_name: str) -> str:
        """
        获取材料属性
        
        Args:
            material_name: 材料名称
        """
        try:
            conn = HFSSManager.get_connection()
            mat = conn.hfss.materials[material_name]
            
            info = f"""📋 材料属性: {material_name}
  介电常数 εr: {mat.permittivity}
  磁导率 μr: {mat.permeability}
  电导率: {mat.conductivity} S/m
  介电损耗角正切: {mat.dielectric_loss_tangent}
  磁损耗角正切: {mat.magnetic_loss_tangent}
"""
            return info
        except Exception as e:
            return f"❌ 获取材料属性失败: {str(e)}"
    
    @mcp.tool()
    def assign_perfect_e(object_name: str) -> str:
        """
        将对象设置为理想导体 (Perfect E)
        
        Args:
            object_name: 对象名称
        """
        try:
            conn = HFSSManager.get_connection()
            conn.hfss.assign_perfect_e(
                object_name,
                is_infinite_ground=False,
            )
            return f"✅ 已将 '{object_name}' 设置为 Perfect E 边界"
        except Exception as e:
            return f"❌ 设置 Perfect E 失败: {str(e)}"
