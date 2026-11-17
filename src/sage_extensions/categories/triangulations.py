r"""Chosen triangulations over an exact geometric or complex target."""

from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.owned_category import _object_of
from sage_extensions.owned_category_bases import CategoryWithAxiom


for _axiom in ("Integral", "Unimodular"):
    if _axiom not in all_axioms:
        all_axioms.add(_axiom)


def _unplaced_polytope(polytope):
    r"""The polytope ``polytope`` is, or the polytope a placed one places.

    A placed polytope is one polytope of a lattice moved into another ambient
    space by one injective affine map, and that map carries a subset to a
    subset, an intersection to an intersection and a normalized volume to the
    same normalized volume.  The cells of a placed polytope are placed by that
    polytope's own placement, so a question about them is a question about the
    polytopes they place, and this answers that polytope.
    """
    match hasattr(polytope, "underlying_polytope"):
        case True:
            return polytope.underlying_polytope()
        case False:
            return polytope


class ChosenTriangulationMor(CategoricalMor):
    r"""Simplicial maps commuting with the two realization maps to the target."""

    class ElementMethods:
        def __init__(self, parent, simplicial_map):
            Morphism.__init__(self, parent)
            self._simplicial_map = simplicial_map

        def simplicial_map(self):
            return self._simplicial_map

        def __mul__(self, other):
            pass

    def _element_constructor_(self, simplicial_map):
        pass

    @object_level
    def identity(self):
        pass


class ChosenTriangulationMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = ChosenTriangulationMor


