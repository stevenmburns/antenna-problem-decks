import sys, re
# yagi geometry with every radius set to one value (control: no radius steps)
r = sys.argv[2]
for line in open(sys.argv[1]):
    if line.startswith("GW"):
        f = line.split(); f[-1] = r; line = " ".join(f) + "\n"
    sys.stdout.write(line)
