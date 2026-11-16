r"""An Eichler transvection is the rank-two update of the identity that equation (4) states.

For isotropic \(e\) and \(a\in e^\perp\),

\[
t(e,a)\colon v\longmapsto v-(a,v)\,e+(e,v)\,a-\tfrac12(a,a)(e,v)\,e ,
\]

equation (4) of Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1, printed
p. 8, which as a linear map on the framing of the lattice is

\[
t(e,a) = \mathrm{id} - e\otimes b(a,\cdot) + a\otimes b(e,\cdot)
         - \tfrac12 q(a)\, e\otimes b(e,\cdot) .
\]

The first test asserts that tensor form, with the identity, the Gram pairings and
the outer products all read off the tensor layer.  The second asserts the images
the formula gives, on a control whose half coefficient \(\tfrac12 q(a)\) is
neither zero nor \(q(a)\).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _control():
    r"""`U + <6>` over `QQ`: `e = e_0` isotropic, `f = e_1` its hyperbolic partner, `a = e_2` of square six.

    The square is six rather than two so that `(1/2)q(a) = 3`: a construction
    that wrote `q(a)` where the formula has `(1/2)q(a)` sends the hyperbolic
    partner to `f + a - 6e` instead of `f + a - 3e`, and the half coefficient
    three is neither zero nor the square six itself.
    """
    lattice = Lattices(QQ)([[0, 1, 0], [1, 0, 0], [0, 0, 6]])
    labels = tuple(lattice.module_generating_set())
    return (
        lattice,
        lattice.module_generator(labels[0]),
        lattice.module_generator(labels[1]),
        lattice.module_generator(labels[2]),
    )


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


def test_the_transvection_is_the_rank_two_update_of_the_identity() -> None:
    r"""`t(e,a) = id - e (x) b(a,.) + a (x) b(e,.) - (q(a)/2) e (x) b(e,.)`.

    The right-hand side is equation (4) of Gritsenko--Hulek--Sankaran,
    arXiv:0810.1614, section 3.1, printed p. 8, stated as the tensor it is: one
    rank-two update of the identity endomorphism of the coordinate module.
    `(x)` is the outer product of a vector with a covector, `b` is the Gram
    tensor of the lattice -- symmetric, so the contraction `gram * v` is the
    covector `b(v,.)` -- and the identity is the Kronecker delta of the chosen
    framing.  The left-hand side is the transvection's own tensor, so the
    equation is the matrix of `t(e,a)` entry for entry.

    The control's half coefficient is `q(a)/2 = 3`, so the last term is the
    coefficient a construction can get wrong by a factor two, and three is
    neither zero nor the square six.
    """
    lattice, isotropic, _partner, orthogonal = _control()
    ring = lattice.base_ring()
    labels = tuple(lattice.module_generating_set())
    gram = lattice.gram_tensor()

    def coordinate(element):
        return tensor.vector(
            ring, tuple(element.to_vector()(label) for label in labels)
        )

    isotropic_vector = coordinate(isotropic)
    orthogonal_vector = coordinate(orthogonal)
    half_norm = ring(orthogonal.q()) / ring(2)

    update = (
        tensor.identity(ring, lattice.module_rank())
        - isotropic_vector.tensor_product(gram * orthogonal_vector)
        + orthogonal_vector.tensor_product(gram * isotropic_vector)
        - (half_norm * isotropic_vector).tensor_product(gram * isotropic_vector)
    )

    assert tensor.from_morphism(
        lattice.eichler_transvection(isotropic, orthogonal)
    ) == update
