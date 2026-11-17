r"""Restriction of the dual pairing preserves the discriminant value periods."""

from sage_extensions.all import *


def test_a_changed_redundant_family_spans_the_quadratic_form_of_u2() -> None:
    r"""For U(2), q(a,b)=ab modulo 2 and b((a,b),(c,d))=(ad+bc)/2 modulo 1."""
    form = Lattices(ZZ)([[0, 2], [2, 0]]).discriminant_quadratic_form()
    e, f = tuple(form.module_generators())
    subobject = form.subobject_generated_by((e + f, e, f, e + f))
    inclusion = subobject.inclusion()
    x = inclusion.lift(e + f)
    y = inclusion.lift(e)

    assert subobject.cardinality() == 4
    assert x.q().lift() == 1
    assert y.q().lift() == 0
    assert x.b(y).lift() == QQ(1) / 2


def test_a_cyclic_subobject_keeps_the_one_third_bilinear_pairing() -> None:
    r"""In diag(3,5), 5(e^*+f^*) generates Z/3 with norm 1/3 modulo 1."""
    form = Lattices(ZZ)([[3, 0], [0, 5]]).discriminant_bilinear_form()
    e, f = tuple(form.module_generators())
    generator = 5 * (e + f)
    subobject = form.subobject_generated_by((generator, 2 * generator, generator))
    x = subobject.inclusion().lift(generator)

    assert subobject.cardinality() == 3
    assert x.b(x).lift() == QQ(1) / 3


def test_an_odd_discriminant_form_retains_its_off_diagonal_pairing() -> None:
    r"""The inverse of [[3,1],[1,2]] is (1/5)[[2,-1],[-1,3]]."""
    form = Lattices(ZZ)([[3, 1], [1, 2]]).discriminant_bilinear_form()
    e, f = tuple(form.module_generators())
    normalized = form.invariant_factor_form()
    x, y = normalized(e), normalized(f)

    assert normalized.codomain().cardinality() == 5
    assert x.b(x).lift() == QQ(2) / 5
    assert x.b(y).lift() == QQ(4) / 5
    assert y.b(y).lift() == QQ(3) / 5
