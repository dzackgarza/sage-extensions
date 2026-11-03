r"""The generated finite character image: orders, index, transversals and splits.

OrthogonalCharacterQuotient realizes the character image from the ambient
group's selected finite generating family as a generated group (GAP
stabilizer chains), instead of listing the image with one live lift per
element.  On arithmetic subgroups the image is far too large to list, so the
generated model is the only realization; on small models the elementwise
listing remains and is used here as an independent oracle.  The models are
U = [[0,1],[1,0]] and M = <2>+<2>, the Enriques-pattern lattice of the
character-intersection referee (nontrivial discriminant group (Z/2)^2,
O(A_M) of order 2, spinor-kernel intersection Gamma of index 4, where the
separate character indices are 2 and 2 and the exact index exceeds both).
"""

from sage.libs.gap.libgap import libgap

from sage_extensions.all import *


def _m_model(with_op=True):
    L = Lattices(ZZ)([[2, 0], [0, 2]])
    G = L.O()
    A = L.discriminant_group()
    OG = A.orthogonal_group()
    pre = G.discriminant_preimage(OG.trivial_subgroup())
    if with_op:
        inter = G.intersection(pre, L.O_plus())
    else:
        inter = pre
    return L, G, OG, pre, inter


def test_discriminant_image_of_the_full_target_is_the_true_rho_image_not_the_target() -> None:
    # m8's refutation specimen, reproduced: H = O(A_L) is a legal retained
    # target, its preimage is all of O(L), so rho(Gamma) = rho(O(L)) of order
    # 8 -- where the fd5ab11 separate-marginal formula returned O(A_L), order
    # 16.  Complete character data, no sign kernels; the joint preimage then
    # projection is the only formula that is right here.
    L = Lattices(ZZ)([[6, 0], [0, 6]])
    G = L.O()
    OG = L.discriminant_group().orthogonal_group()
    assert int(OG.cardinality()) == 16
    ambient_image = L.discriminant_image()
    assert int(ambient_image.cardinality()) == 8
    preimage = G.discriminant_preimage(OG)
    assert preimage.character_data_is_complete()
    image = preimage.discriminant_image()
    assert int(image.cardinality()) == 8
    assert all(a in ambient_image for a in image.group_generators())
    assert all(a in image for a in ambient_image.group_generators())


def test_generated_orders_and_index_match_the_listed_image() -> None:
    _L, _G, _OG, _pre, inter = _m_model()
    q = inter.finite_character_quotient()
    # The generated image answers what the listed image answers
    assert q.image_order() == int(q.image_keys().cardinality())
    assert q.subgroup_image_order() == int(q.subgroup_image_keys().cardinality())
    assert q.index() == 4
    # The exact index exceeds each separate character index (2 and 2): the
    # intersection is a genuine two-factor intersection, so a bound computed
    # from one factor alone, or from max rather than product, is refuted here.
    assert q.index() > 2
    # The subgroup cardinality through the character route is |G| |S| / |Q|.
    assert inter.supergroup().cardinality() == 8
    assert inter.cardinality() == 2


def test_right_coset_transversal_lifts_are_a_transversal_of_the_listed_image() -> None:
    _L, G, _OG, _pre, inter = _m_model()
    q = inter.finite_character_quotient()
    transversal = q.right_coset_transversal()
    assert len(transversal) == q.index()
    image_keys = q.image_keys()
    subgroup_keys = q.subgroup_image_keys()
    # Every lift is an isometry of the ambient group whose character image is
    # one of the listed image keys, and the lifts meet distinct H-cosets.
    seen_subsets = []
    for lift in transversal:
        assert lift in G
        key = q.image(lift)
        assert key in image_keys
        coset = frozenset(q._multiply(s, key) for s in subgroup_keys)
        assert coset not in seen_subsets
        seen_subsets.append(coset)
    # The cosets partition the listed image
    assert frozenset().union(*seen_subsets) == frozenset(image_keys)


