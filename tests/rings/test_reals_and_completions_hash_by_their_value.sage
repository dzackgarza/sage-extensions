r"""The reals and the elements of an adic completion hash by their value.

:class:`Sets` states that every object hashes consistently with its equality.
An exact real decides equality of two presentations through the difference of
its expression, exactly and by algebra: ``sqrt(2)^2`` and ``2`` are one real,
and the coercion from the integers makes ``RR(2)`` and ``2`` one real too.
An element of an adic completion decides it on the retained exact source
expressions, so ``x + 1`` and ``x + 1`` computed from the two summands are one
element, and the image of a ring element is that ring element.  Neither
equality reads a presentation, so neither class can hash one; each hashes the
value, and equal elements hash alike.
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


def test_an_exact_real_hashes_as_the_number_it_equals() -> None:
    r"""``RR(2) = 2`` and ``RR(1/2) = 1/2``: the real and the exact number it is.

    The integers and the rationals coerce into the exact reals, so ``RR(2)``
    and ``2`` are one real and ``RR(1/2)`` and ``1/2`` are one real.  A finite
    ordered set holds one point for each pair, and a dictionary finds the value
    it was given by either name, which is the hash agreeing with that equality.

    ``sqrt(2)^2`` is the same real as ``2`` by the algebraic decision, so it
    enters such a set as the integer's point too.
    """
    two = RR(2)
    half = RR(QQ(1) / 2)

    assert two == ZZ(2)
    assert hash(two) == hash(ZZ(2))
    assert half == QQ(1) / 2
    assert hash(half) == hash(QQ(1) / 2)
    assert {ZZ(2): "two"}[two] == "two"
    assert FiniteOrderedSets()((two, ZZ(2))).cardinality() == 1
    assert FiniteOrderedSets()((RR(2).sqrt() ** 2, ZZ(2))).cardinality() == 1
    assert FiniteOrderedSets()((half, QQ(1) / 2)).cardinality() == 1


def test_two_algebraic_presentations_of_one_irrational_real_are_one_point() -> None:
    r"""``sqrt(8)/2 = sqrt(2)``: one value, two expressions, one point.

    The algebraic decision of the difference places both in the same real
    algebraic number, so they hash alike; the rational ``2`` is a different
    value, so a set of it and ``sqrt(2)`` holds two points.
    """
    root = RR(2).sqrt()
    eighth_root_halved = RR(8).sqrt() / 2

    assert root == eighth_root_halved
    assert hash(root) == hash(eighth_root_halved)
    assert FiniteOrderedSets()((root, eighth_root_halved)).cardinality() == 1
    assert FiniteOrderedSets()((root, RR(2))).cardinality() == 2


def test_a_real_written_transcendentally_hashes_as_the_value_it_equals() -> None:
    r"""``cos(1)^2 + sin(1)^2 = 1``: one real, whatever the presentation's shape.

    Equality decides this by normalizing the difference, and the normalization
    places ``sin(1)^2 + cos(1)^2`` at the algebraic number ``1``.  The hash
    answers the same question about the same value, so it reads the value
    through that normalization too; a hash that read only the presentation's
    shape would separate two reals it has already decided are one.
    ``2 sin(1)^2 + 2 cos(1)^2`` is the same value with a coefficient in front
    of it, and the same holds of ``log(2)`` written as an exponential.
    """
    one = RR(1)
    trigonometric = one.sin() ** 2 + one.cos() ** 2
    scaled = RR(2) * trigonometric
    exponential = RR(2).log().exp()

    assert trigonometric == one
    assert hash(trigonometric) == hash(one)
    assert FiniteOrderedSets()((one, trigonometric)).cardinality() == 1
    assert scaled == RR(2)
    assert hash(scaled) == hash(RR(2))
    assert FiniteOrderedSets()((scaled, RR(2))).cardinality() == 1
    assert exponential == RR(2)
    assert hash(exponential) == hash(RR(2))


def test_the_image_of_a_ring_element_hashes_as_that_ring_element() -> None:
    r"""``image(1)`` is the ring's own ``1``, so the two are one point.

    The completion map is a ring map, so ``image(1)`` and ``plane.one()`` are
    one element of the completion, and the completion retains the exact source
    expression of every image.  A finite ordered set of the image and the ring
    element therefore holds one point, and the same holds for ``x`` and for
    ``x + 1``.
    """
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    completion = plane.adic_completion(plane.ideal(x), precision=3)
    image = completion.completion_map()

    assert image(1) == plane.one()
    assert hash(image(1)) == hash(plane.one())
    assert FiniteOrderedSets()((image(1), plane.one())).cardinality() == 1
    assert hash(image(x)) == hash(x)
    assert FiniteOrderedSets()((image(x), x)).cardinality() == 1
    assert hash(image(x + 1)) == hash(plane(x + 1))


def test_a_completion_element_with_no_source_hashes_the_value_it_is() -> None:
    r"""``(1 - x)^{-1} (1 - x) = 1`` in the completion, which keeps no source for it.

    The completion decides this on its exact arithmetic, so the product is the
    element ``1`` and the two presentations are one point of a finite ordered
    set.  The product keeps no exact source expression: the inverse of ``1 - x``
    is no polynomial in ``x`` and ``y``.  The value it is, though, is the
    truncation the completion computes, read back in the source ring, and that
    is what the hash reads -- the same datum the completion's own projection
    reads, and the ring's ``1`` for this element.
    """
    plane = QQ.polynomial_ring(("x", "y"))
    x = plane.algebra_generator("x")
    completion = plane.adic_completion(plane.ideal(x), precision=3)
    image = completion.completion_map()
    unit = image(1 - x)
    product = unit.inverse_of_unit() * unit

    assert product.exact_source_expression() is None
    assert product == image(1)
    assert hash(product) == hash(image(1))
    assert FiniteOrderedSets()((product, image(1))).cardinality() == 1
    assert FiniteOrderedSets()((product, image(1), completion.one())).cardinality() == 1


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
