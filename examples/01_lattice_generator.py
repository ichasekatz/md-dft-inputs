"""LAMMPS data file generation from a POSCAR unit cell.

Reads a POSCAR file, tiles it into a supercell, and writes a LAMMPS data
file. Update the lattice parameters and supercell dimensions to match your
system.
"""

from __future__ import annotations

from pathlib import Path

from md_dft_inputs import generate_lammps_data

# POSCAR file — use one of the examples in data/ or supply your own
poscar = Path(__file__).parent.parent / "data" / "H2O2.poscar"

# Lattice parameters in Å (match your POSCAR SCALE + lattice vectors)
a = 3.97
b = 3.97
c = 7.49

# Supercell dimensions
nx, ny, nz = 5, 5, 3

if __name__ == "__main__":
    out = generate_lammps_data(
        poscar_path=poscar,
        a=a, b=b, c=c,
        nx=nx, ny=ny, nz=nz,
        output_path=Path("lattice.lammps"),
    )
    print(f"Written: {out}")
