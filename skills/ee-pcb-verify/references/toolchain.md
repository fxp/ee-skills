# 验证工具链：哪些 `verify.method` 现在就能在本机无头跑通

调研日期 2026-10-20 · 机器：macOS arm64（Darwin 25.5.0） · KiCad 10.0.6 · uv Python 3.14.6 · 被测板：作者的参考板（ESP32-C3 猫咪喂食器 rev C，尚未公开；命令适用于任意 KiCad 10 板，板上的具体数值仅供参考；**只对拷贝操作**）。
配套机器可读目录：`catalog/verifiers.yaml`（38 条，字段见 SCHEMA.md）。下文标 **[实测]** 的都在本机真的跑过，命令与输出原样记录；标 **[文档]** 的读过官方文档但没跑；标 **[未验证]** 的只做了可用性检查。

## 0. 一页结论

**今天就能无头跑通（全部 [实测]）**

* KiCad ERC / DRC（含自定义 `.kicad_dru` 规则）、网表 / BOM / 位置 / IPC-D-356 / 统计导出，均用 `kicad-cli`，单次 0.7–1 s。
* DRC 自定义规则覆盖约 30 种约束类型；用 `fromTo()` 能度量“两个指定焊盘之间的**走线路径长度**”，用“辅助规则区 + assertion”能表达“元件距某焊盘不超过 N mm”。
* `pcbnew` Python（KiCad 自带 Python 3.9）读取任意几何。
* SPICE：KiCad 自带的 `libngspice`（ngspice-45.2）可由 uv 的 Python 3.14 通过 `ctypes` 直接驱动：瞬态、AC、噪声、`.op`、`.meas`、温度扫描、传输线反射、PDN 阻抗均对解析值验证通过。
* 原理图 ↔ PCB 网表按引脚集合比对（40 行原型，对干净板零噪声，对注入的 3 类缺陷全部命中）。
* 只含走线的 IR drop 求解（numpy/scipy）原型，以及 IPC-2221 线宽 / 微带阻抗公式。

**无法无头做 / 本机没有**

* `kicad-cli` 没有仿真子命令；KiCad 的原理图仿真器是 GUI；PCB Calculator 是 GUI；KiCad IPC API 需要运行中的 GUI。
* 没有任何电磁（openEMS、Elmer：brew 无配方、无 macOS 二进制）、热、IBIS、商用 SI/PI 工具。
* 没有 IC 的 SPICE 模型（AMS1117、INA199、MOSFET），原理图 → 带模型网表的流程没走通。

**最该先补的 3 个缺口**：① 规则 ID → 检查器的绑定层 + 一次导出的 `geometry.json`（本库的 `ee-pcb-verify` 已实现第一版）；② 原理图语义规则引擎（网表 + BOM 字段，做去耦 / 上拉 / 极性 / 降额）；③ SPICE 模型库与“原理图 → 带模型网表 → libngspice”流程（再接 PDN / IR drop 的平面感知求解）。

## 1. (a) `verify.method` → 本机最佳工具 → 缺口

| method | 本机最佳工具（verifiers.yaml id） | 已实测能做 | 缺口 / 下一步 |
|---|---|---|---|
| `erc` | KiCad ERC `V-KICAD-ERC` | 引脚未连、电源脚无驱动、标签悬空、引脚类型冲突、重复位号；参考板 0 违规，删 3 根线得 6 个 error | ERC 不懂元件值、去耦、上拉、极性、额定值。需要在 `kicadxml` 网表 + 符号字段上写**语义规则层**（见 §3）。`simulation_model_issue` 等 4 项默认被忽略 |
| `drc` | KiCad DRC `V-KICAD-DRC` + 自定义规则 `V-KICAD-DRU` + `V-KICAD-DRU-FROMTO` + `V-KICAD-DRU-RULEAREA` | 约 30 种约束全部加载；courtyard→板边、线宽、过孔、孔径、环宽、网络总长、skew、via_count、creepage、禁布；与独立几何脚本数值一致 | 做不了：任意两焊盘欧氏距离上限（只能变通）、回路面积、并行段/串扰、返回路径、铜面积/缝合密度、拓扑顺序（见 §2.5）。语法错误会**静默丢弃全部自定义规则**（用金丝雀） |
| `netlist_diff` | `V-KICAD-NETLIST`（kicadxml + pcbnew 焊盘网络，引脚集合比较）；`V-KICAD-PARITY`；`V-KICAD-IPCD356` | 干净板 diff 全空；删封装 / 接错网络 / 改值 3 类缺陷全部命中 | parity 自带 111 条基线噪声（网络名 `/` 前缀、Datasheet 字段、安装孔）；原型只有 40 行，需要工程化（忽略 H*/FID*/测试点、NC 引脚） |
| `bom_check` | `V-KICAD-BOM`（`sch export bom`、`pcb export pos`） | 分组 BOM、字段完整性；pos 导出 | 没有降额 / 生命周期 / 库存 / 价格；原理图里没有 LCSC、电压、容差字段。需要字段约定 + 参数规则表 + JLC 零件数据 |
| `geometry_script` | `V-PCBNEW-PY`（KiCad 自带 Python 3.9）、`V-KICAD-STATS` | 焊盘边到边精确距离（`Shape.Collide` 二分）、courtyard 到板边、禁布区、走线长、回路面积代理、铜区面积 | 手写审计脚本往往硬编码某块板；只出数字没判据；pcbnew 只能子进程调用。要做“一次导出 `geometry.json`，检查在 Python 3.14 里跑” |
| `spice` | `V-LIBNGSPICE`（ctypes）、`V-KICAD-SPICE-NETLIST` | RC 阶跃（误差 4e-6）、AC（−44.88° @ fc）、噪声（相对差 <1e-5）、`.meas`、温度扫描、XSPICE 代码模型加载 | 无 IC 模型；Sim.* 字段 → 网表流程未验证；无 `.step`（Python 循环代替）；无独立 ngspice/LTspice/Xyce（可选） |
| `tline_calc` | 公式实现 `V-PY-TLINE-FORMULAS`；KiCad PCB Calculator（GUI，`V-KICAD-PCBCALC`） | IPC-2221 线宽、HJ 微带阻抗（50 Ω ≈ 2.95 mm @ 1.6 mm FR4） | 公式没和 GUI / 场求解器交叉验证；缺耦合微带、带状线、CPW、差分阻抗。scikit-rf（pip 有 2.2.0，未装）可补 |
| `em_sim` | 无（openEMS、Elmer、Qucs-S 均未装） | — | openEMS / Elmer 在 macOS 无现成包，需源码构建；且没有 KiCad → 求解器的几何导入。对 2 层低速板优先级低 |
| `si_sim` | `V-SI-TLINE-SPICE`（ngspice T 线） | 理想线反射 0.6667 V = 解析值 | 无 IBIS、无串扰 / 眼图。本板信号都是低速，暂不需要 |
| `pi_sim` | `V-PDN-SPICE`（AC 阻抗）、`V-PY-IRDROP`（走线 IR drop） | 100 nF 自谐振 19.05 MHz（解析 19.02）；+5V 路径 28.4 mΩ | IR drop 不含铜皮（GND 铺铜）；电容模型是理想 C+ESR+ESL；无平面电感提取 |
| `thermal_sim` | 无求解器，只有 numpy/scipy 积木 `V-PY-THERMAL` | — | 完全空白；先用数据手册 θ 值 + IPC-2221 温升公式做估算规则，再考虑自写二维有限差分 |
| `emc_precompliance` | 无 | — | 无仪器接口；几何代理量（回路面积、噪声源到敏感点距离）可由 geometry 检查器给出 |
| `bench` | 无 | — | 允许规则状态 `manual_pending`，实测数据用 CSV/JSON 回填 |
| `review` | `V-REVIEW`（清单）、`V-JLC-DFM`（云端，未访问） | — | 评审结论必须带 evidence（位号 / 网络 / 坐标） |

## 2. (b) 已实测的命令与结果

### 2.1 约定

```bash
# 以下每个 shell 片段都假定先执行（只在拷贝目录里工作，不碰原文件）
W=work/verifiers                     # 已在 .gitignore 里；不要用 /tmp
export KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
export KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3     # Python 3.9.13 + pcbnew 10.0.6
export KICAD_CONFIG_HOME=$W/_cfg KICAD_DOCUMENTS_HOME=$W/_docs     # 私有目录，避免写 ~/Library/Preferences/kicad 和扫描 ~/Documents（macOS 的 TCC 会卡死）
export KICAD10_SYMBOL_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols KICAD10_FOOTPRINT_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints
cp <板目录>/cat_feeder_rev_c.kicad_pcb  $W/board/                 # 板拷贝
cp <原理图目录>/cat_feeder_rev_c.{kicad_sch,kicad_pro} <原理图目录>/{sym,fp}-lib-table $W/sch/
cp $W/sch/cat_feeder_rev_c.kicad_pro $W/board/                              # 板目录里原本没有 .kicad_pro，netclass 与板级阈值都在它里面
```

