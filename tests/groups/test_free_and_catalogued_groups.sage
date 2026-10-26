r"""Free groups, cyclic subgroups and the orders of catalogued groups.

The free group on $\{a, b\}$ is nonabelian, finitely presented with no
relations, and $a b b^{-1} = a$; the word $a b a^{-1}$ is reduced.  A group
morphism out of it is determined by the images of $a$ and $b$ (the
universal property of the free group).  In $C_4 = \langle g \rangle$ the
cyclic subgroups $\langle g \rangle$ and $\langle g^2 \rangle$ have orders
$4$ and $2$.  The hyperoctahedral group $W(B_2)$ of signed permutations of
two letters has order $2^2 \cdot 2! = 8$.  $|\mathrm{SL}_2(\mathbb{F}_q)| =
q(q^2 - 1)$ and $\mathrm{PSL}_2(\mathbb{F}_7) = \mathrm{SL}_2(\mathbb{F}_7) /
\{\pm 1\}$ has order $7 \cdot 48 / 2 = 168$.  The Heisenberg group of upper
unitriangular $3 \times 3$ matrices over $\mathbb{Z}/3$ has $3^3 = 27$
elements.  $\mathrm{SL}_2(\mathbb{Z})$ is infinite and arithmetic, and the
braid group on three strands is infinite (it surjects onto $\mathbb{Z}$ by
the exponent sum).  All are computations from the definitions.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_free_group_on_two_letters_is_nonabelian_and_freely_reduces_words() -> None:
    free = Groups.Free(2)
    a, b = free.group_generators()

    assert free.number_of_group_generators() == cardinal(2)
    assert a * b * ~b == a
    assert a * b != b * a
    assert not free.is_abelian()
    assert free.is_finitely_generated()
    assert free.is_finitely_presented_as_group()
    assert free.free_generator(0) == a
    assert free.reduced_word(a * b * a**-1).cardinality() == cardinal(3)


def test_a_morphism_out_of_the_free_group_is_given_by_the_images_of_its_letters() -> None:
    r"""$a \mapsto (1\,2)$, $b \mapsto (1\,2\,3)$ is onto $S_3$ and sends $a b$ to $(1\,2)(1\,2\,3)$."""
    free = Groups.Free(2)
    a, b = free.group_generators()
    symmetric = Groups.S(3)
    morphism = free.Mor(symmetric)({a: symmetric((1, 2)), b: symmetric((1, 2, 3))})

    assert morphism.image().order() == 6
    assert morphism(a * b) == symmetric((1, 2)) * symmetric((1, 2, 3))


def test_generator_images_must_generate_the_whole_source() -> None:
    # A single transposition generates only C2 inside S3. Its image
    # cannot specify a homomorphism on arbitrary elements of S3.
    from sage_extensions.categories.group.groups import _engine_generator_epimorphism

    group = Groups.S(3)
    transposition = group((1, 2))
    try:
        _engine_generator_epimorphism(group, (transposition,))
    except ValueError as error:
        assert "do not generate the source group" in str(error)
    else:
        assert False, "an incomplete generator family defined a whole-group morphism"


def test_engine_generator_image_family_has_exact_arity() -> None:
    from sage_extensions.categories.group.groups import _gap_model

    symmetric = Groups.S(3)
    cyclic = Groups.C(2)
    generators = list(symmetric.group_generators())
    assert generators
    try:
        symmetric.Mor(cyclic)([])
    except ValueError as error:
        assert "images were supplied" in str(error)
    else:
        assert False, "an empty image tuple was accepted for a nontrivial group presentation"
    try:
        symmetric.Mor(cyclic)._from_engine_generator_images(
            list(_gap_model(symmetric).GeneratorsOfGroup()), []
        )
    except ValueError as error:
        assert "selected generators" in str(error)
    else:
        assert False, "direct engine-morphism ingress accepted missing generator images"

    # The same ingress must reject maps which violate source relations,
    # even with a complete generator-image family: C4 cannot map its
    # generator to an element of order three.
    from sage_extensions.categories.group.groups import _element_to_engine

    four = Groups.C(4)
    three = Groups.C(3)
    try:
        four.Mor(three)._from_engine_generator_images(
            list(_gap_model(four).GeneratorsOfGroup()),
            [_element_to_engine(three, three.group_generators()[0])],
        )
    except ValueError as error:
        assert "do not satisfy the source relations" in str(error)
    else:
        assert False, "an image of order three was accepted for a C4 generator"

    # The public dictionary constructor also has check=False by default.
    # Its generator images must nevertheless descend through C4's relation.
    try:
        four.Mor(three)({four.group_generators()[0]: three.group_generators()[0]})
    except ValueError as error:
        assert "relations" in str(error)
    else:
        assert False, "an invalid generator assignment was admitted without check=True"


def test_gap_group_morphism_requires_its_selected_endpoints() -> None:
    from sage_extensions.categories.group.groups import _gap_model
    from sage.libs.gap.libgap import libgap

    two = Groups.C(2)
    three = Groups.C(3)
    identity_of_two = libgap.IdentityMapping(_gap_model(two))
    try:
        three.Mor(three)(identity_of_two)
    except ValueError as error:
        assert "does not have the selected endpoints" in str(error)
    else:
        assert False, "a GAP map of C2 was admitted as an endomorphism of C3"

    # The default Mor constructor does not request optional validation.
    # Even so, an unchecked GAP mapping violating a defining relation
    # cannot represent an arrow in the owned category of groups.
    four = Groups.C(4)
    model_four = _gap_model(four)
    model_three = _gap_model(three)
    bad = libgap.GroupHomomorphismByImagesNC(
        model_four, model_three,
        model_four.GeneratorsOfGroup(),
        model_three.GeneratorsOfGroup(),
    )
    try:
        four.Mor(three)(bad)
    except ValueError as error:
        assert "does not satisfy the source relations" in str(error)
    else:
        assert False, "unchecked GAP mapping C4 to a generator of C3 was admitted"



def test_the_cyclic_subgroups_of_c4_have_orders_four_and_two() -> None:
    group = Groups.C(4)
    generator = group.group_generators()[0]

    assert generator.cyclic_subgroup().order() == 4
    assert (generator**2).cyclic_subgroup().order() == 2


def test_symmetric_group_retains_its_chosen_point_set_and_action() -> None:
    points = Sets.Δ[2]
    group = SymmetricGroups()(points)
    assert group in SymmetricGroups()
    assert group.ambient_category() is OwnedGroups()
    assert group is Groups.S(points)
    assert group not in OwnedGroups().Commutative()
    assert SymmetricGroups()(Sets.Δ[1]) in OwnedGroups().Commutative()
    assert group.order() == 6
    assert group.natural_points() is points
    action = group.natural_g_set()
    assert action.point_set() is points
    from sage_extensions.categories.group.g_sets import _permutation_from_point_map

    try:
        _permutation_from_point_map(group, points, lambda _point: points(0))
    except ValueError as error:
        assert "not represented by a permutation" in str(error)
    else:
        assert False, "a constant point map was accepted as a permutation"
    identity = group.one()
    for point in points:
        assert action.act(identity, point) == point
    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
    # The common PermutationGroups owner must not silently extend an
    # unlabelled permutation's action beyond its represented domain.
    unlabelled = Groups.S(3)
    try:
        unlabelled.action_on(finite_ordered_set((1, 2, 3, 4)))
    except AssertionError as error:
        assert "selected domain" in str(error)
    else:
        assert False, "the common permutation category invented an action on a larger set"
    try:
        unlabelled.one()(-1)
    except ValueError as error:
        assert "outside the selected permutation domain" in str(error)
    else:
        assert False, "the common permutation action silently fixed an external point"

    labelled = finite_ordered_set(("alpha", "beta", "gamma"))
    labelled_group = SymmetricGroups()(labelled)
    assert labelled_group.natural_points() is labelled
    permutation = labelled_group((1, 2))
    labelled_action = labelled_group.natural_g_set()
    selected_action = labelled_group.action_on(labelled)
    assert selected_action is labelled_group.natural_g_set()
    assert selected_action.permutation_representation() is labelled_group.natural_g_set().permutation_representation()
    representation = labelled_group.natural_permutation_representation()
    assert representation is selected_action.permutation_representation()
    assert representation.domain() is labelled_group
    assert selected_action.acting_group() is labelled_group
    assert labelled_action.act(permutation, labelled("alpha")) == labelled("beta")
    assert permutation(labelled("alpha")) == labelled("beta")
    assert permutation(labelled("beta")) == labelled("alpha")
    try:
        permutation("outside")
    except ValueError as error:
        assert "outside the selected permutation domain" in str(error)
    else:
        assert False, "a permutation silently acquired a fixed point outside its selected domain"
    assert selected_action.act(permutation, labelled("alpha")) == labelled("beta")
    assert labelled_action.act(permutation, labelled("beta")) == labelled("alpha")
    assert labelled_action.act(permutation, labelled("gamma")) == labelled("gamma")

    # The defining action is transported along the actual ranking
    # isomorphism: products and inverses must respect that transport.
    cycle = labelled_group((1, 2, 3))
    for point in labelled:
        assert (permutation * cycle)(point) == permutation(cycle(point))
        assert (~cycle)(cycle(point)) == point
        assert labelled_action.act(cycle, point) == cycle(point)


def test_symmetric_group_arrows_are_induced_by_bijections() -> None:
    r"""An arrow of ``SymmetricGroups()`` is ``sigma |-> f sigma f^-1`` for a bijection ``f``.

    Mathlib ``Equiv.permCongr``.  ``Z(S_3)`` is trivial, so the six
    bijections ``Delta[2] -> {a, b, c}`` induce six distinct arrows, while
    ``S_3`` has ten group endomorphisms (four of them with image of order at
    most two, one of them trivial).
    """
    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

    points = Sets.Δ[2]
    labels = finite_ordered_set(("a", "b", "c"))
    source = SymmetricGroups()(points)
    target = SymmetricGroups()(labels)
    arrows = SymmetricGroups().Mor(source, target)
    unrank = labels.ranking_map().inverse()
    relabel = Sets().Mor(points, labels)(lambda point: unrank(int(point))).as_isomorphism()
    assert relabel in Sets().Core().Mor(points, labels)
    induced = arrows(relabel)
    transposition = source((1, 2))
    assert induced(transposition)(labels("a")) == labels("b")
    assert induced(transposition)(labels("c")) == labels("c")
    assert arrows.cardinality() == cardinal(6)
    assert SymmetricGroups().Mor(source, source).cardinality() == cardinal(6)
    assert source.Mor(source).cardinality() == cardinal(10)
    assert SymmetricGroups().Mor(source, SymmetricGroups()(Sets.Δ[1])).cardinality() == cardinal(0)
    assert SymmetricGroups()(Groups.S(3).natural_points()) is Groups.S(3)


def test_symmetric_group_of_an_infinite_set_is_outside_the_computed_cases() -> None:
    try:
        SymmetricGroups()(NN)
    except AssertionError as error:
        assert "finite point set" in str(error)
    else:
        assert False, "Sym(NN) was realized by a finite permutation engine"


def test_orders_of_catalogued_finite_groups_from_their_definitions() -> None:
    assert Groups.Weyl(["B", 2]).order() == 8
    assert Groups.PSL(2, 7).order() == 168


def test_coxeter_group_retains_its_matrix_and_type_a2_order() -> None:
    matrix = [[1, 3], [3, 1]]
    group = CoxeterGroups()(matrix)
    assert group in OwnedGroups().Finite()
    assert group in CoxeterGroups()
    assert group in FreeGroupQuotients()
    assert group.ambient_category() is OwnedGroups()
    assert group is Groups.Coxeter([[1, 3], [3, 1]])
    retained = group.coxeter_matrix()
    assert group.coxeter_matrix() is retained
    assert group.order() == 6
    # A2 has simple reflections s,t with (st)^3=1 and s,t distinct, so
    # its Coxeter group is S3 and is not abelian. Construction must not
    # eagerly require Sage's unavailable generic is_abelian() engine query.
    assert not group.is_abelian()
    assert group.is_isomorphic_to(SymmetricGroups()(Sets.Δ[2]))
    # The Coxeter realization is not Sage's FinitelyPresentedGroup; its
    # canonical reduced words must nevertheless lift through the selected
    # Coxeter presentation when adjoining a normal relator.
    first_reflection = tuple(group.group_generators())[0]
    collapsed, collapse_map = group.quotient_by_relators(
        (first_reflection,), return_projection=True
    )
    assert collapsed.order() == 1
    assert collapse_map.domain() is group
    assert collapse_map.codomain() is collapsed
    assert collapse_map(first_reflection) == collapsed.one()

    # With no added normal relations, the map is an isomorphism of
    # abstract groups. In particular it must respect noncommuting words,
    # which detects reversing the Coxeter matrix and GAP word laws.
    unchanged, unchanged_map = group.quotient_by_relators((), return_projection=True)
    simple = tuple(group.group_generators())
    assert unchanged.order() == group.order()
    assert unchanged_map(simple[0] * simple[1]) == unchanged_map(simple[0]) * unchanged_map(simple[1])
    assert unchanged_map(simple[1] * simple[0]) == unchanged_map(simple[1]) * unchanged_map(simple[0])
    assert unchanged_map(simple[0] * simple[1]) != unchanged_map(simple[1] * simple[0])

    # Killing the product s*t in A2 identifies the two simple
    # reflections, leaving one involution. Unlike killing s alone,
    # this tests a genuinely nontrivial reduced-word relator and its
    # orientation under the opposite GAP/free-group multiplication law.
    identified, identification = group.quotient_by_relators(
        (simple[0] * simple[1],), return_projection=True
    )
    assert identified.order() == 2
    assert identification(simple[0]) == identification(simple[1])
    assert identification(simple[0] * simple[1]) == identified.one()
    assert identification(simple[1] * simple[0]) == identified.one()

    # For an even Coxeter bond, killing one reflection leaves the other
    # involution (unlike A2's odd bond, which kills both reflections).
    b2 = CoxeterGroups()([[1, 4], [4, 1]])
    b2_reflection = tuple(b2.group_generators())[0]
    b2_quotient, b2_map = b2.quotient_by_relators((b2_reflection,), return_projection=True)
    assert b2_quotient.order() == 2
    assert b2_map(b2_reflection) == b2_quotient.one()

    # Imposing (s*t)^2 in the dihedral Coxeter group I_2(4)
    # forces s and t to commute, giving C2 x C2 rather than C2.
    # This separates the transport of a nontrivial reduced-word relation
    # from the normal closure of an individual reflection.
    b2_s, b2_t = tuple(b2.group_generators())
    commuting_quotient, commuting_map = b2.quotient_by_relators(
        ((b2_s * b2_t)**2,), return_projection=True
    )
    assert commuting_quotient.order() == 4
    assert commuting_map(b2_s) != commuting_map(b2_t)
    assert commuting_map(b2_s * b2_t) == commuting_map(b2_t * b2_s)

    # The infinite dihedral Coxeter presentation has no braid relation.
    # Adjoining (s*t)^3 makes precisely I_2(3) = S_3; the quotient is
    # finite even though its source is provably infinite. This separates
    # Coxeter presentation relations from inherited source finiteness.
    infinite_dihedral = CoxeterGroups()([[1, -1], [-1, 1]])
    infinite_s, infinite_t = tuple(infinite_dihedral.group_generators())
    finite_dihedral, finite_projection = infinite_dihedral.quotient_by_relators(
        ((infinite_s * infinite_t)**3,), return_projection=True
    )
    assert infinite_dihedral.is_finite() is False
    assert finite_dihedral.order() == 6
    assert finite_dihedral.is_isomorphic_to(SymmetricGroups()(Sets.Δ[2]))
    assert finite_projection(infinite_s * infinite_t) == (
        finite_projection(infinite_s) * finite_projection(infinite_t)
    )

    # The matrix-group realization must carry the Coxeter presentation
    # through the common GroupsWithChosenFinitePresentation Mor owner.
    source = group.presenting_free_group()
    projection = group.quotient_projection()
    assert projection.domain() is source
    assert projection.codomain() is group
    assert all(projection(relation) == group.one() for relation in group.defining_relations())
    symmetric = SymmetricGroups()(Sets.Δ[2])
    free_generators = tuple(source.group_generators())
    f = source.Mor(symmetric)({
        free_generators[0]: symmetric((1, 2)),
        free_generators[1]: symmetric((2, 3)),
    })
    descended = group.descend_homomorphism(f)
    assert descended.domain() is group
    assert descended.codomain() is symmetric
    assert all(descended(projection(g)) == f(g) for g in free_generators)


def test_rank_two_coxeter_infinitude_depends_on_the_bond() -> None:
    commuting = CoxeterGroups()([[1, 2], [2, 1]])
    finite = CoxeterGroups()([[1, 4], [4, 1]])
    infinite = CoxeterGroups()([[1, -1], [-1, 1]])
    assert commuting in (OwnedGroups().Commutative())
    assert commuting in (OwnedGroups().Finite())
    assert finite in (OwnedGroups().Finite())
    assert infinite in (OwnedGroups().Infinite())
    assert infinite not in (OwnedGroups().Finite())

    commuting_rank_three = CoxeterGroups()([[1, 2, 2], [2, 1, 2], [2, 2, 1]])
    assert commuting_rank_three in (OwnedGroups().Finite())
    assert commuting_rank_three in (OwnedGroups().Commutative())
    two_a2_components = CoxeterGroups()([
        [1, 3, 2, 2], [3, 1, 2, 2], [2, 2, 1, 3], [2, 2, 3, 1]
    ])
    assert two_a2_components in (OwnedGroups().Finite())
    assert two_a2_components not in (OwnedGroups().Commutative())
    a4 = CoxeterGroups()([
        [1, 3, 2, 2], [3, 1, 3, 2], [2, 3, 1, 3], [2, 2, 3, 1]
    ])
    affine_a3 = CoxeterGroups()([
        [1, 3, 2, 3], [3, 1, 3, 2], [2, 3, 1, 3], [3, 2, 3, 1]
    ])
    assert a4 in (OwnedGroups().Finite())
    assert affine_a3 not in (OwnedGroups().Finite())
    assert affine_a3 in (OwnedGroups().Infinite())
    b4 = CoxeterGroups()([
        [1, 4, 2, 2], [4, 1, 3, 2], [2, 3, 1, 3], [2, 2, 3, 1]
    ])
    affine_c3 = CoxeterGroups()([
        [1, 4, 2, 2], [4, 1, 3, 2], [2, 3, 1, 4], [2, 2, 4, 1]
    ])
    assert b4 in (OwnedGroups().Finite())
    assert affine_c3 not in (OwnedGroups().Finite())
    assert affine_c3 in (OwnedGroups().Infinite())
    d4 = CoxeterGroups()([
        [1, 3, 3, 3], [3, 1, 2, 2], [3, 2, 1, 2], [3, 2, 2, 1]
    ])
    assert d4 in (OwnedGroups().Finite())
    f4 = CoxeterGroups()([
        [1, 3, 2, 2], [3, 1, 4, 2], [2, 4, 1, 3], [2, 2, 3, 1]
    ])
    h4 = CoxeterGroups()([
        [1, 5, 2, 2], [5, 1, 3, 2], [2, 3, 1, 3], [2, 2, 3, 1]
    ])
    assert f4 in (OwnedGroups().Finite())
    assert h4 in (OwnedGroups().Finite())
    # E6: the central vertex has arms of lengths 1, 2, 2.
    e6 = CoxeterGroups()([
        [1, 3, 2, 2, 2, 2], [3, 1, 3, 2, 2, 2],
        [2, 3, 1, 3, 2, 3], [2, 2, 3, 1, 3, 2],
        [2, 2, 2, 3, 1, 2], [2, 2, 3, 2, 2, 1],
    ])
    assert e6 in (OwnedGroups().Finite())
    # Affine E6 has three arms of length two, so it is not spherical.
    affine_e6 = CoxeterGroups()([
        [1, 3, 2, 2, 2, 2, 2], [3, 1, 3, 2, 2, 2, 2],
        [2, 3, 1, 3, 2, 3, 2], [2, 2, 3, 1, 3, 2, 2],
        [2, 2, 2, 3, 1, 2, 2], [2, 2, 3, 2, 2, 1, 3],
        [2, 2, 2, 2, 2, 3, 1],
    ])
    assert affine_e6 not in (OwnedGroups().Finite())
    infinite_rank_three = CoxeterGroups()([[1, -1, 2], [-1, 1, 2], [2, 2, 1]])
    assert infinite_rank_three in (OwnedGroups().Infinite())
    affine_a2 = CoxeterGroups()([[1, 3, 3], [3, 1, 3], [3, 3, 1]])
    assert affine_a2 in (OwnedGroups().Infinite())
    assert affine_a2 not in (OwnedGroups().Finite())
    affine_c2 = CoxeterGroups()([[1, 4, 4], [4, 1, 2], [4, 2, 1]])
    hyperbolic_triangle = CoxeterGroups()([[1, 5, 5], [5, 1, 5], [5, 5, 1]])
    spherical_triangle = CoxeterGroups()([[1, 3, 3], [3, 1, 2], [3, 2, 1]])
    assert affine_c2 in (OwnedGroups().Infinite())
    assert hyperbolic_triangle in (OwnedGroups().Infinite())
    assert spherical_triangle not in (OwnedGroups().Infinite())
    assert spherical_triangle in (OwnedGroups().Finite())


def test_mutating_selected_coxeter_matrix_does_not_change_its_group() -> None:
    r"""Rows of a Coxeter matrix are read once into the owned matrix; mutating them later changes nothing."""
    matrix = [[1, 3], [3, 1]]
    group = CoxeterGroups()(matrix)
    retained = group.coxeter_matrix()
    matrix[0][1] = matrix[1][0] = 4
    assert group.coxeter_matrix() is retained
    assert group.order() == 6


def test_free_group_quotient_retains_source_and_dihedral_relations() -> None:
    free = Groups.Free(2)
    a, b = tuple(free.group_generators())
    relators = (a**2, b**3, (a*b)**2)
    quotient = FreeGroupQuotients()(free, relators)
    assert quotient in FreeGroupQuotients()
    assert quotient.ambient_category() is OwnedGroups()
    assert quotient.order() == 6
    assert quotient.presenting_free_group() is free
    assert set(quotient.defining_relations()) == set(relators)
    projection = quotient.quotient_projection()
    assert projection.domain() is free
    assert projection.codomain() is quotient
    assert all(projection(relation) == quotient.one() for relation in relators)
    descended = quotient.descend_homomorphism(projection)
    assert descended.domain() is quotient
    assert descended.codomain() is quotient
    assert all(descended(projection(generator)) == projection(generator) for generator in (a, b))
    assert all(descended(projection(word)) == projection(word) for word in (a*b, b*a, a*b*a, b**2*a))
    symmetric = SymmetricGroups()(Sets.Δ[2])
    free_to_symmetric = free.Mor(symmetric)(
        {a: symmetric((1, 2)), b: symmetric((1, 2, 3))}
    )
    symmetric_descent = quotient.descend_homomorphism(free_to_symmetric)
    assert symmetric_descent.domain() is quotient
    assert symmetric_descent.codomain() is symmetric
    assert all(
        symmetric_descent(projection(word)) == free_to_symmetric(word)
        for word in (a, b, a*b, b*a, a*b*a, b**2*a)
    )
    cyclic = Groups.C(2)
    wrong = free.Mor(cyclic)({a: cyclic.one(), b: cyclic.group_generators()[0]})
    # The same relator obstruction must hold at the shared GroupMor owner,
    # not only in the convenience descent operation: b^3 is nontrivial.
    quotient_a, quotient_b = tuple(quotient.group_generators())
    try:
        quotient.Mor(cyclic)(
            {quotient_a: cyclic.one(), quotient_b: cyclic.group_generators()[0]},
            check=True,
        )
    except ValueError as error:
        assert "relations" in str(error)
    else:
        assert False, "the presented group Mor admitted generator images violating b^3"
    try:
        quotient.descend_homomorphism(wrong)
    except ValueError as error:
        assert "defining relators" in str(error)
    else:
        assert False, "a map not killing the relations descended to the quotient"
    assert quotient.is_isomorphic_to(SymmetricGroups()(Sets.Δ[2]))

    # The ordinary quotient operation is another entry into the same
    # mathematical construction, not a weaker anonymous presentation.
    from_operation = free.quotient_by_relators(relators)
    assert from_operation in FreeGroupQuotients()
    assert from_operation is quotient
    assert FreeGroupQuotients()(free, tuple(reversed(relators))) is quotient
    assert from_operation.presenting_free_group() is free
    assert set(from_operation.defining_relations()) == set(relators)
    free_quotient, free_projection = free.quotient_by_relators(
        relators, return_projection=True
    )
    assert free_projection is free_quotient.quotient_projection()
    assert free_projection.domain() is free
    assert free_projection.codomain() is free_quotient

    # Quotienting a presented group must adjoin the new normal relators
    # to its original free presentation, not treat its generators as free.
    # S_3 / <<(123)>> = C_2, whereas a fresh free quotient would forget
    # the original a^2, b^3 and (ab)^2 relations.
    second_quotient, second_projection = quotient.quotient_by_relators(
        (projection(b),), return_projection=True
    )
    assert second_projection.domain() is quotient
    assert second_projection.codomain() is second_quotient
    assert second_projection(projection(b)) == second_quotient.one()
    # Universal property of the *iterated* quotient, with the actual
    # domain S_3 rather than the presenting free group: a homomorphism
    # killing b factors through q, including on non-generator words.
    target_c2 = Groups.C(2)
    target_involution = tuple(target_c2.group_generators())[0]
    source_to_c2 = quotient.Mor(target_c2)(
        (target_involution, target_c2.one()), check=True
    )
    factored = second_quotient.Mor(target_c2)(
        (target_involution, target_c2.one()), check=True
    )
    descended_quotient = second_quotient.descend_homomorphism(
        source_to_c2, through=second_projection
    )
    assert all(
        factored(second_projection(projection(word))) == source_to_c2(projection(word))
        for word in (a, b, a*b, b*a, a*b*a, b**2*a)
    )
    assert all(
        descended_quotient(second_projection(projection(word))) == source_to_c2(projection(word))
        for word in (a, b, a*b, b*a, a*b*a, b**2*a)
    )
    # Identity on S_3 does not descend through S_3 / <<b>>: the
    # quotient kills b, whereas identity preserves its nontrivial image.
    identity_on_source = quotient.Mor(quotient)(
        tuple(quotient.group_generators()), check=True
    )
    assert identity_on_source(projection(b)) != quotient.one()
    try:
        quotient.descend_homomorphism(identity_on_source, through=identity_on_source)
    except ValueError as error:
        assert "selected normal-quotient" in str(error)
    else:
        assert False, "an arbitrary group Mor was admitted as a quotient witness"
    try:
        second_quotient.descend_homomorphism(
            identity_on_source, through=second_projection
        )
    except ValueError:
        pass
    else:
        assert False, "a map nontrivial on the quotient kernel descended"
    assert second_projection(projection(a * b * a)) == (
        second_projection(projection(a))
        * second_projection(projection(b))
        * second_projection(projection(a))
    )
    assert second_quotient.order() == 2
    assert second_quotient.is_isomorphic_to(Groups.C(2))
    assert second_quotient.quotient_projection().domain() is second_quotient.presenting_free_group()
    assert second_quotient.presentation_source_group() is second_quotient
    assert second_quotient.presentation_isomorphism().domain() is second_quotient

    try:
        quotient.quotient_by_relators(NN, return_projection=True)
    except ValueError as error:
        assert "finite relators" in str(error)
    else:
        assert False, "an infinite relation family was exhausted by the quotient constructor"

    try:
        quotient.quotient_by_relators((Groups.C(2).one(),))
    except ValueError as error:
        assert "group being quotiented" in str(error)
    else:
        assert False, "the normal closure accepted an element of another group"


def test_a_chosen_generating_set_does_not_make_a_group_free() -> None:
    cyclic = Groups.C(3)
    assert cyclic.has_selected_group_resolution()
    try:
        FreeGroupQuotients()(cyclic, (cyclic.one(),))
    except AssertionError as error:
        assert "free group on a chosen set" in str(error)
    else:
        assert False, "a nonfree cyclic group was admitted as a free source"


def test_presentations_outside_the_computed_cases_and_foreign_relators() -> None:
    r"""``F/<<R>>`` is defined for every free group and every relator set (Mathlib
    ``PresentedGroup``); it is computed for a finite basis and finitely many relators.
    """
    infinite_free = Groups.Free(index_set=NN)
    try:
        FreeGroupQuotients()(infinite_free, ())
    except AssertionError as error:
        assert "finite free basis" in str(error)
    else:
        assert False, "an infinite-rank free group was handed to a finitely presented engine"

    finite_free = Groups.Free(1)
    try:
        FreeGroupQuotients()(finite_free, NN)
    except AssertionError as error:
        assert "finitely many relators" in str(error)
    else:
        assert False, "an infinite set of relators was handed to a finitely presented engine"

    # Relations from another presented group are not words in this
    # selected free source, even if both have one chosen generator.
    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
    other_free = Groups.Free(index_set=finite_ordered_set(("z",)))
    other_generator = other_free.group_generators()[0]
    try:
        FreeGroupQuotients()(finite_free, (other_generator,))
    except ValueError as error:
        assert "presenting free group" in str(error)
    else:
        assert False, "a relator from another free group changed the selected presentation"


def test_presented_group_arrows_are_induced_by_maps_of_presentations() -> None:
    r"""An arrow of ``FreeGroupQuotients()`` is induced by ``f: F -> F'`` with ``f(R) subset R'``.

    Mathlib ``PresentedGroup.map``.  On ``F(a, b)``, the swap ``a <-> b``
    sends ``{a^2, b^2, (ab)^3}`` into itself, so it induces an automorphism
    of ``<a, b | a^2, b^2, (ab)^3> = S_3``, exchanging the two generators.
    """
    free = Groups.Free(2)
    a, b = tuple(free.group_generators())
    relators = (a**2, b**2, (a*b)**3)
    quotient = FreeGroupQuotients()(free, relators)
    swap = free.Mor(free)({a: b, b: a})
    induced = FreeGroupQuotients().Mor(quotient, quotient)(swap, check=True)
    projection = quotient.quotient_projection()
    assert induced(projection(a)) == projection(b)
    assert induced(projection(b)) == projection(a)
    collapse = free.Mor(free)({a: a, b: a})
    try:
        FreeGroupQuotients().Mor(quotient, quotient)(collapse, check=True)
    except ValueError as error:
        assert "not a map of presentations" in str(error)
    else:
        assert False, "a free-group map sending (ab)^3 to a^6, not a relator, was admitted"


def test_quotient_descent_with_identified_presenting_generators() -> None:
    free = Groups.Free(2)
    a, b = tuple(free.group_generators())
    quotient = FreeGroupQuotients()(free, (a * ~b, a**2))
    projection = quotient.quotient_projection()
    assert projection(a) == projection(b)

    cyclic = Groups.C(2)
    involution = cyclic.group_generators()[0]
    compatible = free.Mor(cyclic)({a: involution, b: involution})
    descended = quotient.descend_homomorphism(compatible)
    assert descended.domain() is quotient
    assert descended.codomain() is cyclic
    assert descended(projection(a)) == descended(projection(b)) == involution
    checked = quotient.Mor(cyclic)(
        {projection(a): involution}, check=True
    )
    assert checked(projection(a)) == checked(projection(b)) == involution

    incompatible = free.Mor(cyclic)({a: involution, b: cyclic.one()})
    try:
        quotient.descend_homomorphism(incompatible)
    except ValueError as error:
        assert "defining relators" in str(error)
    else:
        assert False, "identified quotient generators received different target images"


def test_quotient_descent_respects_the_selected_free_basis_labels() -> None:
    labels = Sets.Δ[1]
    free = Groups.Free(index_set=labels)
    a = free.free_generator(labels(0))
    b = free.free_generator(labels(1))
    quotient = FreeGroupQuotients()(free, (a**2, b**3, (a*b)**2))
    projection = quotient.quotient_projection()
    via_operation, operation_projection = free.quotient_by_relators(
        (a**2, b**3, (a*b)**2), return_projection=True
    )
    # The quotient arrow must use the actual labelled free source, not
    # the incidental ordinal order of GAP's quotient generators.
    assert operation_projection is via_operation.quotient_projection()
    assert operation_projection.domain() is free
    quotient_generators = tuple(via_operation.group_generators())
    assert operation_projection(free.free_generator(labels(0))) == quotient_generators[0]
    assert operation_projection(free.free_generator(labels(1))) == quotient_generators[1]
    # The quotient universal arrow and the chosen presentation arrow are
    # literally the same Mor for a free source. Descent through that Mor
    # must reconstruct the identity without erasing the chosen labels.
    through_free_quotient = via_operation.descend_homomorphism(
        operation_projection, through=operation_projection
    )
    assert through_free_quotient.domain() is via_operation
    assert through_free_quotient.codomain() is via_operation
    assert all(
        through_free_quotient(operation_projection(free.free_generator(i)))
        == operation_projection(free.free_generator(i))
        for i in labels
    )
    descended = quotient.descend_homomorphism(projection)
    assert descended.domain() is quotient
    assert descended.codomain() is quotient
    assert all(descended(projection(free.free_generator(i))) == projection(free.free_generator(i)) for i in labels)


def test_general_linear_group_retains_ring_and_rank() -> None:
    group = GeneralLinearGroups()(GF(2), 2)
    assert group in GeneralLinearGroups()
    assert group.ambient_category() is OwnedGroups()
    assert group is Groups.GL(2, GF(2))
    assert group in OwnedGroups().Finite()
    assert group.coefficient_ring() is GF(2)
    assert group.degree() == 2
    assert group.order() == 6
    assert group.is_isomorphic_to(SymmetricGroups()(Sets.Δ[2]))

    # Repeated constructions must retain the same selected ring and rank;
    # the temporary pair passed to the engine cache is not a datum identity.
    second_group = GeneralLinearGroups()(GF(3), 2)
    assert second_group.coefficient_ring() is GF(3)
    assert second_group.degree() == 2
    assert second_group.order() == 48

    # GL_1(ZZ) is the group of units {+1,-1}, while GL_2(ZZ)
    # contains an infinite cyclic subgroup of unipotent matrices.
    assert GeneralLinearGroups()(ZZ, 1) in OwnedGroups().Finite()
    assert GeneralLinearGroups()(ZZ, 1) in OwnedGroups().Commutative()
    assert GeneralLinearGroups()(QQ, 1) in OwnedGroups().Commutative()
    assert GeneralLinearGroups()(GF(2), 2) not in OwnedGroups().Commutative()
    assert GeneralLinearGroups()(ZZ, 2) not in OwnedGroups().Finite()
    assert GeneralLinearGroups()(ZZ, 2) in OwnedGroups().Infinite()
    assert GeneralLinearGroups()(QQ, 1) in OwnedGroups().Infinite()
    assert GeneralLinearGroups()(QQ, 2) in OwnedGroups().Infinite()
    assert GeneralLinearGroups()(QQ["t"].fraction_field(), 1) in OwnedGroups().Infinite()


def test_general_linear_arrows_are_induced_by_ring_maps() -> None:
    r"""An arrow of ``GeneralLinearGroups()`` is ``GL_n(phi)``, ``phi`` applied entrywise.

    Mathlib ``Matrix.GeneralLinearGroup.map``.  Reduction ``ZZ -> GF(2)``
    sends the unipotent ``[[1, 1], [0, 1]]`` of infinite order to the
    transvection ``[[1, 1], [0, 1]]`` of order two.
    """
    integral = GeneralLinearGroups()(ZZ, 2)
    reduced = GeneralLinearGroups()(GF(2), 2)
    reduction = OwnedRings().Mor(ZZ, GF(2))(lambda n: GF(2)(n))
    induced = GeneralLinearGroups().Mor(integral, reduced)(reduction)
    unipotent = integral([[1, 1], [0, 1]])
    assert induced(unipotent) == reduced([[1, 1], [0, 1]])
    assert induced(unipotent).order() == 2
    assert induced(integral([[0, -1], [1, 0]])) == reduced([[0, 1], [1, 0]])


def test_general_linear_rank_cannot_be_truncated() -> None:
    try:
        GeneralLinearGroups()(GF(2), QQ(3) / 2)
    except AssertionError as error:
        assert "integer" in str(error)
    else:
        assert False, "a nonintegral rank was silently truncated"


def test_the_heisenberg_group_over_z_mod_three_has_twenty_seven_elements() -> None:
    assert Groups.Heisenberg(1, 3).order() == 27


def test_sl2z_and_the_three_strand_braid_group_are_infinite() -> None:
    modular = Groups.SL(2, ZZ)

    assert not modular.is_finite()
    assert modular.is_arithmetic_group()
    assert not Groups.Braid(3).is_finite()


def test_special_linear_rank_is_not_truncated() -> None:
    try:
        Groups.SL(QQ(5) / 2, ZZ)
    except ValueError as error:
        assert "integral rank" in str(error)
    else:
        assert False, "SL of nonintegral degree was admitted as SL2"


def test_named_matrix_group_families_require_integral_degree() -> None:
    for constructor in (Groups.GL, Groups.Sp, Groups.SO):
        try:
            constructor(QQ(5) / 2, ZZ)
        except ValueError as error:
            assert "degree must be an integer" in str(error)
        else:
            assert False, "a matrix group was constructed at a fractional degree"
