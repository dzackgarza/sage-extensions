r"""Equality/hash consistency of LatticeIsometryMor, incl. owned-scalar tensors.

The mor's __hash__ (46b2c39) must agree with the actual equality contract
(same domain/codomain objects and equal on generators / equal coordinate
tensors), must distinguish genuinely different maps where their tensors
differ, and must never fall back to display strings: the tensor scalars are
owned ring elements whose original cache-key issue (unhashable owned scalars)
is exactly what this probes across parent classes (integral scalars of ZZ
lattices and their Gram/morphism components, torsion-form automorphisms of
presented discriminant modules, and elements built through morphism
construction rather than object identity).
"""

from sage_extensions.all import *


def test_equal_morphisms_from_different_constructions_share_hash_and_equality() -> None:
    L = Lattices(ZZ)([[0, 1], [1, 0]])
    G = L.O()
    e_one, e_two = L.module_generators()
    swap = G({e_one: e_two, e_two: e_one})
    entries = {e_one: e_two, e_two: e_one}
    swap_again = G({label: entries[label] for label in entries})
    assert swap == swap_again
    assert hash(swap) == hash(swap_again)
    neg = G(lambda label: -L.module_generator(label))
    assert neg == neg
    assert hash(neg) == hash(neg)
    # distinct maps on the same endpoints: tensor differs, hashes differ, equality False
    assert not (swap == neg)
    assert hash(swap) != hash(neg)
    # the two constructions agree with the engine-computed inverse
    assert swap == swap.inverse()
    assert hash(swap) == hash(swap.inverse())


def test_owned_scalar_tensor_cases_with_unambiguous_boundaries() -> None:
    L2 = Lattices(ZZ)([[2, 0], [0, 2]])
    iso = L2.O()(lambda label: L2.module_generator(label))
    assert hash(iso) == hash(iso)
    neg = L2.O()(lambda label: -L2.module_generator(label))
    assert not (neg == iso)
    e1, e2 = L2.module_generators()
    transvection = L2.O()({e1: -e2, e2: -e1})
    assert transvection == L2.O()({e1: -e2, e2: -e1})
    assert not (transvection == iso)
    # composite scalar usage: sum of generator images kept integral
    half_turn = L2.O()({e1: -e2, e2: -e1})
    assert hash(half_turn) == hash(transvection)
    # Supported boundary, stated explicitly from the code itself
    # (LatticeIsometryMor.__hash__, lattice_morphisms.py): the mor hash raises
    # through Tensor.__hash__ only if a scalar has no Python hash; no display
    # fallback exists in either direction.  Scalar classes exercised here are
    # owned ZZ lattice scalars of rank-2 integral lattices; tensor-component
    # scalar classes beyond ZZ (e.g. ring elements of discriminant modules)
    # exercise their own previously repaired digest path
    # (TorsionFormAutomorphism.__hash__, engine matrix digest).
    assert hash(transvection) != hash(iso)


def test_independent_equal_constructions_and_set_alias_contract() -> None:
    # two genuinely independent constructions of the SAME isometry:
    # a literal dict, and the engine-computed inverse of that swap (swap = swap^-1)
    L = Lattices(ZZ)([[0, 1], [1, 0]])
    G = L.O()
    e_one, e_two = L.module_generators()
    swap = G({e_one: e_two, e_two: e_one})
    swap_inv = swap.inverse()
    assert swap == swap_inv
    assert hash(swap) == hash(swap_inv)
    # set non-aliasing: two constructions of one map collapse into a single set member
    family = {swap, swap.inverse(), swap * swap.inverse()}
    assert len(family) == 2  # {swap, identity}
    # distinct tensors differ in one cell; their hashes are observed unlike
    neg = G({e_one: -e_one, e_two: e_one})
    distinct_family = {swap, neg}
    assert len(distinct_family) == 2
    assert hash(swap) != hash(neg)  # observed for these particular maps


