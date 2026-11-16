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
neither zero nor \(q(a)\).  The third asserts the refusal of a transvection whose
update leaves the ring: the construction carries the transvection, the lattice and
the coefficient of the update that lies outside the ring, where a refusal by the
conversion of one entry carries only that rational.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


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
    framing.  `e` and `a` enter as `tensor.coordinates`, their coordinate vectors
    in that framing.  The left-hand side is the transvection's own tensor, so the
    equation is the matrix of `t(e,a)` entry for entry.

    The control's half coefficient is `q(a)/2 = 3`, so the last term is the
    coefficient a construction can get wrong by a factor two, and three is
    neither zero nor the square six.
    """
    lattice, isotropic, _partner, orthogonal = _control()
    ring = lattice.base_ring()
    gram = lattice.gram_tensor()

    isotropic_vector = tensor.coordinates(isotropic)
    orthogonal_vector = tensor.coordinates(orthogonal)
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


def test_a_transvection_that_does_not_preserve_the_lattice_is_refused() -> None:
    r"""`U + <1>`: `q(a) = 1` is odd and `e = e_0` has divisibility one, so `t(e,a)` leaves `L`.

    The update's half coefficient is `q(a) b(e, e_1)/2 = 1/2`, and
    `t(e,a)(f) = f + a - (1/2)e` is not a vector of `L`.  `eichler_transvection`
    refuses the pair, and the refusal is the construction's own: it carries the
    transvection's pair `(e, a)`, the lattice and the coefficient of the update
    that leaves the ring, together with the position it stands at, so a reader of
    the refusal knows which transvection, which lattice and which coefficient.
    The reading of the update over `ZZ` refuses the same coefficient as a rational
    it cannot convert, and names only that rational.

    The coefficient is `-1/2`, the entry of the first row and the hyperbolic
    partner's column: `t(f) = f + a - (1/2)e` read in the framing `(e, f, a)`, so
    the refusal's position is the first row and the second column.

    The second specimen is the same lattice with `e` replaced by `2e_0`.  Then
    `b(e, x)` is even for every `x`, the half coefficient is an integer, and the
    transvection is an isometry of `L`: `t(f) = f + 2a - 2e`.
    """
    lattice = Lattices(ZZ)([[0, 1, 0], [1, 0, 0], [0, 0, 1]])
    labels = tuple(lattice.module_generating_set())
    isotropic, partner, orthogonal = (
        lattice.module_generator(label) for label in labels
    )
    assert isotropic.q() == ZZ.zero()
    assert isotropic.b(orthogonal) == ZZ.zero()
    assert isotropic.b(partner) == ZZ.one()
    assert orthogonal.q() == ZZ.one()

    with pytest.raises(ValueError) as caught:
        lattice.eichler_transvection(isotropic, orthogonal)
    refusal = caught.value
    assert (refusal.isotropic, refusal.orthogonal) == (isotropic, orthogonal)
    assert refusal.lattice == lattice
    assert refusal.coefficient == QQ(-1) / QQ(2)
    assert refusal.position == (0, 1)

    doubled = lattice.scalar_multiple(2, isotropic)
    transvection = lattice.eichler_transvection(doubled, orthogonal)
    assert transvection(doubled) == doubled
    assert transvection(partner) == (
        partner
        + lattice.scalar_multiple(2, orthogonal)
        - lattice.scalar_multiple(2, isotropic)
    )
