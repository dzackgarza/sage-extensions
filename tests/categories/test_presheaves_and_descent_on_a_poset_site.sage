r"""Presheaves, covers and descent on the poset of open sets of a two-point discrete space.

The site is the poset $\{E \le A, B \le X\}$: the opens $\emptyset$,
$\{a\}$, $\{b\}$, $\{a, b\}$ of a discrete two-point space, ordered by
inclusion.  As a thin category it has one arrow $V \to W$ exactly when
$V \le W$: four identities and five others.  $X$ is covered by $A$ and $B$
with overlap $E$.

For a presheaf $F$ the descent comparison is the canonical map
$F(X) \to \operatorname{Eq}(F(A) \times F(B) \rightrightarrows F(E))$.  For
the constant presheaf with value $2 = \{0, 1\}$ both restriction maps are
identities, so the equalizer is the diagonal of $2 \times 2$, with two
points, and the canonical map $x \mapsto (x, x)$ is a bijection.
Postcomposing a presheaf with the power-set functor gives the presheaf
$V \mapsto P(F(V))$, which has $2^2 = 4$ elements over each open.  The
Yoneda presheaf $\mathrm{Mor}(-, X)$ has one element over each open, since
every open lies in $X$.  All of these are the definitions of the
constructions.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _open_sets_of_two_points():
    labels = Sets()(("X", "A", "B", "E"))
    below = {("A", "X"), ("B", "X"), ("E", "A"), ("E", "B"), ("E", "X")}
    return PosetCategory(labels, le=lambda left, right: left == right or (left, right) in below)


def _cover_of_the_whole_space(site):
    def arrow(source, target):
        return site.Mor(site(source), site(target)).unique()

    families = CoveringFamilies(site)
    cover = families.family(
        site("X"),
        {"A": arrow("A", "X"), "B": arrow("B", "X")},
        {("A", "B"): (site("E"), arrow("E", "A"), arrow("E", "B"))},
    )
    return Coverage(site, families), cover


def _constant_two(site):
    presheaves = site.presheaves()
    return presheaves(presheaves.constant_functor(Sets.Δ[1]))


def test_the_poset_of_opens_is_a_thin_category_with_nine_arrows() -> None:
    site = _open_sets_of_two_points()
    empty_to_whole = site.Mor(site("E"), site("X"))
    empty_to_point = site.Mor(site("E"), site("A")).unique()
    point_to_whole = site.Mor(site("A"), site("X")).unique()

    assert site.arrows().cardinality() == cardinal(9)
    assert site.le("E", "X")
    assert not site.le("X", "E")
    assert empty_to_whole.cardinality() == cardinal(1)
    assert site.Mor(site("X"), site("E")).cardinality() == cardinal(0)
    assert point_to_whole * empty_to_point == empty_to_whole.unique()
    assert site.identity(site("X")) == site.Mor(site("X"), site("X")).unique()


def test_the_cover_of_the_whole_space_by_its_two_points_has_the_empty_overlap() -> None:
    site = _open_sets_of_two_points()
    _coverage, cover = _cover_of_the_whole_space(site)
    reversed_overlap = cover.overlap_span("B", "A")

    assert cover.target() is site("X")
    assert cover.index_set().cardinality() == cardinal(2)
    assert cover.member("A") == site.Mor(site("A"), site("X")).unique()
    assert reversed_overlap.left_leg() == site.Mor(site("E"), site("B")).unique()
    assert reversed_overlap.right_leg() == site.Mor(site("E"), site("A")).unique()


def test_the_constant_presheaf_two_satisfies_descent_for_the_cover() -> None:
    site = _open_sets_of_two_points()
    coverage, cover = _cover_of_the_whole_space(site)
    presheaf = _constant_two(site)
    two = Sets.Δ[1]
    equalizer = DescentEqualizer(coverage, presheaf, cover)
    canonical = equalizer.canonical_map()

    assert equalizer.local_product_construction().object().cardinality() == cardinal(4)
    assert equalizer.matching_product_construction().object().cardinality() == cardinal(2)
    assert equalizer.equalizer_object().cardinality() == cardinal(2)
    assert canonical.domain() is two
    assert canonical(two(0)) != canonical(two(1))


def test_the_descent_parallel_pair_is_a_pair_of_maps_of_sets() -> None:
    r"""The two Čech maps $F(A) \times F(B) \rightrightarrows F(E)$ are the two projections."""
    site = _open_sets_of_two_points()
    coverage, cover = _cover_of_the_whole_space(site)
    left, right = DescentEqualizer(coverage, _constant_two(site), cover).parallel_maps()

    assert left != right


def test_trivial_descent_data_make_the_constant_presheaf_a_sheaf_for_the_trivial_coverage() -> None:
    site = _open_sets_of_two_points()
    presheaf = _constant_two(site)
    data = DescentData.trivial(presheaf)
    sheaves = data.coverage().sheaves()
    sheaf = sheaves(presheaf, data)

    assert sheaf in site.presheaves()
    assert sheaf.descent_data() is data
    assert sheaves.identity(sheaf) == site.presheaves().Mor(sheaf, sheaf).identity()


def test_the_trivial_descent_comparison_on_the_identity_cover_is_the_identity() -> None:
    r"""For the identity cover of $X$ the descent comparison is the identity of $F(X)$."""
    site = _open_sets_of_two_points()
    data = DescentData.trivial(_constant_two(site))
    comparison = data.comparison(data.coverage().family(site("X"))).isomorphism()

    assert comparison.domain() is Sets.Δ[1]
    assert all(comparison(point) == point for point in Sets.Δ[1])


def test_postcomposing_with_the_power_set_functor_squares_the_values() -> None:
    site = _open_sets_of_two_points()
    transport = Cat().presheaf_transport(IdentityFunctor(site), Sets().power_set_functor())
    transported = transport(_constant_two(site))

    assert transported.functor()(site.opposite()(site("A"))).cardinality() == cardinal(4)
    assert transported.functor()(site.opposite()(site("E"))).cardinality() == cardinal(4)


def test_presheaf_transport_carries_the_identity_transformation_to_the_identity() -> None:
    site = _open_sets_of_two_points()
    presheaves = site.presheaves()
    presheaf = _constant_two(site)
    transport = Cat().presheaf_transport(IdentityFunctor(site), Sets().power_set_functor())

    assert transport(presheaves.Mor(presheaf, presheaf).identity()) == transport(presheaf).Mor(
        transport(presheaf)
    ).identity()


def test_the_yoneda_presheaf_of_the_whole_space_has_one_section_over_each_open() -> None:
    site = _open_sets_of_two_points()
    representable = site.yoneda_embedding()(site("X")).functor()

    assert representable(site.opposite()(site("A"))).cardinality() == cardinal(1)
    assert representable(site.opposite()(site("X"))).cardinality() == cardinal(1)
