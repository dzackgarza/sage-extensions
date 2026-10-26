r"""Weyl chambers of the hyperbolic plane \(\langle 2\rangle\oplus\langle -2\rangle\).

Its roots are the vectors \(ae_0 + be_1\) of square \(-2\), i.e. \(b^2 - a^2 = 1\),
so \(\pm e_1\): one mirror \(e_1^\perp = \mathbb Z e_0\), two chambers, and the
Weyl group \(\{1, s_{e_1}\}\).
"""

from sage_extensions.all import *


def test_the_reflection_in_the_wall_root_carries_the_chamber_across_the_wall() -> None:
    r"""\(s_r\) sends the chamber \(\{b(r,-)\ge 0\}\) to \(\{b(-r,-)\ge 0\}\) and fixes the
    timelike \(e_0\), which spans the shared wall \(r^\perp\)."""
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    timelike, spacelike = lattice.module_generators()
    chamber = lattice.fundamental_chamber()
    complex_ = lattice.chamber_complex()
    root = chamber.wall_roots()[0]

    assert chamber.wall_roots().cardinality() == 1
    assert root in (spacelike, -spacelike)

    adjacency = complex_.fundamental_adjacencies()[root]
    reflection = lattice.reflection(root)

    assert adjacency.transporter() == reflection
    assert adjacency.target().wall_roots()[0] == -root
    face = adjacency.shared_face()
    assert face.dimension() == chamber.dimension() - 1
    assert face.contains(timelike)
    assert reflection(timelike) == timelike
    assert reflection(root) == -root


def test_crossing_the_same_wall_twice_is_the_identity() -> None:
    r"""\(s_r^2 = 1\)."""
    lattice = Lattices(ZZ)([[2, 0], [0, -2]])
    chamber = lattice.fundamental_chamber()
    complex_ = lattice.chamber_complex()
    root = chamber.wall_roots()[0]

    assert complex_.transporter_from_word((root, root)) == lattice.O().one()
    assert complex_.chamber_from_word((0, 0)).wall_roots() == chamber.wall_roots()
