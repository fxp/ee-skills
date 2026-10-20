# 叠层与规则（stackup）

28 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-STK-005](../../skills/ee-general-pcb/references/rules.md#GEN-STK-005) | 按板厂能力设板级约束，不贴着极限设计 | must | high | drc (full) |
| [GEN-STK-001](../../skills/ee-general-pcb/references/rules.md#GEN-STK-001) | 按最高频率与辐射风险选层数，2 层板要补偿 | should | medium | geometry_script (partial) |
| [GEN-STK-002](../../skills/ee-general-pcb/references/rules.md#GEN-STK-002) | 4 层板信号层贴近邻接平面，两平面间用厚芯板 | should | high | geometry_script (full) |
| [GEN-STK-003](../../skills/ee-general-pcb/references/rules.md#GEN-STK-003) | 每个走线层邻接参考平面，高频线埋在两平面之间 | should | high | geometry_script (full) |
| [GEN-STK-004](../../skills/ee-general-pcb/references/rules.md#GEN-STK-004) | 2 层板：底层做地参考，元件只放顶层 | should | high | geometry_script (full) |
| [GEN-STK-006](../../skills/ee-general-pcb/references/rules.md#GEN-STK-006) | 网络类宽度只是默认值，必须用自定义规则落成 DRC | should | high | drc (full) |
| [GEN-STK-007](../../skills/ee-general-pcb/references/rules.md#GEN-STK-007) | 按电流和温升算线宽，IPC-2221 作保守下限 | should | medium | tline_calc (full) |
| [GEN-STK-008](../../skills/ee-general-pcb/references/rules.md#GEN-STK-008) | 载流层间过孔至少两个，并按孔壁截面估算电流 | should | medium | geometry_script (partial) |

## 电源与功率

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [PWR-STK-001](../../skills/ee-power/references/rules.md#PWR-STK-001) | 按电流选外层铜厚并确认板厂实际铜厚 | consider | medium | tline_calc (partial) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-STK-001](../../skills/ee-rf/references/rules.md#RF-STK-001) | 用板厂实际叠层算 50 Ω 线宽，并接受 Dk 与阻抗公差 | should | high | tline_calc (partial) |
| [RF-STK-002](../../skills/ee-rf/references/rules.md#RF-STK-002) | 50 Ω 馈线优先用带地共面波导（CPWG） | should | high | tline_calc (full) |
| [RF-STK-003](../../skills/ee-rf/references/rules.md#RF-STK-003) | 分立射频优先 4 层；2 层板底层须为整块实心地 | should | high | geometry_script (full) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-STK-001](../../skills/ee-audio/references/rules.md#AUD-STK-001) | 含 Class-D 的音频板用 4-6 层，第二层整层做地 | should | high | drc (partial) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-STK-001](../../skills/ee-analog/references/rules.md#ANA-STK-001) | 给模拟信号层配一层完整的地 | consider | medium | geometry_script (partial) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-STK-001](../../skills/ee-high-speed/references/rules.md#HSD-STK-001) | 高速线紧邻完整 GND 参考面，外层微带优先 | must | high | geometry_script (full) |
| [HSD-STK-002](../../skills/ee-high-speed/references/rules.md#HSD-STK-002) | 用板厂实际叠层参数计算阻抗，写明受控线所在层 | should | medium | tline_calc (partial) |
| [HSD-STK-003](../../skills/ee-high-speed/references/rules.md#HSD-STK-003) | 长距离高速差分对对抗玻纤编织偏斜 | consider | high | geometry_script (partial) |

## EMC / ESD / 浪涌

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [EMC-STK-001](../../skills/ee-emc-esd/references/rules.md#EMC-STK-001) | 两层板：栅格化地 + 电源地叠放，逼近四层效果 | should | high | geometry_script (partial) |
| [EMC-STK-002](../../skills/ee-emc-esd/references/rules.md#EMC-STK-002) | 20H 规则有争议，不当作强制规则 | consider | medium | em_sim (partial) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-STK-001](../../skills/ee-hv-safety/references/rules.md#HVS-STK-001) | 板材 CTI 按数据手册定材料组 | should | medium | review (manual) |
| [HVS-STK-002](../../skills/ee-hv-safety/references/rules.md#HVS-STK-002) | 低压（非安规）间距按 IPC-2221B 表设 DRC | should | medium | drc (full) |

## 热设计

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [THM-STK-001](../../skills/ee-thermal/references/rules.md#THM-STK-001) | 按功耗选铜厚 | consider | high | thermal_sim (partial) |
| [THM-STK-002](../../skills/ee-thermal/references/rules.md#THM-STK-002) | 需要更低热阻时优先加内层地平面 | consider | high | thermal_sim (manual) |
| [THM-STK-003](../../skills/ee-thermal/references/rules.md#THM-STK-003) | 用板面积规则做第一遍可行性检查 | consider | high | thermal_sim (full) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-STK-001](../../skills/ee-dfm/references/rules.md#DFM-STK-001) | DRC 的线宽线距不低于板厂能力并留余量 | must | high | drc (full) |
| [DFM-STK-002](../../skills/ee-dfm/references/rules.md#DFM-STK-002) | 钻孔、过孔与孔环的最小值 | must | high | drc (full) |
| [DFM-STK-003](../../skills/ee-dfm/references/rules.md#DFM-STK-003) | 焊盘与走线、孔与走线的间距下限 | must | high | drc (full) |
| [DFM-STK-004](../../skills/ee-dfm/references/rules.md#DFM-STK-004) | 阻焊桥与阻焊开口的最小值 | must | high | drc (full) |
