r"""The reals and the elements of an adic completion hash by their value.

:class:`Sets` states that every object hashes consistently with its equality.
An exact real decides equality of two presentations through the difference of
its expression, exactly and by algebra: ``sqrt(2)^2`` and ``2`` are one real.
An element of an adic completion decides it on the retained exact source
expressions, so ``x + 1`` and ``x + 1`` computed from the two summands are one
element.  Neither equality reads a presentation, so neither class can hash one;
each hashes its own field, and equal elements still hash alike.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_two_presentations_of_one_real_are_one_point_of_a_finite_ordered_set() -> None:
    r"""``sqrt(2)^2 = 2``, so these two reals are one point, and ``1`` and ``2`` are two.

    The equality is the algebraic one: the difference ``sqrt(2)^2 - 2`` is zero
    in the real algebraic numbers.  Distinct reals are separated by the same
    decision, so a set of them keeps both even though the two hashes agree.
    """
    square = RR(2).sqrt() ** 2
    two = RR(2)

    assert square == two
    assert hash(square) == hash(two)
    assert FiniteOrderedSets()((square, two)).cardinality() == 1
    assert FiniteOrderedSets()((RR(1), RR(2))).cardinality() == 2


def test_two_presentations_of_one_completion_element_are_one_point() -> None:
    r"""The completion of ``QQ[x, y]`` at ``(x)``: ``x + 1`` is the image of ``1`` plus ``x``.

    The completion map is a ring map, so ``image(x + 1) = image(x) + image(1)``
    as elements; the two presentations retain ``x + 1`` and the sum of the
    images of ``x`` and ``1``, and their difference is a source element of the
    kernel ``(x)``.
    """
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    completion = plane.adic_completion(plane.ideal(x), precision=3)
    image = completion.completion_map()
    sum_of_images = image(x) + image(1)

    assert image(x + 1) == sum_of_images
    assert hash(image(x + 1)) == hash(sum_of_images)
    assert FiniteOrderedSets()((image(x + 1), sum_of_images)).cardinality() == 1
    assert FiniteOrderedSets()((image(x),)).cardinality() == 1
