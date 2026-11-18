r"""The incidence's vertices are its own cusp rows, read by span (#381).

An incidence row is a relation between two vertex rows that the same subgroup
already presents: the plane vertices are ``cusps(2)`` and the line vertices
``cusps(1)``, and each edge joins a line of a plane to that plane.  The call is
therefore computed at each plane cusp's own representative, and a term is
identified with a vertex by its *span* -- the sublattice it generates in the
ambient lattice -- because a vertex's representative is a plane and a flag's
plane term is an equal-but-distinct copy of it.

**What the span statement is.**  Two subobjects of one lattice with each in the
other's span are one sublattice: the same plane, presented twice.  The identity
of the ambient orthogonal group carries one to the other, and the identity lies
in every subgroup of that group, so an edge's certificate needs no transporter
search on the plane side.  This file gates that hypothesis where it is decided
-- on the lattice's own spans -- for every edge the call returns, and it gates
the relation itself against the flag row, a different public call.

**Why the vertex identification is by span and not by a search.**  A kernel row
of ``T_Co`` has 189720 plane cusps and 189720 planes; asking each cusp whether
it carries each plane is 189720 witness questions at every one of those planes,
and each question asks the lift registry for two lifts.  A span costs one row
Hermite form.  The witness search remains for a term that is *not* a
representative, which is what the flag route's plane terms are.

**The lattices.**  ``6JRS = U + U + <-2>`` has ``|O(A_L)| = 1``, so its kernel
rows are its ambient rows; ``U + U + <-4>`` has ``|O(A_L)| = 2``, so its kernel
rows are genuinely smaller than the ambient ones.  The ``U + U(2) + <2k>``
family is not gateable here: its ambient flag row cannot be built in this ring,
and the drivers run it in the image's own interpreter.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _6jrs():
    r"""``6JRS = U + U + <-2>``: rank five, ``|A_L| = 2`` and ``|O(A_L)| = 1``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])


def _u_u_m4():
    r"""``U + U + <-4>``: rank five, ``|A_L| = 4`` and ``|O(A_L)| = 2``."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-4]])


def _lies_in(source, target) -> bool:
    r"""Whether every retained generator of ``source`` lies in ``target``'s span."""
    inclusion = source.inclusion()
    domain = inclusion.domain()
    return all(
        bool(target.inclusion().is_in_image(inclusion(domain.module_generator(label))))
        for label in domain.module_generating_set()
    )


def _spans_one_another(left, right) -> bool:
    r"""Whether two subobjects of one lattice are one span, presented twice."""
    return _lies_in(left, right) and _lies_in(right, left)


def _assert_vertices_are_the_cusp_rows(subgroup):
    r"""Each edge's plane term is its plane cusp's representative's span, and every vertex carries an edge."""
    lattice = subgroup.supergroup().domain()
    assert subgroup.supergroup().one() in subgroup
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    relation = subgroup.tits_building_incidence()
    endpoints = set()
    for incidence in tuple(relation):
        assert incidence.lattice() is lattice
        assert incidence.line_cusp() in lines
        assert incidence.plane_cusp() in planes
        assert _spans_one_another(incidence.plane(), incidence.plane_cusp().representative())
        assert _lies_in(incidence.line(), incidence.plane())
        endpoints.add((incidence.line_cusp(), incidence.plane_cusp()))
    assert set(line_cusp for line_cusp, _plane_cusp in endpoints) == set(lines)
    assert set(plane_cusp for _line_cusp, plane_cusp in endpoints) == set(planes)
    return relation


def test_the_kernel_incidence_vertices_of_6jrs_are_its_cusp_rows() -> None:
    r"""``6JRS``: the kernel row is the ambient row, and its vertices are its own cusps."""
    lattice = _6jrs()
    relation = _assert_vertices_are_the_cusp_rows(lattice.stable_orthogonal_group())
    assert relation.cardinality() == cardinal(1)


def test_incidence_reconstructs_its_verified_flag_on_demand() -> None:
    r"""Retain the verified basis, not every constructed flag parent in the row."""
    lattice = _6jrs()
    relation = lattice.stable_orthogonal_group().tits_building_incidence()
    edge = next(iter(relation))
    assert edge._flag is None
    assert len(edge._flag_basis) == 2
    flag = edge.flag()
    assert flag is edge.flag()
    line, plane = flag.terms()
    assert _lies_in(line, plane)
    assert _spans_one_another(
        edge.line_transporter().transport_isotropic_object(line),
        edge.line_cusp().representative(),
    )
    assert _spans_one_another(
        edge.plane_transporter().transport_isotropic_object(plane),
        edge.plane_cusp().representative(),
    )
    edge.release_flag()
    assert edge._flag is None
    reconstructed = edge.flag()
    assert reconstructed is not flag
    assert _spans_one_another(reconstructed.terms()[0], line)
    assert _spans_one_another(reconstructed.terms()[1], plane)


def test_the_plus_kernel_incidence_vertices_of_6jrs_are_its_cusp_rows() -> None:
    r"""``6JRS``: ``Otilde+`` is ``O^+(L)`` there, and its vertices are its own cusps."""
    lattice = _6jrs()
    stable = lattice.stable_orthogonal_group()
    relation = _assert_vertices_are_the_cusp_rows(stable.intersection(lattice.O_plus()))
    assert relation.cardinality() == cardinal(1)


def test_the_kernel_incidence_vertices_of_u_u_m4_are_its_cusp_rows() -> None:
    r"""``U + U + <-4>``: the kernel row is smaller than the ambient one, and its vertices are its own cusps."""
    lattice = _u_u_m4()
    relation = _assert_vertices_are_the_cusp_rows(lattice.stable_orthogonal_group())
    assert relation.cardinality() == cardinal(1)


def test_the_plus_kernel_incidence_vertices_of_u_u_m4_are_its_cusp_rows() -> None:
    r"""``U + U + <-4>``: the same for ``Otilde+``, the finer of the two kernel rows."""
    lattice = _u_u_m4()
    stable = lattice.stable_orthogonal_group()
    relation = _assert_vertices_are_the_cusp_rows(stable.intersection(lattice.O_plus()))
    assert relation.cardinality() == cardinal(1)


def test_the_sign_kernel_incidence_of_6jrs_is_its_cusp_rows() -> None:
    r"""``6JRS``: ``O^+(L)`` is cut by the spinor sign alone, and its row is its own cusps.

    The parabolic covering the incidence is built from descends to the finite
    image of whatever characters cut the subgroup, and this row cuts one that
    is not the discriminant representation: its finite image is the sign
    character's, of order two.
    """
    lattice = _6jrs()
    relation = _assert_vertices_are_the_cusp_rows(lattice.O_plus())
    assert relation.cardinality() == cardinal(1)