def test_splitting_isometries_match_elementwise_double_cosets() -> None:
    L, G, _OG, _pre, inter = _m_model()
    q = inter.finite_character_quotient()
    e1 = next(iter(L.module_generators()))
    stabilizer = tuple(G.vector_stabilizer_generators(e1))
    assert stabilizer
    splitting = q.splitting_isometries(stabilizer)
    image_keys = q.image_keys()
    subgroup_keys = tuple(q.subgroup_image_keys())
    stabilizer_keys = tuple(q.stabilizer_image_keys(stabilizer))

    def in_double(key, center):
        return any(
            q._multiply(s, q._multiply(center, t)) == key
            for s in subgroup_keys
            for t in stabilizer_keys
        )

    # Count against the elementwise oracle and pairwise distinctness.
    cosets = []
    for lift in splitting:
        assert lift in G
        key = q.image(lift)
        assert key in image_keys
        assert not any(in_double(key, q.image(other)) for other in cosets)
        cosets.append(lift)
    covered = frozenset(
        key
        for key in image_keys
        if any(in_double(key, q.image(lift)) for lift in splitting)
    )
    assert covered == frozenset(image_keys)
    # The elementwise count itself
    distinct = {
        min(
            (q._multiply(s, q._multiply(x, t)) for s in subgroup_keys for t in stabilizer_keys),
            key=str,
        )
        for x in image_keys
    }
    assert len(splitting) == len(distinct) == len(cosets)
    assert len(splitting) == 2


def test_discriminant_image_equals_the_generated_image_of_the_schreier_family() -> None:
    L = Lattices(ZZ)([[2, 0], [0, 2]])
    G = L.O()
    OG = L.discriminant_group().orthogonal_group()
    pre_full = G.discriminant_preimage(OG)
    inter = G.intersection(pre_full, L.O_plus())
    assert inter.finite_character_quotient().index() == 2
    image = inter.discriminant_image()
    rho = L.discriminant_representation()
    # The image the same question has without the generated model: the
    # discriminant images of the realized Schreier generating family.
    schreier = tuple(inter.group_generators())
    generated = OG.subgroup_on(tuple(rho(g) for g in schreier))
    assert image.cardinality() == generated.cardinality() == 2
    assert all(g in image for g in generated.group_generators())
    assert all(g in generated for g in image.group_generators())
    # The generic image_under dispatch answers through the same case.
    assert inter.image_under(rho).cardinality() == image.cardinality()


def test_adjust_witness_into_subgroup_matches_elementwise_search() -> None:
    _L, G, _OG, _pre, inter = _m_model()
    q = inter.finite_character_quotient()
    outside = next(g for g in G.group_generators() if g not in inter)
    inside = next(g for g in G.group_generators() if g in inter and g != G.one())
    ambient = tuple(G.group_generators())
    # With the whole ambient as stabilizer the outside element is adjustable
    adjusted = q.adjust_witness_into_subgroup(outside, ambient)
    assert adjusted is not None and adjusted in inter
    # and the elementwise condition certifies the same existence.
    subgroup_keys = tuple(q.subgroup_image_keys())
    stabilizer_keys = tuple(q.stabilizer_image_keys(ambient))
    witness_key = q.image(outside)
    assert any(
        q._multiply(t, witness_key) in subgroup_keys for t in stabilizer_keys
    )
    # The trivial stabilizer cannot adjust an outside element.
    assert q.adjust_witness_into_subgroup(outside, (G.one(),)) is None
    assert not any(
        q._multiply(t, witness_key) in subgroup_keys for t in (q.image(G.one()),)
    )
    # An element already inside is returned unchanged.
    assert q.adjust_witness_into_subgroup(inside, ambient) is inside


def test_single_character_factors_are_generated_without_a_direct_product() -> None:
    L = Lattices(ZZ)([[2, 0], [0, 2]])
    G = L.O()
    OG = L.discriminant_group().orthogonal_group()
    spinor = L.O_plus()
    q = spinor.finite_character_quotient()
    assert q.image_order() == int(q.image_keys().cardinality()) == 2
    assert q.index() == 2
    assert len(q.right_coset_transversal()) == 2
    det_kernel = G.predicate_subgroup(
        lambda g: g.determinant() == 1,
        "determinant one",
        character_data={"determinant_kernel": True},
        character_data_complete=True,
    )
    qd = det_kernel.finite_character_quotient()
    assert qd.image_order() == int(qd.image_keys().cardinality()) == 2
    assert qd.index() == 2
    pre_only = G.discriminant_preimage(OG.trivial_subgroup())
    qp = pre_only.finite_character_quotient()
    assert qp.image_order() == int(qp.image_keys().cardinality())
    assert qp.index() == 2
    # Without discriminant characters the discriminant image is uncharacterized.
    for quotient in (q, qd):
        try:
            quotient.discriminant_image()
            raise AssertionError("expected ValueError: no discriminant character")
        except ValueError:
            pass
    image = qp.discriminant_image()
    assert image.cardinality() == 1


