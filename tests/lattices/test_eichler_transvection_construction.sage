r"""An Eichler transvection crosses into the owned ring with the rank, not with its square.

For isotropic \(e\) and \(a\in e^\perp\),

\[
t(e,a)\colon v\longmapsto v-(a,v)\,e+(e,v)\,a-\tfrac12(a,a)(e,v)\,e ,
\]

equation (4) of Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, printed
p. 8.  Its matrix in a basis of rank \(n\) has \(n^2\) entries, and the
arithmetic those entries need is the engine's: the vectors' coordinates and the
Gram matrix already are engine data, and the matrix the construction returns is
engine data.  The owned ring keeps the one decision only it can make,
integrality of \(\tfrac12 q(a)b(e,x)\), asked once per generator.

The first test measures the crossings that statement is about, on two ranks: a
construction that did the entries' arithmetic in the owned ring crosses once per
entry, so doubling the rank would quadruple its crossings.  The second test
asserts the images the formula gives, on a control whose half coefficient
\(\tfrac12 q(a)\) is neither zero nor \(q(a)\).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _control():
    r"""`U + <6>` over `QQ`: `e = e_0` isotropic, `f = e_1` its hyperbolic partner, `a = e_2` of square six.

    The square is six rather than two so that `(1/2)q(a) = 3`: a construction
    that wrote `q(a)` where the formula has `(1/2)q(a)` sends the hyperbolic
    partner to `f + a - 6e` instead of `f + a - 3e`, and six is neither zero nor
    the square itself.
    """
    lattice = Lattices(QQ)([[0, 1, 0], [1, 0, 0], [0, 0, 6]])
    labels = tuple(lattice.module_generating_set())
    return (
        lattice,
        lattice.module_generator(labels[0]),
        lattice.module_generator(labels[1]),
        lattice.module_generator(labels[2]),
    )


def test_a_transvection_crosses_into_the_owned_ring_once_per_generator() -> None:
    r"""Doubling the rank at most doubles one transvection's owned-ring crossings.

    The rank-three lattice is `U + <6>` and the rank-six one is its orthogonal
    direct sum with itself, so `rank^2` goes from nine to thirty-six while the
    generator count goes from three to six.  An arrangement that did the
    entries' arithmetic in the owned ring would multiply the crossings by the
    entries, and its ratio here would be four; the assertion is that the ratio
    is at most two, which is what one decision per generator costs.
    """
    small, small_isotropic, _small_partner, small_orthogonal = _control()
    large = _control()[0] + _control()[0]
    large_labels = tuple(large.module_generating_set())
    large_isotropic = large.module_generator(large_labels[0])
    large_orthogonal = large.module_generator(large_labels[2])

    small_transvection, small_crossings = owned_ring_crossings(
        lambda: small.eichler_transvection(small_isotropic, small_orthogonal)
    )
    large_transvection, large_crossings = owned_ring_crossings(
        lambda: large.eichler_transvection(large_isotropic, large_orthogonal)
    )

    assert small.module_rank() == 3
    assert large.module_rank() == 6
    assert small_transvection(small_isotropic) == small_isotropic
    assert large_transvection(large_isotropic) == large_isotropic
    assert large_crossings <= 2 * small_crossings


def test_a_transvection_moves_the_hyperbolic_partner_by_the_half_coefficient() -> None:
    r"""`t(e) = e`, `t(a) = a - q(a)e` and `t(f) = f + a - (1/2)q(a)e`, with `q(a) = 6`.

    The two non-diagonal images are the formula's two coefficients: `t(a)` fixes
    the sign of the `-(a,v)e` term, and `t(f)` reads `(1/2)q(a)`, which is the
    coefficient a construction can get wrong by a factor two.  `b(e,f) = 1`, so
    the term `(e,v)a` vanishes on `a` and is `a` on `f`.
    """
    lattice, isotropic, partner, orthogonal = _control()
    ring = lattice.base_ring()
    assert isotropic.q() == ring.zero()
    assert isotropic.b(orthogonal) == ring.zero()
    assert isotropic.b(partner) == ring.one()
    half_norm = orthogonal.q() / ring(2)
    assert half_norm == ring(3)

    transvection = lattice.eichler_transvection(isotropic, orthogonal)

    assert transvection(isotropic) == isotropic
    assert transvection(orthogonal) == orthogonal - lattice.scalar_multiple(orthogonal.q(), isotropic)
    assert transvection(partner) == partner + orthogonal - lattice.scalar_multiple(half_norm, isotropic)
