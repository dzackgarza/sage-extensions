r"""Universal constructions a mathematician expects in every category the session owns.

Products, coproducts, biproducts, kernels, cokernels, pushouts, fiber
products and subobject categories in sets, modules over every ring, and
groups; slices, coslices, opposites, products of categories, functor
categories, natural transformations, cores, and the Hom, End, Aut, Mono, Epi
and Iso constructions.
"""

from sage_extensions.all import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Limits and colimits in Sets.
# ---------------------------------------------------------------------------


def test_products_and_coproducts_of_finite_sets() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    sets = Sets()
    product = sets.product((two, three))
    coproduct = sets.coproduct((two, three))

    assert product.cardinality() == cardinal(6)
    assert product in Sets()
    assert product.projection(0).codomain() is two
    assert product.projection(1).codomain() is three
    assert coproduct.cardinality() == cardinal(5)
    assert coproduct.injection(0).domain() is two
    assert coproduct.injection(1).domain() is three
    assert sets.product((sets.product((three, three)), three)).cardinality() == cardinal(27)
    one = Sets.Δ[0]
    assert sets.product((one, three)).cardinality() == cardinal(3)
    assert sets.coproduct((one, three)).cardinality() == cardinal(4)


def test_the_universal_property_of_the_product_of_sets() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    product = Sets().product((two, three))
    first = Sets().Mor(three, two)(lambda point: two(int(point) % 2))
    second = Sets().Mor(three, three).identity()
    induced = product.from_maps(
        three,
        lambda index: first if int(index) == 0 else second,
    )
    assert induced.domain() is three
    assert induced.codomain() is product
    assert product.projection(0) * induced == first
    assert product.projection(1) * induced == second


def test_pushouts_and_fiber_products_of_finite_sets() -> None:
    one = Sets.Δ[0]
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    into_two = Sets().Mor(one, two)(lambda point: two(0))
    into_three = Sets().Mor(one, three)(lambda point: three(0))
    glued = Sets().pushout(into_two, into_three)
    assert glued.cardinality() == cardinal(4)

    onto_one_from_two = Sets().Mor(two, one)(lambda point: one(0))
    onto_one_from_three = Sets().Mor(three, one)(lambda point: one(0))
    pulled_back = Sets().fiber_product(onto_one_from_two, onto_one_from_three)
    assert pulled_back.cardinality() == cardinal(6)
    assert pulled_back.left_projection().codomain() is two


def test_subobjects_of_a_finite_set_form_its_power_set() -> None:
    three = Sets.Δ[2]
    subobjects = Sets().Subobjects(three)
    singleton = three.power_set()((three(0),))
    pair = three.power_set()((three(0), three(1)))
    assert subobjects in Cat()
    assert subobjects.cardinality() == cardinal(8)
    assert Sets().Subobjects(three).cardinality() == cardinal(8)
    assert singleton in subobjects
    assert singleton.inclusion().codomain() is three
    assert singleton.underlying_set() is singleton.inclusion().domain()
    assert singleton.category() is subobjects
    factor = subobjects.Mor(singleton, pair)
    assert factor.domain() is singleton
    assert factor.codomain() is pair
    assert factor(singleton.inclusion().factor_through(pair.inclusion())).left().domain() is singleton.underlying_set()

    four = Sets.Δ[3]
    same_points = four.power_set()((four(0),))
    assert same_points.inclusion().codomain() is four
    assert singleton != same_points
    assert singleton.inclusion() != same_points.inclusion()


# ---------------------------------------------------------------------------
# Limits and colimits in modules over every ring.
# ---------------------------------------------------------------------------


def test_products_coproducts_and_biproducts_of_modules(commutative_ring) -> None:
    ring = commutative_ring
    left = ring.free_module(2)
    right = ring.free_module(3)
    modules = Modules(ring)
    for both in (
        modules.product((left, right)),
        modules.coproduct((left, right)),
        modules.biproduct((left, right)),
    ):
        assert both in Modules(ring)
        assert both.module_rank() == cardinal(5)
    assert left.tensor_product(right).module_rank() == cardinal(6)
    assert modules.product((left, right)) == modules.coproduct((left, right))


