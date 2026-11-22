r"""The completeness contract of the plane stabilizer, checked where the Levi image is a proper congruence subgroup.

`T_{En}.Aut().stabilizer(Pi, action="setwise")` answers with
`parabolic_stabilizer_generators()` when `is_parabolic_complete()`, and with a route of its own
otherwise, so a caller never receives a family whose completeness is unestablished.  The family is
assembled from the block decomposition of an integral parabolic, `P_I = U_I rtimes L_I`; in the block
basis `(U | P | K)` of `plane_block_basis` an element is

.. math::
    \begin{pmatrix} g_{11} & 0 & 0 \\ a & 1 & \tau \\ c & 0 & g_{22} \end{pmatrix},

and the three pieces are the three places a family can fall short:

* the **definite Levi action** `(g_{11}, g_{22}) in GL(I) x O(I^perp/I)` -- the quotient lattice is
  negative definite at a maximal isotropic plane, so its orthogonal group is finite and its action
  is a finite computation; the plane action `g_{11}` is what has to fall in the classes of `GL(I)`
  that admit an integral lift;
* the **unipotent block** `c in Hom(U, K)`, a lattice parameter, one generator per lattice vector;
* the **remaining translations**: `tau = -J^{-1} c^t A` is determined by `c` and `a` by `c` up to the
  skew part, which is the centre of `U_I` (`unipotent_block_solution`), so the radical's parameters
  are `c` together with that one central coordinate.

The tests below take the two smallest decisive planes.  `ZZ e + ZZ Sterk_4` is the one whose image in
`GL(I)` is a proper congruence subgroup -- it has no splitting complement, its factors are
`(1, 3, 1)`, and a decision that asked for the whole product `GL(I) x O(I^perp/I)` would refuse it
and discard the correct family; H. Sterk, *Compactifications of the period space of Enriques
surfaces, Part I*, Math. Z. 207 (1991), (4.6) and (4.7), gives `Gamma^1(2)`, of index three, for that
class.  `{2,4,5}` of (4.3.17) is the plane whose factors are all `1`.  At both, the public operation
is asserted to return the block family itself, so what is certified and what is returned are the same
family.

The orbit row on the eight antipodal pairs of `(-2)`-classes of `Pi^perp/Pi`, `(1, 1, 2, 1, 2)` at
Sterk's five plane types, is the regression oracle of sage-extensions#616 and is checked where it is
computed (`test_the_preimage_relation_that_cuts_the_enriques_family.sage`, two planes gated, all five
measured); it is not a substitute for the completeness argument above and is not used by these tests.
"""

from sage_extensions.all import *  # noqa: F401,F403

_PLANES = {}
_FAMILIES = {}


def _the_public_family(plane):
    r"""The generators `setwise_stabilizer` returns at this plane, read once per session."""
    if plane not in _FAMILIES:
        _FAMILIES[plane] = tuple(
            NamedLattices.TEn.Aut()
            .stabilizer(plane, action="setwise")
            .group_generators()
        )
    return _FAMILIES[plane]


def _the_plane_of_the_conjugate_line():
    r"""`ZZ e + ZZ Sterk_4`: a plane of `T_{En}` with no splitting complement."""
    if "conjugate" not in _PLANES:
        lattice = NamedLattices.TEn
        _PLANES["conjugate"] = lattice.primitive_isotropic_subobject(
            lattice.module_generator("e"),
            Sterk.selected_isotropic_vectors()["Sterk_4"],
        )
    return _PLANES["conjugate"]


def _the_first_type_plane():
    r"""Type `{2,4,5}` of (4.3.17)."""
    if "first" not in _PLANES:
        lattice = NamedLattices.TEn
        module_generators = tuple(lattice.module_generators())

        def vector_of(coordinates):
            total = lattice.zero()
            for index, coefficient in enumerate(coordinates):
                if coefficient:
                    total = total + coefficient * module_generators[index]
            return total

        _PLANES["first"] = lattice.primitive_isotropic_subobject(
            vector_of((0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0)),
            vector_of((-2, -2, 0, -2, -1, -1, 0, 0, 0, 0, 0, 0)),
        )
    return _PLANES["first"]


def _assert_the_family_is_the_certified_one(plane) -> None:
    r"""The public stabilizer returns the block family, and that family is certified complete."""
    block = plane.parabolic_stabilizer_generators()
    family = _the_public_family(plane)
    assert family
    assert all(member in block for member in family)
    assert all(member in family for member in block)


def test_the_completeness_at_a_plane_whose_image_is_a_proper_congruence_subgroup() -> None:
    r"""`ZZ e + ZZ Sterk_4`: factors `(1, 3, 1)`, complete, and the public family is the block family.

    The plane has no splitting complement, so the family is the block construction's and nothing
    else; its plane actions fall in `Gamma^1(2)`, of index three, which the decision accepts and a
    product criterion would refuse.
    """
    plane = _the_plane_of_the_conjugate_line()
    assert plane.splitting_complement() is None
    assert plane.unipotent_radical_index() == 1
    assert plane.levi_plane_action_index(trivial_on_quotient=True) == 3
    assert plane.levi_quotient_image_index(trivial_on_plane=True) == 1
    assert plane.is_parabolic_complete() is True
    _assert_the_family_is_the_certified_one(plane)


def test_the_completeness_at_the_plane_whose_three_factors_are_one() -> None:
    r"""Type `{2,4,5}`: factors `(1, 1, 1)`, complete, and the public family is the block family."""
    plane = _the_first_type_plane()
    assert plane.unipotent_radical_index() == 1
    assert plane.levi_plane_action_index(trivial_on_quotient=True) == 1
    assert plane.levi_quotient_image_index(trivial_on_plane=True) == 1
    assert plane.is_parabolic_complete() is True
    _assert_the_family_is_the_certified_one(plane)
