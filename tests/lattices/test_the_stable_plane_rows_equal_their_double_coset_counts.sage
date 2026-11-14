r"""The kernel plane rows equal their double-coset counts, exactly (#390).

The two kernel plane rows of the Coble lattice -- the orbits of primitive
isotropic planes under ``Otilde(T_Co) = ker rho`` and ``Otilde+(T_Co) =
ker(rho, sn_RR)``, `T_Co = <2> + U(2) + E8(-2)` of D. Dolgachev and
S. Kondō, Izv. Math. 77:3 (2013), section 3, eq. (3.6), printed p. 513 --
are the CI job ``tests/coble_kernel_plane_rows.py``: each realizes one plane
per double coset, and the two rows number 189720 double cosets each, so they
are beyond the per-test gate.  This file gates, on lattices the gate can
afford, the walk those rows ride on and the guarantees the cited construction
gives for every output of a kernel plane row:

* each representative is a primitive totally isotropic plane;
* the count of a row is the sum, over the ambient ``O(L)``-classes, of the
  number of double cosets ``chi(Gamma) \\ chi(O(L)) / chi(Stab P)`` -- the
  index per finite class -- asserted **exactly**, for ``Otilde`` and for
  ``Otilde+`` alike, against an independent enumeration of those double
  cosets (GAP's ``DoubleCosets`` on the subgroup's finite character image,
  through ``splitting_isometries_from_stabilizer_image``: the product-model
  route the rows used before the walk, one checked lift per double coset);
* the ``Otilde+`` row has at least as many planes as the ``Otilde`` row --
  the group ``Otilde+ = ker(rho, sn_RR)`` is contained in
  ``Otilde = ker rho``, so its orbits are at least as many.

**The route.**  For each ``O(L)``-orbit of planes the ``Gamma``-orbits inside
it are the double cosets ``rho(Gamma) \\ rho(O(L)) / rho(Stab P)`` (D. Dutour
Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces -- computational
aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, Lemma 3.6,
printed p. 22), and the rows realize them by a breadth-first walk over the
right-coset action of ``rho(O(L))`` on ``rho(O(L)) / rho(Stab P)``: the point
stabilizers of that action are exactly the conjugates of the certified
stabilizer image, so the walk cannot undercount the way a natural point such
as a divided class set can (on ``T_Co`` the plane's class set is one
``rho(O(L))``-orbit of 23715 points where the stabilizer image has index
189720).  Each reached point of the walk carries the word that carries the
trivial coset to it, and a lift to ``O(L)`` of an element of ``rho(O(L))``
written as a word in the rho-images of the ambient generators is the same
word in those generators, so one walk realizes every double coset without a
per-coset word problem.  The ``ker(rho, sn_RR)`` rows ride the same walk
through the kernel-sign witness machinery their line rows already use.

**The lattices.**  ``6JRS = U + U + <-2>``, ``U + U``, and
``U + U(2) + <-2>``, whose ``Otilde`` row splits into two orbits -- a count
for which the equality with the double cosets is not vacuous.  The third
lattice's ``is_parabolic_complete`` decision is observed to flip with the
ambient row's per-process representative choice (the #373 Levi search is
not conjugation-covariant), so its gate row fails when that choice falls on
a representative the search cannot cover; it stays in this file and fails
there rather than leaving the test.  No count here is a card value: the rows
of all three lattices wait on lattice-database#13, so the expected numbers
are computed, never typed.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _assert_primitive_isotropic_plane(lattice, plane) -> None:
    r"""``plane`` is a rank-two primitive totally isotropic subobject of ``lattice``."""
    assert plane.inclusion().codomain() is lattice
    assert plane.module_rank() == cardinal(2)
    assert plane.is_primitive() is True
    labels = plane.module_generating_set()
    for left in labels:
        for right in labels:
            assert lattice.b(
                plane.inclusion()(plane.module_generator(left)),
                plane.inclusion()(plane.module_generator(right)),
            ) == ZZ(0)


def _double_coset_count(subgroup, plane):
    r"""The number of ``Gamma``-double cosets at one ambient plane, enumerated independently.

    The count is the double cosets ``chi(Gamma) \\ chi(O(L)) / chi(Stab P)``
    (Dutour Sikirić--Hulek, Lemma 3.6, printed p. 22), enumerated by GAP's
    ``DoubleCosets`` on the subgroup's finite character image with the plane's
    certified parabolic family supplying ``chi(Stab P)`` -- the product-model
    route of ``splitting_isometries_from_stabilizer_image``, one checked lift
    per double coset.  It is a computation independent of the coset walk the
    row itself rides: a different group model and a different algorithm.
    """
    quotient = subgroup.finite_character_quotient()
    family = tuple(plane.parabolic_stabilizer_generators())
    splittings = quotient.splitting_isometries_from_stabilizer_image(
        tuple(quotient.image(element) for element in family)
    )
    return int(splittings.cardinality())


def _expected_row_count(subgroup):
    r"""The row count the construction names: the per-class indices, summed."""
    return sum(
        _double_coset_count(subgroup, plane)
        for plane in subgroup.supergroup().isotropic_orbit_representatives(2)
    )


def _assert_both_kernel_rows(lattice) -> None:
    r"""Both kernel plane rows return primitive isotropic planes, exactly their double cosets."""
    stable = lattice.stable_orthogonal_group()
    stable_plus = stable.intersection(lattice.O_plus())

    planes = stable.isotropic_orbit_representatives(2)
    planes_plus = stable_plus.isotropic_orbit_representatives(2)

    assert planes.cardinality() != cardinal(0)
    for plane in planes:
        _assert_primitive_isotropic_plane(lattice, plane)
    for plane in planes_plus:
        _assert_primitive_isotropic_plane(lattice, plane)
    assert planes.cardinality() == cardinal(_expected_row_count(stable))
    assert planes_plus.cardinality() == cardinal(_expected_row_count(stable_plus))
    assert planes_plus.cardinality() >= planes.cardinality()


def test_the_kernel_plane_rows_of_6jrs_equal_their_double_coset_counts() -> None:
    r"""``6JRS``: both kernel plane rows equal their independently enumerated double cosets."""
    _assert_both_kernel_rows(Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]]))


def test_the_kernel_plane_rows_of_the_unimodular_plane_sum_equal_their_double_coset_counts() -> None:
    r"""``U + U``: both kernel plane rows equal their independently enumerated double cosets."""
    _assert_both_kernel_rows(Lattices(ZZ)("U") + Lattices(ZZ)("U"))


def test_the_kernel_plane_rows_of_u_plus_u2_plus_root_equal_their_double_coset_counts() -> None:
    r"""``U + U(2) + <-2>``: the two-orbit ``Otilde`` row equals its double cosets exactly."""
    _assert_both_kernel_rows(
        Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]]) + Lattices(ZZ)([[-2]])
    )
