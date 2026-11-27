r"""A group equalizer is the preimage of the diagonal under $(f, g)$.

For parallel homomorphisms $f, g: G \to H$ with $H$ finite, the equalizer is
$E = (f,g)^{-1}(\Delta H) \le G$: the product $H \times H$ supplies the pair
map and the diagonal, and the preimage owner supplies the finite-index coset
space and the Schreier generating morphism of $E$.

The specimen is $G = F(a,b)$, $H = S_3$, $f(a) = (12)$, $f(b) = (123)$ and
$g = \mathrm{conj}_{(12)} \circ f$.  Then $E = f^{-1}(C_{S_3}((12)))$ has index
3, $a \in E$, and $bab^{-1} \notin E$, so $E$ is not a kernel.
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


def test_the_equalizer_is_the_preimage_of_the_diagonal() -> None:
    a, b, f, g, construction, equalizer, inclusion = _the_equalizer_specimen()
    free = inclusion.codomain()
    assert equalizer in Subgroups(free)
    assert inclusion.domain() is equalizer and inclusion.codomain() is free
    assert f(inclusion(a)) == g(inclusion(a))
    assert a in equalizer
    assert b * a * ~b not in equalizer
    assert equalizer in PreimageSubgroups(free)
    pair_map, diagonal = equalizer.preimage_morphism(), equalizer.target_subgroup()
    assert pair_map.domain() is free and diagonal.supergroup() is pair_map.codomain()
    assert diagonal.is_parent_of(pair_map(a)) and not diagonal.is_parent_of(pair_map(b))
    # The pair map's image is u(G), of order 6, not the whole product H x H.
    assert pair_map.image().cardinality() == cardinal(6)


def test_the_equalizer_retains_its_coset_space_and_generating_epimorphism() -> None:
    a, b, f, g, construction, equalizer, inclusion = _the_equalizer_specimen()
    assert equalizer.coset_space().cardinality() == cardinal(3)
    assert equalizer.index() == cardinal(3)
    augmentation = equalizer.schreier_generating_morphism()
    words = equalizer.schreier_generators()
    assert augmentation.codomain() is equalizer
    assert augmentation.domain().free_basis() == words.index_set()
    assert all(augmentation(x) in equalizer for x in augmentation.domain().group_generators())
