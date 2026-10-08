"""nec2c with and without its free-end cap (NOCAP=1, see nec2c-nocap.patch) on
the radius-study dipoles and the 0.8 / 2.2 lambda Yagis, EK on.

    python nocap.py   (nec2c only, small decks)

The instrument is nec2c 1.3.1 plus study/nec2c-nocap.patch: with NOCAP=1 the
free-end factor xxi (~ J1(ka)/J0(ka)) in the end-segment current
coefficients is zeroed, so a free end gets the plain I = 0 condition that
momwire and NEC-5 use. With the switch unset it is stock nec2c.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbl
import nbs
import radius
import run

# nec2c 1.3.1 built with nec2c-nocap.patch (this directory)
EXE = os.environ.get("NEC2C_NOCAP", "nec2c-nocap")


def nec2c(deck, nocap):
    env = dict(os.environ)
    if nocap:
        env["NOCAP"] = "1"
    else:
        env.pop("NOCAP", None)
    with tempfile.TemporaryDirectory() as d:
        Path(d, "d.nec").write_text(deck)
        subprocess.run([EXE, "-i", "d.nec", "-o", "d.out"], cwd=d, env=env,
                       capture_output=True, timeout=600)
        return Path(d, "d.out").read_text(errors="replace")


def main():
    print("dipole 0.47 lambda, EK: Z with cap | Z without cap")
    for dl in (0.001, 0.0085):
        print(f"d/lambda {dl}")
        for n in radius.NS:
            if (radius.L / n) / (dl / 2) < 0.7:
                continue
            dk = radius.deck(n, dl / 2, True, False)
            zc = nbs.parse_nec2_printout(nec2c(dk, False))[0]
            zn = nbs.parse_nec2_printout(nec2c(dk, True))[0]
            print(f"  n={n:4d} Δ/a={(radius.L / n) / (dl / 2):6.1f}  "
                  f"{zc.real:7.2f}{zc.imag:+7.2f}j | {zn.real:7.2f}{zn.imag:+7.2f}j")

    designs = nbs.load_designs()
    trim = run.load_trim()
    print("\nYagis, EK: forward dBi / F/B, with cap | without cap")
    for lab in ("0.8", "2.2"):
        Ld = trim["designs"][lab]["driven_len_lambda"]
        print(lab)
        for n in dbl.ODD:
            dk = dbl.decks(n, lab, designs[lab], Ld, True, False)
            out = []
            for nocap in (False, True):
                z, g = nbs.parse_nec2_printout(nec2c(dk, nocap))
                az, el = nbs.split_cuts(g)
                m = nbs.cut_metrics(az, el)
                out.append(f"{m['fwd_dbi']:7.3f} / {m['fb_db']:5.2f}  X {z.imag:+6.2f}")
            print(f"  n={n:4d}  " + " | ".join(out))


if __name__ == "__main__":
    main()
