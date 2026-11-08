r"""An integral norm-four reflection prevents splitting the Enriques null-line orbit."""

from sage_extensions.all import *


def test_the_enriques_divisor_one_line_does_not_split_under_o_plus():
    r"""In U+U(2)+E8(-2), reflection in e_2+f_2 fixes e_1 and reverses the component."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U").twist(2) + Lattices(ZZ)("E8").twist(2)
    basis = tuple(lattice.module_generators())
    vector = basis[0]
    root = basis[2] + basis[3]
    assert root.q() == ZZ(4)
    assert root.is_integral_reflection_vector() is True
    reflection = lattice.reflection(root)
    assert reflection(vector) == vector
    plus = lattice.O_plus()
    assert reflection not in plus
    arrows = Cat().Mor(FiniteOrdinalCategory(2), Lattices(ZZ))
    marked = arrows(lattice.subobject_on([vector]).inclusion())
    representatives = lattice.Aut().split_orbit(marked, plus)
    assert representatives.cardinality() == cardinal(1)
    assert next(iter(representatives)) is marked
