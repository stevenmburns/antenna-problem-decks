"""Ladder rung decks: every GW segment count x m (m odd), EX re-centred to
(s-1)*m + (m+1)/2 -- the antenna-problem-decks verdicts' rule. Writes the
NEC-2 rung and its NEC-5 twin (antennaknobs export --dialect nec5)."""
import pathlib, subprocess, sys

def rung(text, m):
    out = []
    for line in text.splitlines():
        f = line.split()
        if f and f[0] == "GW":
            f[2] = str(int(f[2]) * m)
            line = " ".join(f)
        elif f and f[0] == "EX":
            s = int(f[3])
            f[3] = str((s - 1) * m + (m + 1) // 2)
            line = " ".join(f)
        out.append(line)
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    base, name, ms = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
    ground = sys.argv[4] if len(sys.argv) > 4 else "free"
    d = pathlib.Path("rungs"); d.mkdir(exist_ok=True)
    text = pathlib.Path(base).read_text()
    for m in ms:
        p2 = d / f"{name}_m{m}.nec"
        p2.write_text(rung(text, m))
        p5 = d / f"{name}_m{m}.nec5"
        r = subprocess.run(["antennaknobs", "export", "--builder", f"@{p2}",
                            "--dialect", "nec5", "--ground", ground, "--out", str(p5)],
                           capture_output=True, text=True)
        if r.returncode:
            print(name, m, "nec5 export failed:", r.stderr.strip()[-300:])
