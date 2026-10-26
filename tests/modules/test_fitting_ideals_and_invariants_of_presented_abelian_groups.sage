r"""Fitting ideals, annihilators, exponents and ranks of presented abelian groups.

For $M = \operatorname{coker}(A: \mathbb Z^r \to \mathbb Z^n)$ the $k$-th Fitting ideal is generated
by the $(n - k)$-minors of $A$ (all of $\mathbb Z$ when $n - k \le 0$, and $0$ when $n - k$ exceeds
the number of relations); it depends only on $M$.  For
$M = \mathbb Z^2 / (6u) \cong \mathbb Z/6 \oplus \mathbb Z$ with relation matrix $(6, 0)$:
$\operatorname{Fitt}_0 = 0$, $\operatorname{Fitt}_1 = (6)$, $\operatorname{Fitt}_2 = \mathbb Z$; $M$ has
rank $1$, is not torsion, has annihilator and exponent $0$, is countably infinite, and has
projective dimension $1$ (it is not projective since $\mathbb Z/6$ is not).  For
$N = \mathbb Z^2 / 2\mathbb Z^2 = (\mathbb Z/2)^2$ with relation matrix $2I$:
$\operatorname{Fitt}_0 = (4)$, $\operatorname{Fitt}_1 = (2)$, $\operatorname{Fitt}_2 = \mathbb Z$, the
annihilator and exponent are $2$, $\lvert N \rvert = 4$ and the rank is $0$.  The cokernel of an
isomorphism is $0$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def z6_plus_z():
    r"""$\operatorname{coker}(\mathbb Z \to \mathbb Z^2,\ 1 \mapsto 6u)$."""
    plane = ZZ ^ 2
    return (ZZ ^ 1).Mor(plane)({0: 6 * plane.module_generator(0)}).cokernel()


def z2_squared():
    r"""$\operatorname{coker}(2: \mathbb Z^2 \to \mathbb Z^2)$."""
    plane = ZZ ^ 2
    u, v = plane.module_generator(0), plane.module_generator(1)
    return plane.End()({0: 2 * u, 1: 2 * v}).cokernel()


def test_the_fitting_ideals_of_z6_plus_z_are_0_6_and_1() -> None:
    r"""$(6, 0)$ has no $2$-minor, the $1$-minors generate $(6)$, and $\operatorname{Fitt}_2 = \mathbb Z$."""
    module = z6_plus_z()

    assert module.fitting_ideal(0) == ZZ.ideal(0)
    assert module.fitting_ideal(1) == ZZ.ideal(6)
    assert module.fitting_ideal(2) == ZZ.ideal(1)


def test_the_fitting_ideals_of_z2_squared_are_4_2_and_1() -> None:
    r"""$\det 2I = 4$, the $1$-minors of $2I$ generate $(2)$, and $\operatorname{Fitt}_2 = \mathbb Z$."""
    module = z2_squared()

    assert module.fitting_ideal(0) == ZZ.ideal(4)
    assert module.fitting_ideal(1) == ZZ.ideal(2)
    assert module.fitting_ideal(2) == ZZ.ideal(1)


def test_the_ranks_of_z6_plus_z_and_z2_squared_are_one_and_zero() -> None:
    r"""$\operatorname{rank}(\mathbb Z/6 \oplus \mathbb Z) = 1$ and $\operatorname{rank}(\mathbb Z/2)^2 = 0$."""
    assert z6_plus_z().module_rank() == 1
    assert z2_squared().module_rank() == 0


def test_z6_plus_z_is_neither_torsion_nor_projective() -> None:
    r"""$\mathbb Z/6 \oplus \mathbb Z$: not torsion, not projective, not zero."""
    module = z6_plus_z()

    assert not module.is_torsion()
    assert not module.is_projective()
    assert not module.is_zero()


def test_z6_plus_z_has_annihilator_and_exponent_zero() -> None:
    r"""The free summand is killed only by $0$."""
    module = z6_plus_z()

    assert module.annihilator() == ZZ.ideal(0)
    assert module.exponent() == 0


def test_z6_plus_z_has_projective_dimension_one() -> None:
    r"""$0 \to \mathbb Z \xrightarrow{(6, 0)} \mathbb Z^2 \to M \to 0$ and $M$ is not projective."""
    assert z6_plus_z().projective_dimension() == 1


def test_z6_plus_z_is_countably_infinite() -> None:
    r"""$\lvert \mathbb Z/6 \oplus \mathbb Z \rvert = \aleph_0$, the cardinality of $\mathbb Z$."""
    assert z6_plus_z().cardinality() == ZZ.cardinality()


def test_z2_squared_is_a_torsion_module_killed_by_two() -> None:
    r"""$(\mathbb Z/2)^2$ is torsion, with annihilator $(2)$ and exponent $2$."""
    module = z2_squared()

    assert module.is_torsion()
    assert module.annihilator() == ZZ.ideal(2)
    assert module.exponent() == 2


def test_z2_squared_has_four_elements() -> None:
    r"""$\lvert (\mathbb Z/2)^2 \rvert = 4$."""
    assert z2_squared().cardinality() == 4


def test_the_cokernel_of_the_identity_is_zero() -> None:
    r"""$\operatorname{coker}(\mathrm{id}_{\mathbb Z^2}) = 0$, while $\operatorname{coker}(2) \neq 0$."""
    assert (ZZ ^ 2).End().one().cokernel().is_zero()
    assert not z2_squared().is_zero()
