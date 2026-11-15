r"""Which category level answers the operations a refinement rebuilds a class for.

Refining an object into another category rebuilds its class with the categories
it now reaches, and when two of those levels declare the same operation the
rebuild keeps the one the final category order names.  Three operations answer
that way, each measured here by what it returns.

``QQ(i)`` is the object all three act on: an algebra over ``QQ`` that is also a
finitely generated framed free module, a module with a chosen finite
presentation, and an infinite ring.

* ``order_ideal`` is ``Modules.ElementMethods.order_ideal`` -- the image of the
  linear functionals -- not the coordinate reading of
  ``FramedFreeModules.ElementMethods.order_ideal``.
* ``__iter__`` is ``OwnedRings.ParentMethods.__iter__``, which enumerates a ring
  only among finite sets, not the fair coordinate enumeration of
  ``FramedFreeModules.FinitelyGenerated.ParentMethods``.
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
    coordinate reading states an ideal of the same ring as well, so the returned
    ideal alone does not say which of the two answered.
    """
    field = QuadraticField(-1)
    element = field(1 + field.primitive_element())

    assert element.order_ideal() == QQ.ideal(1)


def test_an_infinite_ring_states_no_enumeration_of_its_points() -> None:
    r"""$\mathbf{Q}(i)$ is not finite, so ``__iter__`` refuses instead of enumerating.

    ``OwnedRings.ParentMethods.__iter__`` answers: a ring enumerates its points
    through its selected engine when it is placed among finite sets, and
    $\mathbf{Q}(i)$ is infinite.  The framed free module's enumeration of
    coordinate tuples over $\{1, i\}$ would hand back an iterator instead of
    refusing, so the refusal is the statement that the ring's points are not
    enumerated at all.
    """
    field = QuadraticField(-1)

    with pytest.raises(TypeError):
        iter(field)


def test_the_ring_states_the_completion_of_the_field_at_the_zero_ideal() -> None:
    r"""$\lim_n \mathbf{Q}(i)/(0)^n = \mathbf{Q}(i)$: the ring's own completion.

    ``OwnedRings.ParentMethods.adic_completion`` answers.  The module level's
    base change $M \otimes_R \hat{R}$ would need the ideal to be an ideal of the
    module's base ring, and the zero ideal of $\mathbf{Q}(i)$ is not an ideal of
    $\mathbf{Q}$; the ring's inverse limit is defined, and at $(0)$ in a field
    every quotient $\mathbf{Q}(i)/(0)^n$ is the field itself.
    """
    field = QuadraticField(-1)
    completion = field.adic_completion(field.ideal(0))

    assert completion.completion_source() is field
    assert completion.completion_map().domain() is field
