# 网表与约束（netlist）

19 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-NET-003](../../skills/ee-general-pcb/references/rules.md#GEN-NET-003) | 差分对的两个网络同名并用一致的 _P/_N 后缀 | must | high | erc (full) |
| [GEN-NET-004](../../skills/ee-general-pcb/references/rules.md#GEN-NET-004) | 网络只在原理图里改，PCB 变更要反向标注 | must | high | netlist_diff (full) |
| [GEN-NET-005](../../skills/ee-general-pcb/references/rules.md#GEN-NET-005) | 原理图与 PCB 奇偶性检查要连警告一起设为门禁 | must | high | netlist_diff (full) |
| [GEN-NET-001](../../skills/ee-general-pcb/references/rules.md#GEN-NET-001) | 信号网络显式命名并统一命名风格 | should | medium | erc (full) |
| [GEN-NET-002](../../skills/ee-general-pcb/references/rules.md#GEN-NET-002) | 网络类承载约束并保证每个网络都有归属 | should | high | erc (full) |
| [GEN-NET-006](../../skills/ee-general-pcb/references/rules.md#GEN-NET-006) | 出图前做网表差异对比并附 IPC-D-356 | should | medium | netlist_diff (full) |
| [GEN-NET-007](../../skills/ee-general-pcb/references/rules.md#GEN-NET-007) | 排查孤立标签、单引脚网络和意外短接 | should | high | erc (full) |
| [GEN-NET-008](../../skills/ee-general-pcb/references/rules.md#GEN-NET-008) | 引脚 / 门交换只在功能等价的引脚间进行 | should | high | netlist_diff (partial) |

## 低功耗 / 电池

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [LPW-NET-001](../../skills/ee-low-power/references/rules.md#LPW-NET-001) | 用 BOM 加网表脚本核算常开轨漏电与 Iq 总和 | should | medium | bom_check (partial) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-NET-001](../../skills/ee-rf/references/rules.md#RF-NET-001) | 射频网络单独设网络类，线宽恒定、不分支 | should | medium | drc (full) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-NET-001](../../skills/ee-audio/references/rules.md#AUD-NET-001) | Class-D 输出、自举、Vsense 和电源分别设网络类 | should | medium | drc (full) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-NET-001](../../skills/ee-analog/references/rules.md#ANA-NET-001) | 分流电阻的 sense 抽头用独立网络 | must | high | netlist_diff (full) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-NET-001](../../skills/ee-high-speed/references/rules.md#HSD-NET-001) | 差分对网络按同基名加 P/N 或 +/- 后缀命名 | must | high | netlist_diff (full) |
| [HSD-NET-002](../../skills/ee-high-speed/references/rules.md#HSD-NET-002) | DDR 信号分网络类与字节通道，限定可交换范围 | should | high | netlist_diff (full) |
| [HSD-NET-003](../../skills/ee-high-speed/references/rules.md#HSD-NET-003) | 在 .kicad_dru 中为高速网络类写长度/偏斜/间距规则 | should | high | drc (full) |
| [HSD-NET-004](../../skills/ee-high-speed/references/rules.md#HSD-NET-004) | 把走线失配预算化为时序裕量的 1% | should | high | geometry_script (partial) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-NET-001](../../skills/ee-hv-safety/references/rules.md#HVS-NET-001) | 隔离两侧用独立网络名和网络类，让 DRC 能识别 | should | medium | netlist_diff (full) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-NET-001](../../skills/ee-dfm/references/rules.md#DFM-NET-001) | BOM、CPL 与 PCB 必须一一对应 | must | medium | netlist_diff (full) |
| [DFM-NET-002](../../skills/ee-dfm/references/rules.md#DFM-NET-002) | 位号不得靠大小写区分 | must | high | netlist_diff (full) |
