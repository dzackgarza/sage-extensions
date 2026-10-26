from sage_extensions.all import *


def factors():
    return Sets.Δ[1], Sets.Δ[2]


def product():
    return Sets().product(factors())


def test_the_category_and_the_object_constructions_agree() -> None:
    two, three = factors()
    assert two.product_with(three) == product()


def test_the_categories_of_the_product() -> None:
    assert product() in Sets()
    assert product() in FiniteSets()


def test_the_product_has_six_elements() -> None:
    assert product().cardinality() == 6


def test_the_projections() -> None:
    two, three = factors()
    assert product().projection(0).codomain() is two
    assert product().projection(1).codomain() is three
    assert product().projection(0).is_surjective()


def test_the_universal_property_of_the_product() -> None:
    r"""Maps $f: Z \to X$ and $g: Z \to Y$ factor uniquely through $X \times Y$."""
    two, three = factors()
    both = product()
    first = Sets().Mor(three, two)(lambda point: two(0))
    second = Sets().Mor(three, three).identity()
    induced = both.from_maps(three, lambda index: first if index == 0 else second)
    assert induced.domain() is three
    assert induced.codomain() is both
    assert both.projection(0) * induced == first
    assert both.projection(1) * induced == second


def test_the_product_has_one_endomorphism_category() -> None:
    both = product()
    endomorphisms = both.Mor(both)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert both.Mor(both) is endomorphisms
    assert identity * identity == identity
