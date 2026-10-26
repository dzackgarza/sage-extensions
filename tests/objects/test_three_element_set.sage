from sage_extensions.all import *


def three():
    return Set([1, 2, 3])


def test_the_list_and_the_tuple_constructions_agree() -> None:
    assert Set((1, 2, 3)) == three()


def test_the_category_applied_to_the_points_agrees() -> None:
    assert Sets()([1, 2, 3]) == three()


def test_the_standard_three_element_set_is_isomorphic() -> None:
    r"""$|\operatorname{Iso}(\{1,2,3\}, \{0,1,2\})| = 3! = 6$."""
    assert Sets.Δ[2].cardinality() == 3
    assert Sets().Iso(three(), Sets.Δ[2]).cardinality() == 6


def test_the_categories_of_a_three_element_set() -> None:
    assert three() in Sets()
    assert three() in FiniteSets()
    assert three() in CountableSets()


def test_membership_and_cardinality() -> None:
    points = three()
    assert points.cardinality() == 3
    assert 2 in points
    assert 4 not in points


def test_maps_out_of_and_into_a_three_element_set() -> None:
    r"""$|\operatorname{End}| = 3^3 = 27$, $|\operatorname{Aut}| = 3! = 6$, and one map to a point."""
    points = three()
    assert points.End().cardinality() == 27
    assert points.Aut().order() == 6
    assert points.Aut().is_isomorphic_to(Groups.S(3))
    assert Sets().Mor(points, Sets.Δ[0]).cardinality() == 1


def test_a_subset_by_a_condition() -> None:
    points = three()
    large = points.condition_set(lambda n: n > 1)
    assert large.cardinality() == 2
    assert 3 in large
    assert 1 not in large
    assert large.inclusion().codomain() is points


def test_a_subset_by_an_image() -> None:
    r"""$\{n^2 : n \in \{1,2,3\}\} = \{1, 4, 9\}$; the image of the identity is everything."""
    points = three()
    squares = points.image_set(lambda n: n ^ 2)
    assert squares.cardinality() == 3
    assert 4 in squares
    assert 2 not in squares
    assert Sets.Δ[2].image_set(lambda n: n).cardinality() == 3


def test_a_three_element_set_has_one_endomorphism_category() -> None:
    points = three()
    endomorphisms = points.Mor(points)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert points.Mor(points) is endomorphisms
    assert points.End() is endomorphisms
    assert identity * identity == identity
