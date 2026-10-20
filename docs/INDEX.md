# 电路设计最佳实践库 — 索引

共 **531** 条规则，331 个不同的来源 URL。本文件由 `tools/build_docs.py` 从 `catalog/*.yaml` 生成。

## 领域 × 环节

| 领域 | 架构与选型 | 符号封装库 | 原理图 | 网表与约束 | 叠层与规则 | 分区规划 | 器件布局 | 布线 | 平面与铺铜 | 出图与制造 | 签核验证 | 合计 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [通用 / 数模混合 MCU 板](../skills/ee-general-pcb/SKILL.md)（垂直） | 10 | 8 | 17 | 8 | 8 | 8 | 9 | 15 | 11 |  | 9 | **103** |
| [电源与功率](../skills/ee-power/SKILL.md)（垂直） | 7 | 2 | 16 |  | 1 | 2 | 7 | 8 | 4 |  | 7 | **54** |
| [低功耗 / 电池](../skills/ee-low-power/SKILL.md)（垂直） | 13 | 1 | 14 | 1 |  |  | 1 | 2 |  | 2 | 6 | **40** |
| [射频与天线](../skills/ee-rf/SKILL.md)（垂直） | 6 | 1 | 8 | 1 | 3 | 6 | 2 | 5 | 5 | 1 | 7 | **45** |
| [音频](../skills/ee-audio/SKILL.md)（垂直） | 4 | 1 | 16 | 1 | 1 | 3 | 3 | 5 | 2 | 1 | 6 | **43** |
| [精密模拟 / 传感器前端](../skills/ee-analog/SKILL.md)（垂直） | 10 | 1 | 13 | 1 | 1 | 2 | 4 | 5 | 3 | 1 | 5 | **46** |
| [高速数字](../skills/ee-high-speed/SKILL.md)（垂直） | 5 |  | 11 | 4 | 3 | 2 | 4 | 14 | 3 | 1 | 5 | **52** |
| [EMC / ESD / 浪涌](../skills/ee-emc-esd/SKILL.md)（横向） | 5 |  | 14 |  | 2 | 6 | 4 | 6 | 3 |  | 6 | **46** |
| [高压 / 隔离 / 安规](../skills/ee-hv-safety/SKILL.md)（横向） | 6 | 1 | 3 | 1 | 2 | 2 | 1 | 3 | 1 | 1 | 2 | **23** |
| [热设计](../skills/ee-thermal/SKILL.md)（横向） | 8 | 1 |  |  | 3 |  | 2 | 5 | 3 | 1 | 5 | **28** |
| [可制造 / 可装配 / 可测试](../skills/ee-dfm/SKILL.md)（横向） | 5 | 7 | 2 | 2 | 4 | 6 | 4 | 4 | 2 | 12 | 3 | **51** |
| **合计** | 79 | 23 | 114 | 19 | 28 | 37 | 41 | 72 | 37 | 20 | 61 | **531** |

按环节看：[架构与选型](by-stage/architecture.md)　[符号封装库](by-stage/library.md)　[原理图](by-stage/schematic.md)　[网表与约束](by-stage/netlist.md)　[叠层与规则](by-stage/stackup.md)　[分区规划](by-stage/floorplan.md)　[器件布局](by-stage/placement.md)　[布线](by-stage/routing.md)　[平面与铺铜](by-stage/plane_pour.md)　[出图与制造](by-stage/manufacturing.md)　[签核验证](by-stage/verification.md)

## 级别与可信度

| | high | medium | low | 合计 |
|---|---|---|---|---|
| must | 95 | 21 | 2 | 118 |
| should | 235 | 114 | 6 | 355 |
| consider | 21 | 32 | 5 | 58 |

含 `conflicts`（来源有分歧）的规则：144 条。

## 验证覆盖

每条规则可有多种验证方式；下表按方式统计规则条数（同一规则在多行重复计入）。