def test_discriminant_image_is_the_joint_preimage_then_projection_on_three_correlated_characters() -> None:
    from sage_extensions.categories.group.predicate_subgroups import IntersectionSubgroups

    L = Lattices(ZZ)([[0, 2], [2, 0]])
    G = L.O()
    OG = L.discriminant_group().orthogonal_group()
    pre = G.discriminant_preimage(OG.trivial_subgroup())
    spinor_kernel = L.O_plus()
    det_kernel = G.predicate_subgroup(
        lambda g: g.determinant() == 1,
        "determinant one",
        character_data={"determinant_kernel": True},
        character_data_complete=True,
    )
    inter = IntersectionSubgroups(G)((pre, spinor_kernel, det_kernel))
    q = inter.finite_character_quotient()

    # Exact oracle: the listed joint image, filtered by the conjunction of
    # the three characters, projected to the discriminant factor.  Compare by
    # subgroup content: elements of a subgroup and elements of O(A_L) have
    # different parents, so equality is membership plus cardinality.
    allowed = [key for key in q.image_keys() if q._allowed(key)]
    oracle = OG.subgroup_on(tuple(key["discriminant"] for key in allowed))
    image = q.discriminant_image()
    assert int(image.cardinality()) == 1
    assert int(image.cardinality()) == int(oracle.cardinality())
    assert all(g in image for g in oracle.group_generators())
    # On this lattice the marginal separate-image formula happens to agree:
    # the stable kernel supplies every sign pattern, so the correlated-sign
    # distinction is not witnessed here; what is checked is exactness against
    # the listed oracle, with three character factors present.
    rho = L.discriminant_representation()
    marginal_pieces = [OG.trivial_subgroup()]
    for kernel in (spinor_kernel, L.SO()):
        marginal_pieces.append(
            OG.subgroup_on(tuple(rho(g) for g in tuple(kernel.group_generators())))
        )
    from sage_extensions.categories.group.groups import (
        _element_to_engine,
        _gap_model,
        _subgroup_from_gap,
    )

    marginal = marginal_pieces[0]
    for piece in marginal_pieces[1:]:
        marginal = _subgroup_from_gap(
            OG,
            libgap.Intersection(
                libgap.Subgroup(
                    _gap_model(OG), [_element_to_engine(OG, g) for g in marginal.group_generators()]
                ),
                libgap.Subgroup(
                    _gap_model(OG), [_element_to_engine(OG, g) for g in piece.group_generators()]
                ),
            )
        )
    assert int(marginal.cardinality()) == int(image.cardinality())


def test_discriminant_image_over_a_nonsurjective_representation_meets_the_target_with_the_joint_image() -> None:
    L = Lattices(ZZ)([[6, 0], [0, 6]])
    G = L.O()
    OG = L.discriminant_group().orthogonal_group()
    ambient_image = L.discriminant_image()
    outsider = next(a for a in OG if a not in ambient_image)
    target = OG.subgroup_on((outsider,))
    assert int(target.cardinality()) == 4
    preimage = G.discriminant_preimage(target)
    image = preimage.discriminant_image()
    # rho(preimage) is the target's MEET with the joint image, not the
    # target itself: taking the embedded target alone overcounts by the
    # elements rho never reaches.  Compare content by membership in both
    # directions plus cardinality: subgroup elements and O(A_L) elements
    # carry different parents.
    assert int(image.cardinality()) == 2
    expected_members = [a for a in target if a in ambient_image]
    assert len(expected_members) == 2
    assert all(a in image for a in expected_members)


def test_discriminant_lift_follows_the_image_exactly() -> None:
    L = Lattices(ZZ)([[6, 0], [0, 6]])
    G = L.O()
    OG = L.discriminant_group().orthogonal_group()
    image = L.discriminant_image()
    assert int(OG.cardinality()) == 16
    assert int(image.cardinality()) == 8
    lifts, nones, multi_letter = [], [], 0
    for automorphism in OG:
        lift = G.discriminant_lift(automorphism)
        if lift is None:
            assert automorphism not in image
            nones.append(automorphism)
        else:
            assert lift in G
            # Exact endpoint/composition check: the lifted word's induced
            # action on the discriminant module is the requested automorphism.
            # On this specimen the FQF engine multiplies by the reversed law
            # (automorphisms act on the right), so a word evaluated without
            # the law reversal induces the automorphism of the reversed word,
            # and this assert fails on every multi-letter factorization.
            assert lift.discriminant_morphism() == automorphism
            lifts.append(automorphism)
    # Surjectivity fails on exactly the elements outside rho_L(O(L)).
    assert len(lifts) == 8 and len(nones) == 8
    # The test is degenerate without a genuine multi-letter word among the
    # eight factorizations: single-letter words are reversal-invariant.
    section = G._discriminant_word_section()
    from sage_extensions.categories.group.groups import _element_to_engine

    for automorphism in lifts:
        letters = section.letters_of(_element_to_engine(OG, automorphism))
        multi_letter = max(multi_letter, len(letters))
    assert multi_letter >= 2
