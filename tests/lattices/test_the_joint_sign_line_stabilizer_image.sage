r"""The joint determinant-and-spinor line row is read off the stabilizer's own elements.

`Gamma = ker(rho, det, sn)` is the smallest of the character-kernel subgroups of
`O(L)`, and its orbits of primitive isotropic lines are the double cosets
`chi(Gamma) \ chi(O(L)) / chi(Stab_{O(L)}(x))` for one ambient line `x` (D. Dutour
Sikirić and K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22).  With
`chi(Gamma)` trivial that is the index `[chi(O(L)) : chi(Stab(x))]`, so the row is
decided by the stabilizer's image and by nothing the row transports.

*What presents the sign cosets.*  `-id` carries `v` to `-v`, so it fixes the line as a
set, and its discriminant image is trivial whenever `-1` acts trivially on `A_L`.  The
Levi part `1_plane + (-1)_complement` of the parabolic at the line fixes it pointwise
(S. Zemel, *The Structure of Integral Parabolic Subgroups of Orthogonal Groups*,
J. Algebra 559 (2020), arXiv:1902.08264v2, Proposition 1.10, p. 13), and the integral
reflections in the vectors orthogonal to `v` fix it too.  On the specimen below these
elements realize both sign patterns, so `chi(Stab(x)) = chi(O(L))` and the joint row
has exactly as many line orbits as `O(L)` does.  A lattice on which they realized only
a proper subspace would have twice as many; that is the case this file does not claim.

The counts asserted here are derived from that argument and from
`Lattices.eichler_criterion_applies`, not read off a card: the `T_Co` card is
lattice-database#7 and is not minted, and nothing here states a `T_Co` number.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""``L = U + U + <-2>``: rank five, signature ``(2, 3)``, ``A_L = Z/2``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


def test_the_joint_sign_line_row_does_not_split_the_ambient_line() -> None:
    r"""``ker(rho, det, sn)`` has as many primitive isotropic lines as ``O(L)`` does."""
    lattice = _specimen()
    stable = lattice.stable_orthogonal_group()
    joint = stable.intersection(lattice.SO()).intersection(lattice.O_plus())
    ambient = lattice.Aut().isotropic_orbit_representatives(1)

    assert lattice.eichler_criterion_applies() is True
    assert ambient.cardinality() == 1
    joint_lines = joint.isotropic_orbit_representatives(1)
    assert joint_lines.cardinality() == ambient.cardinality()
    for line in joint_lines:
        vector = line.inclusion()(line.module_generator(0))
        assert vector.q() == ZZ(0)
        assert vector.is_primitive() is True


def test_the_negation_fixes_the_line_and_presents_the_determinant_coset() -> None:
    r"""``-id`` lies in the line stabilizer with trivial discriminant and spinor ``1``.

    That is one of the two sign patterns the joint subgroup's stabilizer image has to
    present: the negation is in `ker rho` and in `O^+`, and its determinant is ``-1``
    because the rank is odd, so it is not in the determinant kernel.
    """
    lattice = _specimen()
    labels = tuple(lattice.module_generating_set())
    orthogonal = lattice.Aut()
    negation = orthogonal({label: -lattice.module_generator(label) for label in labels})
    line = orthogonal.isotropic_orbit_representatives(1)
    assert line.cardinality() == 1
    for subobject in line:
        vector = subobject.inclusion()(subobject.module_generator(0))
        assert negation(vector) == -vector

    assert negation * negation == orthogonal.one()
    assert negation in lattice.stable_orthogonal_group()
    assert negation in lattice.O_plus()
    assert negation not in lattice.SO()
