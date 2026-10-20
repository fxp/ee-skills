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
