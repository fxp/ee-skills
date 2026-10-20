# 符号封装库（library）

23 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-LIB-001](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-001) | 符号的引脚号、名称和电气类型逐脚对照数据手册 | must | high | erc (full) |
| [GEN-LIB-002](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-002) | 焊盘图形取自厂商推荐或 IPC-7351 并1:1核对 | must | medium | geometry_script (partial) |
| [GEN-LIB-005](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-005) | 自动核对符号引脚与封装焊盘一致 | must | high | erc (full) |
| [GEN-LIB-003](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-003) | 每个封装画闭合的 courtyard 并满足外扩量 | should | medium | drc (full) |
| [GEN-LIB-004](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-004) | 带散热焊盘的封装补全焊盘编号、过孔与钢网开窗 | should | high | geometry_script (partial) |
| [GEN-LIB-006](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-006) | 3D 模型对准焊盘并核对与贴片厂的旋转约定 | should | medium | geometry_script (partial) |
| [GEN-LIB-007](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-007) | 库只有一个来源：项目内库表且纳入版本控制 | should | high | erc (full) |
| [GEN-LIB-008](../../skills/ee-general-pcb/references/rules.md#GEN-LIB-008) | 库器件携带制造商、型号、数据手册和厂方料号 | should | high | bom_check (full) |

## 电源与功率

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [PWR-LIB-001](../../skills/ee-power/references/rules.md#PWR-LIB-001) | 1117 类 SOT-223 的散热 tab 必须接 VOUT | must | high | netlist_diff (full) |
| [PWR-LIB-002](../../skills/ee-power/references/rules.md#PWR-LIB-002) | 四端子开尔文分流电阻封装要分开力端与感测端 | should | high | netlist_diff (full) |

## 低功耗 / 电池

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [LPW-LIB-001](../../skills/ee-low-power/references/rules.md#LPW-LIB-001) | 在符号或 BOM 里记录低功耗参数及其测试条件 | should | medium | bom_check (full) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-LIB-001](../../skills/ee-rf/references/rules.md#RF-LIB-001) | 天线/模组封装自带厂商禁布区并保持不改 | should | high | drc (full) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-LIB-001](../../skills/ee-audio/references/rules.md#AUD-LIB-001) | MEMS 话筒封装库带声孔与垫圈尺寸 | should | high | geometry_script (full) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-LIB-001](../../skills/ee-analog/references/rules.md#ANA-LIB-001) | 分流电阻用四端子封装并保留开尔文焊盘 | should | high | geometry_script (full) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-LIB-001](../../skills/ee-hv-safety/references/rules.md#HVS-LIB-001) | 高压器件封装库要校核焊盘间距与爬电 | should | low | geometry_script (partial) |

## 热设计

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [THM-LIB-001](../../skills/ee-thermal/references/rules.md#THM-LIB-001) | 带裸露焊盘的封装必须有等大的散热焊盘并焊在板上 | must | high | geometry_script (partial) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-LIB-002](../../skills/ee-dfm/references/rules.md#DFM-LIB-002) | 两端片式元件的两个焊盘必须完全对称 | must | medium | geometry_script (full) |
| [DFM-LIB-006](../../skills/ee-dfm/references/rules.md#DFM-LIB-006) | 封装必须与数据手册极性一致并有可见的 1 脚 / 极性标记 | must | medium | geometry_script (partial) |
| [DFM-LIB-001](../../skills/ee-dfm/references/rules.md#DFM-LIB-001) | 封装按 IPC-7351 密度等级选，默认 Nominal | should | medium | geometry_script (partial) |
| [DFM-LIB-003](../../skills/ee-dfm/references/rules.md#DFM-LIB-003) | QFN/SON 焊盘按 TI 的趾跟宽与间隙建立 | should | high | geometry_script (partial) |
| [DFM-LIB-004](../../skills/ee-dfm/references/rules.md#DFM-LIB-004) | 细间距 QFN 的阻焊开口要成组并圆角 | should | high | drc (partial) |
| [DFM-LIB-005](../../skills/ee-dfm/references/rules.md#DFM-LIB-005) | 通孔封装的孔径按引脚加余量并满足孔环 | should | medium | drc (full) |
| [DFM-LIB-007](../../skills/ee-dfm/references/rules.md#DFM-LIB-007) | 丝印与焊盘保持间距 | should | high | drc (full) |
