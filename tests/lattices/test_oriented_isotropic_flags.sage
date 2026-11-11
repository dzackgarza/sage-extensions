r"""Oriented primitive isotropic sublattices and flags.

The Levi factor of the parabolic of the maximal null plane I in 2U is
GL(I), which contains determinant -1. So the two orientations of I are
equivalent and the oriented stabilizer has index two in P_I.
"""

from sage_extensions.all import *


def test_oriented_maximal_null_plane_has_one_class_and_index_two_stabilizer():
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic
    group = ambient.O()
    assert group.oriented_isotropic_orbit_representatives(FlagType((2,))).cardinality() == cardinal(1)
    e1, f1, e2, f2 = tuple(ambient.module_generators())
    positive = OrientedIsotropicFlag(ambient, (e1, e2))
    negative = OrientedIsotropicFlag(ambient, (e2, e1))
    witness = group.oriented_isotropic_equivalence_witness(positive, negative)
    assert witness is not None
    assert all(ambient.b(witness(x), witness(y)) == ambient.b(x, y) for x in (e1, f1, e2, f2) for y in (e1, f1, e2, f2))
    plane = ambient.primitive_isotropic_subobject(e1, e2)
    assert plane.inclusion().is_in_image(witness(e1)) and plane.inclusion().is_in_image(witness(e2))
    swap = ambient.Aut()(dict(zip(tuple(ambient.module_generating_set()), (e2, f2, e1, f1), strict=True)))
    oriented = tuple(group.oriented_isotropic_stabilizer_generators(positive))
    assert all(plane.inclusion().is_in_image(element(point)) for element in oriented for point in (e1, e2))

    def determinant(element):
        coordinates = tuple(plane.inclusion().lift(element(point)).to_vector() for point in (e1, e2))
        labels = tuple(plane.inclusion().domain().module_generating_set())
        return coordinates[0](labels[0])*coordinates[1](labels[1]) - coordinates[0](labels[1])*coordinates[1](labels[0])

    assert determinant(swap) == -1
    assert all(determinant(element) == 1 for element in oriented)


