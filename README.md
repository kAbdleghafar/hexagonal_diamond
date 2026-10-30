# Shock / high-strain-rate compression of AB graphite (ACE + D2)

Files needed in this folder: `c_ace.yace`, `d2.table`, `graphite_ortho.data`.
LAMMPS must be built with **ML-PACE** (pair pace) and **SHOCK** (fix msst).

## Workflow

```bash
# 1. relax + equilibrate at 300 K, 0 GPa  ->  graphite_eq.data
mpirun -np N lmp -in in.01_equil.lammps

# 2a. uniaxial-strain ramp along c, adiabatic (NVE), constant strain rate
mpirun -np N lmp -in in.02a_ramp.lammps -var srate 1e10 -var emax 0.40 -var thold 10

# 2b. MSST: the steady shocked state for shock speed Us (km/s); scan Us
for us in 5 6 7 8 9 10 11; do
  mpirun -np N lmp -in in.02b_msst.lammps -var Us $us -log log.msst_Us$us
done
```

Any `index` variable at the top of a script can be overridden with `-var name value`
(`dir` = z | x | y picks c-axis / zigzag / armchair loading).

## Outputs

| file | content |
|---|---|
| `ramp_profile.txt` | strain, V/V0, rho, T, P_long, P_lat, shear, dHug, sp3/sp2 fraction, equivalent Us/up |
| `msst_Us<Us>_profile.txt` | V/V0, rho, T, P_long, P_lat, shear, rho0*Us*up, up, dHug, dRay, sp3/sp2 fraction |
| `dump.*.lammpstrj` | positions, velocities, coordination (`c_cn`: 3 = sp2, 4 = sp3), per-atom PE (open in OVITO) |

## Checks
* Step 1: `lz/40` should come out near 3.3-3.4 A. The supplied cell has 3.90 A.
* MSST: `dHug` and `dRay` should go to ~0 and `v_econs` should stay constant.
  If V/V0 keeps oscillating, raise `mu`. If the compression is too violent, raise `q`.
* The ramp (2a) is quasi-isentropic, so dHug > 0: it is colder than the real shock state at the same V.

## `lcbop_run/`: same workflow, 128,000 atoms, cheap LCBOP potential (qualitative only)
`pair_style lcbop` replaces ACE+D2; everything else is unchanged. Driver: `run_all.sh`
(override `LMP`). Plots: `python plot_results.py`, `python plot_snapshots.py <dump> [dt=..] t1 t2 ...`.

Trajectories are stored gzipped (OVITO and `plot_snapshots.py` read `.gz` directly):

| file | run | frames |
|---|---|---|
| `lcbop_run/dump.ramp.lammpstrj.gz` | ramp | every 1 ps, 0-11 ps (12 frames) |
| `lcbop_run/dump.msst_Us15.lammpstrj.gz` | MSST Us = 15 km/s | every 1 ps, 0-4 ps (5 frames) |
| `lcbop_run/dump.msst_Us13.lammpstrj.gz` | MSST Us = 13 km/s | every 1 ps, 0-2 ps (3 frames) |

Columns: id type x y z vx vy vz c_cn (coordination within 1.9 A) c_peatom (eV).

| run | V/V0 | P_zz (GPa) | T (K) | sp3 |
|---|---|---|---|---|
| 300 K, 0 GPa: a = 2.4585 A, interlayer 3.392 A, rho0 = 2.247 g/cc | 1 | 0 | 300 | 0 % |
| ramp 5e10 1/s to 0.45 strain, 2 ps hold | 0.550 | 266 (peak 658 before collapse) | 6780 | 96 % |
| MSST Us = 13 km/s (stopped at 2.85 of 4 ps by a container restart; steady from 1.5 ps) | 0.647 | 134 | 3730 | 0.2 % |
| MSST Us = 15 km/s, dt 0.25 fs | 0.581 | 212 | 9370 | 88 % |

Caveats: LCBOP converts graphite only above ~140-200 GPa (real graphite: ~20 GPa), and at
>6000 K its energy drifts (~30 meV/atom/ps at Us = 15, ~130 K/ps of spurious heating), so
treat temperatures as upper bounds. Use the ACE+D2 inputs one level up for real numbers.
