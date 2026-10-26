r"""The identity A2 isometry has only its order-one cyclotomic piece and restricts to stable lines."""

from sage_extensions.all import *  # noqa: F401,F403


def test_a2_identity_has_full_order_one_cyclotomic_summand() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()
    decomposition = identity.cyclotomic_decomposition(1)
    summand = identity.cyclotomic_summand(1)

    assert decomposition is not None
    assert summand.module_rank() == lattice.module_rank()


def test_a2_identity_restricts_to_a_stable_rank_one_sublattice() -> None:
    lattice = Lattices(ZZ)("A2")
    identity = lattice.O().one()
    line = lattice.subobject_on((lattice.module_generator(0),))
    restricted = identity.equivariant_sublattice(line)

    assert restricted.domain() is line
    assert restricted.codomain() is line
