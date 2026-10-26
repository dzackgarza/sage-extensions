r"""Stalks of the structure sheaf of the affine line over QQ."""

from sage_extensions.all import *


def test_stalks_of_the_affine_line_at_the_origin_and_the_generic_point() -> None:
    r"""`\mathcal{O}_{\mathbb{A}^1, (x)} = \mathbb{Q}[x]_{(x)}` is a local ring of
    dimension 1 with residue field `\mathbb{Q}`; the stalk at the generic point is the
    field `\mathbb{Q}(x)`, of dimension 0."""
    line = AffineSpaces(QQ)(1, names=("x",))
    ring = line.coordinate_ring()
    x = ring.algebra_generator("x")
    origin = line.underlying_space()(ring.ideal(x))
    generic = line.underlying_space().generic_point()

    at_origin = line.stalk(origin)
    at_generic = line.stalk(generic)

    assert at_origin in LocalRings()
    assert at_origin.krull_dimension() == 1
    assert at_origin.residue_field().is_isomorphic(QQ)
    assert at_generic in Fields()
    assert at_generic.krull_dimension() == 0
