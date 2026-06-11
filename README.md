# HFSS MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AEDT 2022+](https://img.shields.io/badge/AEDT-2022%2B-green.svg)](https://www.ansys.com/products/electronics/ansys-electronics-desktop)

**Ansys HFSS 的模型上下文协议 (MCP) 服务器** — 让 AI Agent 直接控制 HFSS 进行天线设计与 PCB 仿真。

> 🎯 一句话：用自然语言描述天线，AI 帮你建模、仿真、出结果。

---

## ✨ 特性

### 🎯 天线设计
- **预定义模板**：贴片天线、偶极子、喇叭天线、阵列
- **任意天线建模**：螺旋、Vivaldi、缝隙、介质谐振器等
- **自动计算**：根据频率自动计算天线尺寸
- **完整仿真**：S 参数、增益、VSWR、远场方向图

### 🔌 PCB 仿真
- **叠层管理**：多层 PCB 结构定义
- **信号完整性**：走线、过孔、差分对分析
- **文件导入**：支持 BRD、ODB++ 格式
- **阻抗分析**：S 参数、插入损耗、回波损耗

### 🛠️ 建模能力
- **基本几何体**：长方体、圆柱、球体
- **曲线建模**：螺旋线、样条曲线
- **布尔运算**：合并、减去、相交
- **阵列复制**：线性/旋转阵列
- **CAD 导入**：STEP、IGES、SAT 格式

### 📊 后处理
- **S 参数**：回波损耗、插入损耗
- **天线参数**：增益、带宽、效率
- **阻抗分析**：VSWR、阻抗匹配
- **远场方向图**：3D 方向图、切面图
- **数据导出**：Touchstone (.s1p/.s2p)、场分布图

---

## 📦 安装

### 前置要求

- **Python** 3.8+（推荐 3.10+）
- **Ansys AEDT** 2022 R1+（HFSS 模块）
- **PyAEDT**（自动安装）

### 版本兼容性

| AEDT 版本 | 接口 | 平台 | 状态 |
|-----------|------|------|------|
| 2022 R1 | COM | 仅 Windows | ✅ 支持 |
| 2022 R2 | gRPC/COM | Windows/Linux | ✅ **推荐** |
| 2023 R1+ | gRPC | Windows/Linux | ✅ 推荐 |
| 2024 R1+ | gRPC | Windows/Linux | ✅ 推荐 |
| 2025 R1+ | gRPC | Windows/Linux | ✅ 推荐 |

> **注意**：
> - 2022 R1 只能在 Windows 上使用 COM 接口
> - 2022 R2 及以上版本推荐使用 gRPC 接口（更快、支持远程连接）
> - Linux 用户必须使用 2022 R2 或更高版本

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/gfgf2023/hfss-mcp-server.git
cd hfss-mcp-server

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
```

---

## 🚀 快速开始

### 1. 启动服务器

```bash
# STDIO 模式（本地使用，推荐）
python -m src.server

# HTTP 模式（远程/多客户端）
python -m src.server --transport http --host 127.0.0.1 --port 8765

