r"""Lattice constructions a mathematician expects, over the rings lattices live over.

A lattice here is a free module with a symmetric bilinear form, so the base
ring ranges over the integers, the rationals, the reals, the $p$-adics, finite
fields and rings of integers alike; the claims are the ones a Gram matrix
determines over any of them.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403

LATTICE_RINGS = ["ZZ", "QQ", "RR", "CC", "AA", "QQ_3", "ZZ_3", "GF(3)", "GF(5)", "ZZ[i]", "ZZ[phi]", "QQ[x]", "ZZ_(5)"]

A2_GRAM = [[2, 1], [1, 2]]


@pytest.fixture(params=LATTICE_RINGS, ids=str)
def lattice_ring(request, build):
    if request.param == "GF(3)":
        return GF(3)
    return build(request.param)


def test_a_gram_matrix_builds_a_lattice_over_every_ring(lattice_ring) -> None:
    ring = lattice_ring
    lattice = Lattices(ring)(A2_GRAM)
    e0, e1 = lattice.module_generator(0), lattice.module_generator(1)

    assert lattice in Lattices(ring)
    assert lattice in FiniteRankLattices(ring)
    assert lattice in SymmetricBilinearFormModules(ring)
    assert lattice in FormModules(ring)
    assert lattice in FramedFreeModules(ring)
    assert lattice in FreeModules(ring)
    assert lattice in Modules(ring)
    assert lattice.base_ring() is ring
    assert all(
        lattice.gram_tensor()[row, column].parent() is ring
        for row in range(2)
        for column in range(2)
    )
    assert lattice.module_rank() == cardinal(2)
    assert lattice.b(e0, e1) == ring.one()
    assert lattice.b(e0, e0) == 2 * ring.one()
    assert e0.b(e1) == lattice.b(e1, e0)
    assert lattice.b(e0 + e1, e0 + e1) == 6 * ring.one()
    assert lattice.determinant() == 3 * ring.one()
    assert lattice.is_even()
    assert lattice in EvenLattices(ring)


def test_nondegeneracy_is_decided_by_the_base_ring(lattice_ring) -> None:
    r"""$\det = 3$, so the form degenerates exactly where $3 = 0$."""
    ring = lattice_ring
    lattice = Lattices(ring)(A2_GRAM)
    expected = 3 * ring.one() != ring.zero()

    assert lattice.is_nondegenerate() == expected
    assert (lattice in NondegenerateLattices(ring)) == expected
    assert lattice.radical().module_rank() == cardinal(0 if expected else 1)


def test_dual_lattice_over_every_ring(lattice_ring) -> None:
    ring = lattice_ring
    lattice = Lattices(ring)(A2_GRAM)
    if 3 * ring.one() == ring.zero():
        return
    dual = lattice.dual_lattice()
    assert dual.module_rank() == cardinal(2)
    assert dual.determinant() * lattice.determinant() == lattice.determinant().parent().one()
    assert lattice.dual_module().module_rank() == cardinal(2)


@pytest.mark.parametrize("name", ["ZZ", "ZZ[i]", "ZZ[phi]", "ZZ_3", "ZZ_(5)", "QQ[x]", "QQ", "GF(5)"])
def test_discriminant_group_has_the_order_of_the_determinant(build, name) -> None:
    r"""$A_L = L^\#/L \cong R^2/GR^2$ has order $|R/3R|$ when $G$ is the $A_2$ Gram matrix."""
    ring = build(name)
    lattice = Lattices(ring)(A2_GRAM)
    assert lattice.discriminant_group().cardinality() == ring.quotient_ring(ring.ideal(ring(3))).cardinality()


def test_direct_sums_and_twists(lattice_ring) -> None:
    ring = lattice_ring
    lattice = Lattices(ring)(A2_GRAM)
    double = lattice + lattice
    twisted = lattice.twist(2)

    assert double in Lattices(ring)
    assert double.module_rank() == cardinal(4)
    assert double.determinant() == 9 * ring.one()
    assert double.summands().cardinality() == cardinal(2)
    assert twisted.module_rank() == cardinal(2)
    assert twisted.determinant() == 12 * ring.one()
    assert twisted.b(twisted.module_generator(0), twisted.module_generator(1)) == 2 * ring.one()


def test_named_gram_tensors_over_every_ring(lattice_ring) -> None:
    ring = lattice_ring
    plane = Lattices(ring)("U")
    e8 = Lattices(ring)("E8")

    assert plane.module_rank() == cardinal(2)
    assert plane.determinant() == -ring.one()
    assert plane.b(plane.module_generator(0), plane.module_generator(0)) == ring.zero()
    assert e8.module_rank() == cardinal(8)
    assert e8.determinant() == ring.one()
    assert e8.is_unimodular() == (ring.one() != ring.zero())
    assert e8.is_even()


def test_euclidean_lattice_of_a_given_rank(lattice_ring) -> None:
    ring = lattice_ring
    cube = Lattices(ring)(3)
    assert cube.module_rank() == cardinal(3)
    assert cube.determinant() == ring.one()
    assert cube.is_unimodular()
    assert not cube.is_even()


@pytest.mark.parametrize("name", ["ZZ", "QQ", "RR", "AA", "ZZ_(5)"])
def test_signature_over_an_ordered_ring(build, name) -> None:
    ring = build(name)
    assert Lattices(ring)(A2_GRAM).signature_pair() == signature_pair(2, 0)
    assert Lattices(ring)("U").signature_pair() == signature_pair(1, 1)
    assert Lattices(ring)([[-2, 1], [1, -2]]).signature_pair() == signature_pair(0, 2)
    assert Lattices(ring)(A2_GRAM).is_positive_definite()
    assert Lattices(ring)(A2_GRAM).is_definite()
    assert not Lattices(ring)("U").is_definite()


