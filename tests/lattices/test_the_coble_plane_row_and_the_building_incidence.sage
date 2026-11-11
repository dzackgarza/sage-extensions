r"""The plane rows of $T_{\mathrm{En}}$ and $T_{\mathrm{Co}}$, and the Tits building (#360).

Two rows, in the order the issue asks for them.

**The known family.**  $T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)$ under
$O(T_{\mathrm{En}})$: the count of `L.Aut().isotropic_orbit_representatives(2)`
is card ``029J``'s ``integral.primitive_orbits.O.planes`` field, read by tag
through :func:`sage_extensions.lattice_database.card_plane_orbit_row`.  The card
cites H. Sterk, *Compactifications of the period space of Enriques surfaces,
Part I*, Math. Z. 207 (1991), Proposition 4.6 (p. 29): the primitive isotropic
planes of $T_{\mathrm{En}}$ form **two** $O$-orbits.

**The Coble lattice.**  $T_{\mathrm{Co}} = \langle 2\rangle \oplus U(2) \oplus
E_8(-2)$, D. Dolgachev and S. Kondo, *Enriques surfaces and
Borel--Weil--Bott type duality*, Izv. Math. 77:3 (2013), section 3, equation
(3.6), printed p. 513.  Its primitive isotropic planes do not split off the
lattice, so the divided-class count of
:meth:`...PredicateSubgroups.ParentMethods.isotropic_plane_orbits` is not the
orbit count there: the plane's setwise stabilizer maps onto a subgroup of index
`8` in the stabilizer of its order-four isotropic subgroup ($|1981808640|$ /
$|247726080|$, computed), while its divided class set is one
$\rho(O(T_{\mathrm{Co}}))$-orbit of `23715` points.  With the plane's own
stabilizer generators from :meth:`...parabolic_stabilizer_generators`, which
:meth:`...is_parabolic_complete` establishes at a $T_{\mathrm{Co}}$ plane, the
call computes the double cosets themselves and returns the ambient orbit as the
one orbit it is.

**Recorded, not asserted.**  `results/issue360-coble-plane-row.md`, with the runs
under `.tmp/qc-evidence/`:

* the $T_{\mathrm{En}}$ row: **2**, the card's value, in 156 s under load;
* the $T_{\mathrm{Co}}$ plane row by its own stabilizer: **1** orbit, in 73.7 s,
  with $[O(T_{\mathrm{Co}}) : \Gamma] = 1$ and the parabolic decided complete on
  its three factors (radical `1` in 6.4 s, plane actions `1` in 41.0 s,
  quotient images `1` in 4.9 s), `105` stabilizer generators, and
  `stabilizer_discriminant_image_orders() = (1981808640, 247726080)`, index
  `8` — research #645's `thm:plane-fibre` index;
* `L.Aut().isotropic_orbit_representatives(2)` on $T_{\mathrm{Co}}$ and
  therefore `tits_building_incidence()` do **not** return: the ambient plane
  classification needs the primitive isotropic classes of the reduction
  $v^\perp/\mathbf{Z}v$ of a line, and the port's
  `INDUCTION.isotropic_vector_classes` asks the lattice for an isotropic
  witness, which reaches PARI's `qfsolve` and stops with
  `PariError: sorry, qfsolve, dim >= 10 is not yet implemented`
  (`lattice_engines.py:496`, from `isotropic_orbits.py:1393`,
  `lattices.py:4687`).  Deciding isotropy of an indefinite lattice without
  that witness search is the prerequisite that unit needs.

The counts asserted here are the card's and the mathematical content of what
comes back: every returned representative is a primitive totally isotropic
plane of the lattice, and the orbits are pairwise distinct.  The page-proof
counts are never asserted (sage-extensions#286's rule: a computed value that
disagrees with a page proof is a defect filed on research, not a number this
suite pins).
"""

from sage_extensions.all import *  # noqa: F401,F403


