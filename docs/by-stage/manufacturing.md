# 出图与制造（manufacturing）

20 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 低功耗 / 电池

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [LPW-MFG-002](../../skills/ee-low-power/references/rules.md#LPW-MFG-002) | 预留可单独测量睡眠电流的断点或测试点 | should | medium | bom_check (full) |
| [LPW-MFG-001](../../skills/ee-low-power/references/rules.md#LPW-MFG-001) | 对 nA 级高阻节点规定清洗与涂覆工艺并验证 | consider | medium | review (manual) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-MFG-001](../../skills/ee-rf/references/rules.md#RF-MFG-001) | 下单前锁定叠层与阻抗要求，换板厂须重算射频线宽 | should | high | geometry_script (partial) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-MFG-001](../../skills/ee-audio/references/rules.md#AUD-MFG-001) | MEMS 话筒工艺：声孔不镀铜、钢网破环、回流后禁水洗 | should | high | geometry_script (partial) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-MFG-001](../../skills/ee-analog/references/rules.md#ANA-MFG-001) | 出厂/首次上电做零点与增益两点校准 | should | high | bench (partial) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-MFG-001](../../skills/ee-high-speed/references/rules.md#HSD-MFG-001) | 下单时声明阻抗控制层、目标值、公差和叠层 | must | medium | bom_check (partial) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-MFG-001](../../skills/ee-hv-safety/references/rules.md#HVS-MFG-001) | 涂覆或阻焊能否缩小间距要按标准确认 | consider | low | review (manual) |

## 热设计

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [THM-MFG-001](../../skills/ee-thermal/references/rules.md#THM-MFG-001) | 裸露焊盘的焊接面积与空洞要有上限并用 X 光验证 | should | high | thermal_sim (full) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-MFG-001](../../skills/ee-dfm/references/rules.md#DFM-MFG-001) | Gerber 输出集合完整、带 X2 属性、单位为 mm | must | high | geometry_script (full) |
| [DFM-MFG-002](../../skills/ee-dfm/references/rules.md#DFM-MFG-002) | 钻孔文件按 PTH / NPTH 分开并用成品孔径 | must | high | geometry_script (full) |
| [DFM-MFG-003](../../skills/ee-dfm/references/rules.md#DFM-MFG-003) | BOM 文件格式与内容 | must | medium | bom_check (full) |
| [DFM-MFG-004](../../skills/ee-dfm/references/rules.md#DFM-MFG-004) | CPL 坐标文件的列、单位与方向 | must | medium | geometry_script (full) |
| [DFM-MFG-005](../../skills/ee-dfm/references/rules.md#DFM-MFG-005) | 逐个核对 JLC 库与 KiCad 封装的旋转差 | must | medium | bom_check (partial) |
| [DFM-MFG-006](../../skills/ee-dfm/references/rules.md#DFM-MFG-006) | 不贴的零件和通孔件同时移出 BOM 与 CPL | should | medium | bom_check (full) |
| [DFM-MFG-007](../../skills/ee-dfm/references/rules.md#DFM-MFG-007) | 丝印文字与线宽达到可制造下限 | should | high | drc (full) |
| [DFM-MFG-010](../../skills/ee-dfm/references/rules.md#DFM-MFG-010) | 每个电源轨与关键信号至少有一个探测点 | should | medium | netlist_diff (full) |
| [DFM-MFG-011](../../skills/ee-dfm/references/rules.md#DFM-MFG-011) | 细间距或需平整焊盘的器件选 ENIG / OSP | should | low | bom_check (partial) |
| [DFM-MFG-012](../../skills/ee-dfm/references/rules.md#DFM-MFG-012) | 钢网开孔：QFN 散热焊盘开窗，细间距缩小 | should | high | geometry_script (partial) |
| [DFM-MFG-008](../../skills/ee-dfm/references/rules.md#DFM-MFG-008) | 为序列号 / 二维码预留位置，不再用 JLCJLCJLCJLC | consider | medium | review (manual) |
| [DFM-MFG-009](../../skills/ee-dfm/references/rules.md#DFM-MFG-009) | 测试点的尺寸、间距与可达性 | consider | medium | geometry_script (full) |
