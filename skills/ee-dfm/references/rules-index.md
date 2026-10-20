# 可制造 / 可装配 / 可测试 — 规则索引

51 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-ARC-001 | 按所选 JLC 贴片档位的能力边界选型 ⚠ | must | high | bom_check(partial) |
| DFM-ARC-004 | 器件必须耐受 JLC 回流峰值并核对 MSL | must | medium | bom_check(partial) |
| DFM-ARC-002 | 优先选 JLC 基础库 / Preferred 器件 ⚠ | should | medium | bom_check(partial) |
| DFM-ARC-003 | 下单前核对每个料号的库存与封装匹配 | should | medium | bom_check(partial) |
| DFM-ARC-005 | 默认按 IPC Class 2 订板，Class 3 另行评估 ⚠ | consider | medium | review(manual) |

## 符号封装库（library）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-LIB-002 | 两端片式元件的两个焊盘必须完全对称 | must | medium | geometry_script(full) |
| DFM-LIB-006 | 封装必须与数据手册极性一致并有可见的 1 脚 / 极性标记 | must | medium | geometry_script(partial) |
| DFM-LIB-001 | 封装按 IPC-7351 密度等级选，默认 Nominal | should | medium | geometry_script(partial) |
| DFM-LIB-003 | QFN/SON 焊盘按 TI 的趾跟宽与间隙建立 | should | high | geometry_script(partial) |
| DFM-LIB-004 | 细间距 QFN 的阻焊开口要成组并圆角 | should | high | drc(partial) |
| DFM-LIB-005 | 通孔封装的孔径按引脚加余量并满足孔环 ⚠ | should | medium | drc(full) |
| DFM-LIB-007 | 丝印与焊盘保持间距 | should | high | drc(full) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-SCH-001 | 原理图符号里带 LCSC 料号字段和 DNP 标记 | should | medium | bom_check(full) |
| DFM-SCH-002 | 在原理图里预留固件下载与调试入口 ⚠ | should | medium | erc(partial) |

## 网表与约束（netlist）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-NET-001 | BOM、CPL 与 PCB 必须一一对应 | must | medium | netlist_diff(full) |
| DFM-NET-002 | 位号不得靠大小写区分 | must | high | netlist_diff(full) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-STK-001 | DRC 的线宽线距不低于板厂能力并留余量 ⚠ | must | high | drc(full) |
| DFM-STK-002 | 钻孔、过孔与孔环的最小值 ⚠ | must | high | drc(full) |
| DFM-STK-003 | 焊盘与走线、孔与走线的间距下限 | must | high | drc(full) |
| DFM-STK-004 | 阻焊桥与阻焊开口的最小值 ⚠ | must | high | drc(full) |

## 分区规划（floorplan）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-FLR-002 | 按元件和板形选 V-cut 还是邮票孔拼板 | must | high | review(partial) |
| DFM-FLR-004 | 孔、槽与异形开口的制造下限 | must | high | drc(full) |
| DFM-FLR-001 | 为贴片预留工艺边、工装孔与 MARK 点 ⚠ | should | medium | geometry_script(partial) |
| DFM-FLR-003 | 高大件和应力敏感件远离分板线 | should | medium | geometry_script(full) |
| DFM-FLR-005 | 外壳与安装孔的配合要吃下制造公差 | should | medium | geometry_script(partial) |
| DFM-FLR-006 | 元件离板边与工艺边保持足够距离 ⚠ | should | low | geometry_script(full) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-PLC-002 | 封装 courtyard 不得重叠 ⚠ | must | low | drc(full) |
| DFM-PLC-001 | 元件间距满足 JLC 最小间距表 ⚠ | should | medium | geometry_script(partial) |
| DFM-PLC-003 | 放置 3 个不对称的全局 MARK 点 ⚠ | should | high | geometry_script(full) |
| DFM-PLC-004 | 细间距器件旁加局部 MARK 点 | consider | medium | geometry_script(partial) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-RTE-002 | 2 层板不要在 SMD 焊盘里放开口过孔 ⚠ | must | medium | geometry_script(full) |
| DFM-RTE-001 | 片式元件两端的铜连接要热平衡 ⚠ | should | medium | geometry_script(partial) |
| DFM-RTE-003 | QFN 1 脚旁保留走线与过孔禁区 | should | medium | review(manual) |
| DFM-RTE-004 | 过孔覆盖方式与孔径、间距要匹配 | should | high | drc(full) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-PLN-001 | 铜皮与走线到板边、V-cut 线的距离 | must | high | drc(full) |
| DFM-PLN-002 | 铺铜上的焊盘用热焊盘，散热焊盘除外 ⚠ | should | medium | drc(partial) |

## 出图与制造（manufacturing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-MFG-001 | Gerber 输出集合完整、带 X2 属性、单位为 mm | must | high | geometry_script(full) |
| DFM-MFG-002 | 钻孔文件按 PTH / NPTH 分开并用成品孔径 | must | high | geometry_script(full) |
| DFM-MFG-003 | BOM 文件格式与内容 | must | medium | bom_check(full) |
| DFM-MFG-004 | CPL 坐标文件的列、单位与方向 ⚠ | must | medium | geometry_script(full) |
| DFM-MFG-005 | 逐个核对 JLC 库与 KiCad 封装的旋转差 | must | medium | bom_check(partial) |
| DFM-MFG-006 | 不贴的零件和通孔件同时移出 BOM 与 CPL | should | medium | bom_check(full) |
| DFM-MFG-007 | 丝印文字与线宽达到可制造下限 | should | high | drc(full) |
| DFM-MFG-010 | 每个电源轨与关键信号至少有一个探测点 | should | medium | netlist_diff(full) |
| DFM-MFG-011 | 细间距或需平整焊盘的器件选 ENIG / OSP ⚠ | should | low | bom_check(partial) |
| DFM-MFG-012 | 钢网开孔：QFN 散热焊盘开窗，细间距缩小 | should | high | geometry_script(partial) |
| DFM-MFG-008 | 为序列号 / 二维码预留位置，不再用 JLCJLCJLCJLC ⚠ | consider | medium | review(manual) |
| DFM-MFG-009 | 测试点的尺寸、间距与可达性 ⚠ | consider | medium | geometry_script(full) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| DFM-VER-001 | 用板厂能力而不是 EDA 默认值跑 DRC | must | high | drc(full) |
| DFM-VER-003 | 下单前核对 CPL 与板文件的几何一致 | must | medium | geometry_script(full) |
| DFM-VER-002 | 用独立查看器重新读一遍出图结果 | should | medium | geometry_script(partial) |
