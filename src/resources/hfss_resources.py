# HFSS MCP Server - 资源定义
from typing import Dict, List, Optional
from ..hfss_connection import HFSSManager
import logging

logger = logging.getLogger(__name__)


def register_resources(mcp):
    """注册 MCP 资源"""
    
    @mcp.resource("hfss://projects")
    def get_projects() -> Dict:
        """获取所有打开的项目"""
        try:
            conn = HFSSManager.get_connection()
            projects = conn.hfss.project_list
            return {
                "projects": projects,
                "current_project": conn.hfss.project_name,
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://materials")
    def get_materials() -> Dict:
        """获取可用材料库"""
        try:
            conn = HFSSManager.get_connection()
            materials = conn.hfss.materials.material_keys
            
            # 分类材料
            metals = []
            dielectrics = []
            others = []
            
            for mat in materials:
                mat_lower = mat.lower()
                if any(m in mat_lower for m in ["copper", "aluminum", "gold", "silver", "iron", "steel"]):
                    metals.append(mat)
                elif any(m in mat_lower for m in ["fr4", "rogers", "duroid", "teflon", "glass"]):
                    dielectrics.append(mat)
                else:
                    others.append(mat)
            
            return {
                "total_count": len(materials),
                "metals": sorted(metals),
                "dielectrics": sorted(dielectrics),
                "others": sorted(others)[:50],  # 限制数量
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://materials/{material_name}")
    def get_material_info(material_name: str) -> Dict:
        """获取特定材料的详细信息"""
        try:
            conn = HFSSManager.get_connection()
            mat = conn.hfss.materials[material_name]
            
            return {
                "name": material_name,
                "permittivity": mat.permittivity,
                "permeability": mat.permeability,
                "conductivity": mat.conductivity,
                "dielectric_loss_tangent": mat.dielectric_loss_tangent,
                "magnetic_loss_tangent": mat.magnetic_loss_tangent,
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://design/{design_name}")
    def get_design_info(design_name: str) -> Dict:
        """获取设计信息"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            return {
                "project_name": hfss.project_name,
                "design_name": hfss.design_name,
                "solution_type": hfss.solution_type,
                "mesh_type": hfss.mesh_type,
                "objects": hfss.modeler.object_names,
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://objects")
    def get_objects() -> Dict:
        """获取当前设计中的所有对象"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            objects = {}
            for obj_name in hfss.modeler.object_names:
                obj = hfss.modeler[obj_name]
                objects[obj_name] = {
                    "material": obj.material_name,
                    "bounding_box": obj.bounding_box,
                    "volume": obj.volume,
                }
            
            return {
                "count": len(objects),
                "objects": objects,
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://objects/{object_name}")
    def get_object_info(object_name: str) -> Dict:
        """获取特定对象的详细信息"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            obj = hfss.modeler[object_name]
            
            return {
                "name": object_name,
                "material": obj.material_name,
                "bounding_box": obj.bounding_box,
                "volume": obj.volume,
                "face_area": obj.face_area,
                "center": obj.center,
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://setups")
    def get_setups() -> Dict:
        """获取所有求解设置"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            setups = {}
            for setup_name in hfss.setup_names:
                setup = hfss.get_setup(setup_name)
                setups[setup_name] = {
                    "frequency": setup.props.get("Frequency"),
                    "max_passes": setup.props.get("MaximumPasses"),
                    "max_delta_s": setup.props.get("MaxDeltaS"),
                }
            
            return {
                "count": len(setups),
                "setups": setups,
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://setups/{setup_name}")
    def get_setup_info(setup_name: str) -> Dict:
        """获取特定求解设置的详细信息"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            setup = hfss.get_setup(setup_name)
            
            return {
                "name": setup_name,
                "props": dict(setup.props),
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://boundaries")
    def get_boundaries() -> Dict:
        """获取所有边界条件"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            boundaries = {}
            for bound_name in hfss.boundaries:
                boundaries[bound_name] = {
                    "type": hfss.boundaries[bound_name].type,
                }
            
            return {
                "count": len(boundaries),
                "boundaries": boundaries,
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://ports")
    def get_ports() -> Dict:
        """获取所有端口"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            ports = {}
            for port_name in hfss.excitations:
                ports[port_name] = {
                    "impedance": hfss.excitations[port_name].props.get(" impedance"),
                }
            
            return {
                "count": len(ports),
                "ports": ports,
            }
        except Exception as e:
            return {"error": str(e)}
    
    @mcp.resource("hfss://mesh")
    def get_mesh_stats() -> Dict:
        """获取网格统计信息"""
        try:
            conn = HFSSManager.get_connection()
            hfss = conn.hfss
            
            mesh_info = hfss.mesh.get_mesh_stats()
            
            return mesh_info
        except Exception as e:
            return {"error": str(e)}


# 常用材料参考数据
MATERIAL_REFERENCE = {
    "metals": {
        "copper": {
            "conductivity": 5.8e7,
            "permeability": 0.999991,
            "description": "常用导体，高导电性",
        },
        "aluminum": {
            "conductivity": 3.8e7,
            "permeability": 1.0,
            "description": "轻质金属，良好导电性",
        },
        "gold": {
            "conductivity": 4.1e7,
            "permeability": 1.0,
            "description": "贵金属，抗氧化",
        },
        "silver": {
            "conductivity": 6.3e7,
            "permeability": 1.0,
            "description": "最高导电性金属",
        },
    },
    "dielectrics": {
        "FR4_epoxy": {
            "permittivity": 4.4,
            "loss_tangent": 0.02,
            "description": "常用 PCB 基板材料",
        },
        "Rogers4003": {
            "permittivity": 3.55,
            "loss_tangent": 0.0027,
            "description": "高频低损耗基板",
        },
        "Rogers4350": {
            "permittivity": 3.66,
            "loss_tangent": 0.0037,
            "description": "高频基板，性价比高",
        },
        "Rogers5880": {
            "permittivity": 2.2,
            "loss_tangent": 0.0009,
            "description": "超低损耗，毫米波应用",
        },
        "Duroid5870": {
            "permittivity": 2.33,
            "loss_tangent": 0.0012,
            "description": "低损耗，微波应用",
        },
        "Teflon": {
            "permittivity": 2.1,
            "loss_tangent": 0.0002,
            "description": "超低损耗，特种应用",
        },
        "Alumina": {
            "permittivity": 9.8,
            "loss_tangent": 0.0001,
            "description": "高介电常数，小型化设计",
        },
    },
    "common_substrate_heights": {
        "FR4": [0.4, 0.8, 1.0, 1.6, 2.0, 3.2],
        "Rogers": [0.254, 0.508, 0.762, 1.524],
    },
}


@mcp.resource("hfss://reference/materials")
def get_material_reference() -> Dict:
    """获取常用材料参考数据"""
    return MATERIAL_REFERENCE