class ChosenTriangulations(OwnedParameterizedCategory):
    r"""Pairs ``(T, |T| -> K)`` over one exact represented target ``K``.

    A chosen triangulation of a target ``K`` is the family of the cells of one
    triangulation of ``K``: finitely many cells of ``K`` whose union is ``K``
    and whose pairwise intersections are common faces.  The collection receives
    those cells -- :meth:`on` for a family of them and
    :meth:`_from_engine_triangulation` for a private computation's answer -- and
    computes none of them: which cells a triangulation has is a property of the
    target, which answers it in ``triangulate``.  Covering and meeting along
    common faces are the two decisions the resulting object answers, and the
    axioms ``Integral`` and ``Unimodular`` refine it by the cells' lattice and
    their normalized volumes.
    """

    _MorCategory = ChosenTriangulationMorCategoryConstruction

    def parameter_category(self):
        return Objects()

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "chosen triangulations"

    def an_object(self):
        pass

    class SubcategoryMethods:
        def Integral(self):
            r"""Return this category with the axiom that every cell is integral.

            A cell is integral relative to the target's selected lattice when
            its vertices are lattice points of it
            (:meth:`Integral.ParentMethods.simplex_vertices_are_integral`).
            """
            return self._with_axiom("Integral")

        def Unimodular(self):
            r"""Return this category with the axiom that every cell is unimodular.

            A cell is unimodular when its normalized volume is one
            (:meth:`Unimodular.ParentMethods.normalized_volume`).
            """
            return self._with_axiom("Unimodular")

    def on(self, cells):
        r"""Select ``cells`` as the cells of a triangulation of the target.

        A cell of a triangulation of a polytope is a polytope of the polytope's
        own ambient lattice lying in it, so a family is admitted when each of
        its members is one of those: the family is then a family of subsets of
        the target and nothing more is claimed about it.  Whether the family
        covers the target and whether its members meet along common faces are
        the two decisions the resulting object answers
        (:meth:`ParentMethods.covers_target`,
        :meth:`ParentMethods.intersections_are_common_faces`); construction does
        not charge the caller for either (``OWN-22``).

        The cells are not recomputed here: the family a triangulation has is
        what the target answers in ``triangulate``, and this receives it.  A
        placed target's cells are placed polytopes and an unplaced target's are
        polytopes of its lattice; both are read at the polytope each cell is,
        since the placement carries subsets, intersections and volumes.
        """
        from sage_extensions.categories.schemes.polytopes import ConvexPolytopes

        target = self.target()
        core = _unplaced_polytope(target)
        lattice = core.ambient_lattice()
        selected = finite_ordered_set(tuple(cells))
        assert int(selected.cardinality()) > 0, (
            f"a triangulation of {target} has at least one cell, and the family given "
            "has none"
        )
        for cell in selected:
            cell_core = _unplaced_polytope(cell)
            assert cell_core in ConvexPolytopes(lattice), (
                f"a cell of a triangulation of {target} is a polytope of {lattice}, but "
                f"{cell} is an object of {cell_core.category()}"
            )
            assert cell_core.is_contained_in(core) is True, (
                f"a cell of a triangulation of {target} is a subset of it, but {cell} is "
                f"not a subset of {target}"
            )
        return _object_of(self, target=target, cells=selected)

    def integral(self, cells):
        r"""The chosen triangulation on ``cells``, placed in ``Integral()``.

        The placements of a construction named for a property are its claim, so
        this decides the claim rather than assuming it: the cells' vertices are
        points of the target's selected lattice or the family is refused,
        naming the axiom's own decision.  That decision is finite -- one
        lattice-membership question per cell -- so it is asked, and a failure
        raises ``ValueError``.
        """
        from sage_extensions.refine import refine

        return refine(self.on(cells), self.Integral())

    def unimodular(self, cells):
        r"""The chosen triangulation on ``cells``, placed in ``Unimodular()``.

        A unimodular triangulation is an integral one whose cells each have
        normalized volume one, so this decides both claims and refuses a family
        that fails either: the cells' normalized volumes are read once and the
        answer ``ValueError`` names the decision that failed.
        """
        from sage_extensions.refine import refine

        return refine(self.on(cells), self.Unimodular())

    def _from_engine_triangulation(self, engine_triangulation, vertex_map):
        r"""Raise a private point-configuration triangulation over the exact target.

        ``engine_triangulation`` is the private polyhedral computation's answer:
        finitely many simplices, each the positions of its vertices in
        ``vertex_map``, which is what ``ConvexPolytopes.triangulate`` holds
        beside its own answer
        (``ConvexPolytopes.ParentMethods._owned_vertices_in_engine_order``).
        ``vertex_map`` is indexed by those positions and answers the target's
        vertex there -- a point of the target's ambient space, which the
        target's own ``rational_point`` also admits as its coordinates.

        This is a translation of positions and of nothing else: a cell is the
        convex hull of the points those positions name, in the target's own
        lattice.  An answer that does not name a position of ``vertex_map`` --
        a position out of its range, or a cell repeating one, so that it is not
        a simplex -- is refused rather than read as a cell of something else,
        and a cell whose points are not lattice points of that lattice is
        refused where the lattice's polytopes are constructed.  What the engine
        answers is then either converted faithfully or refused; nothing is
        guessed.
        """
        from sage_extensions.categories.schemes.polytopes import ConvexPolytopes

        target = self.target()
        core = _unplaced_polytope(target)
        lattice = core.ambient_lattice()
        labels = tuple(core.ambient_space().module_generating_set())
        positions = tuple(range(len(vertex_map)))

        def point_at(position):
            match position in positions:
                case True:
                    return core.rational_point(vertex_map[position])
                case False:
                    raise ValueError(
                        f"the engine's triangulation of {target} names the position "
                        f"{position} of a vertex, and {vertex_map} has the positions "
                        f"{positions[0]} to {positions[-1]}"
                    )

        def cell_of(simplex):
            chosen = tuple(int(position) for position in simplex)
            match len(set(chosen)) == len(chosen):
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"the engine's triangulation of {target} answers the cell {chosen}, "
                        "which repeats a vertex and is therefore not a simplex"
                    )
            return ConvexPolytopes(lattice)(
                tuple(
                    tuple(point.to_vector()(label) for label in labels)
                    for point in (point_at(position) for position in chosen)
                )
            )

        return self.on(
            cell_of(simplex) for simplex in tuple(engine_triangulation)
        )

    def target(self):
        return self.parameter()

    class ParentMethods:
        def __init__(self, target, cells, **rest):
            self._target = target
            self._cells = cells
            super().__init__(**rest)

        def target(self):
            return self._target

        def cells(self):
            r"""The cells of this triangulation, as the polytopes it received.

            A cell is a polytope of the target's lattice lying in the target, or,
            for a placed target, that polytope placed where the target places its
            points.  The family is retained and not rebuilt: it is what the
            target answered in ``triangulate``.
            """
            return self._cells

        def covers_target(self):
            r"""Decide that the union of the cells is the target.

            Each cell is a subset of the target by construction, so the union is
            one too, and the answer is read off the normalized volumes: a
            finite union of closed cells whose volumes add up to the target's is
            the target.  Suppose the union missed a point of the target; the
            union is closed, so it misses a ball of the affine hull, and its
            volume is then smaller than the target's -- but a union's volume is
            at most the sum of its members' volumes, which is the target's.

            That decides coverage whenever the cells' interiors are pairwise
            disjoint, which is the case for the cells of a triangulation: their
            volumes then add up to the union's, so a union equal to the target
            has volumes adding up to the target's.  A family whose cells overlap
            in interior has a volume sum larger than its union's, and this
            answers ``False`` there: the addition it decides on does not see the
            union of an overlapping family.
            """
            target = _unplaced_polytope(self._target)
            cells = self._unplaced_cells()
            if not all(cell.is_contained_in(target) is True for cell in cells):
                return False
            return (
                sum(cell.normalized_volume() for cell in cells)
                == target.normalized_volume()
            )

        def intersections_are_common_faces(self):
            r"""Decide that two cells of this triangulation meet in a common face.

            For each pair of distinct cells the intersection is computed in the
            target's own lattice and asked whether it is a face of each cell: a
            face of a polytope is one of the polytopes of its face object, so
            the question is membership there, and the intersection of two cells
            that shares no face is not one of them.  An empty intersection is
            the empty face, which is a face of every polytope, so disjoint cells
            agree here.

            Two cells that touch along a part of a face -- a piece of an edge of
            each, say -- are answered ``False``: their intersection is a
            subpolytope of that face and not a face of either, so the pair is
            not a pair of closed cells meeting along a common face.
            """
            cells = self._unplaced_cells()
            for index, cell in enumerate(cells):
                for other in cells[index + 1:]:
                    meet = cell.intersection(other)
                    if int(meet.dimension()) < 0:
                        continue
                    if meet not in cell.face_poset():
                        return False
                    if meet not in other.face_poset():
                        return False
            return True

        def cells_are_integral(self):
            r"""Decide that every cell's vertices are lattice points of the target's lattice.

            The decision :class:`Integral` reads: each cell is asked whether it
            is a lattice polytope, which is whether every one of its vertices is
            a point of the lattice it is framed by -- the target's own.
            """
            return all(
                cell.is_lattice_polytope() is True for cell in self._unplaced_cells()
            )

        def cells_are_unimodular(self):
            r"""Decide that every cell has normalized volume one.

            The decision :class:`Unimodular` reads: the normalized volume of a
            cell of dimension ``d`` is ``d!`` times its lattice measure, so a
            cell has normalized volume one exactly when its vertices generate
            the lattice and its edge vectors span a fundamental parallelepiped.
            """
            return all(
                cell.normalized_volume() == 1 for cell in self._unplaced_cells()
            )

        def _unplaced_cells(self):
            r"""The polytopes the cells are, each read at the polytope it places."""
            return tuple(_unplaced_polytope(cell) for cell in self._cells)

    class Integral(CategoryWithAxiom):
        r"""Chosen triangulations integral relative to the target's selected lattices."""

        _certifying_predicate = "cells_are_integral"

        class ParentMethods:
            def lattice_comparison(self):
                pass

            def simplex_vertices_are_integral(self, simplex):
                r"""Decide that one cell's vertices are points of the target's lattice.

                A cell's vertices are points of the lattice the cell is framed
                by, and a cell of a triangulation of the target is framed by the
                target's own lattice, so the question is whether that frame is
                integral: every vertex of the cell is a point of its lattice.
                """
                return _unplaced_polytope(simplex).is_lattice_polytope() is True

    class Unimodular(CategoryWithAxiom):
        r"""Integral triangulations whose maximal simplices have normalized volume one."""

        _certifying_predicate = "cells_are_unimodular"

        def extra_super_categories(self):
            return [self.base_category().Integral()]

        class ParentMethods:
            def normalized_volume(self, simplex):
                r"""The normalized volume of one cell of this triangulation.

                The cells of a triangulation are its maximal simplices, so the
                normalized volumes this answers are the ones the axiom states:
                every one of them is one.  The volume is the cell's own, read in
                the lattice parallel to its affine hull, and not a measure of the
                ambient space.
                """
                return _unplaced_polytope(simplex).normalized_volume()
