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


def test_moving_divisor_three_null_line_has_one_discriminant_kernel_orbit():
    r"""For 3e+3f+h in U squared plus <-18>, negation exchanges the two nonzero classes."""
    lattice = Lattices(ZZ)([[0, 1, 0, 0, 0], [1, 0, 0, 0, 0], [0, 0, 0, 1, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, -18]])
    e, f, u, v, h = tuple(lattice.module_generators())
    vector = 3 * e + 3 * f + h
    assert vector.q() == ZZ.zero()
    assert vector.is_primitive() is True
    assert lattice.div(vector) == ZZ(3)
    c = lattice.divided_discriminant_class(vector)
    assert c != -c
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    marked = arrows(lattice.subobject_on([vector]).inclusion())
    representatives = lattice.Aut().split_orbit(marked, lattice.stable_orthogonal_group())
    assert representatives.cardinality() == cardinal(1)
    for representative in representatives:
        assert representative in arrows
        arrow = representative.arrow()
        image = arrow(next(iter(arrow.domain().module_generators())))
        assert image.q() == ZZ.zero()
        assert lattice.div(image) == ZZ(3)
        assert lattice.divided_discriminant_class(image) in (c, -c)
