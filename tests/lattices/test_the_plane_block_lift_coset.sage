r"""The free parameter of the plane block equations, and its exact search (#336).

The `P_2` equation of Dutour Sikirić--Hulek, Theorem 4.9, printed pp. 33--34, is

$$(P_1 J P_2^t)^t + P_1 J P_2^t = \mathrm{remainder},$$

so its rational solutions are $P_2 = (\mathrm{remainder}/2+sK)^t(P_1J)^{-t}$.
The period of the affine rational parameter divides $|\det J|$, but this does
not imply that an integral solution is represented by an integral parameter.
The actual lift solves the integer symmetric system and allows the mixed
block Q2 in the third equation. The Enriques examples test the period and
integral lifts; the nonsplit example requires a nonzero mixed block.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _representatives(lattice):
    r"""Sterk's $P_1$ and $P_2$ of $T_{\mathrm{En}}$ (Math. Z. 207 (1991), Prop. 4.6, p. 29)."""
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    assert lattice.q(w) == ZZ(-8)
    return (
        lattice.primitive_isotropic_subobject(first, third),
        lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third),
    )


def test_the_parameter_period_divides_the_plane_block_determinant() -> None:
    r"""The period of the free parameter divides $|\det J|$.

    Both planes of $T_{\mathrm{En}}$ are checked, because they carry different
    block data: $J=\mathrm{diag}(1,2)$ at $P_1$ and $J=2 I_2$ at $P_2$,
    with determinant $2$ and $4$ respectively. The period is independent
    of the integrality offset of the symmetric equation.
    """
    lattice = NamedLattices.TEn

    for plane in _representatives(lattice):
        _change, _inverse, _H, J, _K, _A = plane.plane_block_gram()
        determinant = abs(int(J.determinant()))
        actions = plane.levi_plane_action_generators()
        assert actions != ()
        for action in actions:
            period = int(plane.plane_block_parameter_period(action))
            assert period > 0
            assert determinant % period == 0
            assert period <= 2 * determinant + 2


def test_every_returned_plane_block_lift_carries_the_plane_onto_itself() -> None:
    r"""Each returned lift is an element of the parabolic: $g(P) = P$ and $g^{-1}(P) = P$.

    The assertion is on the returned element and not on the search that produced it,
    and it is asked of the plane actions of the parabolic's own family, which are the
    candidates `levi_lift_generators` searches.  `stabilizes` asks both inclusions, so
    it also exercises the inverse: an element that is not invertible cannot pass.
    """
    lattice = NamedLattices.TEn

    for plane in _representatives(lattice):
        lifted = 0
        for action in plane.levi_plane_action_generators():
            lift = plane.plane_block_lift(action)
            if lift is None:
                continue
            lifted += 1
            assert plane.stabilizes(lift) is True
        assert lifted > 1


def test_nonsplit_levi_action_requires_nonzero_mixed_block() -> None:
    r"""A nonsplit integral parabolic need not admit a zero mixed block.

    In the ordered basis (u,v,p,q,d) the plane is <p,q>.  The isometry
    u->-u, p->-p, d->d-p (fixing v,q) preserves the given Gram matrix,
    acts by diag(-1,1) on the plane and fixes the definite quotient.
    The zero mixed-block equation would require P3=(-1/2,0)^t,
    so no normalized integral lift with that block zero exists.
    """
    lattice = Lattices(ZZ)([[0, 0, 2, 0, 1], [0, 0, 0, 2, 0], [2, 0, 0, 0, 0], [0, 2, 0, 0, 0], [1, 0, 0, 0, -4]])
    u, v, p, q, d = tuple(lattice.module_generators())
    plane = lattice.primitive_isotropic_subobject(p, q)
    group = lattice.O()
    actual = group(dict(zip(lattice.module_generating_set(), (-u, v, -p, q, d - p), strict=True)))
    assert actual in group and plane.stabilizes(actual)
    action = plane.plane_block_gram()[3].parent()([[-1, 0], [0, 1]])
    lift = plane.plane_block_lift(action)
    assert lift in group and plane.stabilizes(lift)
    assert lift(p) == -p and lift(q) == q
    assert plane.inclusion().is_in_image(lift(d) - d)


def test_nonsplit_quotient_sign_lifts_with_nonzero_mixed_block() -> None:
    r"""The quotient sign need not lift with a zero translation into the plane.

    On the rank-five lattice below, the isometry fixing u,v,p,q and sending
    d to p-d acts as -1 on the negative definite quotient. It preserves the
    pairing with u since (u,p-d)=2-1=1. The actual quotient-action lift must
    realize this sign, not just preserve the plane.
    """
    lattice = Lattices(ZZ)([[0, 0, 2, 0, 1], [0, 0, 0, 2, 0], [2, 0, 0, 0, 0], [0, 2, 0, 0, 0], [1, 0, 0, 0, -4]])
    u, v, p, q, d = tuple(lattice.module_generators())
    plane = lattice.primitive_isotropic_subobject(p, q)
    group = lattice.O()
    actual = group(dict(zip(lattice.module_generating_set(), (u, v, p, q, p - d), strict=True)))
    assert actual in group and plane.stabilizes(actual)
    reduction = plane.isotropic_reduction()
    quotient_action = reduction.levi_action()(actual)
    lift = plane.levi_quotient_lift(quotient_action)
    assert lift in group and plane.stabilizes(lift)
    assert reduction.levi_action()(lift) == quotient_action
