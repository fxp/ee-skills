# 分区规划（floorplan）

37 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-FLR-007](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-007) | 板框闭合，铜到板边满足板厂最小间距 | must | high | drc (full) |
| [GEN-FLR-001](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-001) | 按功能和噪声等级分区，快逻辑靠近电源、模拟最远 | should | high | geometry_script (partial) |
| [GEN-FLR-002](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-002) | 电源入口、稳压器、MCU 依次相邻，地在三者间单点汇合 | should | medium | geometry_script (partial) |
| [GEN-FLR-003](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-003) | 各子系统的走线只在自己的分区内，跨区只走指定通道 | should | high | geometry_script (full) |
| [GEN-FLR-004](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-004) | 大电流路径和开关环路远离敏感小信号 | should | medium | geometry_script (partial) |
| [GEN-FLR-005](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-005) | 连接器集中在板边，噪声源与晶振远离连接器 | should | medium | geometry_script (partial) |
| [GEN-FLR-006](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-006) | 带板载天线的模块放在板边，天线区空出 | should | high | geometry_script (partial) |
| [GEN-FLR-008](../../skills/ee-general-pcb/references/rules.md#GEN-FLR-008) | 安装孔预先定位，孔径和孔距满足板厂，并留地回流接点 | consider | medium | drc (full) |

## 电源与功率

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [PWR-FLR-001](../../skills/ee-power/references/rules.md#PWR-FLR-001) | 电机/开关电源功率区与模拟、射频区分区 | should | medium | geometry_script (partial) |
| [PWR-FLR-002](../../skills/ee-power/references/rules.md#PWR-FLR-002) | 电源入口按防护、储能、稳压顺序布局 | should | high | geometry_script (partial) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-FLR-001](../../skills/ee-rf/references/rules.md#RF-FLR-001) | 天线放板边或板角，馈点贴近板边，辐射部分悬出板外 | must | high | geometry_script (partial) |
| [RF-FLR-002](../../skills/ee-rf/references/rules.md#RF-FLR-002) | 天线禁布区内所有铜层禁铜、禁线、禁件、禁螺丝 | must | high | drc (full) |
| [RF-FLR-003](../../skills/ee-rf/references/rules.md#RF-FLR-003) | 外壳内天线周围留净空，金属件远离天线 | should | high | review (partial) |
| [RF-FLR-004](../../skills/ee-rf/references/rules.md#RF-FLR-004) | 天线远离晶振、高速时钟、开关电源、电机以及 USB/UART | should | medium | geometry_script (partial) |
| [RF-FLR-005](../../skills/ee-rf/references/rules.md#RF-FLR-005) | 单极类天线按厂商参考板提供足够的地平面 | should | high | geometry_script (partial) |
| [RF-FLR-006](../../skills/ee-rf/references/rules.md#RF-FLR-006) | 多天线或收发之间拉开距离、正交放置 | consider | high | em_sim (partial) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-FLR-001](../../skills/ee-audio/references/rules.md#AUD-FLR-001) | 音频板分区：模拟输入、数字、Class-D 功率级各占一区 | should | high | geometry_script (partial) |
| [AUD-FLR-002](../../skills/ee-audio/references/rules.md#AUD-FLR-002) | 定 AGND/DGND 策略：默认单一地平面分区，按 codec 手册例外 | should | high | geometry_script (full) |
| [AUD-FLR-003](../../skills/ee-audio/references/rules.md#AUD-FLR-003) | 平衡接口屏蔽接机壳，信号地与机壳单点连接 | should | medium | review (manual) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-FLR-001](../../skills/ee-analog/references/rules.md#ANA-FLR-001) | 把模拟区与数字/射频/开关区分开 | should | high | geometry_script (full) |
| [ANA-FLR-002](../../skills/ee-analog/references/rules.md#ANA-FLR-002) | 精密元件远离热源和板边气流 | should | high | geometry_script (partial) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-FLR-001](../../skills/ee-high-speed/references/rules.md#HSD-FLR-001) | 以太网前端分区：PHY、磁件、RJ45 的距离与隔离 | should | medium | geometry_script (full) |
| [HSD-FLR-002](../../skills/ee-high-speed/references/rules.md#HSD-FLR-002) | DDR 通道专用走线区，SDRAM 与 SoC 同面 | should | high | geometry_script (partial) |

## EMC / ESD / 浪涌

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [EMC-FLR-003](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-003) | 连接器到 TVS 之间划 ESD 入口禁布区 | must | high | geometry_script (full) |
| [EMC-FLR-001](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-001) | 按功能分区，高速逻辑靠电源入口，模拟远离 | should | high | geometry_script (partial) |
| [EMC-FLR-002](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-002) | 连接器集中在板边一侧，ESD 敏感电路放中央 | should | high | geometry_script (partial) |
| [EMC-FLR-004](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-004) | 电机/继电器/驱动区与 MCU 和模拟采样区分开 | should | medium | geometry_script (partial) |
| [EMC-FLR-005](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-005) | MCU 靠稳压器，稳压器靠供电入口，地在三者间单点参考 | should | medium | geometry_script (partial) |
| [EMC-FLR-006](../../skills/ee-emc-esd/references/rules.md#EMC-FLR-006) | 线缆屏蔽层 360° 端接到壳体，禁用长辫子 | consider | low | review (manual) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-FLR-001](../../skills/ee-hv-safety/references/rules.md#HVS-FLR-001) | 定义隔离栅禁布区，任何层都不得有铜跨越 | must | high | drc (full) |
| [HVS-FLR-002](../../skills/ee-hv-safety/references/rules.md#HVS-FLR-002) | 危险电压铜皮与板边、安装孔、外壳可触及件也要满足间距 | should | medium | drc (full) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-FLR-002](../../skills/ee-dfm/references/rules.md#DFM-FLR-002) | 按元件和板形选 V-cut 还是邮票孔拼板 | must | high | review (partial) |
| [DFM-FLR-004](../../skills/ee-dfm/references/rules.md#DFM-FLR-004) | 孔、槽与异形开口的制造下限 | must | high | drc (full) |
| [DFM-FLR-001](../../skills/ee-dfm/references/rules.md#DFM-FLR-001) | 为贴片预留工艺边、工装孔与 MARK 点 | should | medium | geometry_script (partial) |
| [DFM-FLR-003](../../skills/ee-dfm/references/rules.md#DFM-FLR-003) | 高大件和应力敏感件远离分板线 | should | medium | geometry_script (full) |
| [DFM-FLR-005](../../skills/ee-dfm/references/rules.md#DFM-FLR-005) | 外壳与安装孔的配合要吃下制造公差 | should | medium | geometry_script (partial) |
| [DFM-FLR-006](../../skills/ee-dfm/references/rules.md#DFM-FLR-006) | 元件离板边与工艺边保持足够距离 | should | low | geometry_script (full) |
