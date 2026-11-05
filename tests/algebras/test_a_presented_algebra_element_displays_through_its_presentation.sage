r"""An element of a presented algebra displays as the class of a lift.

``A = P / (xy)`` with ``P = QQ[x, y]``: every element of ``A`` is the class
``[f]`` of a polynomial ``f`` of ``P`` (Atiyah--Macdonald, Ch. 1, quotient
rings), so its display is the class of its lift to the presentation ring the
construction names.  Regression for sage-extensions#144.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_an_element_of_a_presented_algebra_is_the_class_of_its_lift() -> None:
    presentation = QQ.polynomial_ring(("x", "y"))
    x, y = presentation.algebra_generators()
    axes = presentation.quotient_by_relations((x * y,))
    element = axes.algebra_generator("x") + 2 * axes.algebra_generator("y")

    assert str(element) == f"[{x + 2 * y}]"
