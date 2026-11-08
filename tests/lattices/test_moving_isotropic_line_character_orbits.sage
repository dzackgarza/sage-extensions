r"""Moving primitive null lines retain their marking under finite character splitting."""

from sage_extensions.all import *


def test_moving_unimodular_null_line_has_one_orbit_for_each_character_kernel():
    r"""In U squared, Eichler transitivity and a perpendicular +2 reflection give one orbit."""
    lattice = Lattices(ZZ)([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
    e, f, u, v = tuple(lattice.module_generators())
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    line = lattice.subobject_on([e])
    marked = arrows(line.inclusion())
    for subgroup in (lattice.SO(), lattice.O_plus(), lattice.stable_orthogonal_group()):
        representatives = lattice.Aut().split_orbit(marked, subgroup)
        assert representatives.cardinality() == cardinal(1)
        assert next(iter(representatives)) in arrows
        arrow = next(iter(representatives)).arrow()
        image = arrow(next(iter(arrow.domain().module_generators())))
        assert image.is_primitive() is True
        assert image.q() == ZZ.zero()
    reflection = lattice.reflection(u + v)
    assert reflection(e) == e and reflection(f) == f
    assert reflection not in lattice.SO()
    assert reflection not in lattice.O_plus()