def _assert_primitive_isotropic_plane(lattice, plane) -> None:
    r"""``plane`` is a rank-two primitive totally isotropic subobject of ``lattice``."""
    assert plane.inclusion().codomain() is lattice
    assert plane.module_rank() == cardinal(2)
    assert plane.is_primitive() is True
    points = tuple(plane.inclusion().domain().module_generators())
    assert all(
        lattice.b(plane.inclusion()(left), plane.inclusion()(right)) == ZZ.zero()
        for left in points
        for right in points
    )


def _coble_plane_specimen(lattice):
    r"""The plane of `tests/lattices/test_the_tco_plane_orbit_and_its_composed_automorphisms.sage`.

    With `h` the `<2>` line, `ep, fp` the `U(2)` pair and `a1..a8` the simple
    roots of `E8(-2)`, the two vectors are `ep + fp - (a1 + ... + a8)` and
    `2h - (a1 + a2 + 2a3 + ... + 2a7)`; each has square zero, they pair to zero,
    and the two-by-two minors of their coefficient matrix generate the unit
    ideal, so the plane is primitive.
    """
    labels = tuple(lattice.module_generating_set())

    def vector(coefficients):
        total = lattice.zero()
        for label, coefficient in zip(labels, coefficients, strict=True):
            if coefficient:
                total = total + coefficient * lattice.module_generator(label)
        return total

    return lattice.primitive_isotropic_subobject(
        vector([0, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1]),
        vector([2, 0, 0, -1, -1, -2, -2, -2, -2, -2, 0]),
    )


def _whole_orthogonal_group(lattice):
    r"""$O(L)$ as the character-kernel subgroup lying over its whole discriminant image."""
    target = lattice.discriminant_group().orthogonal_group()
    whole = target.subgroup_on(tuple(target.group_generators()))
    return lattice.Aut().discriminant_preimage(whole)


def test_the_known_family_plane_row_is_the_card_row() -> None:
    r"""The plane orbits of $T_{\mathrm{En}}$ under $O(T_{\mathrm{En}})$ are ``029J``'s ``O`` row.

    The count asserted is the card's, read by tag.  Every returned
    representative is checked to be a primitive totally isotropic plane of
    $T_{\mathrm{En}}$, so the count is a count of the objects the row names.
    """
    lattice = NamedLattices.TEn

    planes = lattice.Aut().isotropic_orbit_representatives(2)

    assert planes.cardinality() == cardinal(card_plane_orbit_row("029J", "O"))
    for plane in planes:
        _assert_primitive_isotropic_plane(lattice, plane)


def test_the_coble_plane_row_of_the_planes_own_stabilizer_returns() -> None:
    r"""$T_{\mathrm{Co}}$: the plane's ambient orbit, split by the plane's own stabilizer.

    $\Gamma = \rho^{-1}(\rho(O(T_{\mathrm{Co}})))$ is all of $O(T_{\mathrm{Co}})$
    here, so $\Gamma g\,\mathrm{Stab} = O(T_{\mathrm{Co}})$ for every $g$ and the
    double-coset space is the single point the identity names.  The count `1`
    asserted below is that identity and not a page's value: a group is
    transitive on its own orbit of a plane, and the call would be wrong if it
    returned anything else.  The representative is the plane the call was
    handed -- its own divided class set is what comes back -- and it is checked
    to be a primitive totally isotropic plane of $T_{\mathrm{Co}}$.
    """
    lattice = NamedLattices.Tco
    group = _whole_orthogonal_group(lattice)
    plane = _coble_plane_specimen(lattice)
    assert group.contains_character_kernel()

    orbits = group.isotropic_plane_orbits([plane])

    assert orbits.cardinality() == cardinal(1)
    orbit = tuple(orbits)[0]
    representative = orbit.representative()
    _assert_primitive_isotropic_plane(lattice, representative)
    assert tuple(orbit.divided_classes()) == _divided_classes(lattice, plane)


def _divided_classes(lattice, plane):
    r"""The divided discriminant classes of the plane's own basis vectors."""
    inclusion = plane.inclusion()
    domain = inclusion.domain()
    return tuple(
        lattice.divided_discriminant_class(inclusion(domain.module_generator(label)))
        for label in domain.module_generating_set()
    )