def test_oriented_complete_flag_in_three_hyperbolic_planes_has_one_class():
    r"""Complete null flags of 3U form one O(3U)-class: hyperbolic completion gives an
    adapted basis e1, f1, e2, f2, e3, f3. The Levi diag(s1, s2, s3) on e1, e2, e3,
    extended by the same signs on f1, f2, f3, stabilizes the flag and acts on the
    graded pieces by (s1, s2, s3), so every orientation is attained and the oriented
    flags form one class. The oriented stabilizer is the kernel of the graded sign map.
    """
    hyperbolic = Lattices(ZZ)("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    group = ambient.O()
    complete = FlagType.complete(3)
    assert group.oriented_isotropic_orbit_representatives(complete).cardinality() == cardinal(1)
    e1, f1, e2, f2, e3, f3 = tuple(ambient.module_generators())
    basis = (e1, f1, e2, f2, e3, f3)
    positive = OrientedIsotropicFlag(ambient, (e1, e2, e3), flag_type=complete)
    reversed_first = OrientedIsotropicFlag(ambient, (-e1, e2, e3), flag_type=complete)
    witness = group.oriented_isotropic_equivalence_witness(positive, reversed_first)
    assert witness is not None
    assert all(ambient.b(witness(x), witness(y)) == ambient.b(x, y) for x in basis for y in basis)
    assert witness(e1) == -e1
    line = ambient.primitive_isotropic_subobject(e1)
    plane = ambient.primitive_isotropic_subobject(e1, e2)
    assert line.inclusion().is_in_image(witness(e2) - e2)
    assert plane.inclusion().is_in_image(witness(e3) - e3)
    oriented = tuple(group.oriented_isotropic_stabilizer_generators(positive))
    for element in oriented:
        assert element(e1) == e1
        assert line.inclusion().is_in_image(element(e2) - e2)
        assert plane.inclusion().is_in_image(element(e3) - e3)


def _apex(category, isomorphism):
    r"""The component of a marked isomorphism on the apex ``L``."""
    return isomorphism.forward().component(tuple(category.domain_category().objects())[-1])


def test_marked_oriented_maximal_null_plane_of_two_u_has_one_class_and_index_two_stabilizer():
    r"""The determinant ``P_I -> GL(I) -> {+-1}`` is onto, since the swap of the two
    hyperbolic summands lies in ``P_I`` and has determinant -1 on ``I``. Its kernel is the
    automorphism group of the oriented plane, of index two in ``P_I``, and both
    orientations of ``I`` form one class.
    """
    lattices = Lattices(ZZ)
    hyperbolic = lattices("U")
    ambient = hyperbolic + hyperbolic
    category = OrientedIsotropicFlags(lattices, 1)
    classes = category.primitive_marking_classes(lattices([[0, 0], [0, 0]]), ambient)
    assert classes.cardinality() == cardinal(1)
    e1, f1, e2, f2 = tuple(ambient.module_generators())
    basis = (e1, f1, e2, f2)
    plane = ambient.primitive_isotropic_subobject(e1, e2)
    labels = tuple(plane.inclusion().domain().module_generating_set())

    def determinant(element):
        coordinates = tuple(plane.inclusion().lift(element(point)).to_vector() for point in (e1, e2))
        return coordinates[0](labels[0])*coordinates[1](labels[1]) - coordinates[0](labels[1])*coordinates[1](labels[0])

    positive = category(OrientedIsotropicFlag(ambient, (e1, e2)))
    negative = category(OrientedIsotropicFlag(ambient, (e2, e1)))
    homset = category.Core().Mor(positive, negative)
    assert homset.is_empty() is False
    witness = _apex(category, homset.an_element())
    assert all(ambient.b(witness(x), witness(y)) == ambient.b(x, y) for x in basis for y in basis)
    assert all(plane.inclusion().is_in_image(witness(point)) for point in (e1, e2))
    # e1 ^ e2 goes to a positive multiple of e2 ^ e1, so the determinant in the basis (e1, e2) is -1.
    assert determinant(witness) == -1
    generators = tuple(_apex(category, element) for element in category.Core().Mor(positive, positive).group_generators())
    assert all(plane.inclusion().is_in_image(element(point)) for element in generators for point in (e1, e2))
    assert all(determinant(element) == 1 for element in generators)
    swap = ambient.Aut()(dict(zip(tuple(ambient.module_generating_set()), (e2, f2, e1, f1), strict=True)))
    assert swap in ambient.O().setwise_stabilizer(plane.inclusion())
    assert determinant(swap) == -1
    assert swap not in category.apex_stabilizer(positive)
    assert ambient.O().split_orbit(positive, ambient.O()).cardinality() == cardinal(1)


def test_marked_oriented_complete_flags_of_three_u_form_one_class():
    r"""The Levi diag(s1, s2, s3) on e1, e2, e3, with the same signs on f1, f2, f3,
    stabilizes the coordinate complete flag of 3U and acts on its graded pieces by
    (s1, s2, s3). Every orientation is attained, so the oriented complete flags form
    one class, and an oriented automorphism acts trivially on each graded piece.
    """
    lattices = Lattices(ZZ)
    hyperbolic = lattices("U")
    ambient = hyperbolic + hyperbolic + hyperbolic
    category = OrientedIsotropicFlags(lattices, 3)
    shape = lattices([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    shape_basis = tuple(shape.module_generators())
    shape_plane = shape.primitive_isotropic_subobject(*shape_basis[:2])
    shape_line = shape_plane.inclusion().domain().primitive_isotropic_subobject(shape_plane.inclusion().lift(shape_basis[0]))
    source = Cat().Mor(FiniteOrdinalCategory(3), lattices)((shape_line.inclusion(), shape_plane.inclusion()))
    assert category.primitive_marking_classes(source, ambient).cardinality() == cardinal(1)
    e1, f1, e2, f2, e3, f3 = tuple(ambient.module_generators())
    basis = (e1, f1, e2, f2, e3, f3)
    complete = FlagType.complete(3)
    positive = category(OrientedIsotropicFlag(ambient, (e1, e2, e3), flag_type=complete))
    reversed_first = category(OrientedIsotropicFlag(ambient, (-e1, e2, e3), flag_type=complete))
    line = ambient.primitive_isotropic_subobject(e1)
    plane = ambient.primitive_isotropic_subobject(e1, e2)
    homset = category.Core().Mor(positive, reversed_first)
    assert homset.is_empty() is False
    witness = _apex(category, homset.an_element())
    assert all(ambient.b(witness(x), witness(y)) == ambient.b(x, y) for x in basis for y in basis)
    # Each graded generator goes to the target's: e1 to -e1, e2 to e2 mod I_1, e3 to e3 mod I_2.
    assert witness(e1) == -e1
    assert line.inclusion().is_in_image(witness(e2) - e2)
    assert plane.inclusion().is_in_image(witness(e3) - e3)
    generators = tuple(_apex(category, element) for element in category.Core().Mor(positive, positive).group_generators())
    for element in generators:
        assert element(e1) == e1
        assert line.inclusion().is_in_image(element(e2) - e2)
        assert plane.inclusion().is_in_image(element(e3) - e3)
    assert ambient.O().split_orbit(positive, ambient.O()).cardinality() == cardinal(1)


def test_oriented_mor_is_the_orientation_preserving_natural_transformations():
    r"""``-1`` on the first summand U of 2U fixes the null plane ``<e1, e2>`` and acts on it
    with determinant -1, so its natural transformation lies in the ``Fun([1], Lattices)``
    Mor of the plane but not in the oriented Mor. The chosen element of the oriented Mor
    from ``e1 ^ e2`` to ``e2 ^ e1`` has determinant -1 in the basis (e1, e2).
    """
    lattices = Lattices(ZZ)
    hyperbolic = lattices("U")
    ambient = hyperbolic + hyperbolic
    category = OrientedIsotropicFlags(lattices, 1)
    e1, f1, e2, f2 = tuple(ambient.module_generators())
    plane = ambient.primitive_isotropic_subobject(e1, e2)
    labels = tuple(plane.inclusion().domain().module_generating_set())

    def determinant(element):
        coordinates = tuple(plane.inclusion().lift(element(point)).to_vector() for point in (e1, e2))
        return coordinates[0](labels[0])*coordinates[1](labels[1]) - coordinates[0](labels[1])*coordinates[1](labels[0])

    positive = category(OrientedIsotropicFlag(ambient, (e1, e2)))
    negative = category(OrientedIsotropicFlag(ambient, (e2, e1)))
    reflection = ambient.Aut()(dict(zip(tuple(ambient.module_generating_set()), (-e1, -f1, e2, f2), strict=True)))
    reversing = category._natural_transformation_from_apex(positive, positive, reflection)
    identity = category._natural_transformation_from_apex(positive, positive, ambient.Aut().one())
    endomorphisms = category.Mor(positive, positive)
    assert reversing not in endomorphisms
    assert identity in endomorphisms
    chosen = category.Mor(positive, negative).an_element()
    assert chosen in category.Mor(positive, negative)
    assert determinant(chosen.component(tuple(category.domain_category().objects())[-1])) == -1


def test_oriented_isometry_between_two_presentations_of_three_u():
    r"""The target presents 3U with e0 replaced by e0 + f0, so its form has b(f0, f0) = 2 and
    f0 - f1 is null. Both lattices are 3U, whose complete null flags form one class with every
    graded sign attained, so the oriented flags (e0, e2, e4) and (f0 - f1, f2, -f4) are isomorphic.
    """
    lattices = Lattices(ZZ)
    gram = [[int(i // 2 == j // 2 and i != j) for j in range(6)] for i in range(6)]
    source = lattices(gram)
    target_gram = [row[:] for row in gram]
    target_gram[0][0] = 2
    target = lattices(target_gram)
    e = tuple(source.module_generators())
    f = tuple(target.module_generators())
    complete = FlagType.complete(3)
    category = OrientedIsotropicFlags(lattices, 3)
    first = category(OrientedIsotropicFlag(source, (e[0], e[2], e[4]), flag_type=complete))
    target_basis = (f[0] - f[1], f[2], -f[4])
    second = category(OrientedIsotropicFlag(target, target_basis, flag_type=complete))
    homset = category.Core().Mor(first, second)
    assert homset.is_empty() is False
    apex = _apex(category, homset.an_element())
    assert apex.domain() is source and apex.codomain() is target
    assert all(target.b(apex(x), apex(y)) == source.b(x, y) for x in e for y in e)
    line = target.primitive_isotropic_subobject(target_basis[0])
    plane = target.primitive_isotropic_subobject(*target_basis[:2])
    assert apex(e[0]) == target_basis[0]
    assert line.inclusion().is_in_image(apex(e[2]) - target_basis[1])
    assert plane.inclusion().is_in_image(apex(e[4]) - target_basis[2])
