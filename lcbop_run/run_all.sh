#!/bin/bash
# Full LCBOP workflow on the 128000-atom AB graphite cell.
# LMP can be overridden, e.g.  LMP="mpirun -np 64 lmp" ./run_all.sh
set -u
cd "$(dirname "$0")"
LMP=${LMP:-"mpirun -np 4 lmp"}

stage() {   # stage <name> <lammps args...>
  local name=$1; shift
  echo "$(date '+%F %T') START $name" >> progress.txt
  if $LMP "$@" -log log.$name > out.$name 2>&1; then
    echo "$(date '+%F %T') DONE  $name" >> progress.txt
  else
    echo "$(date '+%F %T') FAIL  $name" >> progress.txt
    exit 1
  fi
}

stage 01_equil      -in in.01_equil.lammps -var tnpt 4 -var tavg 2 -var tnvt 1
stage 02a_ramp      -in in.02a_ramp.lammps -var srate 5e10 -var emax 0.45 -var thold 2 -var nout 200 -var ndump 2000
stage 02b_msst_Us15 -in in.02b_msst.lammps -var Us 15 -var dt 0.00025 -var trun 4 -var nout 200 -var ndump 4000
stage 02b_msst_Us13 -in in.02b_msst.lammps -var Us 13 -var trun 4 -var nout 100 -var ndump 2000
echo "$(date '+%F %T') ALL DONE" >> progress.txt
