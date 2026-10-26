from sage_extensions.all import *


def e8():
    return Lattices(ZZ)("E8")


def test_the_catalogue_entry_agrees() -> None:
    assert e8() == NamedLattices.E8


def test_the_root_system_construction_agrees() -> None:
    assert e8().is_isometric(Lattices(ZZ)(CartanType(["E", 8])))


def test_the_categories_of_e8() -> None:
    lattice = e8()
    assert lattice in Lattices(ZZ)
    assert lattice in EvenLattices(ZZ)
    assert lattice in NondegenerateLattices(ZZ)
    assert lattice in RootLattices()
    assert lattice in Modules(ZZ)


def test_the_invariants_of_e8() -> None:
    r"""$E_8$ is the even unimodular lattice of rank $8$, negative definite here, with $240$ roots and
    $|O(E_8)| = |W(E_8)| = 696729600$ (Conway--Sloane, Ch. 4, §8.1)."""
    lattice = e8()
    assert lattice.module_rank() == 8
    assert lattice.determinant() == 1
    assert lattice.signature_pair() == signature_pair(0, 8)
    assert lattice.is_even()
    assert lattice.is_unimodular()
    assert lattice.discriminant_group().cardinality() == 1
    assert lattice.roots().cardinality() == 240
    assert lattice.O().order() == 696729600
    assert Lattices(ZZ)("A1").Emb(lattice).cardinality() == 240


def test_the_twist_by_two() -> None:
    r"""$E_8(2)$ has $\det = 2^8$ and $A = (\mathbb Z/2)^8$: Nikulin invariants $(r, a, \delta) = (8, 8, 0)$."""
    twisted = e8().twist(2)
    assert twisted.determinant() == 256
    assert twisted.discriminant_group().cardinality() == 256
    assert twisted.is_p_elementary(2)
    assert EvenTwoElementaryLattices(ZZ)(twisted).two_elementary_invariants() == nikulin_invariants(8, 8, 0)
    assert twisted.is_isometric(NamedLattices.E8_2)


def test_a_lattice_subobject_has_the_restricted_form() -> None:
    r"""For $i: N \hookrightarrow L$, $b_N = i^*b_L$; $N = \langle 2e_0\rangle$ has $b_N(g, g) = b(2e_0, 2e_0) = -8$."""
    lattice = e8()
    e0 = lattice.module_generator(0)
    subobject = lattice.subobject_on([2 * e0])
    generator = subobject.module_generator(0)
    image = subobject.inclusion()(generator)
    assert subobject.module_rank() == 1
    assert subobject.inclusion().codomain() is lattice
    assert subobject.inclusion().is_injective()
    assert generator.b(generator) == -8
    assert generator.b(generator) == image.b(image)
    assert not subobject.is_saturated()
    assert subobject.saturation() == lattice.subobject_on([e0])


def test_the_sum_of_two_subobjects() -> None:
    lattice = e8()
    e0, e1 = lattice.module_generator(0), lattice.module_generator(1)
    total = lattice.subobject_on([2 * e0]).sum(lattice.subobject_on([3 * e1]))
    assert total.module_rank() == 2
    assert total == lattice.subobject_on([2 * e0, 3 * e1])


def test_the_intersection_of_two_subobjects() -> None:
    r"""$\langle 2e_0, 2e_1\rangle \cap \langle 3e_0, 3e_1\rangle = \langle 6e_0, 6e_1\rangle$."""
    lattice = e8()
    e0, e1 = lattice.module_generator(0), lattice.module_generator(1)
    meet = lattice.subobject_on([2 * e0, 2 * e1]).intersection(lattice.subobject_on([3 * e0, 3 * e1]))
    assert meet.module_rank() == 2
    assert meet == lattice.subobject_on([6 * e0, 6 * e1])


def test_e8_has_one_endomorphism_category() -> None:
    lattice = e8()
    endomorphisms = lattice.Mor(lattice)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert lattice.Mor(lattice) is endomorphisms
    assert identity * identity == identity
