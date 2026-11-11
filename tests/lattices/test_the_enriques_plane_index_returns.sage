r"""The plane index on $T_{\mathrm{En}}$, per finite class (#325).

Two calls, one per route into :meth:`isotropic_plane_orbits`:

* the published-index route, which returns the plane orbits and is what
  ``029J``'s ``O`` row (2 primitive isotropic planes modulo $O(T_{\mathrm{En}})$)
  is compared with;
* the supplied-stabilizer route, where the setwise stabilizer's own generators
  are handed to the call so that ``[Q : rho(G_x)]`` closes the sandwich.

The second is the #325 acceptance and is **red on main at the time of this
commit**, for a reason that is not the issue's.  The issue records
``TypeError: int() argument must be a string, a bytes-like object or a real
number, not 'OwnedJoinCategory.element_class'`` at
``sage_indefinite_port/indefinite/recursive.py:154`` as the obstruction.  That
line is ``source_coordinates = tuple(int(coordinates(label)) for label in
source_labels)``, and it is **not** the pinned port's text: at
``991b88b095a42a1e3679569ea42328c900c120f6`` the same statement reads
``_integer(coordinates(label))``, port commit ``ab140b70`` ("read integral
coordinates through the field when a lattice is rational", an ancestor of the
pin) replacing the bare ``int`` at four coordinate crossings.  The recorded
frame is the line of the *image's own* baked-in port at
``/repos/sage-indefinite-port`` (tag of that checkout ``4f0ee50c``, 2026-11-01),
which a launcher that does not bind the port path reaches through the
``__editable__.sage_indefinite_port`` path entry.  With the pinned port bound,
the same calls return: `O(T_En).group_generators()` in 115 s,
`isotropic_orbit_representatives(2)` = 2 in 67 s, and the published-index plane
call below = 2 orbits.

What does stop the supplied-stabilizer route is measured, and it is this
repository's: the twelve Levi lifts on $P$ and the twenty Eichler transvections
of the radical have **trivial** image under
:meth:`discriminant_representation`, and the 120 lifted reflections generate a
subgroup of index ``134912 = 527 * 256`` in $Q = \rho(O(T_{\mathrm{En}}))$,
while the divided class set of $P_1$ has a $Q$-orbit of ``527`` points
(Dutour Sikirić--Hulek, arXiv:2302.01679v2, §3.6, p. 22, supplies the two
indices ``527`` and ``23715`` and the ``24242`` one-dimensional cusps).  So the
family :meth:`parabolic_stabilizer_generators` returns is short of
$\rho(G_{P_1})$ by a factor $256$, and :meth:`_establish_by_stabilizer_generators`
refuses the sandwich rather than returning a count it has not established.
Closing #325 means completing that family; this module states the acceptance so
that the refusal cannot pass for success.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _whole_orthogonal_group(lattice):
    r"""$O(L)$ as the predicate subgroup lying over its whole discriminant image.

    ``isotropic_plane_orbits`` is an operation of the character-kernel
    subgroups, not of the isometry Mor: the subgroup it splits plane orbits
    under is ``rho^-1(H)`` for a subgroup ``H`` of ``O(A_L)``.  For the whole
    $O(L)$ that subgroup is $H = \rho(O(L))$, so the object here is
    $\rho^{-1}(\rho(O(L))) = O(L)$ with complete character data.
    """
    target = lattice.discriminant_group().orthogonal_group()
    whole = target.subgroup_on(tuple(target.group_generators()))
    return lattice.Aut().discriminant_preimage(whole)


def _enriques_plane_representatives(lattice):
    r"""Sterk's two $O(T_{\mathrm{En}})$-orbit representatives of primitive isotropic planes.

    $P_1 = \mathbb{Z} e_1 + \mathbb{Z} e_3$ and
    $P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z} e_3$ with $w$ a vector of
    $E_8(-2)$ of norm $-8$: H. Sterk, *Compactifications of the period space of
    Enriques surfaces, Part I*, Math. Z. 207 (1991), Proposition 4.6 (p. 29), in
    the standard bases $(e_1, e_2)$ of $U$ and $(e_3, e_4)$ of $U(2)$ that
    Dutour Sikirić--Hulek, §3.6, p. 22, use.
    """
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    assert lattice.q(w) == ZZ(-8)
    return (
        lattice.primitive_isotropic_subobject(first, third),
        lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third),
    )


def test_the_o_row_of_the_plane_index_returns_on_the_enriques_lattice() -> None:
    r"""Both of Sterk's representatives are split out, and the count is ``029J``'s ``O`` row.

    The published indices of the two plane stabilizers close the sandwich here,
    so this route returns; the number asserted is the card's, read by tag,
    never this call's own output.
    """
    lattice = NamedLattices.TEn
    group = _whole_orthogonal_group(lattice)
    assert group.contains_character_kernel()
    representatives = _enriques_plane_representatives(lattice)

    orbits = group.isotropic_plane_orbits(representatives)

    assert orbits.cardinality() == cardinal(card_plane_orbit_row("029J", "O"))
    for orbit in orbits:
        plane = orbit.representative()
        assert plane.inclusion().codomain() is lattice
        assert plane.is_primitive() is True
        assert plane.module_rank() == cardinal(2)
        for left in plane.inclusion().domain().module_generators():
            for right in plane.inclusion().domain().module_generators():
                assert lattice.b(plane.inclusion()(left), plane.inclusion()(right)) == ZZ(0)


def test_the_supplied_setwise_stabilizer_generators_close_the_plane_index() -> None:
    r"""The setwise stabilizer's own generators make the index return (#325's acceptance).

    **Red on main at this commit.** The call raises

    ```
    ValueError: the discriminant image of the stabilizer of <the plane of rank 2> is not
    established: the supplied generators generate a subgroup of index 134912 in
    rho(O(T_En)), while the orbit of the plane's divided classes has 527 points.
    ```

    The generators supplied are the ones
    :meth:`parabolic_stabilizer_generators` returns: 20 Eichler transvections of
    the unipotent radical, 120 reflections lifted from the shells of
    $P_1^\perp/P_1$, and 12 integral Levi lifts of elementary matrices of
    $GL(P_1)$.  Measured one family at a time against $Q = \rho(O(T_{\mathrm{En}}))$
    (order $46998591897600$): the transvections generate a subgroup of order 1,
    the Levi lifts a subgroup of order 1, and the reflections a subgroup of
    order $348364800 = |\rho(O(E_8(-2)))|$, of index
    $134912 = 527 \cdot 256$.  An independent computation of the same images
    (dual basis $G^{-1}$, a class read off the fractional coordinates of
    $L^\#/L$) agrees on all 152 generators: the 32 radical and Levi-on-$P$
    generators move no class, the 120 reflections move classes.

    So the obstruction is not the port and not the call: the three families are
    not a generating set of the parabolic, and the missing factor
    $256 = 2^8$ is exactly $|A_{E_8(-2)}|$, the part of $A_L$ the transvections
    and the Levi-on-$P$ lifts leave alone.  Until that family is completed, the
    honest answer of the call is this refusal.

    The same numbers come out on `1756b91`: the setwise stabilizer returns
    150 generators in 493 s and the call raises the index `134912` against
    the class orbit's `527`.
    """
    lattice = NamedLattices.TEn
    plane = _enriques_plane_representatives(lattice)[0]
    group = _whole_orthogonal_group(lattice)
    assert group.contains_character_kernel()

    family = tuple(lattice.Aut().stabilizer(plane, action="setwise").group_generators())
    assert family

    orbits = group.isotropic_plane_orbits((plane,), stabilizer_generators={0: family})

    assert orbits.cardinality() != cardinal(0)
    for orbit in orbits:
        assert orbit.representative().is_primitive() is True
