# 来源 URL 可达性报告

2026-10-20 在本机（macOS，沙箱网络）探测全部 330 个来源 URL：先用 httpx 探一遍，失败的再用 curl（45 s 超时、浏览器 UA）重试。
- 可达：291（含重试后转为 200 的 7 个，以及已换成镜像的 NXP AN11994）
- 本机不可达：39

**不可达不等于链接失效。** 调研 agent 是通过 WebFetch / WebSearch 读到这些页面的（见规则里的 `confidence`：只在搜索结果里见过、没读到原文的一律降为 `medium`），本机的 curl 对 analog.com、edn.com、st.com、eetimes.com 完全连不上，对 Nordic DevZone、KiCad KLC 等返回 403。这些页面本报告**没有**独立复核，只能说明本机复核不了。

| 状态 | 含义 |
|---|---|
| 000 | 本机连不上（超时 / 无响应） |
| 403 | 站点拒绝机器人（403） |
| 404 | 页面不存在 |
| 429 | 限流（429） |

## 按站点

### www.analog.com（10；000×10）
- `000` https://www.analog.com/en/resources/analog-dialogue/articles/ask-the-applications-engineer-25.html
- `000` https://www.analog.com/en/resources/analog-dialogue/articles/staying-well-grounded.html
- `000` https://www.analog.com/en/resources/analog-dialogue/articles/techniques-to-avoid-instability-capacitive-loading.html
- `000` https://www.analog.com/en/resources/app-notes/an-1368.html
- `000` https://www.analog.com/en/technical-articles/avoiding-noise-and-power-problems-with-unused-op-amps.html
- `000` https://www.analog.com/en/technical-articles/layout-for-precision-op-amps.html
- `000` https://www.analog.com/media/en/technical-documentation/application-notes/an88f.pdf
- `000` https://www.analog.com/media/en/technical-documentation/technical-articles/m141_en-battery_power.pdf
- `000` https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf
- `000` https://www.analog.com/mt-031?doc=cn288.pdf

### devzone.nordicsemi.com（6；403×6）
- `403` https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/0842.High-pulse-drain-impact-on-CR2032-coin-cell-battery-capacity.pdf
- `403` https://devzone.nordicsemi.com/f/nordic-q-a/129254/npm2100-nrf54l15-capacitor-bank-design-for-cr2032-cr2450-and-ble-operation/571568
- `403` https://devzone.nordicsemi.com/f/nordic-q-a/16740/nrf52-antenna-design-review
- `403` https://devzone.nordicsemi.com/f/nordic-q-a/35072/estimation-of-battery-life-while-only-advertising
- `403` https://devzone.nordicsemi.com/guides/hardware-design-test-and-measuring/b/nrf5x/posts/general-pcb-design-guidelines-for-nrf52-series
- `403` https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/optimizing-power-on-nrf52-designs

### www.edn.com（6；000×6）
- `000` https://www.edn.com/circuit-board-layout-guidelines-for-class-d-amplifiers/
- `000` https://www.edn.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/
- `000` https://www.edn.com/signal-distortion-from-high-k-ceramic-capacitors/
- `000` https://www.edn.com/spice-models-need-correlation-to-measurements/
- `000` https://www.edn.com/understanding-class-d-amplifier-power-supply-requirements/
- `000` https://www.edn.com/when-to-worry-about-trace-corners-rule-of-thumb-24/

### klc.kicad.org（5；403×5）
- `403` https://klc.kicad.org/footprint/f4/f4.4.html
- `403` https://klc.kicad.org/footprint/f5/f5.3.html
- `403` https://klc.kicad.org/footprint/f9/f9.3/
- `403` https://klc.kicad.org/model/m2/m2.2.html
- `403` https://klc.kicad.org/symbol/s4/s4.6/

### www.digikey.com（2；403×2）
- `403` https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=09748F6FB2B14376BFA057A887CFD3EF
- `403` https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=4032FAAF37CF46A1A3088C1458463D5C

### www.eetimes.com（2；000×2）
- `000` https://www.eetimes.com/filterless-class-d-simplifies-audio-amplifier-design/
- `000` https://www.eetimes.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/

### www.st.com（2；000×2）
- `000` https://www.st.com/resource/en/application_note/an2867-guidelines-for-oscillator-design-on-stm8afals-and-stm32-mcusmpus-stmicroelectronics.pdf
- `000` https://www.st.com/resource/en/application_note/dm00315319-stm32-gpio-configuration-for-hardware-settings-and-lowpower-consumption-stmicroelectronics.pdf

### blog.samtec.com（1；429×1）
- `429` https://blog.samtec.com/post/connector-voltage-and-power-rating-101/

### edn.com（1；000×1）
- `000` https://edn.com/Home/PrintView?contentItemId=4406013

### forum.allaboutcircuits.com（1；403×1）
- `403` https://forum.allaboutcircuits.com/threads/usb-device-cable-shield-connection-grounding-it-or-not.58811/

### toshiba.semicon-storage.com（1；403×1）
- `403` https://toshiba.semicon-storage.com/ap-en/semiconductor/knowledge/faq/diode_tvs-diodes/board-design-considerations-for-tvs-diodes-esd-protection-diodes.html

### www.microcrystal.com（1；000×1）
- `000` https://www.microcrystal.com/fileadmin/Media/Products/RTC/Whitepapers/RV-1805-C3_App-Note_Cap_Backup.pdf

### www.onsemi.com（1；403×1）
- `403` https://www.onsemi.com/company/news-media/blog/industrial/en-us/current-sense-amplifiers-input-and-output-filtering
