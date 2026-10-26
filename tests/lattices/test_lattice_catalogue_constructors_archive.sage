r"""Archive specimens for the standard integral lattice catalogue constructors.

These are the source-backed constructors from
``archives/preamble/categories/modules/framed/formed/lattices.sage`` that are
independent of the still-unresolved Leech-lattice realization.  Each result is
built through the live owned lattice category and its orthogonal sums.
"""

from sage_extensions.all import *

ARCHIVE_RECONCILIATION = {
    "archive_module": "preamble/categories/modules/framed/formed/lattices.sage",
    "live_owner": "sage_extensions/categories/lattices.py",
    "owner_overrides": {
        "Lattices.namespace": "sage_extensions/all.py",
        "Lattices.install": "sage_extensions/all.py",
    },
    "disposition": "reconciled-live-owner",
}


def test_odd_and_even_unimodular_signature_constructors_keep_their_forms() -> None:
    odd = Lattices.IPQ(2, 1)
    even = Lattices.IIPQ(1, 9)
    odd_signature = odd.signature_pair()
    even_signature = even.signature_pair()

    assert odd_signature.first() == 2
    assert odd_signature.second() == 1
    assert abs(odd.gram_matrix().determinant()) == 1
    assert not odd.is_even()

    assert even_signature.first() == 1
    assert even_signature.second() == 9
    assert abs(even.gram_matrix().determinant()) == 1
    assert even.is_even()


def test_polarized_k3_complement_and_rank_one_constructor_have_archived_grams() -> None:
    line = Lattices.rank_one_negative(3)
    complement = Lattices.LK3_2d(2)
    signature = complement.signature_pair()

    assert line.gram_matrix()[0, 0] == ZZ(-6)
    assert complement.module_rank() == 21
    assert signature.first() == 2
    assert signature.second() == 19
    assert abs(complement.gram_matrix().determinant()) == 4


def test_hyperkaehler_bbf_lattices_have_the_standard_ranks_and_signatures() -> None:
    expected = {
        ("K3", 2): (23, (3, 20)),
        ("Kum", 2): (7, (3, 4)),
        ("OG6", 2): (8, (3, 5)),
        ("OG10", 2): (24, (3, 21)),
    }

    for (deformation_type, n), (rank, signature) in expected.items():
        lattice = Lattices.hyperkaehler_lattice(deformation_type, n)
        actual_signature = lattice.signature_pair()
        assert lattice.module_rank() == rank
        assert actual_signature.first() == signature[0]
        assert actual_signature.second() == signature[1]
        assert lattice.base_ring() is ZZ


def test_leech_lattice_uses_the_rootless_even_unimodular_archive_contract() -> None:
    leech = Lattices.leech_lattice()
    signature = leech.signature_pair()

    assert leech.module_rank() == 24
    assert signature.first() == 0
    assert signature.second() == 24
    assert leech.is_even()
    assert abs(leech.gram_matrix().determinant()) == 1
    # Rootlessness is the minimum-four condition; asking for all roots would
    # enumerate vectors in rank 24 merely to discover that there are none.
    assert abs(leech.minimum()) == 4


def test_non_simply_laced_root_lattices_use_the_integral_cartan_symmetrizer() -> None:
    f4 = Lattices.root_lattice("F", 4)
    g2 = Lattices.root_lattice("G", 2)

    assert f4.module_rank() == 4
    assert f4.gram_matrix().determinant() == ZZ(4)
    f4_roots = f4.simple_roots()
    assert f4_roots.cardinality() == 4
    assert abs(f4.b(f4_roots[0], f4_roots[0])) == 4
    assert abs(f4.b(f4_roots[1], f4_roots[1])) == 4
    assert abs(f4.b(f4_roots[2], f4_roots[2])) == 2
    assert abs(f4.b(f4_roots[3], f4_roots[3])) == 2

    assert g2.module_rank() == 2
    assert g2.gram_matrix().determinant() == ZZ(3)
    g2_roots = g2.simple_roots()
    assert g2_roots.cardinality() == 2
    assert abs(g2.b(g2_roots[0], g2_roots[0])) == 6
    assert abs(g2.b(g2_roots[1], g2_roots[1])) == 2