def test_kernels_and_cokernels_of_module_morphisms(commutative_ring) -> None:
    ring = commutative_ring
    plane = ring.free_module(2)
    line = ring.free_module(1)
    projection = plane.Mor(line)({0: line.module_generator(0), 1: line.zero()})
    doubling = line.Mor(line)({0: 2 * line.module_generator(0)})

    assert projection.kernel().module_rank() == cardinal(1)
    assert projection.kernel().inclusion().codomain() is plane
    assert projection.cokernel().cardinality() == cardinal(1)
    assert doubling.cokernel().cardinality() == ring.quotient_ring(ring.ideal(ring(2))).cardinality()
    assert doubling.cokernel().projection().domain() is line
    assert doubling.kernel().module_rank() == cardinal(1 if ring(2) == ring.zero() else 0)


def test_pushouts_and_fiber_products_of_modules(commutative_ring) -> None:
    ring = commutative_ring
    line = ring.free_module(1)
    plane = ring.free_module(2)
    first_axis = line.Mor(plane)({0: plane.module_generator(0)})
    second_axis = line.Mor(plane)({0: plane.module_generator(1)})
    glued = Modules(ring).pushout(first_axis, first_axis)
    assert glued in Modules(ring)
    assert glued.module_rank() == cardinal(3)
    first_projection = plane.Mor(line)({0: line.module_generator(0), 1: line.zero()})
    pulled_back = Modules(ring).fiber_product(first_projection, first_projection)
    assert pulled_back in Modules(ring)
    assert pulled_back.module_rank() == cardinal(3)
    assert Modules(ring).pushout(first_axis, second_axis).module_rank() == cardinal(3)


def test_subobjects_of_a_module_form_a_category(commutative_ring) -> None:
    ring = commutative_ring
    module = ring.free_module(2)
    subobjects = Modules(ring).Subobjects(module)
    line = module.subobject_on([module.module_generator(0)])
    assert subobjects in Cat()
    assert line in subobjects
    assert line in Modules(ring).Subobjects(module)
    assert subobjects.Mor(line, line).identity()(line.module_generator(0)) == line.module_generator(0)


# ---------------------------------------------------------------------------
# Limits and colimits in groups.
# ---------------------------------------------------------------------------


def test_products_coproducts_kernels_and_cokernels_of_groups() -> None:
    symmetric = Groups.S(3)
    two = Groups.C(2)
    three = Groups.C(3)
    groups = Groups()
    product = groups.product((symmetric, two))
    free_product = groups.coproduct((two, three))
    sign = symmetric.Mor(two)(
        {g: (two.group_generators()[0] if g.order() == 2 else two.one()) for g in symmetric.group_generators()}
    )

    assert product in Groups()
    assert product.order() == 12
    assert not product.is_abelian()
    assert free_product in Groups()
    assert free_product not in FiniteGroups()
    assert free_product.cardinality() == aleph0
    assert sign.kernel().order() == 3
    assert sign.kernel().is_abelian()
    assert sign.kernel().inclusion().cokernel().order() == 2
    assert sign.cokernel().order() == 1
    assert groups.product((two, three)).is_isomorphic_to(Groups.C(6))


def test_subgroups_of_the_symmetric_group_form_a_category() -> None:
    symmetric = Groups.S(3)
    subgroups = Groups().Subobjects(symmetric)
    assert subgroups in Cat()
    assert subgroups.cardinality() == cardinal(6)
    assert Groups().Subobjects(Groups.C(6)).cardinality() == cardinal(4)
    assert Groups().Subobjects(Groups.Q()).cardinality() == cardinal(6)


# ---------------------------------------------------------------------------
# Categories built from categories.
# ---------------------------------------------------------------------------


