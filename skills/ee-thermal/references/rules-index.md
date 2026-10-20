# 热设计 — 规则索引

28 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| THM-ARC-001 | 数据手册的 θJA 只对它的测试板成立 | must | high | thermal_sim(partial) |
| THM-ARC-002 | 在最高环境温度下算每个发热件的结温 | must | high | thermal_sim(full) |
| THM-ARC-003 | 线性稳压器的功耗按最坏输入电压和最大电流算 ⚠ | must | high | thermal_sim(full) |
| THM-ARC-006 | MOSFET 导通损耗按热态 Rds(on) 算 | must | high | thermal_sim(full) |
| THM-ARC-004 | 2 层板上预期 θJA 比 4 层测试板的数据差 | should | medium | thermal_sim(partial) |
| THM-ARC-008 | 铝电解电容按本体温度算寿命并远离热源 ⚠ | should | medium | bom_check(partial) |
| THM-ARC-005 | 高海拔使用时放大 θJA | consider | high | thermal_sim(full) |
| THM-ARC-007 | 电机堵转 / 启动的脉冲要对照 MOSFET SOA ⚠ | consider | low | spice(partial) |

## 符号封装库（library）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| THM-LIB-001 | 带裸露焊盘的封装必须有等大的散热焊盘并焊在板上 | must | high | geometry_script(partial) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| THM-STK-001 | 按功耗选铜厚 ⚠ | consider | high | thermal_sim(partial) |
| THM-STK-002 | 需要更低热阻时优先加内层地平面 | consider | high | thermal_sim(manual) |
| THM-STK-003 | 用板面积规则做第一遍可行性检查 | consider | high | thermal_sim(full) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| THM-PLC-001 | 热源与怕热元件分开放 ⚠ | should | medium | geometry_script(partial) |
| THM-PLC-002 | 外壳内的环境温度和空气流动要按实际假设 | should | medium | bench(manual) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| THM-RTE-005 | 散热过孔要实连到尽可能多的层，不用热焊盘 ⚠ | must | high | drc(full) |
| THM-RTE-001 | 大电流走线按 IPC-2152 的温升来定宽 ⚠ | should | low | tline_calc(full) |
| THM-RTE-002 | 散热过孔的孔径、间距与数量 | should | high | geometry_script(full) |
| THM-RTE-004 | 散热过孔的封盖方式要避免焊料流失和空洞 ⚠ | should | high | geometry_script(partial) |
| THM-RTE-003 | 用过孔阵列的并联热阻核算而不是凭感觉 | consider | high | thermal_sim(full) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| THM-PLN-001 | SOT-223 的散热铜面积要按目标 θJA 来定 ⚠ | should | high | geometry_script(partial) |
| THM-PLN-002 | 散热铜优先放在元件面，再用过孔连到背面 | should | high | geometry_script(partial) |
| THM-PLN-003 | 别在散热铜皮上垂直于热流切口 | should | high | geometry_script(partial) |

## 出图与制造（manufacturing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| THM-MFG-001 | 裸露焊盘的焊接面积与空洞要有上限并用 X 光验证 ⚠ | should | high | thermal_sim(full) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| THM-VER-001 | 由外壳温度推结温用 ψJT，不用 θJC | should | high | bench(manual) |
| THM-VER-002 | 测外壳温度的方法要避免热电偶散热误差 | should | high | bench(manual) |
| THM-VER-004 | 在最坏工况、盖好外壳后做稳态热测试 ⚠ | should | medium | bench(manual) |
| THM-VER-003 | MOSFET 结温可用体二极管压降法做电学测量 | consider | medium | bench(manual) |
| THM-VER-005 | 先用热阻网络手算，再决定是否做 FEM | consider | high | thermal_sim(partial) |