# SSE 模式（Server-Sent Events）
python -m src.server --transport sse --host 127.0.0.1 --port 8765
```

### 2. 配置客户端

#### Claude Desktop

编辑 `~/.claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "hfss": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/hfss-mcp-server"
    }
  }
}
```

#### VS Code (Copilot)

编辑 `.vscode/settings.json`：

```json
{
  "mcp.servers": {
    "hfss": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

#### Hermes Agent

在 `~/.hermes/config.yaml` 中添加：

```yaml
mcp:
  servers:
    hfss:
      command: /path/to/venv/bin/python
      args: ["-m", "src.server"]
      cwd: /path/to/hfss-mcp-server
```

### 3. 开始使用

配置完成后，直接用自然语言对话：

```
你: 帮我设计一个 2.4GHz 的贴片天线，基板用 FR4，厚度 1.6mm

AI: 好的，我来帮你设计：
1. 连接 HFSS
2. 创建贴片天线（自动计算尺寸）
3. 设置端口和边界条件
4. 运行仿真
5. 返回 S 参数和天线参数
```

---

## 📖 使用示例

### 天线设计

#### 贴片天线

```python
# 连接 HFSS
connect_hfss(design_name="PatchAntenna", solution_type="DrivenModal")

# 创建 2.4GHz 贴片天线（自动计算尺寸）
create_patch_antenna(
    name="Patch2G4",
    frequency_ghz=2.4,
    substrate_material="FR4_epoxy",
    substrate_height_mm=1.6,
)

# 创建端口
create_wave_port(object_name="Patch2G4_feed", port_name="Port1")

# 创建求解设置
create_antenna_setup(
    setup_name="Setup1",
    frequency_ghz=2.4,
    frequency_sweep_start_ghz=1.5,
    frequency_sweep_stop_ghz=3.5,
)

# 运行仿真
run_simulation(setup_name="Setup1")

# 获取结果
get_antenna_parameters(setup_name="Setup1")
get_vswr(setup_name="Setup1")
get_far_field(setup_name="Setup1")

# 导出数据
export_touchstone(filename="patch_antenna.s1p")
```

#### 阿基米德螺旋天线

```python
# 生成螺旋天线脚本
generate_antenna_script(
    antenna_type="archimedean_spiral",
    parameters={
        "turns": 3,
        "r_inner_mm": 2.0,
        "r_outer_mm": 10.0,
        "wire_radius_mm": 0.5,
    },
)

# 执行脚本
run_pyaedt_script(script=generated_script)

# 仿真
run_simulation()
get_s_parameters()
```

#### 相控阵天线

```python
# 使用脚本创建 8x8 相控阵
run_pyaedt_script(script="""
import numpy as np

rows, cols = 8, 8
spacing = 12.5  # mm (约 0.8λ @ 10GHz)
patch_size = 6.0  # mm

# 创建第一个单元
hfss.modeler.create_box(
    origin=[-patch_size/2, -patch_size/2, 1.6],
    sizes=[patch_size, patch_size, 0.035],
    name="elem_0_0",
    material="copper",
)

# 复制阵列
for row in range(rows):
    for col in range(cols):
        if row == 0 and col == 0:
            continue
        dx = col * spacing
        dy = row * spacing
        hfss.modeler.duplicate_along_line("elem_0_0", vector=[dx, dy, 0])
""")
```

### PCB 仿真

#### 4 层 PCB 信号完整性分析

```python
# 连接 HFSS（DrivenTerminal 模式）
connect_hfss(design_name="PCB_Design", solution_type="DrivenTerminal")

# 创建 4 层叠层
create_pcb_stackup(
    name="PCB",
    layers=[
        {"name": "TOP", "type": "signal", "thickness_mm": 0.035, "material": "copper"},
        {"name": "PREPREG", "type": "dielectric", "thickness_mm": 0.2, "material": "FR4_epoxy"},
        {"name": "GND", "type": "ground", "thickness_mm": 0.035, "material": "copper"},
        {"name": "CORE", "type": "dielectric", "thickness_mm": 1.0, "material": "FR4_epoxy"},
        {"name": "BOTTOM", "type": "signal", "thickness_mm": 0.035, "material": "copper"},
    ],
    board_width_mm=100.0,
    board_length_mm=100.0,
)

# 创建差分走线
create_trace(name="Signal_P", layer="TOP", start_point=[-40, 0], end_point=[40, 0], width_mm=0.15)
create_trace(name="Signal_N", layer="TOP", start_point=[-40, 0.3], end_point=[40, 0.3], width_mm=0.15)

# 创建差分对
create_diff_pair(name="DiffPair1", positive_trace="Signal_P", negative_trace="Signal_N", impedance=100)

# 仿真
run_simulation()
get_s_parameters()
get_insertion_loss()
get_impedance()
```

---

## 🛠️ API 参考

### 项目管理

| 工具 | 说明 | 参数 |
|------|------|------|
| `connect_hfss` | 连接 HFSS | `project_path`, `design_name`, `solution_type`, `desktop_version` |
| `disconnect_hfss` | 断开连接 | - |
| `save_project` | 保存项目 | `path` |
| `list_projects` | 列出项目 | - |
| `get_project_info` | 获取项目信息 | - |

### 几何建模

| 工具 | 说明 | 参数 |
|------|------|------|
| `create_box` | 创建长方体 | `name`, `origin`, `dimensions`, `material` |
| `create_cylinder` | 创建圆柱体 | `name`, `origin`, `radius`, `height`, `axis` |
| `create_sphere` | 创建球体 | `name`, `origin`, `radius`, `material` |
| `create_rectangle` | 创建矩形 | `name`, `origin`, `dimensions`, `axis` |
| `create_circle` | 创建圆形 | `name`, `origin`, `radius`, `axis` |
| `create_polygon` | 创建多边形 | `name`, `points`, `axis`, `material` |
| `subtract_objects` | 布尔减法 | `blank_name`, `tool_names`, `keep_originals` |
| `unite_objects` | 布尔合并 | `object_names`, `new_name` |
| `move_object` | 移动对象 | `name`, `vector` |
| `rotate_object` | 旋转对象 | `name`, `axis`, `angle` |
| `duplicate_object` | 复制对象 | `name`, `count`, `vector`, `angle`, `axis` |
| `list_objects` | 列出对象 | - |
| `get_object_info` | 获取对象信息 | `name` |

### 材料管理

| 工具 | 说明 | 参数 |
|------|------|------|
| `set_material` | 设置材料 | `object_name`, `material_name` |
| `create_custom_material` | 创建自定义材料 | `name`, `permittivity`, `permeability`, `conductivity` |
| `list_materials` | 列出材料库 | - |
| `get_material_properties` | 获取材料属性 | `material_name` |
| `assign_perfect_e` | 设置 Perfect E | `object_name` |

### 天线设计

| 工具 | 说明 | 参数 |
|------|------|------|
| `create_patch_antenna` | 创建贴片天线 | `name`, `frequency_ghz`, `substrate_material`, `substrate_height_mm` |
| `create_dipole_antenna` | 创建偶极子天线 | `name`, `frequency_ghz`, `arm_length_mm`, `arm_radius_mm` |
| `create_horn_antenna` | 创建喇叭天线 | `name`, `frequency_ghz`, `waveguide_a_mm`, `horn_aperture_a_mm` |
| `create_array_antenna` | 创建天线阵列 | `name`, `element_type`, `rows`, `cols`, `spacing_x_mm` |
| `create_wave_port` | 创建波端口 | `object_name`, `port_name`, `impedance` |
| `create_lumped_port` | 创建集总端口 | `object_name`, `port_name`, `impedance` |
| `create_antenna_setup` | 创建天线仿真设置 | `setup_name`, `frequency_ghz`, `max_passes` |

### PCB 仿真

| 工具 | 说明 | 参数 |
|------|------|------|
| `create_pcb_stackup` | 创建 PCB 叠层 | `name`, `layers`, `board_width_mm`, `board_length_mm` |
| `create_trace` | 创建走线 | `name`, `layer`, `start_point`, `end_point`, `width_mm` |
| `create_via` | 创建过孔 | `name`, `position`, `drill_diameter_mm`, `pad_diameter_mm` |
| `create_ground_plane` | 创建接地平面 | `name`, `width_mm`, `length_mm`, `clearance_mm` |
| `create_component_pad` | 创建元件焊盘 | `name`, `position`, `pad_width_mm`, `pad_length_mm` |
| `create_pcb_port` | 创建 PCB 端口 | `signal_name`, `ground_name`, `port_name`, `impedance` |
| `create_pcb_setup` | 创建 PCB 仿真设置 | `setup_name`, `frequency_ghz`, `sweep_start_ghz` |
| `import_brd_file` | 导入 BRD 文件 | `brd_path`, `output_path` |
| `import_odb_file` | 导入 ODB 文件 | `odb_path`, `output_path` |
| `create_diff_pair` | 创建差分对 | `name`, `positive_trace`, `negative_trace`, `impedance` |

### 求解设置

| 工具 | 说明 | 参数 |
|------|------|------|
| `create_setup` | 创建求解设置 | `setup_name`, `frequency_ghz`, `max_passes`, `max_delta_s` |
| `add_frequency_sweep` | 添加频率扫描 | `setup_name`, `sweep_name`, `start_ghz`, `stop_ghz` |
| `add_adaptive_sweep` | 添加自适应扫描 | `setup_name`, `sweep_name`, `start_ghz`, `stop_ghz` |
| `set_mesh_operations` | 设置网格操作 | `object_name`, `max_length_mm` |
| `run_simulation` | 运行仿真 | `setup_name`, `sweep_name` |
| `validate_design` | 验证设计 | - |
| `get_mesh_info` | 获取网格信息 | - |

### 后处理

| 工具 | 说明 | 参数 |
|------|------|------|
| `get_s_parameters` | 获取 S 参数 | `setup_name`, `sweep_name`, `port_i`, `port_j`, `output_format` |
| `get_return_loss` | 获取回波损耗 | `setup_name`, `sweep_name`, `port` |
| `get_insertion_loss` | 获取插入损耗 | `setup_name`, `sweep_name`, `port_i`, `port_j` |
| `get_antenna_parameters` | 获取天线参数 | `setup_name`, `sweep_name`, `frequency_ghz` |
| `get_impedance` | 获取阻抗 | `setup_name`, `sweep_name`, `port` |
| `get_vswr` | 获取 VSWR | `setup_name`, `sweep_name`, `port` |
| `get_far_field` | 获取远场方向图 | `setup_name`, `sweep_name`, `frequency_ghz`, `phi_cut` |
| `export_touchstone` | 导出 Touchstone | `filename`, `setup_name`, `sweep_name` |
| `export_field_plot` | 导出场图 | `quantity`, `output_file`, `setup_name` |
| `generate_report` | 生成报告 | `report_type`, `setup_name`, `sweep_name` |

### 脚本执行

| 工具 | 说明 | 参数 |
|------|------|------|
| `run_pyaedt_script` | 执行 PyAEDT 脚本 | `script`, `description` |
| `run_hfss_script_file` | 执行脚本文件 | `script_path` |
| `generate_antenna_script` | 生成天线脚本 | `antenna_type`, `parameters` |

---

## 🎯 支持的天线类型

### 预定义模板

| 类型 | 名称 | 频率范围 | 增益 | 应用 |
|------|------|----------|------|------|
| `patch` | 矩形微带贴片天线 | 1-10 GHz | 6-8 dBi | 移动通信、GPS |
| `dipole` | 半波偶极子天线 | 100 MHz-10 GHz | 2.15 dBi | 基站、广播 |
| `horn` | 喇叭天线 | 1-100 GHz | 10-20 dBi | 测量、雷达 |
| `array` | 天线阵列 | 任意 | 可定制 | 相控阵、MIMO |

### 模板生成

| 类型 | 名称 | 特点 | 应用 |
|------|------|------|------|
| `archimedean_spiral` | 阿基米德螺旋天线 | 宽带、圆极化 | 电子战、测向 |
| `log_spiral` | 对数螺旋天线 | 频率无关 | 宽带通信 |
| `vivaldi` | Vivaldi 渐变缝隙天线 | 超宽带 | 探地雷达、UWB |
| `yagi` | 八木天线 | 高增益、定向 | 电视接收、业余无线电 |
| `helix` | 螺旋天线（轴向模） | 圆极化 | 卫星通信、GPS |
| `slot` | 缝隙天线 | 平面集成 | 雷达、通信 |
| `monopole` | 单极子天线 | 全向 | 手机、车载 |
| `loop` | 环形天线 | 小型化 | RFID、NFC |

### 自定义建模

通过 `run_pyaedt_script` 可以创建任意天线结构：

- **曲线天线**：螺旋、分形、曲线振子
- **平面天线**：微带贴片变体、缝隙耦合
- **立体天线**：锥形、球形、介质谐振器
- **阵列天线**：线阵、面阵、共形阵
- **宽带天线**：对数周期、行波天线

---

## 📁 项目结构

```
hfss-mcp-server/
├── pyproject.toml                  # 项目配置
├── README.md                       # 本文档
├── LICENSE                         # MIT 许可证
├── claude_desktop_config.example.json  # Claude Desktop 配置示例
├── .vscode/
│   └── mcp.example.json           # VS Code 配置示例
├── config/
│   └── default_config.yaml        # 默认配置
├── src/
│   ├── __init__.py
│   ├── __main__.py                # python -m 入口
│   ├── server.py                  # MCP 服务器主程序
│   ├── hfss_connection.py         # HFSS 连接管理
│   ├── tools/                     # MCP 工具
│   │   ├── project.py             # 项目管理
│   │   ├── geometry.py            # 几何建模
│   │   ├── material.py            # 材料管理
│   │   ├── antenna.py             # 天线设计
│   │   ├── pcb.py                 # PCB 仿真
│   │   ├── setup.py               # 求解设置
│   │   ├── results.py             # 后处理
│   │   └── script.py              # 脚本执行
│   └── resources/                 # MCP 资源
│       └── hfss_resources.py      # HFSS 资源定义
├── examples/                      # 示例
│   ├── patch_antenna.py           # 贴片天线示例
│   ├── pcb_example.py             # PCB 仿真示例
│   ├── connect_2022.py            # AEDT 2022 连接示例
│   └── modeling_demo.py           # 建模演示
└── tests/                         # 测试
    └── ...
```

---

## 🔧 配置

### 默认配置

编辑 `config/default_config.yaml`：

```yaml
hfss:
  version: "2022.2"           # AEDT 版本
  solution_type: "DrivenModal" # 默认求解类型
  non_graphical: false         # 无界面模式

server:
  transport: "stdio"           # 传输方式
  host: "127.0.0.1"
  port: 8765

antenna:
  default_frequency: 2.4       # 默认频率 (GHz)
  default_substrate: "FR4_epoxy"
  default_substrate_height: 1.6

pcb:
  default_trace_width: 0.2    # 默认线宽 (mm)
  default_via:
    drill_diameter: 0.3
    pad_diameter: 0.6

setup:
  max_passes: 20               # 最大迭代次数
  max_delta_s: 0.02            # 收敛阈值
```

### 环境变量

```bash
# AEDT 安装路径（Linux）
export ANSYSEM_ROOT=/opt/AnsysEM/v222/AnsysEM

# PyAEDT 设置
export PYAEDT_NON_GRAPHICAL=false
export PYAEDT_STUDENT_VERSION=false
```

---

## 📚 常用材料参考

### 金属

| 材料 | 电导率 (S/m) | 相对磁导率 | 应用 |
|------|-------------|-----------|------|
| Silver | 6.3×10⁷ | 1.0 | 最高导电性 |
| Copper | 5.8×10⁷ | 1.0 | 常用导体 |
| Gold | 4.1×10⁷ | 1.0 | 抗氧化 |
| Aluminum | 3.8×10⁷ | 1.0 | 轻质 |
| Brass | 1.5×10⁷ | 1.0 | 低成本 |

### 介质基板

| 材料 | 介电常数 (εr) | 损耗角正切 | 应用 |
|------|--------------|-----------|------|
| Rogers5880 | 2.2 | 0.0009 | 毫米波、卫星 |
| Rogers4003 | 3.55 | 0.0027 | 高频通信 |
| Rogers4350 | 3.66 | 0.0037 | 5G、雷达 |
| FR4 | 4.4 | 0.02 | 通用 PCB |
| Alumina | 9.8 | 0.0001 | 小型化、高功率 |
| Teflon | 2.1 | 0.0002 | 超低损耗 |

### 常用基板厚度

| 材料 | 常用厚度 (mm) |
|------|---------------|
| FR4 | 0.4, 0.8, 1.0, 1.6, 2.0, 3.2 |
| Rogers | 0.254, 0.508, 0.762, 1.524 |

---

## 🐛 故障排除

### 连接问题

**问题**: 无法连接到 HFSS

```bash
# 检查 AEDT 是否安装
ls /opt/AnsysEM/

# 检查 PyAEDT 版本
pip show pyaedt

# 尝试无界面模式
connect_hfss(non_graphical=True)
```

**问题**: gRPC 连接失败

```bash
# 检查 gRPC 服务是否启动
# Windows: 检查 AnsysEM 进程
# Linux: 检查 gRPC 端口
netstat -tlnp | grep 50051
```

### 仿真收敛问题

**问题**: 仿真不收敛

```python
# 增加迭代次数
create_setup(setup_name="Setup1", max_passes=30, max_delta_s=0.05)

# 添加网格细化
set_mesh_operations(object_name="antenna", max_length_mm=0.5)
```

**问题**: 网格质量差

```python
# 检查网格信息
get_mesh_info()

# 手动设置网格
set_mesh_operations(object_name="critical_region", max_length_mm=0.2)
```

### 材料问题

**问题**: 找不到材料

```python
# 列出可用材料
list_materials()

# 创建自定义材料
create_custom_material(
    name="my_material",
    permittivity=3.5,
    dielectric_loss_tangent=0.002,
)
```

---

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发环境

```bash
# 克隆仓库
git clone https://github.com/gfgf2023/hfss-mcp-server.git
cd hfss-mcp-server

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/

# 代码格式化
black src/
isort src/

# 类型检查
mypy src/
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [Ansys PyAEDT](https://github.com/ansys/pyaedt) - HFSS Python API
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP 协议规范
- [FastMCP](https://github.com/jlowin/fastmcp) - Python MCP 框架

---

## 📧 联系方式

- 问题反馈：[GitHub Issues](https://github.com/gfgf2023/hfss-mcp-server/issues)
- 邮箱：your.email@example.com

---

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐
