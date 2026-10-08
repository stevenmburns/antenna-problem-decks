"""Is bs2's large EK correction a Galerkin-testing effect? Compare
Z_EK - Z_noEK for sin (point-matched), sin-galerkin and bs2 (both Galerkin)
on the radius-study dipoles.

    python galerkin_ek.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbl
import radius


def z(solver, kw, dk, ek):
    from antennaknobs.engines.momwire import MomwireEngine

    eng = MomwireEngine(dbl.builder_from(dk, "nec2"), solver=solver, solver_kwargs=kw,
                        extended_kernel=ek)
    return complex(eng.impedance()[0])


def main():
    from momwire import BSplineSolver, SinusoidalGalerkinSolver, SinusoidalSolver

    lanes = (("sin", SinusoidalSolver, {}), ("sin-galerkin", SinusoidalGalerkinSolver, {}),
             ("bs2", BSplineSolver, {"degree": 2}))
    for dl in (0.001, 0.0085):
        print(f"d/lambda {dl}: Z (no EK) and the EK correction Z_EK - Z_noEK")
        for n in (9, 19, 37, 75, 151):
            if (radius.L / n) / (dl / 2) < 0.7:
                continue
            dk = radius.deck(n, dl / 2, False, False)
            out = []
            for name, s, kw in lanes:
                z0, z1 = z(s, kw, dk, False), z(s, kw, dk, True)
                d = z1 - z0
                out.append(f"{name} {z0.real:6.2f}{z0.imag:+6.2f}j  Δ{d.real:+5.2f}{d.imag:+5.2f}j")
            print(f"  n={n:3d} Δ/a={(radius.L/n)/(dl/2):5.1f} | " + " | ".join(out))


if __name__ == "__main__":
    main()
