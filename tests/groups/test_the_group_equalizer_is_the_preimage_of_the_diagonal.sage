r"""A group equalizer is the preimage of the diagonal under $(f, g)$.

For parallel homomorphisms $f, g: G \to H$ with $H$ finite, the equalizer is
$E = (f,g)^{-1}(\Delta H) \le G$: the product $H \times H$ supplies the pair
map and the diagonal, and the preimage owner supplies the finite-index coset
space and the Schreier generating morphism of $E$.

The specimen is $G = F(a,b)$, $H = S_3$, $f(a) = (12)$, $f(b) = (123)$ and
$g = \mathrm{conj}_{(12)} \circ f$.  Then $E = f^{-1}(C_{S_3}((12)))$ has index
3, $a \in E$, and $bab^{-1} \notin E$, so $E$ is not a kernel.

The preimage is named through its owner: the morphism whose domain it lies in
constructs it (``GroupMorphism.preimage_subgroup``), and the equalizer reads
its datum back from that construction, the pair map and the diagonal.  A test
does not name the preimage construction's class, which the session does not
publish; the defining relation and the owner's own accessors state the same
subobject.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _the_equalizer_specimen():
    free = Groups.Free(2)
    basis = tuple(free.free_basis())
    a, b = free.free_generator(basis[0]), free.free_generator(basis[1])
    symmetric = Groups.S(3)
    transposition, cycle = symmetric((1, 2)), symmetric((1, 2, 3))
    f = free.Mor(symmetric)({basis[0]: transposition, basis[1]: cycle})
    g = symmetric.Mor(symmetric).elementwise(
        lambda x: transposition * x * ~transposition
    ) * f
    construction = Groups().equalizer_construction(f, g)
    shape = construction.diagram().domain()
    return a, b, f, g, construction, construction.object(), construction.structure_morphism(shape.source())


def _the_equalizer():
    r"""The equalizer subgroup alone, for a measurement of its construction."""
    a, b, f, g, construction, equalizer, inclusion = _the_equalizer_specimen()
    return equalizer


def _specimen_words(a, b):
    r"""Words of $F(a,b)$: ``a``, ``aa``, ``bab`` and ``abab`` lie in $E$, the others do not."""
    return (a, b, b * a, b * a * ~b, a * a, b * a * b, a * b * a * b)


def test_the_equalizer_is_the_preimage_of_the_diagonal() -> None:
    a, b, f, g, construction, equalizer, inclusion = _the_equalizer_specimen()
    free = inclusion.codomain()
    assert equalizer in Subgroups(free)
    assert inclusion.domain() is equalizer and inclusion.codomain() is free
    assert f(inclusion(a)) == g(inclusion(a))
    assert a in equalizer
    assert b * a * ~b not in equalizer
    pair_map, diagonal = equalizer.preimage_morphism(), equalizer.target_subgroup()
    # The equalizer's retained datum is the preimage datum: the pair map and
    # the diagonal, and the relation they cut out.  Restating the preimage
    # through the owner that constructs it yields the same subobject.
    restated = pair_map.preimage_subgroup(
        diagonal, stated_clause=lambda: "f(g) = g(g)"
    )
    assert restated in Subgroups(free)
    assert all(
        (element in equalizer) == (pair_map(element) in diagonal)
        for element in _specimen_words(a, b)
    )
    assert all(
        (element in restated) == (element in equalizer)
        for element in _specimen_words(a, b)
    )
    assert pair_map.domain() is free and diagonal.supergroup() is pair_map.codomain()
    assert diagonal.is_parent_of(pair_map(a)) and not diagonal.is_parent_of(pair_map(b))
    # The pair map's image is u(G), of order 6, not the whole product H x H.
    assert pair_map.image().cardinality() == cardinal(6)


def test_the_equalizer_retains_its_coset_space_and_generating_epimorphism() -> None:
    a, b, f, g, construction, equalizer, inclusion = _the_equalizer_specimen()
    space = equalizer.coset_space()
    base = space.base_point()
    assert space.cardinality() == cardinal(3)
    assert equalizer.index() == cardinal(3)
    # Every coset is reached from the identity coset by an actual element of
    # the ambient group, carried by the section the coset space retains.
    assert all(
        space.act(space.representative_map()(coset), base) == coset for coset in space
    )
    augmentation = equalizer.schreier_generating_morphism()
    words = equalizer.schreier_generators()
    assert augmentation.codomain() is equalizer
    assert augmentation.domain().free_basis() == words.index_set()
    assert all(augmentation(x) in equalizer for x in augmentation.domain().group_generators())
    # The reported family is the coset space's own Schreier family, and its
    # images are the family the equalizer's selected resolution generates E
    # by: every element of E is a product of the reported words.
    assert augmentation is space.schreier_generating_morphism()
    images = tuple(
        augmentation(letter) for letter in augmentation.domain().group_generators()
    )
    assert tuple(equalizer.group_generators()) == images
    assert all(equalizer.is_parent_of(word) for word in images)
    # Elements of E that are not among the reported words, as products of them.
    assert images[0] * images[0] == a * a and a * a in equalizer
    assert a * (b * a * b) in equalizer


def test_the_equalizer_factors_every_cone_through_its_inclusion() -> None:
    a, b, f, g, construction, equalizer, inclusion = _the_equalizer_specimen()
    free = inclusion.codomain()
    shape = construction.diagram().domain()
    source, target = shape.source(), shape.target()
    # f(a) = g(a), so <a> lies in E and is a cone on the parallel pair.
    cyclic = free.subgroup((a,))
    cone = construction.diagram().Cones().cone(
        cyclic,
        lambda index: (
            cyclic.inclusion() if index is source else f * cyclic.inclusion()
        ),
    )
    factor = construction.factor(cone).apex_map()
    assert factor.domain() is cyclic and factor.codomain() is equalizer
    assert all(
        construction.structure_morphism(index) * factor
        == cone.structure_morphism(index)
        for index in (source, target)
    )
    assert inclusion(factor(a)) == a


def test_the_equalizer_derives_its_coset_space_once() -> None:
    r"""The coset space is one datum: the index and the family read it.

    The equalizer's construction computes nothing: no orbit is swept until the
    coset space is asked for.  The coset space asked for twice, the index, and
    the Schreier generating morphism are four requests for one datum, so they
    run one sweep between them.
    """
    equalizer, answer, swept, asked = orbit_sweeps_of(
        _the_equalizer,
        lambda built: (
            built.coset_space(),
            built.coset_space(),
            built.index(),
            built.schreier_generating_morphism(),
        ),
    )
    assert swept == 0
    assert asked == 1
    space, again, index, augmentation = answer
    assert space is again
    assert index == cardinal(3)
    assert space.cardinality() == cardinal(3)
    assert augmentation is space.schreier_generating_morphism()
    assert augmentation.codomain() is equalizer
