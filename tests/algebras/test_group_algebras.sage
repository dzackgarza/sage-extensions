from sage_extensions.all import *  # noqa: F401,F403


def test_regular_representation_has_a_rank_one_group_algebra_basis_isomorphism() -> None:
    r"""R[G] is free of rank one over itself, independently of its R-basis.

    The two coefficient generators of Z[C2] are not a rank-two Z[C2]-basis.
    A basis isomorphism compares the generic matrix Mor with an equivariant
    endomorphism without discarding the coefficient-module presentation.
    """
    from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing

    group = Groups.C(2)
    algebra = ZZ[group]
    framing = algebra.regular_representation_basis_isomorphism()
    free = framing.forward().domain()
    acted = framing.forward().codomain()
    ordinary = OwnedCategoryOverBaseRing.__classcall__(Modules, algebra)
    assert free.module_rank() == 1
    assert acted.module_generating_set().cardinality() == 1
    assert acted.unformed_module().module_generating_set().cardinality() == 2
    from sage_extensions.categories.modules.framed.framed_free_modules import FramedFreeModules
    assert acted in FramedFreeModules(algebra)
    assert acted.module_rank() == 1
    assert acted.coefficient_module_rank() == 2
    assert acted.framing_morphism().domain() is acted.framing_source()
    assert acted._selected_relation_morphism() is None
    assert acted.unformed_module() is algebra
    assert all(
        (framing.forward() * framing.inverse())(acted.module_generator(label))
        == acted.module_generator(label)
        for label in acted.module_generating_set()
    )
    assert all(
        (framing.inverse() * framing.forward())(free.module_generator(label))
        == free.module_generator(label)
        for label in free.module_generating_set()
    )
    matrices = ordinary.Mor(free, free)
    assert matrices in MatrixSpaces(algebra)
    acted_matrices = ordinary.Mor(acted, acted)
    assert acted_matrices in MatrixSpaces(algebra)
    assert acted_matrices in MatrixEndomorphismSpaces(algebra)
    assert acted_matrices.domain() is acted and acted_matrices.codomain() is acted
    equivariant_identity = acted.Mor(acted)(
        framing.forward() * matrices.identity() * framing.inverse()
    )
    assert equivariant_identity.domain() is acted
    assert equivariant_identity.codomain() is acted
    assert all(
        equivariant_identity(acted.module_generator(label)) == acted.module_generator(label)
        for label in acted.module_generating_set()
    )

    # The nonidentity group element gives right multiplication on the left
    # regular module.  Its matrix on the free rank-one source is one entry
    # in R[G], rather than a 2-by-2 R[G]-matrix on the coefficient generators.
    (basis,) = tuple(free.module_generating_set())
    nonidentity = next(g for g in group if g != group.one())
    group_element = algebra.module_generator(nonidentity)
    matrix_arrow = matrices({
        basis: free.scalar_multiple(group_element, free.module_generator(basis))
    })
    equivariant = acted.Mor(acted)(
        framing.forward() * matrix_arrow * framing.inverse()
    )
    assert equivariant.domain() is acted and equivariant.codomain() is acted
    assert equivariant(acted(algebra.one())) == acted(group_element)
    assert equivariant * equivariant == equivariant_identity


def test_the_group_algebra_functor_extends_a_subgroup_inclusion_linearly() -> None:
    symmetric = Groups.S(3)
    rotation = symmetric.group_generators()[0]
    cyclic = symmetric.subgroup([rotation])
    functor = Groups().group_algebra(QQ)

    inclusion = functor(cyclic.inclusion())

    assert inclusion.domain() is QQ[cyclic]
    assert inclusion.codomain() is QQ[symmetric]
    h = cyclic(rotation)
    assert inclusion(QQ[cyclic](h) + 2 * QQ[cyclic](h * h)) == QQ[symmetric](
        rotation
    ) + 2 * QQ[symmetric](rotation * rotation)


def test_the_group_inclusion_lands_in_the_units() -> None:
    symmetric = Groups.S(3)
    algebra = QQ[symmetric]
    inclusion = algebra.group_inclusion()
    rotation = symmetric.group_generators()[0]
    transposition = symmetric((1, 2))

    assert inclusion(rotation) * inclusion(rotation.inverse()) == algebra.one()
    assert inclusion(rotation * transposition) == inclusion(rotation) * inclusion(transposition)
    assert inclusion(rotation * transposition) != inclusion(transposition) * inclusion(rotation)


def test_group_algebra_module_framing_is_not_an_algebra_framing() -> None:
    group_algebra = QQ[Groups.S(3)]
    free_algebra = QQ.free_module(("x",)).tensor_algebra()

    assert group_algebra.is_framed_module()
    assert not group_algebra.is_framed_algebra()
    assert free_algebra.is_framed_algebra()


def test_the_augmentation_over_the_integers_lands_in_the_session_integers() -> None:
    symmetric = Groups.S(3)
    algebra = ZZ[symmetric]
    augmentation = algebra.augmentation()

    assert augmentation.codomain() is ZZ
    assert algebra(ZZ(2)) == ZZ(2) * algebra.one()
    assert augmentation(sum(algebra(g) for g in symmetric)) == 6
    assert augmentation(algebra(symmetric((1, 2))) - algebra.one()) == 0


def test_maschke_decides_semisimplicity_by_the_group_order() -> None:
    symmetric = Groups.S(3)

    assert GF(5)[symmetric].is_semisimple()
    assert not GF(3)[symmetric].is_semisimple()
    assert not ZZ[Groups.C(2)].is_semisimple()


def test_the_centre_of_the_symmetric_group_algebra_counts_partitions() -> None:
    assert QQ[Groups.S(4)].center().dimension() == 5
    assert QQ[Groups.S(4)].center().dimension() == Groups.S(4).conjugacy_classes_representatives().cardinality()
