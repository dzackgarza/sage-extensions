"""Print the current line of each symbol the acceptance table cites."""
import re
from pathlib import Path

SITES = [
    ("lattices.py", "def _pointwise_kernel_generators"),
    ("lattices.py", "def _pointwise_kernel_parameter_vectors"),
    ("lattices.py", "def _pointwise_kernel_transvection"),
    ("lattices.py", "def _isotropic_bezout_partner"),
    ("lattices.py", "def pointwise_levi_image_generators"),
    ("lattices.py", "def _corrected_pointwise_levi_lift"),
    ("lattices.py", "def _rational_pointwise_levi_lift"),
    ("lattice_morphisms.py", "def _computed_group_generators"),
    ("isotropic_parabolics.py", "def _pointed_stabilizer_action"),
    ("isotropic_parabolics.py", "def pointed_stabilizer_generators"),
    ("isotropic_parabolics.py", "def unipotent_radical_generators"),
    ("isotropic_parabolics.py", "def unipotent_parameter_lattice"),
    ("isotropic_parabolics.py", "def unipotent_radical_index"),
    ("rational_integral_stabilizers.py", "def rational_image"),
    ("rational_integral_stabilizers.py", "def stabilizer"),
]

roots = {"lattices.py": "src/sage_extensions/categories/lattices.py",
         "lattice_morphisms.py": "src/sage_extensions/categories/lattice_morphisms.py",
         "isotropic_parabolics.py": "src/sage_extensions/categories/isotropic_parabolics.py",
         "rational_integral_stabilizers.py": "src/sage_extensions/categories/rational_integral_stabilizers.py"}
for name, needle in SITES:
    text = Path(roots[name]).read_text().splitlines()
    hits = [index + 1 for index, line in enumerate(text) if line.strip().startswith(needle)]
    print(f"{name}:{hits[0] if hits else 'MISSING':>6}  {needle}")
