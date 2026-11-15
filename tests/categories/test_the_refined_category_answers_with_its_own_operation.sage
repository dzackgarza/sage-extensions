r"""Which category level answers the operations a refinement rebuilds a class for.

Refining an object into another category rebuilds its class with the categories
it now reaches, and when two of those levels declare the same operation the
rebuild keeps the one the final category order names.

``QQ(i)`` is the object two of these act on: an algebra over ``QQ`` that is
also a finitely generated framed free module, a module with a chosen finite
presentation, and an infinite ring.

* ``order_ideal`` is ``Modules.ElementMethods.order_ideal`` -- the image of the
  linear functionals -- not the coordinate reading of
  ``FramedFreeModules.ElementMethods.order_ideal``.  On ``QQ(i)`` the two agree,
  so that example states the level only in its docstring; the value that tells
  them apart is in
  ``tests/modules/test_the_order_ideal_of_a_ring_element_over_its_base_ring.sage``,
  where the module's dual is a product and only the module level can read it.
* ``__iter__`` is ``OwnedRings.Finite.ParentMethods.__iter__``, which enumerates
  a *finite* ring's points through its selected engine; ``QQ(i)`` is not finite,
  so it states no enumeration of its points and no level of this rebuild gives
  it one.
* ``adic_completion`` is ``OwnedRings.ParentMethods.adic_completion``, the
  ring's inverse limit, not the module's base change to the completed scalar
  ring of ``ModulesWithChosenFinitePresentation.ParentMethods``.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def test_the_module_level_states_the_order_ideal_of_an_algebra_element() -> None:
    r"""$O_{\mathbf{Q}(i)}(1 + i) = \mathbf{Q}$: the image of evaluation at $1 + i$.

    ``Modules.ElementMethods.order_ideal`` answers for an element of
    $\mathbf{Q}(i)$: it is the ideal the values of the linear functionals at the
    element generate, and $1 + i \neq 0$ makes it the unit ideal of
    $\mathbf{Q}$.  The level is stated because the framed free module's
    coordinate reading states an ideal of the same ring as well, and here both
    readings give the same ideal -- so this value alone does not say which of
    the two answered.
    """
    field = QuadraticField(-1)
    element = field(1 + field.primitive_element())

    assert element.order_ideal() == QQ.ideal(1)


def test_a_finite_ring_enumerates_its_points_through_its_engine() -> None:
    r"""$\mathbf{Z}/8$ is finite, so it states its eight residue classes.

    ``OwnedRings.Finite.ParentMethods.__iter__`` answers.  The ring has eight
    points, each an element of it and each different from the others, and the
    classes of $0, \ldots, 7$ are exactly those eight points: the enumeration
    is of the ring's whole underlying set, not of a generating family of it.
    """
    ring = Zmod(8)
    points = tuple(ring)

    assert int(sum(1 for _ in points)) == int(ring.cardinality())
    assert all(point in ring for point in points)
    assert all(
        point != other
        for position, point in enumerate(points)
        for other in points[:position]
    )
    assert all(ring(residue) in points for residue in range(8))


def test_the_ring_states_the_completion_of_the_field_at_the_zero_ideal() -> None:
    r"""$\lim_n \mathbf{Q}(i)/(0)^n = \mathbf{Q}(i)$: the ring's own completion.

    ``OwnedRings.ParentMethods.adic_completion`` answers.  The module level's
    base change $M \otimes_R \hat{R}$ would need the ideal to be an ideal of the
    module's base ring, and the zero ideal of $\mathbf{Q}(i)$ is not an ideal of
    $\mathbf{Q}$; the ring's inverse limit is defined, and at $(0)$ in a field
    every quotient $\mathbf{Q}(i)/(0)^n$ is the field itself, so the completion
    map is injective and its codomain is the field again.

    The map is stated by what it is decided to be.  ``is_injective`` reads the
    kernel, which is the zero ideal; ``is_surjective`` is undecided for these
    two endpoints, because the decision between infinite sets is not
    implemented, so the test does not claim the map is a bijection.
    """
    field = QuadraticField(-1)
    completion = field.adic_completion(field.ideal(0))
    completion_map = completion.completion_map()

    assert completion.completion_map_kernel() == field.ideal(0)
    assert completion_map.is_injective() is True
    assert completion.is_isomorphic_to(field)