def test_slices_coslices_opposites_products_and_functor_categories() -> None:
    module = ZZ.free_module(2)
    for category in (
        Modules(ZZ).SliceOver(module),
        OwnedRings().CosliceUnder(ZZ),
        Sets().opposite(),
        Cat().product((Sets(), Groups())),
        Cat().Mor(Sets(), Sets()),
        Sets().Core(),
        Modules(ZZ),
        Sets(),
        Groups(),
    ):
        assert category in Cat()
    assert module.subobject_on([module.module_generator(0)]) in Modules(ZZ).SliceOver(module)
    assert Sets.Δ[2] in Sets().opposite()
    functor_category = Cat().Mor(Sets(), Sets())
    assert functor_category(Sets().identity_functor()) in functor_category
    assert Fields() in Cat()
    assert Cat() in Cat()


def test_identity_and_inclusion_functors() -> None:
    identity = Sets().identity_functor()
    three = Sets.Δ[2]
    assert identity(three) is three
    assert identity(Sets().Mor(three, three).identity()) == Sets().Mor(three, three).identity()
    inclusion = Fields().inclusion_into(CommutativeRings())
    assert inclusion(QQ) is QQ
    assert inclusion.domain() is Fields()
    assert inclusion.codomain() is CommutativeRings()
    assert AbelianGroups().inclusion_into(Groups())(Groups.C(4)) is Groups.C(4)


def test_natural_transformations_between_functors() -> None:
    identity = Sets().identity_functor()
    transformations = identity.natural_transformations_to(identity)
    assert transformations in Sets()
    three = Sets.Δ[2]
    unit = transformations.identity()
    assert unit.component(three) == Sets().Mor(three, three).identity()
    identity = Sets().Mor(three, three).identity()
    square = unit.naturality_square(identity)
    left = square.parent().projection(0)(square)
    right = square.parent().projection(1)(square)
    assert left == unit.naturality_target_composite(identity)
    assert right == unit.naturality_source_composite(identity)
    assert left == right


def test_isomorphisms_and_the_core() -> None:
    two = Sets.Δ[1]
    swap = Sets().Mor(two, two)(lambda point: two(1 - int(point)))
    isomorphism = Sets().Core().Mor(two, two)(swap, swap)
    assert isomorphism in Sets().Iso(two, two)
    assert isomorphism in Sets().Core().Mor(two, two)
    assert isomorphism.inverse() * isomorphism == Sets().Iso(two, two).identity()
    assert Sets().Iso(two, two).cardinality() == cardinal(2)
    assert Sets().Core().Mor(two, Sets.Δ[2]).cardinality() == cardinal(0)


def test_hom_end_aut_mono_epi_constructions_on_sets() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    assert Sets().Mor(two, three) is Sets().Mor(two, three)
    assert Sets().Mor(two, three).cardinality() == cardinal(9)
    assert Sets().End(three).cardinality() == cardinal(27)
    assert Sets().Aut(three).order() == 6
    assert Sets().Aut(three) in Groups()
    assert Sets().Mono(two, three).cardinality() == cardinal(6)
    assert Sets().Epi(three, two).cardinality() == cardinal(6)
    assert Sets().Epi(two, three).cardinality() == cardinal(0)
    assert Sets().Iso(two, three).cardinality() == cardinal(0)


def test_hom_end_aut_constructions_on_modules_over_a_field(field) -> None:
    plane = field.free_module(2)
    endomorphisms = Modules(field).End(plane)
    automorphisms = Modules(field).Aut(plane)
    assert endomorphisms in Cat()
    assert automorphisms in Groups()
    assert endomorphisms.identity() in automorphisms
    if field.cardinality().is_finite():
        q = field.cardinality()
        assert endomorphisms.cardinality() == cardinal(q**4)
        assert automorphisms.order() == (q**2 - 1) * (q**2 - q)
    else:
        assert automorphisms.cardinality() == field.cardinality()


def test_direct_sum_objects_know_their_summands() -> None:
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    assert lattice in DirectSumObjects(Lattices(ZZ))
    assert lattice.number_of_summands() == cardinal(2)
    assert lattice.summands().cardinality() == cardinal(2)
    assert lattice.summand(0).module_rank() == cardinal(2)
    assert lattice.summand(1).determinant() == 3
