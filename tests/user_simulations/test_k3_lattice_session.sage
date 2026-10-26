r"""A session on the K3 lattice and its catalogue involutions and embeddings.

The K3 lattice, its decomposition, the named involutions with their
invariant and coinvariant lattices, the named embeddings and their
orthogonal complements, discriminant forms, and Nikulin's 2-elementary
invariants.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


INVOLUTIONS = {
    # name: (involution, invariant rank, invariant signature, coinvariant rank, coinvariant named lattice)
    "Nikulin": (lambda: Involutions.I_Nik, 14, (3, 11), 8, lambda: NamedLattices.LmNik),
    "Enriques": (lambda: Involutions.I_En, 10, (1, 9), 12, lambda: NamedLattices.TEn),
    "del Pezzo": (lambda: Involutions.I_dP, 2, (1, 1), 20, lambda: NamedLattices.TdP),
}


def test_the_k3_lattice_and_its_decomposition() -> None:
    k3 = NamedLattices.LK3
    rendered(k3)
    assert k3.module_rank() == cardinal(22)
    assert k3.signature_pair() == signature_pair(3, 19)
    assert k3.is_even()
    assert k3.is_unimodular()
    assert k3 in EvenLattices(ZZ)
    assert k3.discriminant_group().cardinality() == cardinal(1)
    assert k3.summands().cardinality() == cardinal(5)
    assert k3.is_isometric(Lattices(ZZ)("U") ** 3 + Lattices(ZZ)("E8") ** 2)
    assert k3.is_isometric(NamedLattices.U + NamedLattices.U + NamedLattices.U + NamedLattices.E8 + NamedLattices.E8)
    assert not k3.is_isometric(NamedLattices.Mukai)
    assert NamedLattices.Mukai.module_rank() == cardinal(24)
    assert NamedLattices.Mukai.is_isometric(k3 + NamedLattices.U)


@pytest.mark.parametrize("name", sorted(INVOLUTIONS))
def test_a_catalogue_involution_session(name) -> None:
    build, invariant_rank, (positive, negative), coinvariant_rank, coinvariant = INVOLUTIONS[name]
    k3 = NamedLattices.LK3
    involution = build()
    rendered(involution)
    assert involution in k3.O()
    assert involution * involution == k3.O().one()
    assert involution != k3.O().one()

    group = Groups.C(2)
    acted = Lattices(ZZ[group])(k3, lambda g, v: v if g == group.one() else involution(v))
    rendered(acted)
    invariant = acted.invariant_lattice()
    coinvariant_lattice = acted.formed_coinvariants()
    rendered(invariant)
    rendered(coinvariant_lattice)
    assert invariant.module_rank() == cardinal(invariant_rank)
    assert invariant.signature_pair() == signature_pair(positive, negative)
    assert coinvariant_lattice.module_rank() == cardinal(coinvariant_rank)
    assert invariant.module_rank() + coinvariant_lattice.module_rank() == cardinal(22)
    assert invariant.is_even()
    assert coinvariant_lattice.is_even()
    assert coinvariant_lattice.is_isometric(coinvariant())
    assert invariant.discriminant_group().cardinality() == coinvariant_lattice.discriminant_group().cardinality()
    assert invariant.is_p_elementary(2)
    assert coinvariant_lattice.is_p_elementary(2)
    assert acted.character()(group.group_generators()[0]) == invariant_rank - coinvariant_rank
    assert acted.character()(group.one()) == 22

    # Nikulin's (r, a, delta) for the invariant lattice.
    r, a, delta = EvenTwoElementaryLattices(ZZ)(invariant).two_elementary_invariants()
    rendered(EvenTwoElementaryLattices(ZZ)(invariant).two_elementary_invariants())
    assert r == invariant_rank
    assert invariant.discriminant_group().cardinality() == cardinal(2**a)
    assert EvenTwoElementaryLattices(ZZ)(invariant).delta() == delta
    assert nikulin_invariants(r, a, delta) == EvenTwoElementaryLattices(ZZ)(invariant).two_elementary_invariants()


def test_the_catalogue_embeddings_and_their_complements() -> None:
    k3 = NamedLattices.LK3
    for name, source, complement_signature in (
        ("TEn_into_LK3", NamedLattices.TEn, (1, 9)),
        ("TdP_into_LK3", NamedLattices.TdP, (1, 1)),
    ):
        embedding = getattr(Embeddings, name)
        rendered(embedding)
        assert embedding.domain() is source
        assert embedding.codomain() is k3
        assert embedding.is_injective()
        assert embedding.is_primitive()
        complement = embedding.orthogonal_complement()
        rendered(complement)
        assert complement.module_rank() + source.module_rank() == cardinal(22)
        assert complement.signature_pair() == signature_pair(*complement_signature)
        assert complement.is_even()
        assert complement.discriminant_group().cardinality() == source.discriminant_group().cardinality()
        assert complement.discriminant_quadratic_form().is_anti_isometric(source.discriminant_quadratic_form())
    chain = Embeddings.TdP_into_LK3 * Embeddings.TEn_into_TdP
    assert chain.domain() is NamedLattices.TEn
    assert chain.codomain() is k3
    assert chain.is_primitive()


def test_two_elementary_lattices_and_orthogonal_sums() -> None:
    e8_2 = NamedLattices.E8_2
    rendered(e8_2)
    assert e8_2.is_p_elementary(2)
    assert e8_2.discriminant_group().cardinality() == cardinal(256)
    assert EvenTwoElementaryLattices(ZZ)(e8_2).two_elementary_invariants() == nikulin_invariants(8, 8, 0)
    assert e8_2.discriminant_quadratic_form().brown_invariant() == 0
    assert EvenTwoElementaryLattices(ZZ)(NamedLattices.U_2).two_elementary_invariants() == nikulin_invariants(2, 2, 0)
    assert EvenTwoElementaryLattices(ZZ)(NamedLattices.Z_2).two_elementary_invariants() == nikulin_invariants(1, 1, 1)
    sums = two_elementary_orthogonal_sums(signature_pair(1, 9), 10, 0)
    rendered(sums)
    assert sums.cardinality() >= cardinal(1)
    for lattice in sums:
        assert lattice.signature_pair() == signature_pair(1, 9)
        assert lattice.discriminant_group().cardinality() == cardinal(2**10)
        assert lattice.is_isometric(NamedLattices.SEn)
    assert NamedLattices.SEn.is_isometric(NamedLattices.U_2 + NamedLattices.E8_2)
    assert NamedLattices.E10.is_isometric(NamedLattices.U + NamedLattices.E8)
    assert NamedLattices.E10_2.is_isometric(NamedLattices.E10.twist(2))
