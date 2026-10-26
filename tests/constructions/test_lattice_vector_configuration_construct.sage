r"""Stabilizers in ``O(U)`` of families of hyperbolic basis vectors.

``O(U)`` has order four: ``±1`` and ``±`` the exchange of ``e`` and ``f``.
The family ``(e, f)`` is permuted by the identity and by the exchange; the
family ``(e,)`` is fixed by the identity alone.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_hyperbolic_basis_family_is_stabilized_by_the_exchange() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)
    f = lattice.basis_vector(1)
    family = Sets().Mor(Sets.Δ[1], lattice)(lambda i: (e, f)[int(i)])

    assert lattice.O().stabilizer(family).cardinality() == 2


def test_a_single_isotropic_basis_vector_is_fixed_by_the_identity_alone() -> None:
    lattice = NamedLattices.U
    e = lattice.basis_vector(0)
    family = Sets().Mor(Sets.Δ[0], lattice)(lambda _i: e)

    assert lattice.O().stabilizer(family).cardinality() == 1
