r"""A lattice theorist's session: invariants, duals, discriminant forms, sublattices, isometries.

One long session per lattice, typed as into a notebook.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


SESSIONS = {
    # name: (constructor, rank, signature, |discriminant group|, even, definite, |O(L)|, number of roots)
    "U": (lambda: Lattices(ZZ)("U"), 2, (1, 1), 1, True, False, None, None),
    "A2": (lambda: Lattices(ZZ)("A2"), 2, (0, 2), 3, True, True, 12, 6),
    "E8": (lambda: Lattices(ZZ)("E8"), 8, (0, 8), 1, True, True, 696729600, 240),
    "U+U": (lambda: Lattices(ZZ)("U") + Lattices(ZZ)("U"), 4, (2, 2), 1, True, False, None, None),
    "U+A2": (lambda: Lattices(ZZ)("U") + Lattices(ZZ)("A2"), 4, (1, 3), 3, True, False, None, None),
    "ZZ^3": (lambda: Lattices(ZZ)(3), 3, (3, 0), 1, False, True, 48, 12),
    "<2>+<-6>": (lambda: Lattices(ZZ)([[2, 0], [0, -6]]), 2, (1, 1), 12, True, False, None, None),
}


@pytest.mark.parametrize("name", sorted(SESSIONS))
def test_a_lattice_session(name) -> None:
    build, rank, (positive, negative), discriminant_order, even, definite, isometry_order, root_count = SESSIONS[name]

    lattice = build()
    rendered(lattice)
    assert lattice in Lattices(ZZ)
    assert lattice in FinitelyGeneratedFreeModules(ZZ)
    assert lattice.module_rank() == cardinal(rank)
    assert lattice.signature_pair() == signature_pair(positive, negative)
    assert lattice.is_even() == even
    assert (lattice in EvenLattices(ZZ)) == even
    assert lattice.is_definite() == definite
    assert lattice.is_nondegenerate()
    assert lattice in NondegenerateLattices(ZZ)
    assert abs(lattice.determinant()) == discriminant_order
    gram = lattice.gram_tensor()
    rendered(gram)

    # Elements and the form.
    generators = lattice.module_generators()
    rendered(generators)
    assert generators.cardinality() == cardinal(rank)
    e0 = lattice.basis_vector(0)
    v = 2 * e0 - lattice.module_generator(rank - 1)
    rendered(v)
    assert lattice.b(v, v) == v.b(v)
    assert lattice.b(v, e0) == lattice.b(e0, v)
    if even:
        assert lattice.b(v, v) % 2 == 0

    # Dual lattice and discriminant group with its forms.
    dual = lattice.dual_lattice()
    rendered(dual)
    assert dual.module_rank() == cardinal(rank)
    assert dual.determinant() * lattice.determinant() == 1
    assert lattice.dual_module().module_rank() == cardinal(rank)
    discriminant = lattice.discriminant_group()
    rendered(discriminant)
    assert discriminant.cardinality() == cardinal(discriminant_order)
    assert discriminant.O().order() >= 1
    bilinear = lattice.discriminant_bilinear_form()
    rendered(bilinear)
    assert bilinear.cardinality() == cardinal(discriminant_order)
    if even:
        quadratic = lattice.discriminant_quadratic_form()
        rendered(quadratic)
        assert quadratic.cardinality() == cardinal(discriminant_order)
    assert lattice.is_unimodular() == (discriminant_order == 1)

    # Sublattices: the line through v, its orthogonal complement, and saturation.
    line = lattice.subobject_on([v])
    rendered(line)
    assert line.module_rank() == cardinal(1)
    assert line.is_primitive() == (v.div() == 1)
    perpendicular = line.orthogonal_complement()
    rendered(perpendicular)
    assert perpendicular.module_rank() == cardinal(rank - 1)
    assert lattice.b(line.inclusion()(line.basis_vector(0)), perpendicular.inclusion()(perpendicular.basis_vector(0))) == 0
    doubled = lattice.subobject_on([2 * e0])
    assert doubled.module_rank() == cardinal(1)
    assert not doubled.is_saturated()
    assert doubled.saturation().module_rank() == cardinal(1)
    assert doubled.saturation().is_saturated()
    assert doubled.saturation().inclusion().is_injective()

    # Direct sums, twists, and the hyperbolic plane glued on.
    bigger = lattice + Lattices(ZZ)("U")
    rendered(bigger)
    assert bigger.module_rank() == cardinal(rank + 2)
    assert bigger.signature_pair() == signature_pair(positive + 1, negative + 1)
    assert bigger.discriminant_group().cardinality() == cardinal(discriminant_order)
    assert bigger.summands().cardinality() >= cardinal(2)
    twisted = lattice.twist(3)
    rendered(twisted)
    assert twisted.module_rank() == cardinal(rank)
    assert abs(twisted.determinant()) == discriminant_order * 3**rank
    assert twisted.is_even()

    # Roots and isometries of definite lattices.
    if definite:
        roots = lattice.roots()
        rendered(roots)
        assert roots.cardinality() == cardinal(root_count)
        orthogonal = lattice.O()
        rendered(orthogonal)
        assert orthogonal.order() == isometry_order
        assert lattice.Isom(lattice).cardinality() == cardinal(isometry_order)
        assert lattice.is_isometric(lattice.LLL())
        assert lattice.minimum() != 0
        reflection = lattice.reflection(next(iter(roots)))
        assert reflection * reflection == orthogonal.one()
        assert reflection != orthogonal.one()
    else:
        assert lattice.isotropic_line_orbit_representatives().cardinality() >= cardinal(1)
        assert not lattice.is_positive_definite()
        assert not lattice.is_negative_definite()

    # Embeddings of A1 and of U.
    a1 = Lattices(ZZ)("A1")
    embeddings = a1.Emb(lattice)
    rendered(embeddings)
    assert embeddings.cardinality() == lattice.vectors_of_square(-2).cardinality()
    if "U" in name:
        assert Lattices(ZZ)("U").Emb(lattice).cardinality() >= cardinal(1)

    # Genus and local data.
    genus = lattice.genus()
    rendered(genus)
    assert genus.representative().genus() == genus
    assert lattice.is_locally_isometric(lattice, 2)
    assert lattice.level() >= 1
    if even and lattice.is_p_elementary(2):
        invariants = EvenTwoElementaryLattices(ZZ)(lattice).two_elementary_invariants()
        rendered(invariants)

    # Over the rationals and the reals it is a quadratic space.
    rational = lattice.base_change(ZZ.Mor(QQ)(lambda n: QQ(n)))
    rendered(rational)
    assert rational in VectorSpaces(QQ)
    assert rational in Lattices(QQ)
    assert rational.module_rank() == cardinal(rank)
    assert rational.determinant() == QQ(lattice.determinant())
    real = lattice.base_change(ZZ.Mor(RR)(lambda n: RR(n)))
    assert real in Lattices(RR)
    assert real.signature_pair() == signature_pair(positive, negative)

    # As a plain ZZ-module it is free of the same rank, and Hom(L, ZZ) is the dual.
    assert lattice in Modules(ZZ)
    assert lattice.unformed_module().module_rank() == cardinal(rank)
    assert lattice.dual_module() in Modules(ZZ)
    assert lattice.cardinality() == lattice.unformed_module().cardinality()


def test_the_k3_lattice_session() -> None:
    k3 = NamedLattices.LK3
    rendered(k3)
    assert k3.module_rank() == cardinal(22)
    assert k3.signature_pair() == signature_pair(3, 19)
    assert k3.is_even()
    assert k3.is_unimodular()
    assert k3.discriminant_group().cardinality() == cardinal(1)
    assert k3.summands().cardinality() == cardinal(5)
    assert k3.is_isometric(Lattices(ZZ)("U") ** 3 + Lattices(ZZ)("E8") ** 2)
    involution = Involutions.I_Nik
    rendered(involution)
    assert involution * involution == k3.O().one()
    assert involution != k3.O().one()
    embedding = Lattices(ZZ)("U").Emb(k3).an_element()
    rendered(embedding)
    assert embedding.is_injective()
    assert embedding.is_primitive()
    complement = embedding.orthogonal_complement()
    assert complement.module_rank() == cardinal(20)
    assert complement.signature_pair() == signature_pair(2, 18)
    assert complement.is_unimodular()