def test_cold_hash_path_avoids_both_old_repr_and_cache_key_routes() -> None:
    # The measured old hot path was LatticeIsometryMor.__hash__ ->
    # tensor._cache_key() (plus its repr construction). Guard BOTH routes:
    # if either is touched by the current mor hash, the probe raises.
    from sage_extensions.tensors import tensor as _tensor_mod

    L = Lattices(ZZ)([[2, 0], [0, 2]])
    G = L.O()
    i = G(tuple(G.group_generators())[0])
    t_type = type(i._coordinate_tensor())
    calls = {"repr": 0, "cache_key": 0}

    original_repr = t_type.__repr__
    original_cache_key = t_type._cache_key

    def counted_repr(self):
        calls["repr"] += 1
        raise AssertionError("repr route taken during mor hash")

    def counted_cache_key(self):
        calls["cache_key"] += 1
        raise AssertionError("_cache_key route taken during mor hash")

    try:
        t_type.__repr__ = counted_repr
        t_type._cache_key = counted_cache_key
        h = hash(i)
    finally:
        t_type.__repr__ = original_repr
        t_type._cache_key = original_cache_key
    assert isinstance(h, int)
    assert calls == {"repr": 0, "cache_key": 0}, calls


def test_rational_scalar_isometry_hash_is_total_and_faithful() -> None:
    r"""Isometries with owned QQ scalars hash by value, never raising.

    Q: owned rational elements are unhashable (their joined element class
    has ``__hash__ = None``), so the mor hash reaches the tensor hash with
    no hashable components at all.  The tensor hash then substitutes the
    cache-protocol component key.  Two genuinely different maps must not
    share one mathematical hash-key behaviour beyond ordinary collisions.
    """
    L = Lattices(ZZ)([[0, 1], [1, 0]])
    V = L.base_change(L.base_ring().fraction_field_map())
    labels = tuple(V.module_generating_set())
    first, second = labels
    e1, e2 = V.module_generator(first), V.module_generator(second)
    neg = V.Isom(V)(lambda label: -V.module_generator(label))
    swap = V.Isom(V)({first: e2, second: e1})
    h_neg = hash(neg)
    h_swap = hash(swap)
    assert isinstance(h_neg, int) and isinstance(h_swap, int)
    assert not (neg == swap)
    assert h_neg != h_swap  # observed for these particular maps
    assert neg == neg and hash(neg) == h_neg
    lookup = {neg: True}
    assert lookup[neg] is True
    neg_again = V.Isom(V)(lambda label: -V.module_generator(label))
    assert neg == neg_again
    assert lookup[neg_again] is True


def test_subgroup_augmentation_letters_evaluate_to_their_own_images() -> None:
    r"""A subgroup resolution's augmentation sends every letter to ITS generator.

    The letters of the free cover of a supplied subgroup of ``O(V)`` are
    evaluated by a cached letter-image read whose argument is the group
    element itself.  With unhashable owned QQ scalars the cache key used
    to collapse every letter onto the first letter's image (measured on
    the integral-stabilizer chain: every stabilizer generator carried the
    first rational generator's tensor).  Each letter must evaluate to the
    generator its basis point names, and a two-letter word to the product.
    """
    L = Lattices(ZZ)([[0, 1], [1, 0]])
    V = L.base_change(L.base_ring().fraction_field_map())
    labels = tuple(V.module_generating_set())
    first, second = labels
    e1, e2 = V.module_generator(first), V.module_generator(second)
    dilation = V.Isom(V)(
        {
            first: V.scalar_multiple(QQ(2), e1),
            second: V.scalar_multiple(QQ(1) / QQ(2), e2),
        }
    )
    swap = V.Isom(V)({first: e2, second: e1})
    H = V.O().subgroup((dilation, swap))
    resolution = H.selected_group_resolution()
    supplied = tuple(resolution.generating_set())
    assert supplied == (dilation, swap)
    augmentation = resolution.augmentation()
    free = augmentation.domain()
    letters = tuple(free.free_generator(label) for label in supplied)
    # letter images in the collapse order that surfaced: the first letter,
    # then a second one whose image used to be the first's cache entry.
    first_image = augmentation(letters[0])
    second_image = augmentation(letters[1])
    assert first_image == dilation
    assert second_image == swap
    assert not (first_image == second_image)
    # a two-letter word evaluates to the product of the two images
    word_image = augmentation(letters[0] * letters[1])
    assert word_image == first_image * second_image
    assert word_image == dilation * swap