板：66×60 mm 两层，52 个封装（含 H1–H4 安装孔、FID1–FID3 基准点、TP1 测试点），59 个过孔（0.6/0.3 mm），net 名**没有**前导 `/`（`GND`，原理图里是 `/GND`），板坐标原点偏移 (50, 50) mm，netclass `Power`（+5V、+3V3、MOTOR_N、CS_P、VIN）。

### 2.2 ERC **[实测]**

```bash
$KCLI sch erc --format json --severity-all --units mm -o erc.json sch/cat_feeder_rev_c.kicad_sch
#   Found 0 violations / Saved ERC Report to erc.json   (0.7 s, rc=0)
```

JSON 形状：`{"$schema","coordinate_units","date","ignored_checks":[{key,description}],"included_severities","kicad_version","sheets":[{"path","uuid_path","violations":[{"description","items":[{"description","pos":{"x","y"},"uuid"}],"severity","type"}]}],"source"}`。
默认忽略（裸工程）：`single_global_label`、`four_way_junction`、`simulation_model_issue`、`footprint_filter`。

反例：在副本里用脚本删掉 3 个 `(wire …)` 块 →

```
Found 6 violations     # 4× pin_not_connected, 1× label_dangling, 1× power_pin_not_driven (全部 error)
$KCLI sch erc --severity-all --exit-code-violations ...   →  rc=5      (不加该开关 rc=0)
```

注意：JSON 里 `pos` 是原理图 mm 坐标的 **1/100**（label 实际在 (30.48, 50.8) mm，JSON 写 (0.3048, 0.508)），不要用来定位。

### 2.3 DRC 基线与 JSON 形状 **[实测]**

```bash
$KCLI pcb drc --format json --severity-all --all-track-errors --units mm -o board/drc_base.json board/cat_feeder_rev_c.kicad_pcb
#   Found 16 violations / Found 0 unconnected items       (0.8 s, rc=0)
#   16 = 6× silk_overlap + 10× silk_over_copper，全是 warning
```

```json
{
  "$schema": "https://schemas.kicad.org/drc.v1.json", "coordinate_units": "mm", "date": "…", "kicad_version": "10.0.6", "source": "cat_feeder_rev_c.kicad_pcb",
  "included_severities": ["error","warning","exclusion"],
  "ignored_checks": [{"description": "Footprint has no courtyard defined", "key": "missing_courtyard"}, …],
  "unconnected_items": [], "schematic_parity": [],
  "violations": [{
    "description": "Clearance violation (rule 'courtyard_to_edge_3.0' clearance 3.0000 mm; actual 2.6300 mm)",
    "items": [{"description": "Segment on Edge.Cuts", "pos": {"x": 52.0, "y": 50.0}, "uuid": "…"}, {"description": "Footprint U1", "pos": {"x": 83.0, "y": 71.0}, "uuid": "…"}],
    "severity": "error", "type": "clearance"}]
}
```

* 实测值**只在 description 字符串里**（`actual 2.6300 mm`），要正则取；规则名在 `rule 'NAME'`。
* 默认 ignore（裸工程）：`missing_courtyard`、`track_not_centered_on_via`、`tuning_profile_track_geometries`、`footprint_filters_mismatch`、`footprint_type_mismatch`。**缺 courtyard 的封装默认不报**，DFM 规则要把 `missing_courtyard` 设为 error。
* 退出码：默认 0；`--exit-code-violations` 且存在违规 → 5（默认严重度含 warning；`--severity-error` 时只看 error）；板文件打不开 → 3。
* 没有 `.kicad_pro` 时：`hasNetclass('Power')` 恒为假，且多出 45 条 `lib_footprint_issues`。

### 2.4 自定义规则 `.kicad_dru` **[实测 + 文档]**

