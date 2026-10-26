r"""A session with Coxeter diagrams, Coxeter groups and root lattices.

Finite, affine and hyperbolic diagrams, the groups they present, root
lattices with their roots, reflections and orthogonal groups, typed as into
a notebook.
"""

import pytest
from sage.misc.latex import latex

from sage_extensions.all import *  # noqa: F401,F403


def rendered(obj) -> str:
    text = repr(obj)
    assert "object at 0x" not in text
    assert "object at 0x" not in latex(obj)
    return text


FINITE = {
    # Cartan type: (order of the Weyl group, number of roots, Coxeter number, |O(root lattice)|)
    "A2": (["A", 2], 6, 6, 3, 12),
    "A3": (["A", 3], 24, 12, 4, 48),
    "D4": (["D", 4], 192, 24, 6, 1152),
    "E6": (["E", 6], 51840, 72, 12, 103680),
    "E8": (["E", 8], 696729600, 240, 30, 696729600),
}


def test_cartan_type_ingress_accepts_the_owned_integer_emitted_by_the_session() -> None:
    rank = Integer(3)
    scale = Integer(2)

    diagram = CoxeterDiagrams().from_cartan_type(["A", rank])
    rooted = CoxeterDiagrams().from_cartan_type(["A", rank], scale=scale)

    assert diagram.cardinality() == cardinal(rank)
    assert rooted.cardinality() == cardinal(rank)
    assert rooted.is_rooted()


@pytest.mark.parametrize("name", sorted(FINITE))
def test_a_finite_coxeter_session(name) -> None:
    cartan_type, weyl_order, root_count, coxeter_number, isometry_order = FINITE[name]
    diagram = CoxeterDiagrams().from_cartan_type(cartan_type)
    rendered(diagram)
    assert diagram.cardinality() == cardinal(cartan_type[1])
    assert diagram.is_elliptic()
    assert diagram.is_connected()
    assert diagram.connected_components().cardinality() == cardinal(1)
    assert diagram.elliptic_subdiagrams(connected=True).cardinality() >= cardinal(cartan_type[1])
    assert diagram.parabolic_subdiagrams().cardinality() == cardinal(0)
    assert diagram.positive_inertia_index() == cardinal(cartan_type[1])

    weyl = Groups.Coxeter(cartan_type)
    from_matrix = Groups.Coxeter(diagram.coxeter_matrix())
    rendered(weyl)
    assert weyl in FiniteGroups()
    assert weyl.order() == weyl_order
    assert from_matrix.order() == weyl_order
    assert weyl.is_isomorphic_to(from_matrix)
    assert weyl.group_generators().cardinality() == cardinal(cartan_type[1])
    for generator in weyl.group_generators():
        assert generator.order() == 2

    lattice = Lattices(ZZ)(name)
    rendered(lattice)
    assert lattice in RootLattices()
    assert lattice in EvenLattices(ZZ)
    assert lattice.module_rank() == cardinal(cartan_type[1])
    assert lattice.is_definite()
    assert lattice.roots().cardinality() == cardinal(root_count)
    assert lattice.simple_roots().cardinality() == cardinal(cartan_type[1])
    assert lattice.coxeter_number() == coxeter_number
    assert lattice.highest_root().height() == coxeter_number - 1
    assert lattice.O().order() == isometry_order
    reflections = lattice.simple_reflections()
    rendered(reflections)
    assert reflections.cardinality() == cardinal(cartan_type[1])
    generated = lattice.O().subgroup(list(reflections))
    rendered(generated)
    assert generated.order() == weyl_order
    assert generated.is_isomorphic_to(weyl)
    for root in lattice.simple_roots():
        assert root.is_root()
        assert root.is_positive_root()
        assert (-root).is_negative_root()
        assert root.coroot().b(root) == 2 or root.coroot().b(root) == -2
        reflection = lattice.reflection(root)
        assert reflection in lattice.O()
        assert reflection * reflection == lattice.O().one()
        assert reflection(root) == -root
    rooted = CoxeterDiagrams().from_cartan_type(cartan_type, rooted=True)
    assert rooted.is_rooted()
    assert rooted.root_gram_tensor() == lattice.gram_tensor()
    assert lattice.dual_lattice().determinant() * lattice.determinant() == 1


def test_affine_and_hyperbolic_coxeter_sessions() -> None:
    affine = CoxeterDiagrams().from_cartan_type(["A", 2, 1])
    hyperbolic = CoxeterDiagrams().from_coxeter_matrix([[1, 3, 3], [3, 1, 4], [3, 4, 1]])
    ideal = CoxeterDiagrams().from_coxeter_matrix([[1, 3, 4], [3, 1, 4], [4, 4, 1]])
    for diagram in (affine, hyperbolic, ideal):
        rendered(diagram)
        assert diagram.cardinality() == cardinal(3)
        assert diagram.is_connected()
    assert affine.is_parabolic()
    assert affine.zero_inertia_index() == cardinal(1)
    assert hyperbolic.is_hyperbolic()
    assert ideal.is_hyperbolic()
    assert hyperbolic.negative_inertia_index() == 1
    assert hyperbolic.elliptic_subdiagrams(connected=True).cardinality() == cardinal(6)
    assert affine.elliptic_subdiagrams().cardinality() == cardinal(7)
    affine_group = Groups.Coxeter(["A", 2, 1])
    hyperbolic_group = Groups.Coxeter(hyperbolic.coxeter_matrix())
    rendered(affine_group)
    rendered(hyperbolic_group)
    assert affine_group not in FiniteGroups()
    assert hyperbolic_group not in FiniteGroups()
    assert affine_group.group_generators().cardinality() == cardinal(3)
    a, b, c = hyperbolic_group.group_generators()
    assert (a * b).order() == 3
    assert (b * c).order() == 4
    assert (a * c).order() == 3
    hyperbolic_lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    assert hyperbolic_lattice.signature_pair() == signature_pair(1, 3)
    assert not hyperbolic_lattice.is_definite()
    assert hyperbolic_lattice.reflection(hyperbolic_lattice.summand(1).inclusion()(hyperbolic_lattice.summand(1).basis_vector(0))) in hyperbolic_lattice.O()
