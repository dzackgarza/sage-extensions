r"""``Res_f`` acts on morphisms by the identity.

Restriction of scalars along ``f: R -> S`` changes which ring acts and never
the underlying map, so ``Res_f(g)`` is ``g``: it sends the reading of ``x`` in
``Res_f(M)`` to the reading of ``g(x)`` in ``Res_f(N)``.  This holds whether or
not the restricted module carries a framing, and ``Res(QQ^2)`` over ``ZZ``
carries none.

Unverified: written without running the suite.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _swap_of_the_rational_plane():
    r"""``QQ^2`` and the endomorphism exchanging its two basis vectors."""
    plane = QQ.free_module(2)
    e0, e1 = plane.module_generator(0), plane.module_generator(1)
    return plane, plane.module_category().Mor(plane, plane)({0: e1, 1: e0})


def test_restricting_a_rational_endomorphism_to_the_integers_keeps_its_action() -> None:
    r"""``Res(g)`` runs between the restricted parents and acts as ``g`` does."""
    plane, swap = _swap_of_the_rational_plane()
    e0, e1 = plane.module_generator(0), plane.module_generator(1)
    restriction = Modules(QQ).restriction_of_scalars(ZZ.Mor(QQ)(lambda element: QQ(element)))
    space = restriction(plane)

    restricted_swap = restriction(swap)

    assert restricted_swap.domain() is space
    assert restricted_swap.codomain() is space
    assert restricted_swap(space(e0)) == space(e1)
    assert restricted_swap(space(2 * e0 + 3 * e1)) == space(3 * e0 + 2 * e1)
    assert restricted_swap(space(plane.scalar_multiple(QQ(1) / 2, e0))) == space(
        plane.scalar_multiple(QQ(1) / 2, e1)
    )


def test_restricting_along_the_identity_keeps_the_action_of_the_endomorphism() -> None:
    r"""``Res_id(g)`` is ``g`` as well, on a restriction that does carry a framing."""
    plane, swap = _swap_of_the_rational_plane()
    e0, e1 = plane.module_generator(0), plane.module_generator(1)
    restriction = Modules(QQ).restriction_of_scalars(QQ.Mor(QQ)(lambda element: element))
    space = restriction(plane)

    restricted_swap = restriction(swap)

    assert restricted_swap.domain() is space
    assert restricted_swap.codomain() is space
    assert restricted_swap(space(e0)) == space(e1)
    assert restricted_swap(space(2 * e0 + 3 * e1)) == space(3 * e0 + 2 * e1)


def test_restricting_f2_x_mod_x2_to_f2_gives_a_plane_of_four_elements_on_which_x_squares_to_zero() -> None:
    r"""$A = \mathbb F_2[x]/(x^2)$ is free of rank $2$ over $\mathbb F_2$, so $\operatorname{Res}(A^1)$ has
    rank $2$ and $4$ elements; multiplication by $x$ restricts to a nonzero map with kernel and image
    $xA$ of order $2$ and square zero.

    Source: restriction along a finite free extension multiplies ranks; by hand.
    """
    R = GF(2)["x"]
    x = R.algebra_generator("x")
    A = R.quotient_ring(R.ideal(x**2))
    restriction = Modules(A).restriction_of_scalars(GF(2).Mor(A)(lambda scalar: A(scalar)))
    line = A**1
    e = line.module_generator(0)
    restricted = restriction(line)
    assert restricted.module_rank() == 2
    assert restricted.cardinality() == 4

    times_x = restriction(line.End()({0: A(x) * e}))
    assert times_x.kernel().cardinality() == 2
    assert times_x.image().cardinality() == 2
    assert times_x != restricted.End().zero()
    assert times_x * times_x == restricted.End().zero()
