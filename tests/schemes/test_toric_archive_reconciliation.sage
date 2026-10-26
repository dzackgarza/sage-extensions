r"""The toric variety of a lattice polygon and its polarization.

Source: Cox, Little, Schenck, *Toric Varieties*, Prop. 4.3.3: for a full-dimensional lattice polytope `P`, the polarizing line bundle `L_P` on
`X_P` has `h^0(L_P) = |P \cap M|`; the standard triangle gives `(\mathbb{P}^2,
\mathcal{O}(1))` and its double gives `(\mathbb{P}^2, \mathcal{O}(2))`.
"""

from sage_extensions.all import *


def test_the_standard_triangle_polarizes_the_projective_plane_with_sections_its_lattice_points() -> None:
    lattice = ZZ.free_module(2)
    triangle = ConvexPolytopes(lattice)(((0, 0), (1, 0), (0, 1)))
    doubled = ConvexPolytopes(lattice)(((0, 0), (2, 0), (0, 2)))
    variety = triangle.toric_variety(QQ)

    assert variety.is_isomorphic(ProjectiveSpaces(QQ)(2))
    assert variety.polarizing_line_bundle().global_sections().module_rank() == 3
    assert doubled.toric_variety(QQ).polarizing_line_bundle().global_sections().module_rank() == 6
