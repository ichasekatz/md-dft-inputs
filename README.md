<div align="center">

# md-dft-inputs

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**LAMMPS lattice generation and VASP input templates for MD and DFT simulations.**

</div>

## Overview

`md-dft-inputs` provides:

- **`generate_lammps_data`** — tile a VASP POSCAR unit cell into an N×M×K supercell and write a LAMMPS data file
- **`data/`** — ready-to-use VASP input templates (INCAR, KPOINTS, POSCAR) for Au, Pt, and Au-Pt alloy systems

Consolidates the `MD-Lattice-Generator` and DFT input files from `DFT-Toy-Codes`.

## Installation

```bash
git clone https://github.com/ichasekatz/md-dft-inputs.git
cd md-dft-inputs
uv sync
```

## Quick Start

```python
from md_dft_inputs import generate_lammps_data
from pathlib import Path

out = generate_lammps_data(
    poscar_path=Path("data/Au/POSCAR"),
    a=4.065, b=4.065, c=4.065,  # Au lattice parameter
    nx=5, ny=5, nz=5,
    output_path=Path("Au_supercell.lammps"),
)
print(f"Written: {out}")
```

## Data Templates

| System | Files |
|--------|-------|
| `data/Au/` | `INCAR`, `KPOINTS`, `POSCAR` |
| `data/Pt/` | `INCAR`, `KPOINTS`, `POSCAR` |
| `data/Au-Pt/` | `INCAR`, `KPOINTS`, `POSCAR.alloy`, `POSCAR.pure` |
| `data/` | `H2O.poscar`, `H2O2.poscar` (LAMMPS example unit cells) |

## API

```python
read_poscar(poscar_path: Path | str) -> list[tuple[str, float, float, float]]
generate_lammps_data(poscar_path, a, b, c, nx, ny, nz, output_path, seed=42) -> Path
```

## Running Tests

```bash
uv run pytest -v
```

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).
