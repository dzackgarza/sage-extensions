r"""A quotient ring is a finitely presented module over its cover.

$A = R[x]/I$ is generated over $R[x]$ by the class of $1$ -- the quotient map
is onto -- and the relations of that class are the elements of $I$: the
sequence $R[x]^k \xrightarrow{(g_i)} R[x]^1 \to A \to 0$ is exact when
$g_1, \dots, g_k$ generate $I$.  That is a finite presentation, so $A$ carries
a chosen one, and its dual is the kernel of the transpose of that map.

The placement is the construction's: the quotient constructor states that its
object is a module over its cover with a chosen finite presentation, so the
reading does not depend on which data the defining ideal happens to retain.

$\operatorname{Hom}_{\mathbf{Z}[x]}(\mathbf{Z}[x]/(x), \mathbf{Z}[x]) = 0$ and
$\operatorname{Hom}_{\mathbf{Z}}(\mathbf{Z}/8, \mathbf{Z}) = 0$ because both
coefficient rings are domains, and the relation of the class of $1$ is a
non-zero-divisor there: every functional kills the class of $1$, hence
everything.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_class_of_one_modulo_x_is_presented_over_the_polynomial_ring() -> None:
    r"""$\mathbf{Z}[x]/(x)$ is cyclic over $\mathbf{Z}[x]$, and its dual is zero.

    The class of $1$ generates, and the one relation is $x \cdot 1 = 0$.  A
    functional $\varphi$ with $\varphi(1) = m$ satisfies $xm = 0$, and
    $\mathbf{Z}[x]$ is a domain, so $m = 0$: the dual vanishes, and so do the
    values of every functional at the class of $x$.
    """
    ring = ZZ["x"]
    x = ring.algebra_generator("x")
    quotient = ring.quotient_ring(ring.ideal(x))

    assert quotient.number_of_module_generators() == 1
    assert quotient.dual_module().is_zero()
    assert quotient(x).order_ideal() == ring.ideal(0)


def test_the_class_of_three_modulo_eight_is_presented_over_the_integers() -> None:
    r"""$\mathbf{Z}/8$ is cyclic over $\mathbf{Z}$, and its dual is zero.

    The single relation of the class of $1$ is $8 \cdot 1 = 0$, and $8$ is a
    non-zero-divisor of $\mathbf{Z}$, so the dual vanishes and the order ideal
    of the class of $3$ is the zero ideal of $\mathbf{Z}$.
    """
    ring = Zmod(8)

    assert ring.number_of_module_generators() == 1
    assert ring.dual_module().is_zero()
    assert ring(3).order_ideal() == ZZ.ideal(0)


def test_the_quotient_construction_states_its_module_reading_without_building_it() -> None:
    r"""Constructing a quotient states how it is read as a module; it builds nothing.

    The construction's datum is the ring and its defining ideal, and that datum
    already says which module the ring is: generated over its cover by the class
    of $1$, with the ideal's generators as the relations.  The reading itself is
    derived structure -- a category placement, a frame, a relation map and the
    free and regular modules they are stated in -- so it is built on the first
    request and not as a side effect of constructing the ring (``AGENTS.md``,
    "Construction is instant").

    Before that request the ring is therefore not yet an object of
    $\operatorname{ModulesWithChosenFinitePresentation}(\text{cover})$, and it
    still answers when it is asked: the first module read is the request.

    The defining ideal is this test's own.  A ring's module reading, once built,
    stays built, so a specimen that another test has already read as a module
    cannot distinguish stating the reading from building it; the quotient by
    $x^2 + x + 1$ is nobody else's.
    """
    ring = ZZ["x"]
    x = ring.algebra_generator("x")
    quotient = ring.quotient_ring(ring.ideal(x**2 + x + 1))

    assert quotient not in ModulesWithChosenFinitePresentation(ring)
    assert quotient.has_selected_module_resolution()
    assert quotient in ModulesWithChosenFinitePresentation(ring)
    assert quotient.number_of_module_generators() == 1
