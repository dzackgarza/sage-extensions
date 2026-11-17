r"""The stabilizer family is the set of its factors' composites, on the smallest lattices.

``stabilizer_schreier_factors`` states the certificate a consumer needs to
realize a stabilizer family without reading every one of its words: for the
``i``-th lattice-orbit point ``p`` with transport ``t_p: L -> L_p`` and the
``j``-th letter ``s: L_p -> L_(s.p)``, the family's element is the composite

    ~t_(s.p) * middle_(p,s) * t_p,

so ``|letters| + |orbit|`` converted maps carry the whole family of
``|letters| * |orbit|`` words.  That is the route the Enriques line stabilizer
of $N = U \oplus U(2) \oplus E_8(-2)$ is read through; here it is asserted on
the smallest lattices that carry both a nontrivial lattice orbit and a
nonidentity image epimorphism, so the reading of ``L_p``'s own generators is
exercised rather than an identity.

The order of the two factors is the one ``orbit_schreier_factors`` documents,
and the comparison against a realized family is a set because a Schreier family
names words, not distinct elements: on these specimens the family has repeated
images.  For the line, ``Stab_{O(L)}(Zu)`` is the parabolic subgroup, so its own
realized generators are that family's distinct images and the comparison needs
no private stabilizer handle.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _u_plus_u_two():
    r"""$U \oplus U(2)$, rank four and determinant four: $U(2)$ has Gram $\begin{pmatrix}0&2\\2&0\end{pmatrix}$."""
    return Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]])


def _line_specimen():
    lattice = _u_plus_u_two()
    vectors = tuple(lattice.module_generators())
    line = vectors[0]
    return lattice, line, lattice.primitive_isotropic_subobject(line)


def _plane_specimen():
    lattice = _u_plus_u_two()
    vectors = tuple(lattice.module_generators())
    plane = lattice.primitive_isotropic_subobject(vectors[0], vectors[2])
    return lattice, plane


def _orbit_position(records, orbit_lattice):
    r"""The index of ``orbit_lattice`` among the records, by the object the record names."""
    for position, record in enumerate(records):
        if record["lattice"] is orbit_lattice:
            return position
    raise ValueError(f"{orbit_lattice} is not one of the recorded orbit lattices")


def _factor_composites(subobject):
    r"""The Schreier family realized from its factors, in the orbit-outer order it is documented in."""
    letters, _transversals = subobject.stabilizer_schreier_factors()
    records = subobject.orbit_lattice_records()
    transports = tuple(record["transport"] for record in records)
    # ``record["transport"]`` is the integral map ``t_p: L -> L_p`` the orbit point
    # was reached by; ``transversals`` is the same element of the rational group,
    # read there.  The composite below is stated in the lattice category, so the
    # transports are its own maps and the letters are read as arrows on them.
    assert all(
        record["transport"] in subobject.ambient_lattice().Isom(record["lattice"])
        for record in records
    )
    composites = []
    for position, _record in enumerate(records):
        for letter in tuple(letters):
            middle = subobject.middle_transport(position, letter)
            target = _orbit_position(records, middle.codomain())
            composites.append((~transports[target]) * middle * transports[position])
    return tuple(composites)


def test_the_line_stabilizers_family_is_its_factors_composites() -> None:
    r"""Every composite of a letter with its two transports is a member of the realized family.

    A composite is an isometry of ``L`` and it stabilizes the line, and the set
    of composites is exactly the set of the parabolic subgroup's own generators.
    A ``middle_transport`` that read the transported source basis instead of
    ``L_p``'s own generators gives a different map on this specimen, so the two
    sets would differ.
    """
    lattice, line, subobject = _line_specimen()
    parabolic = subobject.parabolic_subgroup()
    composites = _factor_composites(subobject)
    assert all(composite in lattice.Isom(lattice) for composite in composites)
    assert all(
        composite(line) == line
        or composite(line) == lattice.scalar_multiple(lattice.base_ring()(-1), line)
        for composite in composites
    )
    assert set(composites) == set(parabolic.group_generators())


def test_the_line_stabilizers_family_negates_the_line_somewhere() -> None:
    r"""The family is the setwise stabilizer, not the pointwise one.

    ``Stab_{O(L)}(Zu)`` maps the line's generators to ``+-u``, so a family that
    generates it cannot act on the line by ``+1`` alone.  The pointwise
    subgroup is the index-two part; asserting the negation here is what
    separates the two, and it is the property the Enriques consumer reads.
    """
    lattice, line, _subobject = _line_specimen()
    members = tuple(_subobject.parabolic_subgroup().group_generators())
    negated = lattice.scalar_multiple(lattice.base_ring()(-1), line)
    assert any(member(line) == negated for member in members)
    assert all(member(line) == line or member(line) == negated for member in members)


def test_the_plane_stabilizers_composites_are_isometries_that_stabilize_the_plane() -> None:
    r"""The composite law reads ``L_p``'s own generators at rank two as well.

    The plane's stabilizer is ``Stab_{O(L)}(J)`` over a larger lattice orbit and a
    different letter family, so the same composite is built from a different set of
    orbit lattices.  Each one is an isometry of ``L`` and it stabilizes ``J``; a
    composite read on the transported source basis instead of ``L_p``'s own
    generators is neither, which is what the published ``U + <-6>`` line cannot
    separate.
    """
    lattice, plane = _plane_specimen()
    composites = _factor_composites(plane)
    assert all(composite in lattice.Isom(lattice) for composite in composites)
    assert all(plane.stabilizes(composite) for composite in composites)
