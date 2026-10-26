from sage_extensions.all import *


def f3():
    return PrimeFields()(3)


def test_the_finite_field_constructor_agrees() -> None:
    assert GF(3) == f3()


def test_the_quotient_of_the_integers_is_the_prime_field() -> None:
    r"""$\mathbb Z/3\mathbb Z$ is a field with three elements, and $\mathbb Z/3 \to \mathbb F_3$ is the unique ring map."""
    quotient = ZZ.quotient_ring(ZZ.ideal(3))
    assert quotient in Fields()
    assert quotient.cardinality() == 3
    assert quotient.Mor(f3()).cardinality() == 1


def test_the_categories_of_f3() -> None:
    field = f3()
    assert field in Rings()
    assert field in Fields()
    assert field in PrimeFields()
    assert field in FiniteSets()


def test_the_arithmetic_of_f3() -> None:
    field = f3()
    two = field(2)
    assert field.cardinality() == 3
    assert field.characteristic() == 3
    assert two + two == field.one()
    assert two * two == field.one()
    assert two.inverse() == two
    assert field(3) == field.zero()


def test_the_automorphisms_of_f3() -> None:
    assert f3().Aut().order() == 1
    assert f3().End().cardinality() == 1


def test_the_plane_over_f3() -> None:
    r"""$|\mathbb F_3^2| = 9$, $|\operatorname{GL}_2(\mathbb F_3)| = (9 - 1)(9 - 3) = 48$."""
    plane = f3() ^ 2
    assert plane.cardinality() == 9
    assert Modules(f3()).Aut(plane).order() == 48


def test_f3_has_one_endomorphism_category() -> None:
    field = f3()
    endomorphisms = field.Mor(field)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert field.Mor(field) is endomorphisms
    assert identity * identity == identity
