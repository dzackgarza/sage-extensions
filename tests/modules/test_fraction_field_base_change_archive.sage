r"""Scalar extension from $\mathbb Z$ to $\mathbb Q$."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_determinant_two_endomorphism_of_z2_becomes_invertible_over_q() -> None:
    r"""$f(e) = 2e$, $f(f') = e + f'$ has determinant 2: over $\mathbb Z$ its cokernel is
    $\mathbb Z/2$, and $\mathbb Q \otimes f$ is an isomorphism of $\mathbb Q^2$.

    Source: by hand (a square integer matrix is invertible over Q iff its determinant is nonzero).
    """
    M = ZZ**2
    e, f = M.module_generator(0), M.module_generator(1)
    endomorphism = M.End()({0: 2 * e, 1: e + f})
    assert not endomorphism.is_surjective()
    assert endomorphism.cokernel().cardinality() == 2

    extension = Modules(ZZ).scalar_extension(ZZ.fraction_field_map())
    extended = extension(endomorphism)
    assert extended.domain().base_ring() == QQ
    assert extended.is_isomorphism()


def test_the_unit_z2_to_q2_of_scalar_extension_is_injective_and_not_surjective() -> None:
    r"""The unit $M \to \mathbb Q \otimes M$ is injective for torsion-free $M$, with cokernel
    $(\mathbb Q/\mathbb Z)^2 \ne 0$ for $M = \mathbb Z^2$.

    Source: Atiyah–Macdonald, Introduction to Commutative Algebra, 3.7 (Q is flat over Z).
    """
    M = ZZ**2
    unit = Modules(ZZ).base_change_adjunction(ZZ.fraction_field_map()).unit(M)
    assert unit.is_injective()
    assert not unit.is_surjective()
