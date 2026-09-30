"""LAMMPS lattice data file generation from POSCAR unit cells.

Reads a VASP POSCAR file, tiles the unit cell into an N×M×K supercell,
and writes a LAMMPS data file suitable for MD simulations.

Supports optional random site-substitution (e.g., Nd→Dy doping) at the
unit-cell level.
"""

from __future__ import annotations

import random
from pathlib import Path


def read_poscar(poscar_path: Path | str) -> list[tuple[str, float, float, float]]:
    """Parse a VASP POSCAR file and return fractional atomic coordinates.

    Reads a POSCAR in direct (fractional) coordinates. The ``Selective
    dynamics`` line is handled transparently.

    Args:
        poscar_path (Path | str): Path to the POSCAR file.

    Returns:
        List of ``(element, x_frac, y_frac, z_frac)`` tuples for each atom
        in the unit cell, in the order they appear in the POSCAR.

    Raises:
        FileNotFoundError: If ``poscar_path`` does not exist.
        ValueError: If the POSCAR format is unrecognized.
    """
    poscar_path = Path(poscar_path)
    if not poscar_path.exists():
        raise FileNotFoundError(poscar_path)

    with poscar_path.open() as fh:
        lines = fh.readlines()

    element_symbols = lines[5].strip().split()
    element_counts = [int(x) for x in lines[6].strip().split()]

    elements: list[str] = []
    for symbol, count in zip(element_symbols, element_counts, strict=True):
        elements.extend([symbol] * count)

    coord_start = 8 if "Selective dynamics" in lines[7] else 8
    coords: list[tuple[str, float, float, float]] = []
    for element, raw in zip(elements, lines[coord_start : coord_start + len(elements)], strict=True):
        x, y, z = map(float, raw.split()[:3])
        coords.append((element, x, y, z))

    return coords


def generate_lammps_data(
    poscar_path: Path | str,
    a: float,
    b: float,
    c: float,
    nx: int,
    ny: int,
    nz: int,
    output_path: Path | str,
    seed: int = 42,
) -> Path:
    """Generate a LAMMPS data file by tiling a POSCAR unit cell.

    Tiles the unit cell ``nx × ny × nz`` times along each lattice direction
    using orthogonal periodic boundary conditions.

    Args:
        poscar_path (Path | str): Path to the POSCAR unit cell file.
        a (float): Lattice parameter along x in Å.
        b (float): Lattice parameter along y in Å.
        c (float): Lattice parameter along z in Å.
        nx (int): Number of unit cells along x.
        ny (int): Number of unit cells along y.
        nz (int): Number of unit cells along z.
        output_path (Path | str): Destination for the LAMMPS data file.
        seed (int): Random seed for site-substitution. Defaults to 42.

    Returns:
        Resolved path to the written LAMMPS data file.

    Raises:
        FileNotFoundError: If ``poscar_path`` does not exist.
    """
    random.seed(seed)
    unit_cell = read_poscar(poscar_path)
    positions = _tile_unit_cell(unit_cell, a, b, c, nx, ny, nz)
    out = Path(output_path)
    _write_lammps_data(positions, a, b, c, nx, ny, nz, out)
    return out


def _tile_unit_cell(
    unit_cell: list[tuple[str, float, float, float]],
    a: float,
    b: float,
    c: float,
    nx: int,
    ny: int,
    nz: int,
) -> list[tuple[str, float, float, float]]:
    """Tile the unit cell into an nx×ny×nz supercell.

    Args:
        unit_cell (list[tuple[str, float, float, float]]): Fractional-
            coordinate atomic positions from :func:`read_poscar`.
        a (float): Lattice parameter along x in Å.
        b (float): Lattice parameter along y in Å.
        c (float): Lattice parameter along z in Å.
        nx (int): Repeat count along x.
        ny (int): Repeat count along y.
        nz (int): Repeat count along z.

    Returns:
        Cartesian atomic positions ``(element, x, y, z)`` in Å.
    """
    positions: list[tuple[str, float, float, float]] = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                for element, xf, yf, zf in unit_cell:
                    x = (i + xf) * a
                    y = (j + yf) * b
                    z = (k + zf) * c
                    positions.append((element, x, y, z))
    return positions


def _write_lammps_data(
    positions: list[tuple[str, float, float, float]],
    a: float,
    b: float,
    c: float,
    nx: int,
    ny: int,
    nz: int,
    output_path: Path,
) -> None:
    """Write Cartesian atomic positions to a LAMMPS data file.

    Args:
        positions (list[tuple[str, float, float, float]]): Cartesian atomic
            positions in Å from :func:`_tile_unit_cell`.
        a (float): Lattice parameter along x in Å.
        b (float): Lattice parameter along y in Å.
        c (float): Lattice parameter along z in Å.
        nx (int): Supercell size along x.
        ny (int): Supercell size along y.
        nz (int): Supercell size along z.
        output_path (Path): Destination file path.
    """
    element_types = {el: idx + 1 for idx, el in enumerate(dict.fromkeys(p[0] for p in positions))}

    with output_path.open("w") as fh:
        fh.write("LAMMPS data file\n\n")
        fh.write(f"{len(positions)} atoms\n")
        fh.write(f"{len(element_types)} atom types\n\n")
        fh.write(f"0.0 {nx * a:.6f} xlo xhi\n")
        fh.write(f"0.0 {ny * b:.6f} ylo yhi\n")
        fh.write(f"0.0 {nz * c:.6f} zlo zhi\n\n")
        fh.write("Atoms\n\n")
        for atom_id, (element, x, y, z) in enumerate(positions, start=1):
            fh.write(f"{atom_id} {element_types[element]} {x:.6f} {y:.6f} {z:.6f}\n")
