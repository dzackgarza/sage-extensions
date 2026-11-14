r"""The free parameter of the plane block equations, and its exact search (#336).

The `P_2` equation of Dutour Sikirić--Hulek, Theorem 4.9, printed pp. 33--34, is

$$(P_1 J P_2^t)^t + P_1 J P_2^t = \mathrm{remainder},$$

so its solutions are $P_2 = (\mathrm{remainder}/2 + sK)^t (P_1 J)^{-t}$ over the skew
matrices $sK$ with $K = \binom{\ 0\ -1}{1\ \ \ 0}$: one free rational parameter, and the
integral ones form one coset of its period.  `plane_block_lift` searched a range
$\pm(2|\det J| + 2)$ for that period instead of computing it.

`plane_block_parameter_period` computes it, and this module pins the arithmetic that
makes the old range complete: the period divides $|\det J|$, because
$(P_1J)^{-t} = J^{-t}Q_1$ with $J^{-t} = \mathrm{adj}(J)^t/\det J$ and $Q_1$ the
integral plane action.  A lift that exists therefore cannot have been reported as
`None` by that range for an integral action; what the repair removes is the unstated
inequality, not a lost lift.  The candidates are the plane actions the parabolic's own
family lifts, so no matrix is built here and no number is typed in.
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

    `plane_block_lift` searched $\pm(2|\det J| + 2)$ before, which is $2|\det J| + 2$
    integers on each side, so it held a complete residue system.  Both planes of
    $T_{\mathrm{En}}$ are checked, because they carry different block data:
    $J = \mathrm{diag}(1,2)$ at $P_1$ and $J = 2\cdot 1_2$ at $P_2$, with $\det J = 2$
    and $4$.
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