| 验证方式 | full | partial | manual | 规则数 |
|---|---|---|---|---|
| `erc` 原理图 ERC | 22 | 21 | 0 | 41 |
| `drc` PCB DRC / 自定义规则 | 62 | 22 | 1 | 85 |
| `netlist_diff` 网表一致性 | 19 | 7 | 0 | 26 |
| `bom_check` BOM / 器件参数检查 | 33 | 67 | 1 | 101 |
| `geometry_script` 几何脚本 (pcbnew) | 106 | 104 | 0 | 210 |
| `spice` SPICE 仿真 | 8 | 88 | 0 | 96 |
| `tline_calc` 传输线 / 载流计算 | 5 | 10 | 0 | 15 |
| `em_sim` 电磁仿真 | 0 | 12 | 0 | 12 |
| `si_sim` 信号完整性仿真 | 0 | 13 | 0 | 13 |
| `pi_sim` 电源完整性仿真 | 0 | 7 | 0 | 7 |
| `thermal_sim` 热仿真 | 7 | 8 | 3 | 18 |
| `emc_precompliance` EMC 预兼容 | 0 | 0 | 27 | 27 |
| `bench` 实物测量 | 1 | 18 | 163 | 181 |
| `review` 人工评审 | 1 | 13 | 114 | 128 |

至少有一种验证方式可 **完全自动化** 的规则：228 / 531（42%）。

| 领域 | 规则数 | 含完全自动化验证 | 仅人工 / 实测 |
|---|---|---|---|
| 通用 / 数模混合 MCU 板 | 103 | 65 | 3 |
| 电源与功率 | 54 | 28 | 0 |
| 低功耗 / 电池 | 40 | 10 | 2 |
| 射频与天线 | 45 | 15 | 4 |
| 音频 | 43 | 8 | 5 |
| 精密模拟 / 传感器前端 | 46 | 16 | 4 |
| 高速数字 | 52 | 24 | 1 |
| EMC / ESD / 浪涌 | 46 | 13 | 10 |
| 高压 / 隔离 / 安规 | 23 | 11 | 5 |
| 热设计 | 28 | 10 | 6 |
| 可制造 / 可装配 / 可测试 | 51 | 28 | 3 |

## 与示例板（猫咪喂食器）相关（295 条，其中 must 81 条）

标签 `cat-feeder` 表示规则适用于开源示例板 [fxp/cat-feeder](https://github.com/fxp/cat-feeder)（ESP32-C3 模块、电机 MOSFET、INA199 检流、AMS1117 LDO、HX711、2 层板、JLC 贴片）的某个电路，范围较宽。[by-board/cat-feeder.md](by-board/cat-feeder.md) 演示怎样为一块具体的板筛出规则并按优先级排序。

| 领域 | 相关条数 | 其中 must |
|---|---|---|
| 通用 / 数模混合 MCU 板 | 77 | 18 |
| 电源与功率 | 36 | 10 |
| 低功耗 / 电池 | 28 | 5 |
| 射频与天线 | 11 | 3 |
| 精密模拟 / 传感器前端 | 32 | 5 |
| 高速数字 | 11 | 3 |
| EMC / ESD / 浪涌 | 36 | 9 |
| 高压 / 隔离 / 安规 | 5 | 4 |
| 热设计 | 21 | 5 |
| 可制造 / 可装配 / 可测试 | 38 | 19 |

## 文件

* [`catalog/*.yaml`](../catalog/) — 规则本体（唯一事实来源），格式见 [SCHEMA.md](SCHEMA.md)
* [`catalog/verifiers.yaml`](../catalog/verifiers.yaml) — 验证工具目录；[VERIFICATION_TOOLCHAIN.md](VERIFICATION_TOOLCHAIN.md) — 本机已验证的命令与差距
* [VERIFICATION_BACKLOG.md](VERIFICATION_BACKLOG.md) — 规则按验证方式分组的待办（下一步仿真 / EDA 校验的工作包）
* [`skills/`](../skills/) — 按领域生成的 skill（每个含规则索引与全文）；`by-stage/`、`by-board/` — 按环节、按板子的阅读视图
* [RESEARCH_BRIEF.md](RESEARCH_BRIEF.md) — 调研方法与质量要求
