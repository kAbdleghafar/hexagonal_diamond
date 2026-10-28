"""Plot ramp + MSST results:  python plot_results.py  ->  shock_results.png"""
import glob
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]      # validated categorical slots 1-3

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
    "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "lines.linewidth": 2.0, "font.size": 10, "legend.frameon": False,
})

runs = []   # (label, data dict)
try:
    r = np.loadtxt("ramp_profile.txt", comments="#", ndmin=2)
    runs.append(("Ramp 5e10 1/s", dict(t=r[:, 1], VV0=r[:, 3], T=r[:, 5], P=r[:, 6],
                                        sp3=r[:, 10], ramp=True,
                                        hold=r[:, 2] >= r[:, 2].max() - 1e-4)))
except OSError:
    pass
for f in sorted(glob.glob("msst_Us*_profile.txt"), key=lambda s: float(re.findall(r"Us([\d.]+)", s)[0])):
    us = float(re.findall(r"Us([\d.]+)", f)[0])
    m = np.loadtxt(f, comments="#", ndmin=2)
    if len(m) < 5:                                        # run just started, nothing to show yet
        continue
    rho0 = m[0, 3]                                        # density of the unshocked state (g/cc)
    runs.append((f"MSST Us = {us:g} km/s", dict(t=m[:, 1], VV0=m[:, 2], T=m[:, 4], P=m[:, 5],
                                                 sp3=m[:, 12], us=us, rho0=rho0, ramp=False)))

fig, ax = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
(aPV, aT), (aS, aV) = ax

for (label, d), c in zip(runs, SERIES):
    if d["ramp"]:
        aPV.plot(d["VV0"], d["P"], color=c, label=label)
    else:
        n = max(1, len(d["t"]) // 4)                      # final state = last 25 % of the run
        v, p = d["VV0"][-n:].mean(), d["P"][-n:].mean()
        eta = np.linspace(0, 1 - v, 50)                   # Rayleigh line P = rho0 Us^2 (1 - V/V0)
        aPV.plot(1 - eta, d["rho0"] * d["us"] ** 2 * eta, color=c, lw=1.2, ls="--")
        aPV.plot(v, p, "o", ms=9, color=c, mec=SURF, mew=2, label=label + " (final)")
    aT.plot(d["t"], d["T"], color=c, label=label)
    aS.plot(d["t"], 100 * d["sp3"], color=c, label=label)
    aV.plot(d["t"], d["VV0"], color=c, label=label)

aPV.set(xlabel="V / V0", ylabel="Longitudinal stress P_zz (GPa)",
        title="Stress-volume path (dashed: MSST Rayleigh lines)")
aPV.invert_xaxis()
aPV.set_yscale("log")
aPV.set_ylim(bottom=1)
aT.set(xlabel="Time (ps)", ylabel="Temperature (K)", title="Temperature")
aS.set(xlabel="Time (ps)", ylabel="sp3 atoms (%)", title="sp3 fraction (coordination 4 within 1.9 A)")
aV.set(xlabel="Time (ps)", ylabel="V / V0", title="Compression")
for a in ax.flat:
    a.legend(fontsize=9, labelcolor=INK2)
fig.suptitle("AB graphite, 128,000 atoms, LCBOP, loading along c (z)", color=INK, fontsize=12)
fig.savefig("shock_results.png", dpi=150)

print(f"{'run':24s} {'V/V0':>7s} {'P_zz GPa':>9s} {'T K':>8s} {'sp3 %':>6s}   (mean of last 25 %)")
for label, d in runs:
    sel = d["hold"] if d["ramp"] else np.ones(len(d["t"]), bool)   # ramp: hold phase only
    n = max(1, sel.sum() // 4)
    d = {k: v[sel] for k, v in d.items() if isinstance(v, np.ndarray)}
    print(f"{label:24s} {d['VV0'][-n:].mean():7.3f} {d['P'][-n:].mean():9.1f} "
          f"{d['T'][-n:].mean():8.0f} {100 * d['sp3'][-n:].mean():6.1f}")