**用法**：文件名 `<板文件名>.kicad_dru`，放在 `.kicad_pcb` 同目录（同目录要有同名 `.kicad_pro`），然后跑同样的 `kicad-cli pcb drc`。语言参考 [KiCad 10 官方文档 · Custom design rules](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html#custom-design-rules)（本次逐条读过约束、属性、函数三张表）。

```
(version 1)                                     # KiCad 10.0 的规则语言版本是 1
(rule "NAME"                                    # 名字任意字符串，出现在报告 rule 'NAME' 中 → 建议直接用目录规则 ID
    [(severity error|warning|ignore|exclusion)]
    [(layer "F.Courtyard"|outer|inner|…)]       # 比 condition 里写 A.Layer 高效
    [(condition "A.Type == 'Pad' && B.Layer == 'Edge.Cuts'")]
    (constraint <type> (min 0.2mm) (opt …) (max …)))   # 一条规则可带多个 constraint
```

* 倒序求值，**同一约束类型下最后一条命中的规则胜出**（见下面屏蔽实验）。比较 `== != > >= < <= && || !`，所有布尔运算符优先级相同、左到右。单位后缀 `mm mil th in " deg rad`；无后缀时用内部单位（nm、度）。可空属性与 `null` 比较。
* **34 个约束类型**（官方表）：`annular_width assertion bridged_mask clearance connection_width courtyard_clearance creepage diff_pair_gap diff_pair_uncoupled disallow edge_clearance hole_clearance hole_size hole_to_hole length min_resolved_spokes physical_clearance physical_hole_clearance silk_clearance skew solder_mask_expansion solder_paste_abs_margin solder_paste_rel_margin text_height text_thickness thermal_relief_gap thermal_spoke_width track_angle track_segment_length track_width via_count via_dangling via_diameter zone_connection`。
* `disallow` 的对象：`track via through_via micro_via blind_via buried_via pad zone text graphic hole footprint`。
* 条件里的函数：`intersectsArea('名') enclosedByArea('名') intersectsCourtyard('U1'|'R*'|'${Class:X}') (及 Front/Back) memberOfFootprint memberOfGroup memberOfSheet memberOfSheetOrChildren hasComponentClass hasNetclass hasExactNetclass inDiffPair('/USB*') isCoupledDiffPair(AB) isPlated isMicroVia isBlindVia isBuriedVia existsOnLayer getField('LCSC') fromTo('U1-15','R7-2')`；已弃用 `insideArea insideCourtyard memberOf`。
* 属性（节选）：通用 `Layer Locked Parent Position_X Position_Y Type`（Type = Bitmap/Dimension/Footprint/Graphic/Group/Leader/Pad/Target/Text/Text Box/Track/Via/Zone）；铜对象 `Net NetName NetClass`；封装 `Reference Value（实测不可用，见下第 4 条）Library_Link Component_Class Do_not_Populate Exclude_From_* Orientation Keywords Not_in_Schematic Thermal_Relief_*`；焊盘 `Pad_Number Pad_Shape Pad_Type Pin_Name Pin_Type Fabrication_Property Hole_Size_X/Y Size_X/Y Pad_To_Die_Length *_Margin_Override`（`Fabrication_Property` ∈ None / BGA pad / Fiducial, global to board / Fiducial, local to footprint / Test point pad / Heatsink pad / Castellated pad）；走线 `Origin_X/Y End_X/Y Width`；过孔 `Diameter Hole Layer_Top Layer_Bottom Via_Type`；区域 `Name Priority Min_Width Pad_Connections Hatch_*`；图形 `Shape Line_Width Line_Style Filled`；文本 `Text Height Width Thickness Mirrored Visible Name`。

**实跑：courtyard → 板边 ≥ 2.5 mm（2.5 mm 是 SMT 常用的元件到板边经验值，JLC 没有公开数字）**

```
# $W/exp_a_2.5/cat_feeder_rev_c.kicad_dru   （.kicad_pcb / .kicad_pro 是拷贝）
(version 1)
(rule "courtyard_to_edge_2.5"
    (layer "F.Courtyard")
    (constraint physical_clearance (min 2.5mm))
    (condition "B.Layer == 'Edge.Cuts' && A.Reference != 'H*' && A.Reference != 'FID*'"))
```

| 阈值 | 结果 | 违规摘要 |
|---|---|---|
| 2.5 mm | **通过**：除 16 条原有 silk warning 外 0 条新增 | 最小实测 2.63（U1） |
| 3.0 mm | **触发 4 条，全属 U1** | `actual 2.6000`（3 条 courtyard 线段，线宽影响）与 `Footprint U1 actual 2.6300` |
| 3.15 mm | 触发 16 条，属 U1、SW1、SW2、SW3 | SW 的 `Footprint SWn actual 3.0800`（线段 3.0500） |

独立的几何脚本对同一板的 `edge_clearance_courtyard_mm` 是 U1 2.63、SW1–3 3.08、J1–4 3.21，**与 DRC 的 Footprint 级数值一致**。注意：① 不豁免 H* 时 4 个安装孔各报 6–7 条（courtyard 圆到板边 0.88–1.04 mm）；② 同一封装出现多条记录（封装本体 + courtyard 线段，差一个线宽），检查器要按位号去重取最小值；③ 报告 `type` 是 `clearance`（`physical_clearance` 与 `clearance` 同名）。

**全约束实测表**（用一次性脚本逐个片段运行，脚本已随工作目录删除，做法同附录 C：每个片段前面放一条金丝雀规则；“命中”= 在 参考板副本上产生了该规则的违规）

| 约束（片段要点） | 加载 | 命中数 | 违规 `type` 与示例 |
|---|---|---|---|
| `clearance` Power 类 ≥0.35 | 是 | 161 | `clearance`，actual 0.2010 mm |
| `physical_clearance`（F.Cu 上 Pad–Pad 不同网） ≥0.5 | 是 | 4 | `clearance`，actual 0.3000 |
| `track_width` Power ≥0.6 | 是 | 109 | `track_width`，actual 0.5000 |
| `via_diameter` ≥0.7 | 是 | 59 | `via_diameter`，actual 0.6000 |
| `hole_size` ≥0.35（A.Type=='Via'） | 是 | 59 | `drill_out_of_range`，actual 0.3000 |
| `annular_width` ≥0.2（过孔） | 是 | 59 | `annular_width`，actual 0.1500 |
| `hole_to_hole` ≥0.8 | 是 | 3 | `hole_to_hole`，actual 0.7440（≥0.5 时 0 条） |
| `hole_clearance` ≥0.35 | 是 | 4 | `hole_clearance`，actual 0.2505 |
| `physical_hole_clearance` ≥0.5（SMD） | 是 | 47 | `hole_clearance`，actual 0.4000 |
| `edge_clearance` ≥4（非封装对象） | 是 | 29 | `copper_edge_clearance`，actual 3.7500 |
| `courtyard_clearance` ≥2 | 是 | 55 | `courtyards_overlap`，actual 1.2000 |
| `silk_clearance` ≥0.3 | 是 | 386 | `silk_overlap` / `silk_over_copper` |
| `connection_width` ≥0.4 | 是 | 118 | `connection_width`，actual 0.2501 |
| `creepage` Power ≥5 | 是 | 52 | `creepage`，actual 0.5500 |
| `length` IO3 ≤40 | 是 | 1 | `length_out_of_range`，actual 50.3233 |
| `skew` IO3/IO4/IO5 ≤1 | 是 | 2 | `skew_out_of_range`，actual −4.0694 |
| `via_count` IO4 ≤1 | 是 | 1 | `too_many_vias`，actual 4 |
| `track_angle` ≥135（纯数字） | 是 | 12 | `track_angle`，actual 90° |
| `track_angle` ≥135**deg** | **否（整个文件被丢弃）** | — | 语法错误，见下 |
| `track_segment_length` ≥0.3 | 是 | 21 | `track_segment_length`，actual 0.1547 |
| `text_height` ≥1.2 / `text_thickness` ≥0.2 | 是 | 139 / 147 | 同名 type |
| `disallow via`（A.intersectsCourtyard('U1')） | 是 | 8 | `items_not_allowed` |
| `assertion`（`A.getField('LCSC') != ''`，仅封装） | 是 | 52 | `assertion_failure`（52 = 全部封装，板上无 LCSC 字段）；`A.getField('Value') != ''` 0 条 |
| 坐标禁布：`A.Position_Y < 70mm` + `disallow footprint` | 是 | 10 | `items_not_allowed`，与独立几何脚本列出的 10 个 y<20 的元件一致 |
| `fromTo('U1-15','R7-2')` length | 是 | 见 §2.5 | `length_out_of_range` |
| `memberOfSheet('/')`；`Pin_Type == 'Power input'`；`hasComponentClass('Power_Stage')`；`Fabrication_Property == 'Heatsink pad'` + `zone_connection` | 是 | 102 / 0 / 0 / 0 | 第一项为 `clearance`；后三项只验证了加载（板上没有 component class；Pin_Type 0 条原因未查；zone_connection 本身不产生违规） |
| `bridged_mask`、`via_dangling`、`min_resolved_spokes 4`、`diff_pair_gap`、`diff_pair_uncoupled` | 是 | 0 | 本板无触发对象（无差分对、无悬空过孔） |
| `solder_mask_expansion`、`solder_paste_abs/rel_margin`、`thermal_relief_gap`、`thermal_spoke_width`、`zone_connection` | 是 | 0 | 这些是出图 / 铺铜取值，不是检查 |

**四个必须写进框架的语义（均实测）**

1. **语法错误 → 全部自定义规则被静默丢弃，kicad-cli 返回 0、无任何输出**。已测：未知约束名、未知属性、引号嵌套错误、`track_angle (min 135deg)`。后果是“全部通过”的假象。对策：每次运行在规则文件开头放一条金丝雀并检查它出现在结果里：

```
(rule "__canary__" (severity warning) (condition "A.Type == 'Footprint'") (constraint assertion "A.Reference == '__never__'"))
```

   正常时它对每个封装触发一次（参考板 = 52 条 = 封装数，还可作为完整性校验）。金丝雀缺席 → 状态 `error`，并对规则**逐条各跑一次**二分定位坏规则（每次 0.8 s）。
2. **屏蔽**：同一约束类型、条件重叠时，文件里靠后的规则整个吃掉靠前的。实测 Power 类 `clearance 0.35`（前）+ `clearance 0.2`（后）→ 0 条违规；对调顺序 → 167 条。不同约束类型（clearance + track_width）互不影响。对策：**一条目录规则一次 DRC**（并行进程池），或只把条件互斥的规则放进同一个文件。
3. 没有 `.kicad_pro` 时 `hasNetclass()` 为假；本板的 `.kicad_pro` 在 `schematic/` 子目录，不在板目录里。
4. **属性怪癖（10.0.6 实测，与文档不符）**：`A.Value` 永不匹配（`A.Value == '10k'` 0 条，`A.getField('Value') == '10k'` 5 条）；`A.Orientation` 与无单位数比较不命中（`== 90`、`!= 0` 均 0 条；`== 90deg` 11 条）——条件里的角度要带 `deg`，而 `track_angle` 的约束参数相反、不能带。`Reference`、`Library_Link`、`Pad_Type`、`Pad_Shape`、`NetName`、`Position_X/Y`、`Hole`、`Type` 正常。写规则前先在种子板上验证属性是否真的命中。

### 2.5 DRC 做不到的规则形状，以及变通 **[实测 + 文档]**

**做不到**（DRC 语言里没有对应的度量）：

* 两个**指定对象**之间的欧氏距离（中心或边到边）上限 / 下限，如“去耦电容距 VDD 引脚 ≤ 3 mm”；
* **回路面积 / 回路电感**；
* 两条**不同网络**走线的并行长度（串扰）；`diff_pair_uncoupled` 只管同一差分对的两根线；
* 返回路径连续性（走线跨过平面割缝）、参考平面是否完整；
* 铜面积 / 密度 / 平衡，缝合过孔密度或间距，过孔围栏；
* 网络拓扑与顺序（保险丝在 TVS 之前、星形接地）；
* 依赖原理图语义的关联（“某 IC 的每个 VDD 脚配一个 100 nF”）：DRC 只看到封装、焊盘和字段，看不到“哪个电容服务哪个引脚”。

**变通 1：`fromTo` 量走线路径长度 [实测]**。`length` + `A.fromTo('C8-1','U1-1')` 只数这两个焊盘之间的铜路径。用很小的 max 强制触发以读 `actual`：

| fromTo | DRC 路径长度 | 焊盘中心欧氏距离 |
|---|---|---|
| C8-1 → U1-1（3V3 去耦） | 7.4508 mm | 7.4 |
| C4-1 → U1-1 | 9.6631 | 7.9 |
| C1-1 → U2-3（LDO 输入电容） | 2.3092 | 3.1 |
| U3-4 → R10-2（检流 +） | 1.7585 | 2.6 |
| D1-2 → J3-2（续流二极管阳极） | 3.5000 | 3.5 |
| U1-15 → R7-2（IO3 串阻） | 11.9752（整网 IO3 为 50.3233） | — |

限制：量的是**铜路径**（≥ 欧氏距离），两点必须已连通；仅靠铺铜连通的路径（GND）不唯一；from 匹配到多个同网络 to 焊盘时路径不生成（官方文档 From-To 一节）。

**变通 2：辅助规则区 + assertion [实测]**。用 pcbnew 在板**副本**里按目标焊盘加一个命名规则区（附录 E），再写：

```
(rule decap_C8_near_U1_1 (condition "A.Type == 'Footprint' && A.Reference == 'C8'") (constraint assertion "A.intersectsArea('near_U1_1')"))
```

* 以 U1.1（74.25, 65.0）为中心、半边长 5 mm：C8（焊盘距 7.4 mm）→ `assertion_failure`；半边长 8 mm：`intersectsArea` 通过，`enclosedByArea` 仍失败（C8 courtyard 右缘出区）。
* 结论：能表达“最大距离”，但区域是多边形不是欧氏距离；**更直接的做法仍是 pcbnew 脚本算焊盘边距**（§2.7）。

### 2.6 网表 / BOM / parity / IPC-D-356 / 统计 **[实测]**

```bash
$KCLI sch export netlist --format kicadxml  -o net.xml  sch/cat_feeder_rev_c.kicad_sch    # 68 KB；还有 kicadsexpr、cadstar、orcadpcb2、spice、spicemodel、pads、allegro
$KCLI sch export netlist --format spice     -o net.cir  sch/cat_feeder_rev_c.kicad_sch    # 671 B：R/C 有值行（C4 +3V3 GND 100n），IC 为 "U1 __U1" 占位，DNP 件行尾带 "DNP"
$KCLI sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},LCSC,${DNP}' --labels 'Refs,Value,Footprint,Qty,LCSC,DNP' \
      --group-by 'Value,Footprint,LCSC' -o bom.csv sch/cat_feeder_rev_c.kicad_sch
#   "C4,C7-C10,C12","100nF","Capacitor_SMD:C_0603_1608Metric","6","",""      （LCSC 列为空：原理图没有这个字段）
$KCLI pcb export stats --format json -o stats.json board/cat_feeder_rev_c.kicad_pcb
#   66×60 mm, min_track_clearance "0.2750 mm", min_track_width "0.2500 mm", min_drill_diameter "0.3000 mm", through_hole 11 / smd 120 / npth 4
$KCLI pcb export ipcd356 -o board.ipc board/cat_feeder_rev_c.kicad_pcb                     # 327 行=SMD 焊盘 111 条；317 行=通孔/过孔 70 条
```

**Parity**（原理图须与 PCB 同名同目录）：

```bash
$KCLI pcb drc --schematic-parity --format json --severity-all -o drc_parity.json cat_feeder_rev_c.kicad_pcb
#   干净板：Found 111 schematic parity issues      ← 基线噪声（见下）
#   改板后（删 C12、R1.2 改 GND、R2 值改 999k）：112 条，多出 missing_footprint(C12)、net_conflict(R1.2 "GND" vs "/EN")、footprint_symbol_mismatch(R2)
```

基线噪声构成：每个焊盘一条 `net_conflict`（PCB 网络名 `EN` vs 原理图 `/EN`）、每个封装一条 `footprint_symbol_field_mismatch`（Datasheet `''` vs `'~'`）、H1–H4 `extra_footprint`、TP1 的 BOM 属性。所以直接用 parity 要先归一化名字并按 type 过滤。

**更稳的引脚集合 diff（附录 D）**：

```
$ python3 netlist_diff.py net.xml pcb_ok.json      → 5 类全空，退出 0
$ python3 netlist_diff.py net.xml pcb_bad.json     → 退出 1
  "missing_in_pcb": ["C12"], "value_mismatch": ["R2: sch=10k pcb=999k"],
  "net_only_in_sch": ["EN: [C5.1, R1.2, SW1.1, U1.2]", "GND: [… 不含 R1.2 …]"], "net_only_in_pcb": ["EN: [C5.1, SW1.1, U1.2]", "GND: […, R1.2, …]"]
```

### 2.7 pcbnew Python **[实测]**

```bash
$KPY -c "import sys,pcbnew; print(sys.version.split()[0], pcbnew.Version())"        # 3.9.13  10.0.6
$KPY -I -c "import pcbnew"                                                          # 加 -I 隔离 ~/Library/Python/3.9 里的用户包
uv run python -I -c "import sys; sys.path.insert(0,'/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages'); import pcbnew"
#   → ImportError: dlopen(…/_pcbnew.so, 0x0002): Library not loaded: @rpa…   （_pcbnew.so 是 cpython-39 的扩展，3.14 里不行）
```

焊盘边到边精确距离（`Shape.Collide` 带间隙参数，对间隙二分）：

```python
a = b.FindFootprintByReference("C8").FindPadByNumber("1").GetEffectiveShape(pcbnew.F_Cu)     # 注意要传层参数
u = b.FindFootprintByReference("U1").FindPadByNumber("1").GetEffectiveShape(pcbnew.F_Cu)
lo, hi = 0, pcbnew.FromMM(20)
for _ in range(30):
    mid = (lo + hi) // 2
    lo, hi = (lo, mid) if a.Collide(u, mid) else (mid, hi)
# → 6.225 mm（焊盘边到边），而中心距 7.4 mm
```

### 2.8 libngspice **[实测]**

* 库：`/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/libngspice.0.dylib`（23 460 272 字节，arm64+x86_64 通用二进制；`Frameworks/` 下有同大小的副本；XSPICE 代码模型 `PlugIns/sim/ngspice/{analog,digital,spice2poly,table,tlines,xtradev,xtraevt}.cm`）。
* `kicad-cli --help` 与 `sch --help` 的子命令只有 `erc / export / upgrade`：**没有无头仿真**。
* 驱动代码见附录 A（`ctypes`，uv Python 3.14 可直接用，**无需安装任何包**）。结果：

```
version: ngspice-45.2 (KLU)
-- 瞬态 RC：R=1k C=1u tau=1 ms，PULSE(0 1 0 1n 1n 1 2)，.tran 10u 5m          526 点，2 ms
  t=0.5τ sim=0.39346 analytic=0.39347    t=1τ sim=0.63212 analytic=0.63212    t=2τ 0.86467/0.86466    t=3τ 0.95021/0.95021    t=5τ 0.99326/0.99326
  max abs error vs analytic: 4.44e-06  PASS
-- AC：fc=159.15 Hz；最近点 f=158.49 Hz |H|=0.7086 相位 −44.88°（解析 |H|=0.7086）
-- .op 分压 3.3 V×22k/(10k+22k)：2.26875（解析 2.26875）
-- .noise 10 kΩ：onoise_spectrum[0]=1.287474e-8 V/√Hz（解析 √(4kTR)=1.287481e-8）
-- .meas tran t63 WHEN v(out)=0.63212 RISE=1  →  t63 = 1.00000e-03
-- .options temp 扫描 二极管(1 kΩ, 5 V)：−40 °C 0.8007 V，27 °C 0.6929 V，85 °C 0.5966 V
-- codemodel …/analog.cm  → rc=0
-- SI：Rs=50 Ω，T 线 Z0=50 Ω TD=1 ns，RL=100 Ω：Vout(5 ns)=0.6667 V（解析 0.5·(1+Γ)=0.6667，Γ=1/3）
-- PDN：100 nF/ESR 30 mΩ/ESL 0.7 nH，1 A AC 源：最小 |Z|=30.00 mΩ @ 19.05 MHz（解析 f0=19.02 MHz，ESR=30 mΩ）
-- PDN：LDO(50 mΩ+20 nH) ∥ 22 µF ∥ 10 µF ∥ 100 nF（含各自 ESR/ESL）：|Z| 100 kHz 38.4 mΩ，10 MHz 84.3 mΩ，100 MHz 233.2 mΩ
```

### 2.9 公式与 IR drop **[实测：脚本能跑；精度只对照了文献公式，未对照 GUI / 场求解器]**

* [官方文档](https://docs.kicad.org/10.0/en/pcb_calculator/pcb_calculator.html)：KiCad PCB Calculator 含 Regulators、RF 衰减器、E 系列、色环、TransLine（微带 Atwater、耦合微带 Kirschning-Jansen/Jansen、CPW、带状线、同轴、波导、双绞线，基于 Transcalc）、Via Size、Track Width（IPC-2221）、Electrical Spacing（IPC-2221 间距表）、Board Classes（IPC-6011/6012）。全部 GUI，`kicad-cli` 无入口。
* 附录 B 的 Python 复现，输出：

```
IPC-2221 外层 1 oz ΔT=10 °C：0.5 A → 0.115 mm，1 A → 0.300 mm，2 A → 0.781 mm，3 A → 1.367 mm；内层 1 A → 0.781 mm
微带 h=1.6 mm εr=4.5 t=35 µm：w=1.0 → HJ 84.4 Ω / IPC-2141 87.3 Ω；w=2.0 → 61.8 / 63.2；w=3.0 → 49.5 / 49.0；w=3.1 → 48.5 / 47.8
50 Ω 线宽（HJ，二分）：2.945 mm
```

* IR drop 原型（附录 F）：从板子导出走线 / 过孔 / 焊盘，建电阻网络（R=ρL/(w·t)，ρ=1.68e-8 Ω·m，t=35 µm，过孔 0.5 mΩ 占位），用稀疏矩阵求焊盘对有效电阻：

```
+5V:    F1.2 → U2.3  R = 28.4 mΩ，1.0 A 压降 28.4 mV
+5V:    F1.2 → C1.1  R = 31.5 mΩ，0.2 A 压降 6.3 mV
MOTOR_N: J3.2 → Q1.3 R =  7.4 mΩ，1.0 A 压降 7.4 mV
+3V3:   U2.2 → U1.1  R = 31.4 mΩ，0.4 A 压降 12.6 mV
```

只数走线，铺铜网络（GND）是上界；未与独立工具比对。

### 2.10 其它工具的可用性（只读检查）

| 工具 | 检查方式 | 结果 |
|---|---|---|
| ngspice 独立版 | `which ngspice`；`brew info --formula ngspice` | 未安装；brew 稳定版 47（KiCad 自带库为 45.2） |
| LTspice | `brew info --cask ltspice` | 未安装；cask 26.0.2 |
| Xyce / openEMS / Elmer / Qucs-S | `which`；`brew info`（formula 与 cask） | 全部未安装，brew 均无配方；官方页：[Xyce](https://xyce.sandia.gov/)（GPL，页称桌面平台可串行运行，下载页本次访问失败）、[openEMS 安装页](https://docs.openems.de/en/latest/install/index.html)（需“克隆-构建-安装”）、[Elmer 仓库](https://github.com/ElmerCSC/elmerfem)（预编译包列表无 macOS）、[Qucs-S](https://github.com/ra3xdh/qucs_s)（页称含 macOS，后端 ngspice/Xyce/SpiceOpus/Qucsator） |
| gmsh / gnuplot / FreeCAD | `brew info` | brew 有 gmsh 4.15.2、gnuplot 6.0.5、freecad cask；均未装 |
| Python 库（`python3 -m pip index versions`） | 只查版本，未下载 | scikit-rf 2.2.0、kiutils 1.4.8、kicad-skip 0.2.5、KiKit 1.8.1、sexpdata 1.0.2、PySpice 1.5、spicelib 1.6.4、ltspice 1.0.6、skidl 3.0.0、gerbonara 1.6.3、pcb-tools 0.1.6、pygerber 2.4.3、pyibis 2.4.1、kicad-python 0.8.0（IPC API）、gmsh 4.15.2、pyvista 0.49.1、scikit-fem 12.0.2、devsim 2.11.1、pyaedt 1.9.0；**不存在**：openEMS、CSXCAD、ngspyce、pyngspice、skrf-ibis、ibis-parser |
| uv 环境已装 | `uv pip list` | numpy 2.5.4、scipy 1.18.1、networkx 3.7、lxml 6.1.3、rtree 1.4.1、trimesh 5.1.1、pyyaml 6.0.3（没有 shapely / matplotlib / kiutils / PySpice） |
| KiCad IPC API（kipy） | 读 [官方说明](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/) | 需运行中的 GUI；需要运行中的 KiCad 图形界面，未测 |

## 3. (c) 规则检查框架：最小架构与建设顺序

**目标**：`rule id → checker → {status, measured, threshold, evidence}`，对 catalog 里每条规则可重复、可审计地给出 pass / fail。

### 3.1 组件

```
catalog/*.yaml  (规则: id, severity, parameters[], verify[])      ← 已有
bindings/*.yaml (新增) rule_id → {checker, params 映射, applies_when}    ← 把 verify.check 的文字变成可执行绑定
design/<board>.yaml (新增) 角色表：电源网络、IC 电源脚↔去耦电容、噪声源/敏感点、天线禁布区、连接器…
runner.py        读以上三者 + 一份板子的拷贝 → 导出 facts（一次） → 逐条调用 checker（并行） → results.json
facts/           erc.json  netlist.xml  drc_base.json  pcb_nets.json  geometry.json  bom.csv   （每次运行只生成一次，哈希入报告）
checkers/        drc_rule.py  geometry.py  netlist.py  spice.py  manual.py
```

**为什么先导出 `geometry.json` 再检查**：pcbnew 只能在 KiCad 自带 Python 3.9 里用且 SWIG 绑定不稳定。让一个很小的导出脚本（`$KPY -I export_geometry.py board.kicad_pcb geometry.json`，输出封装 / 焊盘多边形 / courtyard / 走线 / 过孔 / 铜区 / 板框 / 网络 / netclass）承担全部 pcbnew 耦合，其后所有几何检查在 uv 的 Python 3.14 里用纯 Python + numpy/scipy/rtree/trimesh 计算：可单测、可并行、不依赖 GUI，将来 pcbnew 绑定变了也只改一处。

### 3.2 结果 JSON（每条规则一个对象）

```json
{
  "rule_id": "DFM-PLC-901",
  "checker": "drc_rule",
  "status": "fail",                      // pass | fail | error（工具失败 / 金丝雀缺席）| skipped（不适用）| manual_pending
  "severity": "must",                    // 抄自 catalog，供汇总决定红绿
  "measured": {"min_courtyard_to_edge_mm": 2.63},
  "threshold": {"op": ">=", "value": 2.5, "unit": "mm", "source_param": "courtyard_to_edge"},   // 来自 catalog parameters[]
  "evidence": [{"refs": ["U1"], "nets": [], "pos_mm": [52.0, 50.0], "message": "Footprint U1 actual 2.6300 mm"}],
  "tool": {"name": "kicad-cli pcb drc", "version": "10.0.6", "canary": true},
  "inputs": {"board_sha256": "…", "dru_sha256": "…"},
  "duration_s": 0.8
}
```

约定：`threshold` 直接取自 catalog 的 `parameters`（`op/value/unit`），检查器不写死数字；每个 checker 必须返回 `measured` 与余量，便于看“差多少”。

### 3.3 四类检查器

| 类型 | 做法 | 现成素材 |
|---|---|---|
| `drc_rule` | 模板 + 参数生成 `.kicad_dru` 规则，名字 = 规则 ID；**一条规则一次 DRC**（进程池并行）；金丝雀校验；按 `rule 'ID'` 反查违规，正则取 `actual`，按位号去重取最小；失败时对规则逐条二分 | 附录 C 原型（43 行，已对 5 条规则跑通，包括一条坏规则导致 `error`） |
| `geometry` | 纯 Python 函数 `(geometry.json, design.yaml, params) → measured, evidence`：焊盘对距离 ≤ / ≥、边到边距离、禁布区、噪声源到敏感点、回路面积代理、铜面积、缝合过孔间距、网络总长 | `Shape.Collide` 二分（精确边距）、`rtree` |
| `netlist` | `kicadxml` + 符号字段 + BOM：netlist_diff、去耦电容存在性（IC 电源脚所在网络上是否有 ≥X nF 电容）、上拉 / 下拉、极性、元件值 vs 额定 | 附录 D 原型 |
| `spice` | 参数化网表模板 + libngspice 驱动 + 断言（过冲 < x%、纹波 < y mV、PDN 峰值 < Ztarget、滤波器 fc 在 ±z% 内） | 附录 A；§2.8 的算例 |

`manual` 检查器只生成清单，状态保持 `manual_pending`，由人或 LLM 回填并附 evidence。

### 3.4 先做什么（按价值 / 工作量；人天为估计）

1. **`drc_rule` 检查器 + 目录绑定 + 金丝雀**（~1 天）：先接 10 条纯阈值规则（板边、线宽、过孔、孔径、环宽、netclass 间距、IO 网络长度、禁布、fromTo 去耦路径长度）。这是现在就能出 pass/fail 的最大一块。
2. **`geometry.json` 导出器 + `geometry` 检查器 + `design/<board>.yaml`**（~2 天）：把手写审计里的焊盘对、回路、噪声源/敏感点搬成带判据的规则；补精确边距和禁布。
3. **`netlist` 检查器**（~1–2 天）：netlist_diff 正式化（忽略 H*/FID*/测试点），再加去耦 / 上拉 / 极性 / BOM 字段规则；给符号加 `Voltage`、`Tolerance`、`LCSC` 字段约定。
4. **`spice` 检查器**（~2 天 + 找模型）：先做 RC 滤波 / 分压 / PDN 阻抗（不需要 IC 模型），再收集 AMS1117、INA199、MOSFET 的厂商模型做 LDO 稳定性、检流链路。
5. 之后再看：平面感知的 IR drop（把铜区栅格化进电阻网络）、热估算、scikit-rf 校验阻抗、EM。

**测试策略**：每个 checker 配“种子缺陷”夹具——用 pcbnew 在板拷贝上制造缺陷（挪元件、删封装、改网络，§2.6 就是这样做的），要求规则在好板上 pass、坏板上 fail；这也是发现 `.kicad_dru` 被静默丢弃的唯一可靠办法。

## 4. (d) 踩到的坑

1. **锁文件 / 原文件**：KiCad 可能正开着这块板（进程 pcbnew）。`kicad-cli` 不管锁文件，但 `pcbnew.SaveBoard`、`pcb drc --refill-zones --save-board` 会写文件——只对拷贝做。拷贝时只拷 `.kicad_pcb/.kicad_pro/.kicad_sch/lib-table`，不要带 `~*.lck`、`_autosave-*`（KiCad 编辑中会有）。拷贝一块正在被 KiCad 保存的板有读到半个文件的风险，先检查末尾是否是 `)`。
2. **kicad-cli 会写文件**：每次运行在工程旁写 `.kicad_prl`；还会改用户配置（有人报告连 `kicad-cli version` 都会把当前目录写进 `kicad_common.json`；本次未单独验证）。设置私有的 `KICAD_CONFIG_HOME` 与 `KICAD_DOCUMENTS_HOME`（后者还能避免 macOS 对 `~/Documents` 的 TCC 卡死）。
3. **Python 版本**：pcbnew 只在 KiCad 自带 Python 3.9.13；uv 的 3.14 里 `import pcbnew` 报 `dlopen … _pcbnew.so`。用子进程 + JSON 交换。必须 `-I`，否则会混入 `~/Library/Python/3.9/lib/python/site-packages`（实测能 import boto3、google-api-*）。KiCad 的 Python 里没有 numpy。
4. **`.kicad_dru` 语法错误被静默吞掉**（最大的坑）：kicad-cli 返回 0、不报错，只给内置检查。用金丝雀（§2.4）。`track_angle` 参数是纯数字，写 `135deg` 就是语法错误。
5. **规则屏蔽**：同类型约束、重叠条件，后写的规则吃掉先写的。一条规则一次 DRC。
6. **DRC 报告里没有数值字段**：`actual` 只在 description 里；`physical_clearance` 的 type 叫 `clearance`；同一对象多条记录；安装孔 / 基准点要豁免。
7. **默认忽略的检查**：`missing_courtyard` 等 5 项（裸工程）；ERC 的 `simulation_model_issue` 等 4 项。要靠 `.kicad_pro` 的 `rule_severities` 打开。
8. **`.kicad_pro` 在哪**：板目录里没有，只有 `schematic/` 里一份；netlist 的 netclass、`hasNetclass()`、板级阈值都依赖它。没有它还会冒出 45 条 `lib_footprint_issues`。
9. **坐标与命名**：DRC 坐标是 KiCad 板坐标（参考板的原点相对规格坐标偏移 50 mm）；ERC JSON 坐标是原理图坐标的 1/100；PCB 网络名无前导 `/`，原理图有；IPC-D-356 网络名限 14 字符。
10. **parity 自带 111 条噪声**：别直接当 pass/fail，用引脚集合 diff 或与基线比差集。
11. **`PCB_VIA.GetWidth()` 不带层参数** 向 stderr 打大量 assert 警告；`PAD.GetEffectiveShape()` 必须传层。
12. **KiCad 的 DRC 填充是文件里存的**：改了几何后需要 `--refill-zones`（写文件，仅副本）。
13. **库位置**：libngspice 在 `PlugIns/sim/`（与 `Frameworks/` 下一份大小相同的副本），代码模型 `.cm` 在 `PlugIns/sim/ngspice/`，加载要给全路径。`ngSpice_Init` 是进程内全局状态，并行用多进程。
14. **不用 /tmp**：本次所有临时文件在工作目录 `work/verifiers/`，结束删除。
15. **SPICE 网表导出的 DNP 记号**：`R14 /IO10 GND 10k DNP` 末尾的 `DNP` 对 ngspice 非法，需要后处理；IC 是 `__REF` 占位，要先给符号配 Sim.* 字段（未验证）。
16. **pcbnew SWIG 绑定的寿命**：官方手册说 API 与 KiCad 内部结构紧耦合、“不稳定、随版本变”；有说法称计划在 KiCad 11 移除（官方 10.0 文档里没找到这句，[未验证]）。所以把 pcbnew 耦合收敛到一个导出脚本（§3.1），备用路径是自写 s-expression 解析器直接读文件。
17. **DRC 条件属性与文档不符**：见 §2.4 第 4 条（`A.Value`、`A.Orientation`）。
18. **调研限制**：本次调研的 WebSearch 额度在中途用尽，Xyce / openEMS / Elmer / Qucs-S / LTspice 的细节只读到了各自官网的主页或安装页目录，macOS 构建可行性均标 [未验证]。

## 5. 参考来源（本次实际打开过）

* KiCad 10 PCB Editor 手册（自定义规则、DRC 检查表、脚本）：https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html
* KiCad 10 Schematic Editor 手册（ERC 检查表）：https://docs.kicad.org/10.0/en/eeschema/eeschema.html
* KiCad 10 CLI 手册（退出码、jobset）：https://docs.kicad.org/10.0/en/cli/cli.html
* KiCad 10 PCB Calculator 手册：https://docs.kicad.org/10.0/en/pcb_calculator/pcb_calculator.html
* KiCad IPC API：https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/
* pcbnew Python Doxygen：https://docs.kicad.org/doxygen-python-10.0/namespaces.html
* openEMS 文档：https://docs.openems.de/ ；Xyce：https://xyce.sandia.gov/ ；Elmer：https://github.com/ElmerCSC/elmerfem ；Qucs-S：https://github.com/ra3xdh/qucs_s ；ngspice：https://ngspice.sourceforge.io/
* kicad-skip：https://github.com/psychogenic/kicad-skip ；KiKit：https://github.com/yaqwsx/KiKit

## 附录：已跑通的原型代码

以下代码都是本次实际运行过的版本。除 `irdrop.py` 需要 numpy + scipy（uv 环境已装）外只依赖标准库；ngspice 驱动、公式、`netlist_diff.py`、`drc_harness.py` 用 uv 的 Python 3.14（或任何 Python 3），`pcb_nets.py`、`mk_keepin.py`、`dump_copper.py` 必须用 KiCad 自带的 Python 3.9。

### 附录 A：libngspice 的 ctypes 驱动（`ngs.py`）

```python
"""Minimal ctypes driver for KiCad's bundled libngspice (works in any Python, here the uv 3.14 env)."""
import ctypes as C, math, os, sys, time
LIB = os.environ.get("NGSPICE_LIB", "/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/libngspice.0.dylib")

class VecInfo(C.Structure):
    _fields_ = [("v_name", C.c_char_p), ("v_type", C.c_int), ("v_flags", C.c_short),
                ("v_realdata", C.POINTER(C.c_double)), ("v_compdata", C.c_void_p), ("v_length", C.c_int)]
class Cplx(C.Structure):
    _fields_ = [("re", C.c_double), ("im", C.c_double)]

class NgSpice:
    def __init__(self, lib=LIB):
        self.lib = C.CDLL(lib)
        self.out = []
        SendChar = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)
        SendStat = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)
        Exit = C.CFUNCTYPE(C.c_int, C.c_int, C.c_bool, C.c_bool, C.c_int, C.c_void_p)
        SendData = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_int, C.c_int, C.c_void_p)
        SendInit = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_int, C.c_void_p)
        BG = C.CFUNCTYPE(C.c_int, C.c_bool, C.c_int, C.c_void_p)
        self._cb = (SendChar(lambda s, i, u: (self.out.append(s.decode(errors="replace")), 0)[1]),
                    SendStat(lambda s, i, u: 0), Exit(lambda *a: 0), SendData(lambda *a: 0), SendInit(lambda *a: 0), BG(lambda *a: 0))
        self.lib.ngSpice_Init.argtypes = [SendChar, SendStat, Exit, SendData, SendInit, BG, C.c_void_p]
        self.lib.ngGet_Vec_Info.restype = C.POINTER(VecInfo)
        self.lib.ngGet_Vec_Info.argtypes = [C.c_char_p]
        self.lib.ngSpice_Command.argtypes = [C.c_char_p]
        self.lib.ngSpice_Circ.argtypes = [C.POINTER(C.c_char_p)]
        self.lib.ngSpice_CurPlot.restype = C.c_char_p
        self.lib.ngSpice_AllVecs.restype = C.POINTER(C.c_char_p)
        self.lib.ngSpice_AllVecs.argtypes = [C.c_char_p]
        self.lib.ngSpice_Init(*self._cb, None)

    def load(self, netlist: str):
        lines = [l.encode() for l in netlist.strip().splitlines()] + [None]
        arr = (C.c_char_p * len(lines))(*lines)
        return self.lib.ngSpice_Circ(arr)

    def cmd(self, c: str):
        return self.lib.ngSpice_Command(c.encode())

    def vec(self, name: str):
        p = self.lib.ngGet_Vec_Info(name.encode())
        if not p:
            raise KeyError(name)
        v = p.contents
        return [v.v_realdata[i] for i in range(v.v_length)]

    def vec_c(self, name: str):  # complex vector (AC analysis)
        p = self.lib.ngGet_Vec_Info(name.encode()); v = p.contents
        cd = C.cast(v.v_compdata, C.POINTER(Cplx))
        return [complex(cd[i].re, cd[i].im) for i in range(v.v_length)]

    def vecs(self, plot=None):
        p = self.lib.ngSpice_AllVecs((plot or self.lib.ngSpice_CurPlot().decode()).encode())
        out, i = [], 0
        while p[i]:
            out.append(p[i].decode()); i += 1
        return out
```

用法片段（RC 阶跃对解析值）：

```python
ng = NgSpice()
ng.load("""RC step
V1 in 0 PULSE(0 1 0 1n 1n 1 2)
R1 in out 1k
C1 out 0 1u
.tran 10u 5m
.end""")
ng.cmd("run")
t, v = ng.vec("time"), ng.vec("v(out)")          # AC 用 ng.vec_c("v(out)")；噪声先 ng.cmd("setplot noise1")
```

### 附录 B：IPC-2221 线宽与微带阻抗（`tl_formulas.py`）

```python
"""Scriptable replacements for KiCad pcb_calculator panels (GUI-only). Formulas as published; see notes on validation."""
import math
def ipc2221_width_mm(i_amp, dT=10.0, oz=1.0, external=True):
    k = 0.048 if external else 0.024                      # IPC-2221 / IPC-D-275 constants (as used by KiCad's Track Width panel)
    area_mil2 = (i_amp / (k * dT ** 0.44)) ** (1 / 0.725)
    thick_mil = 1.378 * oz
    return area_mil2 / thick_mil * 0.0254
def microstrip_z0_hj(w, h, t, er):
    """Hammerstad-Jensen 1980 (quasi-static), mm in; returns (Z0 ohm, eps_eff). t folded into effective width (Hammerstad)."""
    u = w / h
    if t > 0:
        du = (t / (math.pi * h)) * math.log(1 + 4 * math.e / ((t / h) / (math.tanh(math.sqrt(6.517 * u)) ** 2)))
        u += du
    a = 1 + math.log((u**4 + (u/52)**2) / (u**4 + 0.432)) / 49 + math.log(1 + (u/18.1)**3) / 18.7
    b = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    eeff = (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u) ** (-a * b)
    f = 6 + (2 * math.pi - 6) * math.exp(-((30.666 / u) ** 0.7528))
    z01 = 60 * math.log(f / u + math.sqrt(1 + (2 / u) ** 2))
    return z01 / math.sqrt(eeff), eeff
def microstrip_z0_ipc2141(w, h, t, er):
    return 87 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))
print("IPC-2221 external 1oz dT=10C:", {i: round(ipc2221_width_mm(i), 3) for i in (0.5, 1, 2, 3)}, "mm for A")
print("IPC-2221 internal 1oz dT=10C 1A:", round(ipc2221_width_mm(1, external=False), 3), "mm")
for w in (1.0, 2.0, 3.0, 3.1):
    print(f"microstrip w={w} mm h=1.6 t=0.035 er=4.5: HJ Z0={microstrip_z0_hj(w,1.6,0.035,4.5)[0]:.1f} ohm (eeff={microstrip_z0_hj(w,1.6,0.035,4.5)[1]:.2f})  IPC-2141 Z0={microstrip_z0_ipc2141(w,1.6,0.035,4.5):.1f} ohm")
# solve width for 50 ohm by bisection (what a 'tline_calc' rule check would do inversely)
lo, hi = 0.2, 8
for _ in range(60):
    mid = (lo + hi) / 2
    (lo, hi) = (mid, hi) if microstrip_z0_hj(mid, 1.6, 0.035, 4.5)[0] > 50 else (lo, mid)
print("width for 50 ohm (h=1.6, er=4.5, t=35um):", round(mid, 3), "mm")
```

### 附录 C：规则 ID → 自定义 DRC 规则 → pass/fail/evidence（`drc_harness.py`）

```python
"""Prototype: catalog rule id -> custom DRC rule -> pass/fail/error + evidence JSON.  stdlib only (python3.9+).
usage: drc_harness.py BOARD.kicad_pcb PROJECT.kicad_pro CHECKS.json  > results.json"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

CANARY = ('(rule "__canary__" (severity warning) (condition "A.Type == \'Footprint\'")'
          ' (constraint assertion "A.Reference == \'__never__\'"))')
KCLI = os.environ.get("KCLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
ACT = re.compile(r"actual ([-0-9.]+)")

def run_drc(board: Path, pro: Path, rules_text: str, workdir: Path, extra=()):
    shutil.copy(board, workdir / board.name); shutil.copy(pro, workdir / (board.stem + ".kicad_pro"))
    (workdir / (board.stem + ".kicad_dru")).write_text("(version 1)\n" + CANARY + "\n" + rules_text + "\n")
    out = workdir / "drc.json"
    env = dict(os.environ, KICAD_CONFIG_HOME=str(workdir / "cfg"), KICAD_DOCUMENTS_HOME=str(workdir / "docs"))
    p = subprocess.run([KCLI, "pcb", "drc", "--format", "json", "--severity-all", "--units", "mm", *extra, "-o", str(out), str(workdir / board.name)],
                       capture_output=True, text=True, env=env, timeout=240)
    if not out.exists():
        raise RuntimeError(f"kicad-cli failed rc={p.returncode}: {p.stderr[-300:]}")
    return json.loads(out.read_text())

def main(board, pro, checks_json):
    checks = json.loads(Path(checks_json).read_text())
    with tempfile.TemporaryDirectory(dir=os.environ.get("DRC_WORK", ".")) as td:
        td = Path(td)
        rules = "\n".join(c["dru"] for c in checks)
        rep = run_drc(Path(board), Path(pro), rules, td)
        loaded = any("__canary__" in v["description"] for v in rep["violations"])
        results = []
        for c in checks:
            if not loaded:
                results.append({"id": c["id"], "status": "error", "reason": "custom rules not loaded (syntax error in some rule; KiCad drops the whole .kicad_dru silently)"}); continue
            hits = [v for v in rep["violations"] if f"rule '{c['id']}'" in v["description"]]
            ev = []
            for v in hits:
                m = ACT.search(v["description"])
                ev.append({"type": v["type"], "severity": v["severity"], "actual": float(m.group(1)) if m else None,
                           "items": [i["description"] for i in v["items"]], "pos_mm": [v["items"][0]["pos"]["x"], v["items"][0]["pos"]["y"]] if v["items"] else None})
            results.append({"id": c["id"], "status": "fail" if hits else "pass", "n_violations": len(hits), "evidence": ev[:5]})
    print(json.dumps(results, indent=1))

if __name__ == "__main__":
    main(*sys.argv[1:4])
```

`checks.json` 形如 `[{"id": "DFM-PLC-902", "dru": "(rule \"DFM-PLC-902\" (layer \"F.Courtyard\") (constraint physical_clearance (min 3.0mm)) (condition \"B.Layer == 'Edge.Cuts' && A.Type == 'Footprint' && A.Reference != 'H*'\"))"}, …]`。实测输出（参考板副本）：

```
DFM-PLC-901  pass  (courtyard→板边 ≥2.5)
DFM-PLC-902  fail  actual 2.63  Footprint U1        (≥3.0)
HSD-RTE-903  fail  actual 50.3233  IO3 总长 > 40
PWR-PLC-904  fail  actual 7.4508   fromTo C8-1→U1-1 走线 > 6
PWR-RTE-905  pass  Power 类线宽 ≥0.5
再加一条 track_angle (min 135deg) 的坏规则 → 全部 6 条 status=error（金丝雀缺席）
```

### 附录 D：PCB 焊盘网络导出与网表 diff（`pcb_nets.py` + `netlist_diff.py`）

```python
# runs under KiCad's bundled python:  $KPY -I pcb_nets.py BOARD.kicad_pcb OUT.json
import json, sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
out = {"parts": {}, "nets": {}}
for f in b.GetFootprints():
    out["parts"][f.GetReference()] = {"value": f.GetValue(), "fpid": str(f.GetFPID().GetUniStringLibId())}
    for p in f.Pads():
        n = p.GetNetname()
        if n:
            out["nets"].setdefault(n, []).append(f"{f.GetReference()}.{p.GetNumber()}")
json.dump(out, open(sys.argv[2], "w"), indent=1, sort_keys=True)
```

```python
"""netlist_diff: schematic (kicad-cli sch export netlist --format kicadxml) vs PCB pad nets (pcb_nets.py dump). stdlib only.
usage: netlist_diff.py sch.xml pcb_nets.json ; exit 1 on any difference. Nets are compared as pin SETS (names normalised: leading '/' stripped),
so renamed nets don't matter, wrong connections do."""
import json, sys, xml.etree.ElementTree as ET
sch = ET.parse(sys.argv[1]).getroot()
s_nets, s_parts = {}, {}
for c in sch.iter("comp"):
    v = c.findtext("value") or ""
    s_parts[c.get("ref")] = v
for n in sch.iter("net"):
    pins = frozenset(f'{x.get("ref")}.{x.get("pin")}' for x in n.iter("node"))
    if len(pins) > 0:
        s_nets[pins] = n.get("name").lstrip("/")
pcb = json.load(open(sys.argv[2]))
p_nets = {frozenset(v): k.lstrip("/") for k, v in pcb["nets"].items()}
rep = {"missing_in_pcb": [], "extra_in_pcb": [], "value_mismatch": [], "net_only_in_sch": [], "net_only_in_pcb": []}
for r, v in s_parts.items():
    if r.startswith("#"): continue
    if r not in pcb["parts"]: rep["missing_in_pcb"].append(r)
    elif pcb["parts"][r]["value"] != v: rep["value_mismatch"].append(f'{r}: sch={v} pcb={pcb["parts"][r]["value"]}')
rep["extra_in_pcb"] = sorted(r for r in pcb["parts"] if r not in s_parts and not r.startswith(("H", "FID")))
# a PCB net may omit pins that have no pad net (NC) -> compare only pins present on both sides
common = {p for pins in s_nets for p in pins if p.split(".")[0] in pcb["parts"]}
s_set = {frozenset(p for p in pins if p in common): nm for pins, nm in s_nets.items() if any(p in common for p in pins)}
for pins, nm in s_set.items():
    if pins not in p_nets: rep["net_only_in_sch"].append(f"{nm}: {sorted(pins)}")
for pins, nm in p_nets.items():
    if pins not in s_set: rep["net_only_in_pcb"].append(f"{nm}: {sorted(pins)}")
print(json.dumps({k: v for k, v in rep.items()}, indent=1))
sys.exit(1 if any(rep.values()) else 0)
```

### 附录 E：给板副本加命名规则区（`mk_keepin.py`，KiCad Python）

```python
import sys, pcbnew
src, dst, ref, pad, half = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
b = pcbnew.LoadBoard(src)
p = b.FindFootprintByReference(ref).FindPadByNumber(pad).GetPosition()
z = pcbnew.ZONE(b)
z.SetIsRuleArea(True)
z.SetZoneName(f"near_{ref}_{pad}")
z.SetLayer(pcbnew.F_Cu)
z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowZoneFills(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
h = pcbnew.FromMM(half)
o = z.Outline(); o.NewOutline()
for dx, dy in ((-h, -h), (h, -h), (h, h), (-h, h)):
    o.Append(p.x + dx, p.y + dy)
b.Add(z)
pcbnew.SaveBoard(dst, b)
print("wrote", dst, "area", z.GetZoneName(), "centre mm", pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))
```

用法：`$KPY -I mk_keepin.py in.kicad_pcb out.kicad_pcb U1 1 8`（以 U1 焊盘 1 为中心、半边长 8 mm）。

### 附录 F：走线网络 IR drop（`dump_copper.py` 在 KiCad Python 里导出，`irdrop.py` 在 uv Python 里求解）

```python
# $KPY -I dump_copper.py BOARD OUT.json  : tracks/vias/pads per net (mm) for a resistive-network IR-drop solve
import json, sys, pcbnew
mm = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
d = {"tracks": [], "vias": [], "pads": [], "thickness_mm": {"F.Cu": 0.035, "B.Cu": 0.035}}
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        d["vias"].append({"net": t.GetNetname(), "x": mm(t.GetPosition().x), "y": mm(t.GetPosition().y), "drill": mm(t.GetDrill())})
    elif t.GetClass() == "PCB_TRACK":
        d["tracks"].append({"net": t.GetNetname(), "layer": t.GetLayerName(), "x1": mm(t.GetStart().x), "y1": mm(t.GetStart().y),
                            "x2": mm(t.GetEnd().x), "y2": mm(t.GetEnd().y), "w": mm(t.GetWidth())})
for f in b.GetFootprints():
    for p in f.Pads():
        d["pads"].append({"ref": f.GetReference(), "num": p.GetNumber(), "net": p.GetNetname(), "x": mm(p.GetPosition().x), "y": mm(p.GetPosition().y),
                          "layer": "F.Cu" if p.IsOnLayer(pcbnew.F_Cu) else "B.Cu", "tht": p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH})
json.dump(d, open(sys.argv[2], "w"))
```

```python
"""Track-only DC resistance between two pads of a net (copper zones ignored => upper bound for pour nets). Needs numpy+scipy (uv env)."""
import json, math, sys
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl
RHO = 1.68e-8  # ohm*m copper at 20C
d = json.load(open(sys.argv[1])); net, a, b = sys.argv[2], sys.argv[3], sys.argv[4]; amps = float(sys.argv[5])
key = lambda x, y, l: (round(x, 3), round(y, 3), l)
idx, edges = {}, []
def node(k): return idx.setdefault(k, len(idx))
for t in d["tracks"]:
    if t["net"] != net: continue
    L = math.hypot(t["x2"] - t["x1"], t["y2"] - t["y1"]) * 1e-3
    R = RHO * L / (t["w"] * 1e-3 * d["thickness_mm"][t["layer"]] * 1e-3)
    edges.append((node(key(t["x1"], t["y1"], t["layer"])), node(key(t["x2"], t["y2"], t["layer"])), R))
for v in d["vias"]:
    if v["net"] != net: continue
    ka, kb = key(v["x"], v["y"], "F.Cu"), key(v["x"], v["y"], "B.Cu")
    edges.append((node(ka), node(kb), 0.5e-3))  # ~0.5 mOhm barrel (rough placeholder)
pad = {}
for p in d["pads"]:
    if p["net"] == net:
        pad[f'{p["ref"]}.{p["num"]}'] = key(p["x"], p["y"], p["layer"])
        if p["tht"]: edges.append((node(key(p["x"], p["y"], "F.Cu")), node(key(p["x"], p["y"], "B.Cu")), 0.5e-3))
n = len(idx); G = sp.lil_matrix((n, n))
for i, j, R in edges:
    g = 1 / max(R, 1e-9); G[i, i] += g; G[j, j] += g; G[i, j] -= g; G[j, i] -= g
def snap(k, tol=0.6):  # pad centre -> nearest copper node on the same layer (tracks need not end exactly on the pad centre)
    if k in idx: return idx[k]
    c = min((m for m in idx if m[2] == k[2]), key=lambda m: math.hypot(m[0]-k[0], m[1]-k[1]))
    assert math.hypot(c[0]-k[0], c[1]-k[1]) <= tol, f"pad {k} not within {tol} mm of any {net} copper"
    return idx[c]
ia, ib = snap(pad[a]), snap(pad[b])
I = np.zeros(n); I[ia] = amps; I[ib] = -amps
keep = [k for k in range(n) if k != ib]
v = np.zeros(n); v[keep] = spl.spsolve(G.tocsr()[keep][:, keep].tocsc(), I[keep])
print(f"{net}: {a} -> {b}: R = {v[ia]/amps*1e3:.1f} mOhm, drop at {amps} A = {v[ia]*1e3:.1f} mV  (nodes={n}, segments={len(edges)})")
```
