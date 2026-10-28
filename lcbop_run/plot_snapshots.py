"""Side views (x-z) of a thin y-slab, atoms coloured by coordination.
python plot_snapshots.py dump.ramp.lammpstrj 0 9 11  ->  snapshots_ramp.png   (times in ps)
python plot_snapshots.py dump.msst_Us15.lammpstrj dt=0.00025 0 1 4      (timestep if not 0.5 fs)"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURF, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
CLASSES = [("sp2 (CN = 3)", 3, "#2a78d6"), ("sp3 (CN = 4)", 4, "#eb6834")]
OTHER = ("other CN", "#a3a29c")
DT = 0.0005                      # ps per step (default of the input scripts), override with dt=
SLAB = 3.0                       # A, thickness of the y-slab shown


def frames(path):
    with open(path) as fh:
        while True:
            line = fh.readline()
            if not line:
                return
            step = int(fh.readline())
            fh.readline(); n = int(fh.readline())
            fh.readline()
            box = np.array([fh.readline().split()[:2] for _ in range(3)], float)
            cols = fh.readline().split()[2:]
            data = np.loadtxt(fh, max_rows=n)
            yield step, box, dict(zip(cols, data.T))


path = sys.argv[1]
args = sys.argv[2:]
if args and args[0].startswith("dt="):
    DT = float(args.pop(0)[3:])
want = [float(t) for t in args] or [0.0]
snaps = {}
for step, box, d in frames(path):
    t = step * DT
    for w in want:
        if w not in snaps or abs(t - w) < abs(snaps[w][0] - w):
            if abs(t - w) < 1.01:
                snaps[w] = (t, box, d)

fig, axes = plt.subplots(1, len(want), figsize=(4.2 * len(want), 5.2), constrained_layout=True,
                         facecolor=SURF, squeeze=False)
for a, w in zip(axes[0], want):
    t, box, d = snaps[w]
    m = d["y"] - box[1, 0] < SLAB
    x, z, cn = d["x"][m] - box[0, 0], d["z"][m] - box[2, 0], d["c_cn"][m].astype(int)
    known = np.zeros(len(cn), bool)
    for label, val, color in CLASSES:
        s = cn == val
        known |= s
        a.scatter(x[s], z[s], s=4, c=color, lw=0, label=label)
    a.scatter(x[~known], z[~known], s=4, c=OTHER[1], lw=0, label=OTHER[0])
    a.set_aspect("equal")
    a.set_xlim(0, box[0, 1] - box[0, 0])
    a.set_ylim(0, 136)                                    # same z scale in every panel
    a.set_facecolor(SURF)
    a.set_title(f"t = {t:.1f} ps,  Lz = {box[2, 1] - box[2, 0]:.1f} A\n"
                f"whole cell: sp2 {100 * np.mean(d['c_cn'] == 3):.0f} %, sp3 {100 * np.mean(d['c_cn'] == 4):.0f} %",
                color=INK, fontsize=10)
    a.set_xlabel("x, zigzag (A)", color=INK2)
    a.tick_params(colors=INK2)
    for sp in a.spines.values():
        sp.set_color("#e4e3df")
axes[0][0].set_ylabel("z, c-axis (A)", color=INK2)
h, l = axes[0][0].get_legend_handles_labels()
fig.legend(h, l, loc="outside lower center", ncol=3, frameon=False, markerscale=3, labelcolor=INK2)
fig.suptitle(f"{path}: {SLAB:g} A thick slab, coloured by coordination (cutoff 1.9 A)", color=INK)
out = "snapshots_" + path.split("dump.")[-1].split(".lammpstrj")[0] + ".png"
fig.savefig(out, dpi=150)
print("wrote", out, {w: round(snaps[w][0], 2) for w in want})