# ---------------------------------------------------------------------------
# Integral lattices: roots, isometries, embeddings, invariants.
# ---------------------------------------------------------------------------


def test_root_lattices_over_the_integers() -> None:
    a2 = Lattices(ZZ)("A2")
    e8 = Lattices(ZZ)("E8")

    assert a2 in RootLattices()
    assert a2.roots().cardinality() == cardinal(6)
    assert a2.O().order() == 12
    assert a2.Aut().cardinality() == cardinal(12)
    assert a2.discriminant_group().cardinality() == cardinal(3)
    assert e8.roots().cardinality() == cardinal(240)
    assert e8.discriminant_group().cardinality() == cardinal(1)
    assert e8.O().order() == 696729600
    assert e8.minimum() == -2 or e8.minimum() == 2


def test_definite_lattice_invariants() -> None:
    a2 = Lattices(ZZ)(A2_GRAM)
    assert a2.minimum() == 2
    assert a2.shortest_vectors().cardinality() == cardinal(6)
    assert a2.kissing_number() == 6
    assert a2.vectors_of_square(2).cardinality() == cardinal(6)
    assert a2.vectors_of_square(6).cardinality() == cardinal(6)
    assert a2.LLL().determinant() == 3
    assert a2.is_isometric(a2.LLL())


def test_sublattices_and_orthogonal_complements() -> None:
    a2 = Lattices(ZZ)(A2_GRAM)
    e0, e1 = a2.module_generator(0), a2.module_generator(1)
    line = a2.subobject_on([e0])
    complement = line.orthogonal_complement()
    doubled = a2.subobject_on([2 * e0, e1])

    assert line.module_rank() == cardinal(1)
    assert complement.module_rank() == cardinal(1)
    assert complement.inclusion().codomain() is a2
    assert a2.b(line.inclusion()(line.module_generator(0)), complement.inclusion()(complement.module_generator(0))) == 0
    assert doubled.index() == 2
    assert not doubled.is_saturated()
    assert doubled.saturation() == a2.subobject_on([e0, e1])
    assert line.is_primitive()
    assert not doubled.is_primitive()


def test_isometries_and_embeddings_are_counted() -> None:
    a1 = Lattices(ZZ)("A1")
    a2 = Lattices(ZZ)("A2")
    assert a2.Isom(a2).cardinality() == cardinal(12)
    assert a1.Emb(a2).cardinality() == cardinal(6)
    assert a1.Emb(Lattices(ZZ)("E8")).cardinality() == cardinal(240)
    assert a2.Isom(Lattices(ZZ)("A1") + Lattices(ZZ)("A1")).cardinality() == cardinal(0)
    assert a2.is_isometric(a2)
    assert not a2.is_isometric(Lattices(ZZ)("A1") + Lattices(ZZ)("A1"))


def test_named_catalogue_lattices_have_their_invariants() -> None:
    assert NamedLattices.U.signature_pair() == signature_pair(1, 1)
    assert NamedLattices.U.is_unimodular()
    assert NamedLattices.E8.discriminant() == 1
    assert NamedLattices.E8_2.discriminant_group().cardinality() == cardinal(256)
    assert NamedLattices.E8_2.is_p_elementary(2)
    assert NamedLattices.LK3.module_rank() == cardinal(22)
    assert NamedLattices.LK3.signature_pair() == signature_pair(3, 19)
    assert NamedLattices.LK3.is_unimodular()
    assert NamedLattices.LK3.is_even()
    assert NamedLattices.LK3.discriminant_group().cardinality() == cardinal(1)
    assert NamedLattices.TEn.discriminant_group().cardinality() == cardinal(1024)


def test_discriminant_forms_of_integral_lattices() -> None:
    a2 = Lattices(ZZ)("A2")
    form = a2.discriminant_quadratic_form()
    bilinear = a2.discriminant_bilinear_form()
    generator = form.module_generator(0)
    assert form.cardinality() == cardinal(3)
    assert bilinear.cardinality() == cardinal(3)
    assert generator.q() == form.value_module()(QQ(4) / 3)
    assert form.O().order() == 2
    assert a2.discriminant_representation().domain() is a2.O()
    assert a2.discriminant_representation_is_surjective()


def test_genus_and_local_isometry() -> None:
    a2 = Lattices(ZZ)("A2")
    e8 = Lattices(ZZ)("E8")
    assert a2.genus() == a2.LLL().genus()
    assert a2.is_locally_isometric(a2, 2)
    assert a2.is_locally_isometric(a2, 3)
    assert e8.genus().representative().is_isometric(e8)
    assert a2.level() == 3
    assert e8.level() == 1


def test_lattices_over_the_rationals_and_reals_have_no_integral_structure_but_the_form() -> None:
    rational = Lattices(QQ)([[QQ(1) / QQ(2), 0], [0, 3]])
    assert rational.module_rank() == cardinal(2)
    assert rational.determinant() == QQ(3) / QQ(2)
    assert rational.is_nondegenerate()
    assert rational.dual_lattice().determinant() == QQ(2) / QQ(3)
    assert rational.signature_pair() == signature_pair(2, 0)
