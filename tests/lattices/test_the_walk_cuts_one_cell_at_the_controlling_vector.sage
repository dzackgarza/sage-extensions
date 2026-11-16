r"""The lattice cuts one cell at the controlling vector, however often the walk asks.

E. B. Vinberg, *On the groups of unit elements of certain quadratic forms*, Math.
USSR Sb. 16 (1972), §3.2, rule 1 with (39) (p. 27): before the sequence (38)
starts, the normals are the roots whose mirrors pass through the point
\(p_0\), and the cell \(P_0\) at that point is their intersection.  Which roots
those are is a property of the lattice and of the point and of nothing else, so
a walk that writes them down twice writes down one cell.  The layer
enumeration of §4.1 (p. 30) is measured in the coordinates of that same cell,
which is why it can never be the search that cuts it: a walk that restricted
its own initial-cone enumeration to the cell it had cut before would be
enumerating in the coordinates of the answer it is looking for.

The two facts the cell's existence needs are pinned beside that one.  The cell
is cut by the roots of the initial cone, those that pair zero with the
controlling vector, and by no others; and a controlling vector with no root
through it -- a walk whose subgroup admits none of them -- has no cell, so its
layers have no coordinates to be enumerated in and the walk keeps the engine's
whole-lattice enumeration of them.

\(U\oplus A_1\) is the smallest hyperbolic lattice whose cell at the point the
engine picks is cut by more than one normal: the roots of square \(-2\) through
it span \(v_0^\perp\).  The walk is bounded one root past the initial cone
here, because the claim is about the cone and not about the chamber the whole
sequence closes.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _rows(roots):
    r"""The roots as coordinate rows in a fixed order, so two enumerations compare."""
    return tuple(sorted(tuple(int(entry) for entry in root) for root in roots))


def _smallest_hyperbolic_lattice_with_a_cell():
    r"""Return \(U\oplus A_1\), the smallest lattice whose cell has two normals."""
    return Lattices(ZZ)("U") + Lattices(ZZ)("A1")


def test_the_initial_cone_is_one_cell_after_the_walk_has_written_roots() -> None:
    r"""Asked again once it has written roots, the walk writes the cell it wrote before.

    The bounded search writes the initial cone and then one wall of the
    sequence (38), which is what any walk does before it asks for a layer; the
    cone at the controlling vector is then still the intersection of the roots
    through that point, because the walls written after the cone pair
    negatively-or-not-at-all with the point and are not among its normals.
    """
    walk = vinberg_walk(_smallest_hyperbolic_lattice_with_a_cell())
    first = _rows(walk.FundCone())
    walk.FindRoots(max_roots=1)
    second = _rows(walk.FundCone())

    assert second == first
    assert _rows(walk.cell()[0]) == first


def test_the_cell_is_the_roots_of_the_initial_cone_through_the_controlling_vector() -> None:
    r"""The cell's normals are the cone's roots at distance zero from the point.

    A cell that does not span \(v_0^\perp\) integrally in the form the layer
    enumeration uses is not returned at all, so the assertion is that the walk
    returned a cell and that it is this cone and not another.
    """
    walk = vinberg_walk(_smallest_hyperbolic_lattice_with_a_cell())
    cone = walk.FundCone()
    through_the_point = tuple(root for root in cone if walk.v0.inner_product(root) == 0)

    assert _rows(walk.cell()[0]) == _rows(through_the_point)
    assert _rows(walk.cell()[0]) == _rows(cone)


def test_a_walk_that_writes_no_root_through_its_point_cuts_no_cell() -> None:
    r"""No normal through the point, no cell: the layer keeps the whole-lattice search.

    The filter here admits no root at all, so the initial cone is empty for the
    same reason a subgroup with no reflection through the point leaves it empty.
    """
    walk = vinberg_walk(
        _smallest_hyperbolic_lattice_with_a_cell(), admits_root=lambda root: False
    )

    assert _rows(walk.FundCone()) == ()
    assert walk.cell() is None
