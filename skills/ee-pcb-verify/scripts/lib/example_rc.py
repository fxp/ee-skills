"""RC step response through KiCad's bundled libngspice, checked against the analytic value. Run: python example_rc.py"""
import math
from ngspice_ctypes import NgSpice

ng = NgSpice()
ng.load("""RC step
V1 in 0 PULSE(0 1 0 1n 1n 1 2)
R1 in out 1k
C1 out 0 1u
.tran 10u 5m
.end""")
ng.cmd("run")
t, v = ng.vec("time"), ng.vec("v(out)")
tau = 1e-3
i = min(range(len(t)), key=lambda k: abs(t[k] - tau))
want = 1 - math.exp(-t[i] / tau)
print(f"v(out) at t={t[i]*1e3:.3f} ms: {v[i]:.4f} V, analytic {want:.4f} V, error {abs(v[i]-want):.2e} V")
assert abs(v[i] - want) < 5e-3
