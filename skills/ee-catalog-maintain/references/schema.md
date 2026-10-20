# 电路设计最佳实践库 — 数据格式

规则存放在 `catalog/*.yaml`，每个文件是一个 YAML 列表，每条规则一个映射。校验：

```bash
python tools/validate.py                      # 全部
python tools/validate.py catalog/power.yaml   # 单个文件
python tools/validate.py --check-urls         # 另外探测来源 URL 是否可达
```

文字用中文，技术术语、器件名、标准号保留英文。枚举值一律用下面的英文 key。

## 规则字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✔ | `<DOM>-<STG>-<NNN>`，全库唯一。DOM、STG 必须与 `domain`、`stage` 对应（见下表），NNN 三位数字从 001 起 |
| `title` | ✔ | 一句话标题，祈使句，≤ 40 字 |
| `domain` | ✔ | 领域，见下表 |
| `stage` | ✔ | 设计环节，见下表 |
| `severity` | ✔ | `must`（违反会导致功能失效 / 认证不过 / 板厂拒收）· `should`（强烈建议，违反要有理由）· `consider`（取决于场景的权衡） |
| `rule` | ✔ | 规则本身，一到两句，可被检查的陈述 |
| `rationale` | ✔ | 物理机理 / 为什么，一到三句 |
| `verify` | ✔ | 至少一条，怎么验证（见下） |
| `sources` | ✔ | 至少一条，来源（见下） |
| `confidence` | ✔ | `high`（标准 / 厂商应用笔记 / 数据手册，且你实际读过原文）· `medium`（可靠的二手资料、教科书、多个独立来源一致）· `low`（单一社区来源、经验之谈） |
| `applies_to` |  | 适用的子电路 / 拓扑 / 器件类别，字符串列表，如 `[buck, ldo, qfn]` |
| `parameters` |  | 量化参数，见下 |
| `conflicts` |  | 不同来源说法不一致时写在这里，并说明取舍依据 |
| `tags` |  | 自由标签。与示例板 [fxp/cat-feeder](https://github.com/fxp/cat-feeder)（ESP32-C3 模块 + 电机 MOSFET + INA199 分流 + AMS1117 + HX711，2 层板，JLC SMT）相关的规则加 `cat-feeder` |

## `parameters`

```yaml
parameters:
  - name: decap_to_pin_distance      # snake_case，可被脚本引用
    op: "<="                         # <= >= < > == range minimize maximize qualitative
    value: 3                         # 数字；range 用 [lo, hi]；qualitative / minimize / maximize 可写 null
    unit: mm
    note: "100 nF 0402，对 VDD 引脚"  # 条件、适用范围
```

只写来源里真有的数字。凭经验估的写进 `note` 并把 `confidence` 降到 `medium` 或 `low`，不要伪装成出处里的数值。

## `verify`

```yaml
verify:
  - method: geometry_script          # 见下表
    tool: "pcbnew (KiCad bundled Python), 参见 ee-pcb-verify 的 geometry 检查器"
    check: "对每个 VDD 引脚找最近的去耦电容焊盘，测焊盘中心距，≤ 3 mm"
    automatable: full                # full | partial | manual
```

`check` 要写到别人能照着实现的程度：量什么、从哪到哪、通过判据是什么。`automatable: full` 表示不需要人判断就能出 pass/fail。

`method` 取值：

| method | 含义 |
|---|---|
| `erc` | 原理图电气规则检查（KiCad ERC 等） |
| `drc` | PCB 设计规则检查，含自定义规则（`.kicad_dru`） |
| `netlist_diff` | 原理图网表与 PCB 网表 / 元件一致性对比 |
| `bom_check` | 对 BOM 与器件参数做降额、封装、生命周期等检查 |
| `geometry_script` | 读板文件的自定义脚本：距离、面积、环路面积、线长、铜宽 |
| `spice` | 电路仿真（ngspice / Xyce / LTspice）：瞬态、AC、噪声、稳定性、温度扫描 |
| `tline_calc` | 传输线阻抗 / 2D 场求解 / 载流与压降计算器 |
| `em_sim` | 2.5D / 3D 电磁仿真（openEMS、Elmer 等）、S 参数 |
| `si_sim` | 信号完整性：反射、串扰、眼图、IBIS |
| `pi_sim` | 电源完整性：PDN 阻抗、IR drop |
| `thermal_sim` | 热仿真 / 热阻网络估算 |
| `emc_precompliance` | 近场探头、预兼容测试 |
| `bench` | 实物测量（示波器、VNA、功耗仪、热像仪） |
| `review` | 人工评审清单 |

## `sources`

```yaml
sources:
  - title: "AN-xxxx Title"
    url: "https://..."              # 你实际打开过或在搜索结果里看到的 URL；不要编造
    publisher: "Texas Instruments"
    kind: app_note                  # standard datasheet app_note vendor_guide textbook paper tool_doc blog forum
    section: "§5.3"                 # 可选，章节 / 页码
```

* 教科书和付费标准没有可打开的 URL 时，省略 `url`，但必须写 `ref`（书名 / 标准号 / 版本 / 章节），例如 `ref: "IPC-2221B §6.2"`。
* **不要编造 URL。** 没读到原文就不要标 `high`。
* 不要大段复制原文，用自己的话概括。

## `domain`（领域）与 ID 前缀

垂直领域：

| domain | DOM | 含义 |
|---|---|---|
| `general` | GEN | 通用 / 数模混合 MCU 板（跨领域的基础流程与布局） |
| `power` | PWR | 电源与功率：开关电源、LDO、电机驱动、大电流 |
| `low_power` | LPW | 低功耗 / 电池供电 / IoT |
| `rf` | RF | 射频与天线 |
| `audio` | AUD | 音频（含 D 类功放） |
| `analog` | ANA | 精密模拟 / 低噪声 / 传感器前端 / 电流检测 |
| `high_speed` | HSD | 高速数字：USB、以太网、DDR、LVDS、PCIe |

横向关切（叠加在任何垂直领域上）：

| domain | DOM | 含义 |
|---|---|---|
| `emc_esd` | EMC | EMC / ESD / 浪涌 |
| `hv_safety` | HVS | 高压 / 隔离 / 安规（爬电与电气间隙） |
| `thermal` | THM | 热设计 |
| `dfm` | DFM | 可制造 / 可装配 / 可测试 |

## `stage`（设计环节）与 ID 前缀

| stage | STG | 含义 |
|---|---|---|
| `architecture` | ARC | 需求、架构、器件选型、降额 |
| `library` | LIB | 符号、封装、3D 库质量 |
| `schematic` | SCH | 原理图设计与绘制 |
| `netlist` | NET | 网表、网络类、约束、原理图与 PCB 一致性 |
| `stackup` | STK | 叠层、阻抗、板级设计规则 |
| `floorplan` | FLR | 分区、功能块规划、接口位置 |
| `placement` | PLC | 器件布局 |
| `routing` | RTE | 布线、过孔、回流路径 |
| `plane_pour` | PLN | 电源地平面、铺铜、缝合过孔 |
| `manufacturing` | MFG | 出图、板厂 / 贴片工艺、测试点 |
| `verification` | VER | 签核：ERC / DRC / 仿真 / 实测 |

例：`PWR-PLC-003` = 电源领域 · 布局环节 · 第 3 条。

## `verifiers.yaml`（验证工具目录，另一种记录）

`catalog/verifiers.yaml` 记录能做验证的工具及其在参考机（macOS arm64，KiCad 10.0.6）上的可用性：status 描述的是参考机，不是你的机器：

```yaml
- id: V-KICAD-DRC
  name: KiCad DRC (kicad-cli pcb drc)
  methods: [drc]                     # 与 verify.method 同一套枚举
  status: installed                  # installed | bundled | not_installed | cloud
  invocation: "kicad-cli pcb drc --format json --output out.json board.kicad_pcb"
  inputs: [kicad_pcb, kicad_dru]
  outputs: [json]
  can_check: ["clearance", "annular ring", "..."]   # 能验证的规则类型
  limits: ["..."]
  notes: ""
```
