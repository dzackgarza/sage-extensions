r"""Constructions a mathematician spells without looking anything up.

Every test here writes a standard construction in the spelling a working
mathematician would type first, whether or not the session has a name for
it.  The session's names are brought in by the star import, so a spelling
the session lacks fails as an undefined name inside its own test, and that
failure is the finding: the vocabulary of the universe is missing a word.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Group algebras.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["QQ", "ZZ", "GF(2)", "GF(5)"])
def test_the_group_algebra_of_the_symmetric_group(build, name) -> None:
    ring = build(name)
    group = Groups.S(3)
    algebra = Groups().group_algebra(ring)(group)
    assert algebra in Algebras(ring)
    assert algebra.module_rank() == cardinal(6)
    assert algebra not in Algebras(ring).Associative().Unital().Commutative()
    assert algebra.center().module_rank() == cardinal(3)
    assert algebra.augmentation()(algebra(group.one())) == ring.one()
    assert algebra(group.group_generators()[0]) * algebra(group.group_generators()[0].inverse()) == algebra.one()


def test_the_group_algebra_by_subscript_notation() -> None:
    group = Groups.C(4)
    algebra = QQ[group]
    assert algebra in Algebras(QQ).Associative().Unital().Commutative()
    assert algebra.module_rank() == cardinal(4)
    assert algebra.is_semisimple()
    assert not GF(2)[group].is_semisimple()
    assert ZZ[group] in Algebras(ZZ)


def test_the_regular_representation_is_the_group_algebra_as_a_module() -> None:
    group = Groups.S(3)
    regular = Groups().group_algebra(QQ)(group).regular_representation()
    assert regular in Modules(QQ[group])
    assert regular.module_rank() == cardinal(6)
    assert regular.module_invariants().module_rank() == cardinal(1)
    assert regular.character()(group.one()) == 6
    assert regular.character()(group.group_generators()[0]) == 0


# ---------------------------------------------------------------------------
# Ext and Tor.
# ---------------------------------------------------------------------------


def test_ext_and_tor_over_the_integers() -> None:
    six = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((6,))
    four = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((4,))
    integers = ZZ.regular_module()
    assert six.ext(integers, 1).cardinality() == cardinal(6)
    assert six.ext(integers, 0).cardinality() == cardinal(1)
    assert six.ext(four, 1).cardinality() == cardinal(2)
    assert six.ext(four, 2).cardinality() == cardinal(1)
    assert six.tor(four, 1).cardinality() == cardinal(2)
    assert six.tor(four, 0).cardinality() == cardinal(2)
    assert six.tor(integers, 1).cardinality() == cardinal(1)
    assert integers.ext(six, 1).cardinality() == cardinal(1)


def test_ext_and_tor_as_methods(pid) -> None:
    ring = pid
    # ``R/(a)`` is torsion only for nonzero ``a``.  In positive
    # characteristic an integer such as 6 may vanish, so over a field use a
    # unit relation; the resulting zero module is the field case of the same
    # cyclic presentation.
    scalar = ring.one() if ring in Fields() else ring(6)
    torsion = FinitelyPresentedTorsionModules(ring).direct_sum_of_cyclics((scalar,))
    assert torsion.ext(ring.regular_module(), 1).cardinality() == torsion.cardinality()
    assert torsion.tor(torsion, 1).cardinality() == torsion.cardinality()
    assert torsion.projective_dimension() == NN(0 if scalar.is_unit() else 1)
    assert ring.regular_module().projective_dimension() == NN(0)


# ---------------------------------------------------------------------------
# Number fields: Galois groups of extensions, units, class groups, ramification.
# ---------------------------------------------------------------------------


def test_galois_group_of_an_extension_and_its_fixed_fields() -> None:
    field = CyclotomicField(5, "z")
    galois = GaloisGroup(field, QQ)
    assert galois.order() == 4
    assert galois == field.galois_group()
    subgroup = galois.subgroup([galois.group_generators()[0] ** 2])
    fixed = galois.fixed_field(subgroup)
    assert fixed.degree() == 2
    assert fixed.discriminant() == 5
    assert field.subfields().cardinality() == cardinal(3)
    assert field.automorphism_group().order() == 4
    assert field.is_normal()


def test_unit_groups_and_class_groups_of_number_fields(build) -> None:
    gaussian = build("QQ(i)")
    golden = build("QQ(sqrt5)")
    non_principal = build("QQ(sqrt-5)")
    assert gaussian.unit_group().order() == 4
    assert gaussian.unit_group() in FiniteGroups()
    assert golden.unit_group().module_rank() == cardinal(1)
    assert golden.unit_group().torsion_subgroup().order() == 2
    assert golden.fundamental_units().cardinality() == cardinal(1)
    assert gaussian.class_group().order() == 1
    assert non_principal.class_group().order() == 2
    assert non_principal.class_group() in FiniteAbelianGroups()
    assert non_principal.class_group().an_element() ** 2 == non_principal.class_group().one()
    assert golden.regulator() > 0
    assert gaussian.roots_of_unity().cardinality() == cardinal(4)


def test_ramification_index_residue_degree_and_ideal_factorization(build) -> None:
    gaussian = build("QQ(i)")
    integers = gaussian.ring_of_integers()
    above_two = next(iter(gaussian.primes_above(2)))
    above_five = next(iter(gaussian.primes_above(5)))
    above_three = next(iter(gaussian.primes_above(3)))
    assert above_two.ramification_index() == 2
    assert above_two.residue_degree() == 1
    assert above_five.ramification_index() == 1
    assert above_five.residue_degree() == 1
    assert above_three.residue_degree() == 2
    assert above_three.norm() == 9
    assert above_two.norm() == 2
    assert integers.ideal(30).factorization().cardinality() == cardinal(4)
    assert integers.ideal(30).prime_factors().cardinality() == cardinal(4)
    assert integers.ideal(7).is_prime()
    assert integers.ideal(6).norm() == 36
    assert gaussian.different().norm() == 4
    assert gaussian.completion(above_five) in CompleteLocalRings()
    assert gaussian.completion(above_five).residue_field().cardinality() == cardinal(5)


def test_dedekind_zeta_and_the_algebraic_closure(build) -> None:
    gaussian = build("QQ(i)")
    assert gaussian.algebraic_closure() is QQbar
    assert QQ.algebraic_closure() is QQbar
    assert GF(4).algebraic_closure().characteristic() == 2
    assert GF(4).galois_group().order() == 2
    assert GF(4).frobenius_endomorphism()(GF(4).multiplicative_generator()) == GF(4).multiplicative_generator() ** 2
    assert QQ.completion(5) == Qp(5)
    assert QQ.completion(Infinity) == RR
    assert gaussian.dedekind_zeta_function()(2) > 1


# ---------------------------------------------------------------------------
# Curves.
# ---------------------------------------------------------------------------


def test_the_genus_and_points_of_plane_curves() -> None:
    plane = AffineSpaces(GF(5))(2, names=("x", "y"))
    x = plane.coordinate_ring().algebra_generator("x")
    y = plane.coordinate_ring().algebra_generator("y")
    elliptic = plane.closed_subscheme(y**2 - x**3 - x)
    cusp = plane.closed_subscheme(y**2 - x**3)
    assert elliptic.genus() == 1
    assert cusp.geometric_genus() == 0
    assert cusp.arithmetic_genus() == 1
    assert ProjectiveSpaces(GF(5))(1).genus() == 0
    assert elliptic.is_smooth()
    assert not cusp.is_smooth()
    assert cusp.singular_points().cardinality() == cardinal(1)
    assert elliptic.singular_points().cardinality() == cardinal(0)
    assert elliptic.rational_points().cardinality() == cardinal(elliptic.point_count())
    assert elliptic.projective_closure().point_count() == elliptic.point_count() + 1
    assert elliptic.function_field() in Fields()
    assert elliptic.function_field().characteristic() == 5
    assert cusp.normalization().genus() == 0
    assert elliptic.jacobian().dimension() == 1


def test_riemann_roch_on_the_projective_line() -> None:
    line = ProjectiveSpaces(QQ)(1)
    point = line.point((1, 0))
    divisor = 3 * line.divisor(point)
    assert divisor.degree() == 3
    assert line.riemann_roch_space(divisor).module_rank() == cardinal(4)
    assert line.riemann_roch_space(-divisor).module_rank() == cardinal(0)
    assert line.canonical_divisor().degree() == -2
    assert line.picard_group().module_rank() == cardinal(1)
    assert line.euler_characteristic() == 2


# ---------------------------------------------------------------------------
# Root systems, Weyl groups, Clifford algebras, Witt invariants.
# ---------------------------------------------------------------------------


def test_weyl_groups_and_dynkin_diagrams_of_root_lattices() -> None:
    a2 = Lattices(ZZ)("A2")
    e8 = Lattices(ZZ)("E8")
    assert a2.weyl_group().order() == 6
    assert e8.weyl_group().order() == 696729600
    assert WeylGroup(["A", 2]).order() == 6
    assert a2.dynkin_diagram().cardinality() == cardinal(2)
    assert a2.cartan_matrix().determinant() == 3
    assert a2.root_system().module_rank() == cardinal(2)
    assert a2.positive_roots().cardinality() == cardinal(3)
    assert e8.positive_roots().cardinality() == cardinal(120)
    assert a2.weyl_group().is_isomorphic_to(Groups.S(3))
    assert a2.O().order() == 2 * a2.weyl_group().order()


def test_clifford_algebras_and_witt_invariants() -> None:
    a2 = Lattices(QQ)([[2, 1], [1, 2]])
    plane = Lattices(QQ)("U")
    assert CliffordAlgebra(a2).module_rank() == cardinal(4)
    assert CliffordAlgebra(Lattices(QQ)(3)).module_rank() == cardinal(8)
    assert CliffordAlgebra(a2) in Algebras(QQ)
    assert not CliffordAlgebra(a2).is_commutative()
    assert plane.is_isotropic()
    assert not a2.is_isotropic()
    assert plane.witt_index() == 1
    assert a2.witt_index() == 0
    assert a2.hasse_invariant(2) in (1, -1)
    assert a2.hasse_invariant(3) in (1, -1)
    assert a2.represents(2)
    assert not a2.represents(1)
    assert a2.anisotropic_kernel().module_rank() == cardinal(2)
    assert plane.anisotropic_kernel().module_rank() == cardinal(0)
    assert WittGroup(QQ).an_element() in WittGroup(QQ)
    assert WittGroup(RR).is_isomorphic_to(Groups.Abelian([0]))
    assert WittGroup(CC).order() == 2


# ---------------------------------------------------------------------------
# Modules: the spellings every algebraist types.
# ---------------------------------------------------------------------------


def test_quotients_of_modules_by_the_slash(pid) -> None:
    ring = pid
    module = ring.free_module(2)
    submodule = module.subobject_on([2 * module.module_generator(0), module.module_generator(1)])
    quotient = module / submodule
    assert quotient in Modules(ring)
    assert quotient.cardinality() == ring.quotient_ring(ring.ideal(ring(2))).cardinality()
    assert module.quotient(submodule) == quotient
    assert quotient.projection().domain() is module


def test_hom_tensor_and_sum_spelled_as_a_sage_user_would(commutative_ring) -> None:
    ring = commutative_ring
    plane = ring.free_module(2)
    line = ring.free_module(1)
    assert Hom(plane, line).module_rank() == cardinal(2)
    assert plane.hom(line) in Cat()
    assert plane.tensor(line).module_rank() == cardinal(2)
    assert plane.tensor_product(line).module_rank() == cardinal(2)
    assert plane.direct_sum(line).module_rank() == cardinal(3)
    assert (plane + line).module_rank() == cardinal(3)
    assert (plane**3).module_rank() == cardinal(6)
    assert plane.dual_module().module_rank() == cardinal(2)
    assert plane.dimension() == cardinal(2) if ring in Fields() else plane.module_rank() == cardinal(2)
    assert plane.module_generators().cardinality() == cardinal(2)
    assert plane.zero_submodule().module_rank() == cardinal(0)
    assert kernel(plane.Mor(line)({0: line.module_generator(0), 1: line.zero()})).module_rank() == cardinal(1)


def test_symmetric_and_exterior_powers_by_their_usual_names(commutative_ring) -> None:
    module = commutative_ring.free_module(3)
    assert module.symmetric_power(2).module_rank() == cardinal(6)
    assert ExteriorPower(module, 2).module_rank() == cardinal(3)
    assert ExteriorPower(module, 3).module_rank() == cardinal(1)
    assert ExteriorPower(module, 4).module_rank() == cardinal(0)
    assert module.tensor_power(2).module_rank() == cardinal(9)
    assert Sym(module, 2).module_rank() == cardinal(6)
    assert Alt(module, 2).module_rank() == cardinal(3)


def test_torsion_and_length_of_modules_over_the_integers() -> None:
    module = FinitelyPresentedTorsionModules(ZZ).direct_sum_of_cyclics((4, 6))
    free = ZZ.free_module(2)
    assert module.torsion_submodule() == module
    assert free.torsion_submodule().cardinality() == cardinal(1)
    assert free.is_torsion_free()
    assert not module.is_torsion_free()
    assert module.length() == 4
    assert module.elementary_divisors() == Set((2, 2, 3))
    assert module.primary_decomposition().cardinality() == cardinal(2)
    assert module.exponent() == 12
    assert module.minimal_number_of_generators() == 2
    assert free.torsion_free_quotient() == free


# ---------------------------------------------------------------------------
# Rings: the spellings every algebraist types.
# ---------------------------------------------------------------------------


def test_nilradical_jacobson_radical_and_reducedness(commutative_ring) -> None:
    ring = commutative_ring
    nilradical = ring.nilradical()
    assert nilradical in CommutativeIdeals(ring)
    assert ring.is_reduced() == (nilradical == ring.ideal(ring.zero()))
    assert (ring in IntegralDomains()) <= ring.is_reduced()
    assert ring.jacobson_radical() in CommutativeIdeals(ring)
    assert nilradical.is_subideal(ring.jacobson_radical())
    assert nilradical.sum(ring.jacobson_radical()) == ring.jacobson_radical()


def test_dual_numbers_are_not_reduced_and_their_radical_is_epsilon() -> None:
    dual = QQ.dual_numbers()
    epsilon = dual.algebra_generator("epsilon")
    assert not dual.is_reduced()
    assert dual.nilradical() == dual.ideal(epsilon)
    assert dual.jacobson_radical() == dual.ideal(epsilon)
    assert dual.maximal_ideals().cardinality() == cardinal(1)
    assert dual.prime_ideals().cardinality() == cardinal(1)
    assert dual.dimension() == 0
    assert dual.length() == 2
    assert Zmod(12).maximal_ideals().cardinality() == cardinal(2)
    assert Zmod(12).minimal_primes().cardinality() == cardinal(2)
    assert Zmod(12).unit_group().order() == 4
    assert Zmod(12).units().cardinality() == cardinal(4)
    assert Zmod(8).unit_group().is_isomorphic_to(Groups.V4())


def test_normalization_of_the_cusp_and_regularity() -> None:
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    y = plane.algebra_generator("y")
    cusp = plane.quotient_ring(plane.ideal(y**2 - x**3))
    normalization = cusp.normalization()
    assert normalization in PrincipalIdealDomains()
    assert normalization.krull_dimension() == 1
    assert cusp.integral_closure() == normalization
    assert not cusp.is_normal()
    assert plane.is_normal()
    assert plane.is_regular()
    assert not cusp.is_regular()
    assert cusp.singular_locus().cardinality() == cardinal(1)
    origin = cusp.ideal(cusp.quotient_map()(x), cusp.quotient_map()(y))
    assert cusp.localize_at_prime(origin).embedding_dimension() == 2
    assert cusp.localize_at_prime(origin).is_regular() is False
    assert plane.localize_at_prime(plane.ideal(x, y)).is_regular()
    assert plane.localize_at_prime(plane.ideal(x, y)).tangent_space().module_rank() == cardinal(2)


def test_factoring_elements_and_counting_divisors() -> None:
    assert ZZ(12).factor().cardinality() == cardinal(2)
    assert ZZ(12).divisors().cardinality() == cardinal(6)
    assert ZZ(12).euler_phi() == 4
    assert ZZ(12).number_of_divisors() == 6
    assert ZZ(97).is_prime()
    assert ZZ(0).factorial() == 1
    polynomials = QQ.polynomial_ring("x")
    x = polynomials.algebra_generator("x")
    assert (x**2 - polynomials.one()).factor().cardinality() == cardinal(2)
    assert (x**2 + polynomials.one()).is_irreducible()
    assert not (x**2 - polynomials.one()).is_irreducible()
    assert (x**2 - polynomials.one()).roots().cardinality() == cardinal(2)
    assert (x**2 + polynomials.one()).roots().cardinality() == cardinal(0)
    assert (x**2 + polynomials.one()).roots(QQbar).cardinality() == cardinal(2)
    assert (x**3 - x).gcd(x**2 - polynomials.one()) == x**2 - polynomials.one()
    assert (x**2 - polynomials.one()).degree() == 2
    assert (x**2 - polynomials.one()).discriminant() == QQ(4)
    assert (x**2 - polynomials.one()).splitting_field().degree() == 1
    assert (x**3 - polynomials(2)).splitting_field().degree() == 6


# ---------------------------------------------------------------------------
# Groups: the spellings every group theorist types.
# ---------------------------------------------------------------------------


def test_centers_commutators_and_series() -> None:
    symmetric = Groups.S(3)
    quaternion = Groups.Q()
    alternating = Groups.A(5)
    assert symmetric.center().order() == 1
    assert quaternion.center().order() == 2
    assert symmetric.commutator_subgroup().order() == 3
    assert symmetric.derived_series().cardinality() == cardinal(3)
    assert symmetric.is_solvable()
    assert not symmetric.is_nilpotent()
    assert quaternion.is_nilpotent()
    assert alternating.is_simple()
    assert not symmetric.is_simple()
    assert alternating.commutator_subgroup() == alternating
    assert symmetric.exponent() == 6
    assert quaternion.exponent() == 4
    assert Groups.S(4).sylow_subgroup(2).order() == 8
    assert Groups.S(4).sylow_subgroup(3).order() == 3
    assert Groups.S(4).sylow_subgroups(3).cardinality() == cardinal(4)


def test_normal_subgroups_quotients_and_subgroup_lattices() -> None:
    symmetric = Groups.S(3)
    alternating = symmetric.commutator_subgroup()
    assert symmetric.normal_subgroups().cardinality() == cardinal(3)
    assert symmetric.subgroups().cardinality() == cardinal(6)
    assert alternating.is_normal()
    assert alternating.is_normal(symmetric)
    assert (symmetric / alternating).order() == 2
    assert symmetric.quotient(alternating).is_isomorphic_to(Groups.C(2))
    assert symmetric.quotient_map(alternating).is_surjective()
    assert Groups.S(4).normal_subgroups().cardinality() == cardinal(4)
    assert Groups.S(4).quotient(Groups.V4()).is_isomorphic_to(Groups.S(3))
    assert Groups.C(6).subgroups().cardinality() == cardinal(4)
    assert Groups.C(6).subgroup_lattice().cardinality() == cardinal(4)


def test_character_tables_and_irreducible_representations() -> None:
    symmetric = Groups.S(3)
    assert symmetric.character_table().nrows() == 3
    assert symmetric.irreducible_characters().cardinality() == cardinal(3)
    assert symmetric.irreducible_representations(QQ).cardinality() == cardinal(3)
    assert Set(character.degree() for character in symmetric.irreducible_characters()) == Set((1, 2))
    assert sum(character.degree() ** 2 for character in symmetric.irreducible_characters()) == 6
    assert Groups.Q().irreducible_characters().cardinality() == cardinal(5)
    assert Groups.A(5).irreducible_characters().cardinality() == cardinal(5)


def test_products_semidirect_products_and_presentations_of_groups() -> None:
    two = Groups.C(2)
    three = Groups.C(3)
    assert two.direct_product(three).is_isomorphic_to(Groups.C(6))
    assert (two * three).order() == 6
    inversion = two.Mor(three.Aut())({two.group_generators()[0]: three.Aut()(lambda h: h.inverse())})
    assert three.semidirect_product(two, inversion).is_isomorphic_to(Groups.S(3))
    assert Groups.S(3).presentation().group_generators().cardinality() == cardinal(2)
    assert Groups.S(3).presentation().defining_relations().cardinality() >= cardinal(3)
    assert Groups.S(3).cayley_graph().vertices().cardinality() == cardinal(6)
    assert Groups.S(3).class_number() == 3
    assert Groups.S(3).conjugacy_classes().cardinality() == cardinal(3)


def test_orbits_and_stabilizers_spelled_on_the_group() -> None:
    symmetric = Groups.S(4)
    assert symmetric.stabilizer(1).order() == 6
    assert symmetric.orbit(1).cardinality() == cardinal(4)
    assert symmetric.orbits((1, 2, 3, 4)).cardinality() == cardinal(1)
    assert symmetric.action_on((1, 2, 3, 4)) in FiniteGSets(symmetric)
    assert symmetric.is_transitive()
    assert Groups.C(2).action_on((1, 2, 3, 4)).orbits().cardinality() >= cardinal(2)


# ---------------------------------------------------------------------------
# Schemes: the spellings every geometer types.
# ---------------------------------------------------------------------------


def test_dimensions_components_and_base_change_of_schemes() -> None:
    assert (ZZ).affine_spectrum().dimension() == 1
    assert AffineSpaces(ZZ)(1).dimension() == 2
    assert AffineSpaces(QQ)(2).dimension() == 2
    assert (QQ).affine_spectrum().dimension() == 0
    axes = AffineSpaces(QQ)(2, names=("x", "y")).closed_subscheme(
        AffineSpaces(QQ)(2, names=("x", "y")).coordinate_ring().algebra_generator("x")
        * AffineSpaces(QQ)(2, names=("x", "y")).coordinate_ring().algebra_generator("y")
    )
    assert axes.irreducible_components().cardinality() == cardinal(2)
    assert not axes.is_irreducible()
    assert AffineSpaces(QQ)(2).is_irreducible()
    assert axes.is_reduced()
    assert axes.dimension() == 1
    assert AffineSpaces(ZZ)(2).base_change(ZZ.Mor(GF(5))(lambda n: GF(5)(n))).point_count() == 25
    assert AffineSpaces(ZZ)(1).fiber((ZZ).affine_spectrum().underlying_space()(ZZ.ideal(5))).point_count() == 5


def test_proj_blowups_and_global_sections() -> None:
    graded = QQ.polynomial_ring(("x", "y", "z"))
    plane = Proj(graded)
    assert plane == ProjectiveSpaces(QQ)(2)
    assert plane.dimension() == 2
    assert plane.global_sections().module_rank() == cardinal(1)
    assert H(0, plane, plane.structure_sheaf()).module_rank() == cardinal(1)
    assert H(1, plane, plane.structure_sheaf()).module_rank() == cardinal(0)
    assert plane.euler_characteristic() == 3
    assert plane.picard_group().module_rank() == cardinal(1)
    blown_up = AffineSpaces(QQ)(2).blowup(AffineSpaces(QQ)(2).point((0, 0)))
    assert blown_up.dimension() == 2
    assert blown_up.exceptional_divisor().dimension() == 1
    assert blown_up.exceptional_divisor().is_isomorphic_to(ProjectiveSpaces(QQ)(1))
    assert AffineSpaces(QQ)(2).point((1, 2)).residue_field() is QQ
    assert AffineSpaces(QQ)(2).local_ring(AffineSpaces(QQ)(2).point((1, 2))) in LocalRings()
    assert AffineSpaces(QQ)(2).tangent_space(AffineSpaces(QQ)(2).point((1, 2))).module_rank() == cardinal(2)


# ---------------------------------------------------------------------------
# Sets and categories: the spellings everyone types.
# ---------------------------------------------------------------------------


def test_set_operations_by_their_usual_names() -> None:
    left = Set((1, 2, 3))
    right = Set((3, 4))
    assert left.union(right).cardinality() == cardinal(4)
    assert left.intersection(right).cardinality() == cardinal(1)
    assert left.difference(right).cardinality() == cardinal(2)
    assert left.symmetric_difference(right).cardinality() == cardinal(3)
    assert left.cartesian_product(right).cardinality() == cardinal(6)
    assert left.disjoint_union(right).cardinality() == cardinal(5)
    assert Set((3,)).is_subset(left)
    assert not left.is_subset(right)
    assert not left.is_empty()
    assert EmptySet().cardinality() == cardinal(0)
    assert EmptySet().is_empty()
    assert Singleton().cardinality() == cardinal(1)
    assert Set(range(5)).cardinality() == cardinal(5)
    assert FiniteOrderedSet(("a", "b", "c")).cardinality() == cardinal(3)
    assert FiniteOrderedSet(("a", "b", "c")).ranking_map()("b") == 1
    assert OrderedSet(("a", "b", "c")) in TotallyOrderedSets()
    assert Family({"p": 1, "q": 2}).cardinality() == cardinal(2)
    assert Family({"p": 1, "q": 2})["q"] == 2
    assert left.quotient(lambda a, b: a % 2 == b % 2).cardinality() == cardinal(2)
    assert Cardinality(left) == 3


def test_initial_terminal_and_zero_objects_of_the_familiar_categories() -> None:
    assert Sets().initial_object().cardinality() == cardinal(0)
    assert Sets().terminal_object().cardinality() == cardinal(1)
    assert Groups().initial_object().order() == 1
    assert Groups().terminal_object().order() == 1
    assert Groups().zero_object().order() == 1
    assert OwnedRings().initial_object() is ZZ
    assert CommutativeRings().terminal_object().cardinality() == cardinal(1)
    assert Modules(ZZ).zero_object().cardinality() == cardinal(1)
    assert Modules(ZZ).is_abelian()
    assert not Groups().is_abelian_category()
    assert Sets().has_products()
    assert Sets().has_coproducts()
    assert Modules(QQ).has_kernels()
    assert Fields().is_subcategory(CommutativeRings())
    assert Sets().opposite() in Cat()
    assert Sets.Δ[1].Mor(Sets.Δ[2]).cardinality() == cardinal(9)


def test_forgetful_and_free_functors_by_their_usual_names() -> None:
    forget = Groups().underlying_set()
    free = Sets().free_group()
    assert forget(Groups.S(3)).cardinality() == cardinal(6)
    assert forget.is_faithful()
    assert not forget.is_full()
    assert free(Sets.Δ[1]).is_isomorphic_to(Groups.Free(2))
    assert free.right_adjoint() == forget
    assert forget.left_adjoint() == free
    assert (forget * free)(Sets.Δ[0]).cardinality() == aleph0
    assert forget.compose(free) == forget * free
    assert Modules(ZZ).underlying_abelian_group()(ZZ.free_module(2)).is_abelian()
    assert OwnedRings().underlying_abelian_group()(ZZ) in AbelianGroups()
    assert Yoneda(Sets())(Sets.Δ[1]) in Cat().Mor(Sets().opposite(), Sets())
    assert Sets().hom_functor(Sets.Δ[1])(Sets.Δ[2]).cardinality() == cardinal(9)
