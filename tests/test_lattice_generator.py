"""Tests for md_dft_inputs.lattice_generator."""

from __future__ import annotations

from pathlib import Path
from unittest import TestCase

import pytest

from md_dft_inputs import generate_lammps_data, read_poscar

_DATA = Path(__file__).parent.parent / "data"


class TestReadPoscar(TestCase):
    """Tests for read_poscar."""

    def test_missing_file_raises(self):
        """Non-existent POSCAR raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            read_poscar(Path("/nonexistent/POSCAR"))

    def test_returns_list_of_tuples(self):
        """Returns a non-empty list of 4-tuples."""
        poscar = _DATA / "H2O2.poscar"
        if not poscar.exists():
            pytest.skip("H2O2.poscar not present")
        atoms = read_poscar(poscar)
        assert len(atoms) > 0
        assert all(len(a) == 4 for a in atoms)

    def test_fractional_coords_in_range(self):
        """Fractional coordinates are in [0, 1)."""
        poscar = _DATA / "H2O2.poscar"
        if not poscar.exists():
            pytest.skip("H2O2.poscar not present")
        for _, x, y, z in read_poscar(poscar):
            assert 0.0 <= x < 1.0
            assert 0.0 <= y < 1.0
            assert 0.0 <= z < 1.0


def test_output_file_created(tmp_path):
    """Output file is written to the requested path."""
    poscar = _DATA / "H2O2.poscar"
    if not poscar.exists():
        pytest.skip("H2O2.poscar not present")
    out = generate_lammps_data(poscar, a=3.97, b=3.97, c=7.49, nx=2, ny=2, nz=1, output_path=tmp_path / "lattice.lammps")
    assert out.exists()
    assert out.stat().st_size > 0


def test_atom_count_matches_supercell(tmp_path):
    """Atom count in output equals unit cell atoms × supercell volume."""
    poscar = _DATA / "H2O2.poscar"
    if not poscar.exists():
        pytest.skip("H2O2.poscar not present")
    unit_cell = read_poscar(poscar)
    nx, ny, nz = 2, 2, 2
    out = generate_lammps_data(poscar, a=3.97, b=3.97, c=7.49, nx=nx, ny=ny, nz=nz, output_path=tmp_path / "lattice.lammps")
    lines = out.read_text().splitlines()
    atom_count_line = next(ln for ln in lines if "atoms" in ln and "atom types" not in ln)
    n_atoms = int(atom_count_line.split()[0])
    assert n_atoms == len(unit_cell) * nx * ny * nz
