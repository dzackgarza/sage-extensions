r"""Extension and restriction of scalars along $\iota: \mathbb Z \to \mathbb Q$.

Extension of scalars $\mathbb Q \otimes_{\mathbb Z} -$ is left adjoint to restriction
$\operatorname{Res}_\iota$; the unit $M \to \operatorname{Res}_\iota(\mathbb Q \otimes M)$ is
$m \mapsto 1 \otimes m$, and the counit $\mathbb Q \otimes \operatorname{Res}_\iota N \to N$ is
$q \otimes n \mapsto qn$.  Restriction is also left adjoint to coextension
$\operatorname{Hom}_{\mathbb Z}(\mathbb Q, -)$.  So $\mathbb Q \otimes \mathbb Z^2 \cong \mathbb Q^2$ has
rank $2$; $\operatorname{Res}_\iota \mathbb Q^2$ is a torsion-free, countably infinite abelian group,
flat since $\mathbb Q$ is a localization of $\mathbb Z$.  Values from the definitions.
"""

from sage_extensions.all import *  # noqa: F401,F403


def inclusion():
    return ZZ.Mor(QQ)(lambda n: QQ(n))


def test_restricting_q2_to_the_integers_gives_a_module_over_the_integers() -> None:
    r"""$\operatorname{Res}_\iota \mathbb Q^2$ has base ring $\mathbb Z$."""
    restricted = Modules(QQ).restriction_of_scalars(inclusion())(QQ ^ 2)

    assert restricted.base_ring() is ZZ
    assert restricted in AdditiveGroups().AdditiveCommutative()
    action = restricted.scalar_action()
    additive_group = restricted.underlying_additive_group()
    assert action.domain() is ZZ
    assert action.codomain() is AdditiveGroups().AdditiveCommutative().End(additive_group)
    generator = restricted.module_over_extension().module_generator(0)
    assert action(ZZ(2))(additive_group(generator)) == additive_group(
        restricted.module_over_extension().scalar_multiple(QQ(2), generator)
    )


def test_the_restriction_of_q2_is_countable_torsion_free_and_flat() -> None:
    r"""$\lvert \mathbb Q^2 \rvert = \aleph_0$; $\mathbb Q^2$ has no $\mathbb Z$-torsion and is flat."""
    restricted = Modules(QQ).restriction_of_scalars(inclusion())(QQ ^ 2)

    assert restricted.cardinality() == QQ.cardinality()
    assert not restricted.is_torsion()
    assert restricted.is_flat()


def test_extending_z2_to_the_rationals_has_rank_two() -> None:
    r"""$\mathbb Q \otimes_{\mathbb Z} \mathbb Z^2 \cong \mathbb Q^2$."""
    extended = Modules(ZZ).scalar_extension(inclusion())(ZZ ^ 2)

    assert extended.base_ring() is QQ
    assert extended.module_rank() == 2


def test_the_unit_of_extension_and_restriction_sends_e0_to_one_tensor_e0() -> None:
    r"""$\eta: \mathbb Z^2 \to \operatorname{Res}_\iota(\mathbb Q \otimes \mathbb Z^2)$, $e_0 \mapsto 1 \otimes e_0$."""
    adjunction = Modules(ZZ).base_change_adjunction(inclusion())
    lattice = ZZ ^ 2
    unit = adjunction.unit(lattice)
    extended = adjunction.left_adjoint()(lattice)

    assert unit(lattice.module_generator(0)) == unit.codomain()(extended.module_generator(0))
    assert unit(lattice.module_generator(1)) == unit.codomain()(extended.module_generator(1))


def test_the_counit_of_extension_and_restriction_on_q2_lands_in_q2() -> None:
    r"""$\varepsilon_N: \mathbb Q \otimes \operatorname{Res}_\iota N \to N$ for $N = \mathbb Q^2$ ends at $N$."""
    space = QQ ^ 2
    counit = Modules(ZZ).base_change_adjunction(inclusion()).counit(space)

    assert counit.codomain() is space


def test_restriction_to_the_integers_has_a_right_adjoint() -> None:
    r"""$\operatorname{Res}_\iota \dashv \operatorname{Hom}_{\mathbb Z}(\mathbb Q, -)$, whose left adjoint restricts."""
    adjunction = Modules(QQ).restriction_coextension_adjunction(inclusion())

    assert adjunction.left_adjoint()(QQ ^ 2).base_ring() is ZZ
