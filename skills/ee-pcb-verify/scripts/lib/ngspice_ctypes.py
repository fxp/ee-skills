"""Minimal ctypes driver for KiCad's bundled libngspice (works in any Python, here the uv 3.14 env)."""
import ctypes as C, math, os, sys, time
_APP = os.environ.get("EE_KICAD_APP", "/Applications/KiCad/KiCad.app")
LIB = os.environ.get("NGSPICE_LIB", _APP + "/Contents/PlugIns/sim/libngspice.0.dylib")   # macOS KiCad bundle; elsewhere set NGSPICE_LIB (libngspice.so / ngspice.dll)

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
