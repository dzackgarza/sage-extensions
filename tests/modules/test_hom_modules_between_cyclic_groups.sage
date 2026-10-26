r"""The modules $\operatorname{Hom}_{\mathbb Z}(M, N)$ between cyclic and free abelian groups.

A homomorphism out of $\mathbb Z/m$ is determined by the image $n$ of $1$, subject to $mn = 0$, so
$\operatorname{Hom}(\mathbb Z/m, \mathbb Z/k) \cong \mathbb Z/\gcd(m, k)$,
$\operatorname{Hom}(\mathbb Z, N) \cong N$ and $\operatorname{Hom}(\mathbb Z/m, \mathbb Z) = 0$; for free
modules $\operatorname{Hom}(R^a, R^b) \cong R^{ab}$, by hand from the definitions.  Pre- and postcomposition make $\operatorname{Hom}$ a functor: precomposing with
$3: \mathbb Z \to \mathbb Z$ sends $\varphi$ to $3\varphi$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def cyclic(order):
    r"""$\operatorname{coker}(\mathbb Z \xrightarrow{m} \mathbb Z)$."""
    line = ZZ ^ 1
    return line.Mor(line)({0: order * line.module_generator(0)}).cokernel()


def test_hom_from_z6_to_z4_is_z2_generated_by_one_to_two() -> None:
    r"""$\operatorname{Hom}(\mathbb Z/6, \mathbb Z/4) = \{0, 1 \mapsto 2\} \cong \mathbb Z/2$."""
    six, four = cyclic(6), cyclic(4)
    homs = six.Mor(four)
    doubling = homs({0: 2 * four.module_generator(0)})

    assert homs in Modules(ZZ)
    assert homs.is_torsion()
    assert homs.exponent() == 2
    assert homs.annihilator() == ZZ.ideal(2)
    assert doubling(six.module_generator(0)) == 2 * four.module_generator(0)
    assert doubling != homs.zero()
    assert doubling + doubling == homs.zero()


def test_hom_from_z4_to_z6_is_z2() -> None:
    r"""$\operatorname{Hom}(\mathbb Z/4, \mathbb Z/6) \cong \mathbb Z/\gcd(4, 6) = \mathbb Z/2$."""
    homs = cyclic(4).Mor(cyclic(6))

    assert homs.exponent() == 2
    assert homs.annihilator() == ZZ.ideal(2)


def test_the_endomorphisms_of_z6_and_the_homs_from_z_to_z6_are_z6() -> None:
    r"""$\operatorname{End}(\mathbb Z/6) \cong \operatorname{Hom}(\mathbb Z, \mathbb Z/6) \cong \mathbb Z/6$."""
    six = cyclic(6)

    assert six.End().exponent() == 6
    assert (ZZ ^ 1).Mor(six).exponent() == 6
    assert (ZZ ^ 1).Mor(six).annihilator() == ZZ.ideal(6)


def test_the_presentation_of_end_z6_is_the_first_differential_of_its_resolution() -> None:
    r"""A presentation is a resolution truncated at degree $1$, so the presentation of
    $\operatorname{End}(\mathbb Z/6)$ is the differential $d_1$ of its chosen resolution."""
    homs = cyclic(6).End()

    assert homs.has_selected_module_resolution()
    assert homs.presentation() is homs.selected_module_resolution().differential(1)


def test_the_orders_of_hom_modules_between_cyclic_groups() -> None:
    r"""$\lvert \operatorname{Hom}(\mathbb Z/6, \mathbb Z/4) \rvert = 2$ and
    $\lvert \operatorname{End}(\mathbb Z/6) \rvert = 6$."""
    assert cyclic(6).Mor(cyclic(4)).cardinality() == 2
    assert cyclic(6).End().cardinality() == 6


def test_hom_from_z6_to_z_is_zero() -> None:
    r"""$\mathbb Z$ is torsion-free, so $\operatorname{Hom}(\mathbb Z/6, \mathbb Z) = 0$."""
    assert cyclic(6).Mor(ZZ ^ 1).is_zero()


def test_hom_between_free_modules_is_free_of_the_product_rank() -> None:
    r"""$\operatorname{Hom}(\mathbb Z^2, \mathbb Z) \cong \mathbb Z^2$ and
    $\operatorname{Hom}(\mathbb Q^2, \mathbb Q^3) \cong \mathbb Q^6$."""
    assert (ZZ ^ 2).Mor(ZZ ^ 1).module_rank() == 2
    assert (QQ ^ 2).Mor(QQ ^ 3).module_rank() == 6


def test_hom_from_z2_to_z_is_countable_and_not_torsion() -> None:
    r"""$\operatorname{Hom}(\mathbb Z^2, \mathbb Z) \cong \mathbb Z^2$ is countably infinite and torsion-free."""
    homs = (ZZ ^ 2).Mor(ZZ ^ 1)

    assert homs.cardinality() == ZZ.cardinality()
    assert not homs.is_torsion()


def test_precomposition_with_three_multiplies_by_three() -> None:
    r"""$\operatorname{Hom}(3, \mathbb Z): \operatorname{End}(\mathbb Z) \to \operatorname{End}(\mathbb Z)$,
    $\varphi \mapsto \varphi \circ 3$, sends the identity to $3$."""
    line = ZZ ^ 1
    unit = line.module_generator(0)
    tripling = line.End()({0: 3 * unit})
    induced = tripling.internal_mor_map(line.End().one())

    assert induced(line.End().one()) == tripling
