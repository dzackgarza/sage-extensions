r"""Convex polytopes and integral lattice polytopes."""

from math import atan2, factorial

from sage.categories.category import Category
from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism
from sage.geometry.polyhedron.constructor import Polyhedron
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.element import parent as engine_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedCategory,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.hyperbolic_geometry import HyperbolicSpaces
from sage_extensions.categories.metric_affine_spaces import (
    EuclideanSpaces,
    SphericalSpaces,
)
from sage_extensions.categories.real_affine_spaces import (
    AffineSpacesWithLattice,
    RealAffineSpaces,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _own_ring,
    _owned_integers,
    _owned_rationals,
)
from sage_extensions.categories.sets.finite_families import (
    finite_family,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.set_categories import finite_ordinal_set
from sage_extensions.categories.sets.finite_graded_posets import FiniteGradedPosets
from sage_extensions.categories.sets.set_categories import PartiallyOrderedSets, Sets
from sage_extensions.categories.triangulations import ChosenTriangulations
from sage_extensions.owned_category import _object_of
from sage_extensions.owned_category_bases import CategoryWithAxiom

for _axiom in ("Integral", "Polygon"):
    if _axiom not in all_axioms:
        all_axioms.add(_axiom)


def _owned_rational(coordinate):
    r"""One coordinate as an owned rational.

    This is the ingress boundary of the polytope constructors, and the one
    place that admits all three ways a caller writes a coordinate: as an
    ordinary integer, as an engine rational, or as an owned rational.  The
    parent of the incoming value decides which, through Sage's own parent
    function rather than by asking the value for an attribute.
    """
    if engine_parent(coordinate) in (SageZZ, SageQQ):
        return _owned_engine_element(SageQQ, SageQQ(coordinate))
    return _owned_rationals()(coordinate)


class AbstractPolytopes(OwnedCategory):
    r"""Finite graded face posets satisfying the abstract-polytope axioms.

    Morphisms inherit the rank-preserving monotone maps of finite graded
    posets. Isomorphisms and automorphisms are the category's generic ``Isom``
    and ``Aut`` constructions; a geometric placement is further structure.
    """

    def super_categories(self):
        return [FiniteGradedPosets()]

    @classmethod
    def _repr_object_names(cls):
        return "abstract polytopes"

    def an_object(self):
        r"""The face poset of a zero-dimensional polytope.

        Such a polytope has two faces: the empty face, of dimension ``-1``, and
        its single vertex, of dimension ``0``, which covers it.  The finite
        graded poset of those two grades is the whole face poset, so no
        polyhedral computation is asked for it.
        """
        return self.from_face_poset(FiniteGradedPosets().an_object())

    def from_face_poset(self, face_poset):
        r"""Construct from the exact finite graded poset of faces.

        The carrier of ``face_poset`` is the family of faces and its grading is
        the affine dimension of each face, with the empty face of dimension
        ``-1``.
        """
        assert face_poset in FiniteGradedPosets(), (
            f"an abstract polytope is a finite graded poset of faces, but {face_poset} lies in "
            f"{face_poset.category()}"
        )
        return _object_of(
            self,
            underlying_poset=face_poset.underlying_poset(),
            grading_map=face_poset.grading_map(),
            face_poset=face_poset,
        )

    class ParentMethods:
        def __init__(self, face_poset, **rest) -> None:
            self._face_poset = face_poset
            super().__init__(**rest)

        def underlying_graded_poset(self):
            r"""Return the exact finite graded poset of faces, graded by dimension."""
            return self._face_poset

        def faces(self, dimension):
            r"""Faces of the selected rank, as elements of this face poset."""
            selected = int(dimension)
            return finite_ordered_set(
                tuple(face for face in self if int(self.grade(face)) == selected)
            )

        def face_poset(self):
            return self

        def _repr_(self):
            return f"Abstract polytope with {sum(1 for _face in self)} faces"

        def abstract_automorphisms(self):
            r"""Return ``Aut`` of the face poset: the abstract automorphisms.

            The automorphisms of an abstract polytope are the rank-preserving
            monotone self-isomorphisms of its finite graded face poset
            (``lean-categories/LeanCategories/Orders/FiniteGradedPoset.lean``:
            ``Hom`` is an ``OrderHom`` with ``grade_eq``, and ``Aut`` is the
            generic ``Iso`` on the diagonal).  This is that group itself, read on
            the retained face object: an element is a forward and an inverse
            rank-preserving order map of the faces, and applying it to a face is
            that face's image.
            """
            return self.Aut()


class PlacedPolytopeMor(CategoricalMor):
    r"""Ambient maps taking faces to faces and commuting with placements."""

    class ElementMethods:
        def __init__(self, parent, ambient_map, face_poset_map):
            Morphism.__init__(self, parent)
            self._ambient_map = ambient_map
            self._face_poset_map = face_poset_map

        def ambient_map(self):
            return self._ambient_map

        def face_poset_map(self):
            return self._face_poset_map

        def underlying_polytope_morphism(self):
            pass

        def _call_(self, point):
            return self._ambient_map(point)

        def __mul__(self, other):
            pass

    def _element_constructor_(self, ambient_map, face_poset_map):
        pass

    @object_level
    def identity(self):
        pass


class PlacedPolytopeMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = PlacedPolytopeMor


class MetricPolytopeMor(PlacedPolytopeMor):
    r"""Face-preserving arrows induced by ambient isometric embeddings."""

    class ElementMethods(PlacedPolytopeMor.ElementMethods):
        def ambient_isometric_embedding(self):
            return self.ambient_map()

    def _element_constructor_(self, ambient_isometric_embedding, face_poset_map):
        pass


class MetricPolytopeMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = MetricPolytopeMor


class _PlacedPolytopeFacePosetFunctor(Functor):
    def __init__(self, source):
        super().__init__(source, AbstractPolytopes())

    def _apply_object(self, polytope):
        pass

    def _apply_morphism(self, morphism):
        return morphism.face_poset_map()


class _PlacedPolytopeCategory(OwnedParameterizedCategory):
    r"""Polytopes whose selected inclusion has one fixed geometric ambient."""

    _MorCategory = PlacedPolytopeMorCategoryConstruction

    def ambient_space(self):
        return self.parameter()

    def placement_space(self):
        return self.ambient_space()

    def super_categories(self):
        return [Objects()]

    def an_object(self):
        pass

    def on(self, defining_data, ambient_inclusion):
        pass

    @cached_method
    def face_posets(self):
        return _PlacedPolytopeFacePosetFunctor(self)

    class ParentMethods:
        def __init__(self, defining_data, ambient_inclusion, **rest):
            self._defining_data = defining_data
            self._ambient_inclusion = ambient_inclusion
            super().__init__(**rest)

        def defining_data(self):
            return self._defining_data

        def ambient_space(self):
            return self.category().ambient_space()

        def ambient_inclusion(self):
            return self._ambient_inclusion

        def underlying_polytope(self):
            return self._ambient_inclusion.domain()

        def vertices(self):
            pass

        def faces(self, dimension):
            pass

        def face_inclusion(self, face):
            pass

        def face_poset(self):
            pass

        def abstract_automorphisms(self):
            pass

        def geometric_automorphisms(self):
            return self.Aut()

        def geometric_to_abstract_automorphisms(self):
            pass

        def geometric_lifts_of_face_automorphism(self, face_automorphism):
            pass

        def boundary(self):
            pass

        def boundary_inclusion(self):
            pass

        def triangulations(self):
            return ChosenTriangulations(self)

        def triangulate(self):
            pass

    class Polygon(CategoryWithAxiom):
        r"""Placed polytopes of affine or geodesic dimension two."""


class ConvexPolytopesIn(_PlacedPolytopeCategory):
    r"""Bounded convex subsets of one real affine space."""

    def parameter_category(self):
        return RealAffineSpaces()

    @classmethod
    def _repr_object_names(cls):
        return "placed convex affine polytopes"


class LatticePolytopeMor(PlacedPolytopeMor):
    r"""Face-preserving maps compatible with selected affine lattice embeddings."""

    class ElementMethods(PlacedPolytopeMor.ElementMethods):
        def ambient_lattice_map(self):
            return self.ambient_map()

        def underlying_affine_morphism(self):
            pass

    def _element_constructor_(self, ambient_lattice_map, face_poset_map):
        pass


class LatticePolytopeMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = LatticePolytopeMor


class _LatticePolytopeForgetfulFunctor(Functor):
    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, polytope):
        return polytope.underlying_affine_polytope()

    def _apply_morphism(self, morphism):
        return morphism.underlying_affine_morphism()


class LatticePolytopesIn(_PlacedPolytopeCategory):
    r"""Placed convex polytopes with vertices in the selected affine lattice."""

    _MorCategory = LatticePolytopeMorCategoryConstruction

    def parameter_category(self):
        return AffineSpacesWithLattice()

    def placement_space(self):
        return self.ambient_space().underlying_affine_space()

    @classmethod
    def _repr_object_names(cls):
        return "placed lattice polytopes"

    @cached_method
    def forget_lattice(self):
        r"""Forget the selected lattice on objects and face-preserving arrows."""
        affine_ambient = self.ambient_space().underlying_affine_space()
        return _LatticePolytopeForgetfulFunctor(self, ConvexPolytopesIn(affine_ambient))

    class ParentMethods(_PlacedPolytopeCategory.ParentMethods):
        def ambient_lattice_inclusion(self):
            return self.ambient_space().lattice_inclusion()

        def integral_points(self):
            pass

        def underlying_affine_polytope(self):
            pass


class EuclideanPolytopesIn(_PlacedPolytopeCategory):
    r"""Bounded convex polytopes in one selected Euclidean space."""

    _MorCategory = MetricPolytopeMorCategoryConstruction

    def parameter_category(self):
        return EuclideanSpaces()

    @classmethod
    def _repr_object_names(cls):
        return "placed Euclidean polytopes"


class SphericalGeodesicPolytopesIn(_PlacedPolytopeCategory):
    r"""Geodesically convex polytopes in one selected round sphere."""

    _MorCategory = MetricPolytopeMorCategoryConstruction

    def parameter_category(self):
        return SphericalSpaces()

    def from_cone(self, cone, ambient_linear_embedding):
        r"""Select the spherical section of a cone in this sphere's ambient space."""
        pass

    @classmethod
    def _repr_object_names(cls):
        return "placed spherical geodesic polytopes"


class HyperbolicGeodesicPolytopesIn(_PlacedPolytopeCategory):
    r"""Geodesically convex polytopes in one selected hyperbolic space."""

    _MorCategory = MetricPolytopeMorCategoryConstruction

    def parameter_category(self):
        return HyperbolicSpaces(self.parameter().dimension())

    @classmethod
    def _repr_object_names(cls):
        return "placed hyperbolic geodesic polytopes"


class RegularPolytopeMor(CategoricalMor):
    r"""Maps of regular polytopes through their abstract face structures."""

    class ElementMethods:
        def __init__(self, parent, abstract_polytope_map):
            Morphism.__init__(self, parent)
            self._abstract_polytope_map = abstract_polytope_map

        def abstract_polytope_map(self):
            return self._abstract_polytope_map

        def __mul__(self, other):
            pass

    def _element_constructor_(self, abstract_polytope_map):
        pass

    @object_level
    def identity(self):
        pass


class RegularPolytopeMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = RegularPolytopeMor


class _RegularAbstractPolytopeFunctor(Functor):
    r"""Forget the regular presentation on objects and face maps."""

    def __init__(self):
        super().__init__(RegularPolytopes(), AbstractPolytopes())

    def _apply_object(self, polytope):
        return polytope.abstract_polytope()

    def _apply_morphism(self, morphism):
        return morphism.abstract_polytope_map()


class RegularPolytopes(OwnedCategory):
    r"""Finite spherical regular abstract polytopes named by Schlaefli symbols.

    The Schlaefli symbol ``{p_1,...,p_{n-1}}`` determines the string Coxeter
    diagram ``[p_1,...,p_{n-1}]`` of the full reflection symmetry group.  This
    owner records that abstract regular-polytope datum; it is distinct from the
    rational-coordinate convex-polytope owner below, since examples such as the
    dodecahedron require ``sqrt(5)`` coordinates in a Euclidean realization.
    Its underlying combinatorial object is the graded face poset.
    """

    _MorCategory = RegularPolytopeMorCategoryConstruction

    def an_object(self):
        return self.from_schlafli_symbol((3, 3))

    @classmethod
    def _repr_object_names(cls):
        return "finite spherical regular polytopes"

    def super_categories(self):
        return [Objects()]

    @cached_method
    def abstract_face_structure(self):
        return _RegularAbstractPolytopeFunctor()

    def from_schlafli_symbol(self, symbol):
        r"""Return the finite regular abstract polytope with Schlaefli symbol ``symbol``."""
        from sage_extensions.categories.coxeter_diagrams import CoxeterDiagrams

        match symbol:
            case str() as written:
                written = written.strip()
                if not (written.startswith("{") and written.endswith("}")):
                    raise ValueError(
                        f"a Schlaefli symbol is written {{p1,...,pr}}, but {written!r} is not in braces"
                    )
                body = written[1:-1].strip()
                bonds = () if not body else tuple(int(part.strip()) for part in body.split(","))
            case _:
                bonds = tuple(int(bond) for bond in symbol)
        if not bonds or any(bond < 3 for bond in bonds):
            raise ValueError(
                f"a Schlaefli symbol {{p1,...,pr}} needs r >= 1 entries, each at least 3, but it is {bonds}"
            )
        rank = len(bonds) + 1
        entries = tuple(
            tuple(
                1
                if row == column
                else bonds[min(row, column)]
                if abs(row - column) == 1
                else 2
                for column in range(rank)
            )
            for row in range(rank)
        )
        diagram = CoxeterDiagrams().from_coxeter_matrix(entries)
        assert diagram.is_elliptic(), (
            f"the Schlaefli symbol {bonds} does not define a finite regular polytope: its Coxeter "
            "group is infinite (the Coxeter diagram is not spherical)"
        )
        return _object_of(
            self,
            schlafli_bonds=finite_ordered_set(bonds),
            symmetry_coxeter_diagram=diagram,
        )

    class ParentMethods:
        def __init__(self, schlafli_bonds, symmetry_coxeter_diagram, **rest) -> None:
            self._schlafli_bonds = schlafli_bonds
            self._symmetry_coxeter_diagram = symmetry_coxeter_diagram
            super().__init__(**rest)

        def schlafli_symbol(self):
            return self._schlafli_bonds

        def dimension(self):
            return _owned_integers()(self.schlafli_symbol().cardinality() + 1)

        def symmetry_coxeter_diagram(self):
            return self._symmetry_coxeter_diagram

        def symmetry_group(self):
            return self.symmetry_coxeter_diagram().coxeter_group()

        def abstract_polytope(self):
            pass

        def face_poset(self):
            pass

        def abstract_automorphisms(self):
            pass

        def _repr_(self):
            symbol = ",".join(str(bond) for bond in self.schlafli_symbol())
            return f"Regular polytope {{{symbol}}}"


class _RationalPolytopeFacePosetFunctor(Functor):
    r"""Send a rational polytope and its maps to face-incidence objects."""

    def __init__(self, source):
        super().__init__(source, AbstractPolytopes())

    def _apply_object(self, polytope):
        pass

    def _apply_morphism(self, morphism):
        pass


class ConvexPolytopes(OwnedParameterizedCategory):
    r"""Rational convex polytopes in a chosen coordinate lattice.

    Public coordinate data live in the owned modules ``ZZ^n`` and ``QQ^n``.
    Sage's exact ``Polyhedron`` is retained only as the private polyhedral
    computation engine.
    """

    def parameter_category(self):
        from sage_extensions.categories.modules.framed.framed_free_modules import (
            FramedFreeModules,
        )

        return FramedFreeModules(_owned_integers())

    def ambient_lattice(self):
        return self.base()

    @cached_method
    def ambient_space(self):
        rationals = _owned_rationals()
        return rationals.free_module(self.ambient_lattice().module_generating_set())

    def an_object(self):
        r"""The standard simplex in this category's rational coordinate space."""
        labels = tuple(self.ambient_lattice().module_generating_set())
        zero = tuple(0 for _label in labels)
        vertices = [zero]
        for selected in labels:
            vertices.append(tuple(1 if label == selected else 0 for label in labels))
        return self(vertices)

    def _call_(self, vertices, lattice=None):
        r"""Construct the convex polytope on the selected vertices."""
        if lattice is not None and lattice is not self.ambient_lattice():
            raise ValueError(
                f"polytopes in {self} have vertices in the lattice {self.ambient_lattice()}, not in {lattice}"
            )
        return _convex_polytope(vertices, lattice=self.ambient_lattice())

    def from_halfspaces(self, halfspaces, lattice=None):
        r"""The polytope cut out by a family of affine halfspaces.

        Each halfspace is the pair ``(b, a)`` of the constant and the linear
        part of ``b + <a, x> >= 0`` in the coordinates of ``lattice``, so the
        family is the halfspace description of the intersection.  A polytope
        is bounded, and an unbounded intersection is refused rather than
        truncated.  Passing from this description to the vertices is the
        private polyhedral computation.
        """
        if lattice is not None and lattice is not self.ambient_lattice():
            raise ValueError(
                f"polytopes in {self} have vertices in the lattice {self.ambient_lattice()}, not in {lattice}"
            )
        rationals = _owned_rationals()
        labels = tuple(self.ambient_lattice().module_generating_set())
        defining_halfspaces = tuple(
            (
                _owned_rational(constant),
                tuple(_owned_rational(coefficient) for coefficient in linear_part),
            )
            for constant, linear_part in halfspaces
        )
        engine_rows = [
            [
                _engine_element(rationals, constant),
                *(
                    _engine_element(rationals, coefficient)
                    for coefficient in linear_part
                ),
            ]
            for constant, linear_part in defining_halfspaces
        ]
        # The halfspaces are written in the coordinates of the ambient lattice,
        # so the region is a subset of ``L tensor QQ``, of dimension
        # ``len(labels)``.  The engine otherwise reads its dimension off the rows
        # and answers for ``QQ^0`` when the family is empty (TRAPS.md, "Sage's
        # ``Polyhedron`` reads its ambient dimension off the H-representation
        # rows").
        polyhedron = Polyhedron(
            ieqs=engine_rows, ambient_dim=len(labels), base_ring=SageQQ
        )
        if not polyhedron.is_compact():
            raise ValueError(
                f"the halfspaces {halfspaces} cut out an unbounded region, so they do not define a polytope"
            )
        return _convex_polytope(
            engine_polyhedron=polyhedron,
            lattice=self.ambient_lattice(),
            defining_data=("halfspaces", defining_halfspaces),
        )

    @classmethod
    def _repr_object_names(cls):
        return "convex polytopes"

    def super_categories(self):
        return [Sets().Subobjects(self.ambient_space())]

    @cached_method
    def face_posets(self):
        return _RationalPolytopeFacePosetFunctor(self)

    class SubcategoryMethods:
        def ambient_lattice(self):
            return self.base_category().ambient_lattice()

        def ambient_space(self):
            return self.base_category().ambient_space()

        def Integral(self) -> Category:
            r"""Return this category with the axiom that every vertex is a lattice point."""
            return self._with_axiom("Integral")

        def Polygon(self) -> Category:
            r"""Return this category with the axiom that the affine dimension is two."""
            return self._with_axiom("Polygon")

    class ParentMethods:
        def __init__(self, engine_polyhedron, ambient_lattice, defining_data, **rest) -> None:
            r"""Retain the selected presentation and its private exact polyhedron.

            The presentation records vertices or halfspaces in the owned
            coordinate space. The polyhedron computes with that datum over
            the selected ``ZZ^n`` lattice.
            """
            self._polyhedron = engine_polyhedron
            self._ambient_lattice = ambient_lattice
            self._defining_data = defining_data
            super().__init__(**rest)

        def _engine_polyhedron(self):
            r"""Return the private exact polyhedral computation object."""
            return self._polyhedron

        def defining_data(self):
            r"""Return the selected vertex or halfspace presentation in the ambient space."""
            return self._defining_data

        def threejs_html(self):
            r"""Return a local Three.js HTML view of a three-dimensional polytope.

            The private exact Sage polyhedron remains the rendering engine.
            This method does not attach display data to the owned polytope: it
            asks Sage's existing ``Graphics3d`` Three.js serializer for a
            self-contained local HTML representation at the view boundary.
            """
            assert int(self._engine_polyhedron().ambient_dim()) == 3, (
                f"a three-dimensional view of {self} needs its vertices in a lattice of rank 3, but "
                f"the lattice has rank {self._engine_polyhedron().ambient_dim()}"
            )
            graphic = self._engine_polyhedron().plot()
            rich = graphic._rich_repr_threejs(online=False)
            return rich.html.get_str()

        def _owned_rational_coordinate(self, coordinate):
            rationals = _owned_rationals()
            return _owned_engine_element(rationals, SageQQ(coordinate))

        def _owned_integral_coordinate(self, coordinate):
            integers = _owned_integers()
            return _owned_engine_element(integers, SageZZ(coordinate))

        def rational_point(self, point):
            r"""Return ``point`` of ``M`` or ``M_QQ`` as a point of ``M_QQ = M tensor QQ``.

            ``M`` includes into ``M_QQ`` by ``m |-> m tensor 1``, which keeps
            the coordinates of ``m`` in the shared frame.

            A point may also be written by its coordinates: a lattice vertex and
            the point of the ambient space at the same coordinates are one point
            of ``M_QQ``, and the polyhedra of this category are presented in
            coordinates throughout, so a sequence of ambient coordinates is read
            through the ambient space's own ingress.  Any other value is left to
            that ingress too, which refuses what is not a point of it.
            """
            ambient = self.ambient_space()
            lattice = self.ambient_lattice()
            match engine_parent(point):
                case parent if parent is lattice:
                    rationals = _owned_rationals()
                    coordinates = point.to_vector()
                    return ambient.linear_combination(
                        {
                            label: rationals(coordinates(label))
                            for label in coordinates.support().domain()
                        }
                    )
                case _:
                    return ambient(point)

        def _engine_coordinates(self, point):
            rationals = _owned_rationals()
            ambient = self.ambient_space()
            point = self.rational_point(point)
            coordinates = point.to_vector()
            return tuple(
                _engine_element(rationals, coordinates(label))
                for label in ambient.module_generating_set()
            )

        def ambient_lattice(self):
            r"""Return the owned coordinate lattice ``ZZ^n``."""
            return self._ambient_lattice

        def ambient_space(self):
            r"""Return the owned rational coordinate module ``QQ^n``."""
            return self.codomain()

        def dimension(self):
            return _owned_integers()(int(self._engine_polyhedron().dim()))

        def vertices(self):
            if self.is_lattice_polytope():
                vertices = tuple(
                    self.ambient_lattice()(
                        tuple(
                            self._owned_integral_coordinate(coordinate)
                            for coordinate in vertex
                        )
                    )
                    for vertex in self._engine_polyhedron().vertices()
                )
                rational_vertices = tuple(self.rational_point(vertex) for vertex in vertices)
                index_set = finite_ordinal_set(len(vertices))
                indices = tuple(index_set)

                def index_of(point):
                    # The selected integral enumeration has a canonical image
                    # in M_QQ. Its inverse must recognize that image too, so
                    # membership and the ordered-set ranking agree.
                    try:
                        rational_point = self.rational_point(point)
                    except (TypeError, ValueError, AttributeError):
                        return None
                    for index, vertex in zip(indices, rational_vertices, strict=True):
                        if (rational_point == vertex) is True:
                            return index
                    return None

                def contains(point):
                    return index_of(point) is not None

                return FiniteOrderedSets().from_indexed(
                    index_set,
                    lambda index: vertices[int(index)],
                    index_of=index_of,
                    contains=contains,
                    equivalent=lambda left, right: (
                        self.rational_point(left) == self.rational_point(right)
                    ) is True,
                )
            rationals = _owned_rationals()
            return finite_ordered_set(
                tuple(
                    self.ambient_space()(
                        tuple(
                            self._owned_rational_coordinate(coordinate)
                            for coordinate in vertex
                        ),
                    )
                    for vertex in self._engine_polyhedron().vertices()
                )
            )

        def n_vertices(self):
            return _owned_integers()(int(self._engine_polyhedron().n_vertices()))

        @cached_method
        def _vertex_coordinate_set(self):
            r"""Return the vertex set as coordinates in the ambient space's frame.

            A polytope is the convex hull of its vertices, so this set is the
            polytope.  The coordinates are read in ``M tensor QQ``, where a
            lattice vertex and the same point of the ambient space are one
            point, so the polytope of a vertex list and the polytope the
            private exact polyhedron computes from a halfspace description meet
            here.  The set is cached because it is what this polytope's
            equality and hash read, and it is read from that polyhedron.
            """
            return frozenset(
                self._engine_coordinates(self.ambient_space()(tuple(vertex)))
                for vertex in self._engine_polyhedron().vertices()
            )

        def is_contained_in(self, other):
            r"""Whether this polytope lies in another polytope of the ambient space.

            A polytope is the convex hull of its vertices, and a polytope is
            convex, so a convex hull lies in one exactly when its vertices do
            (Mathlib, ``convexHull_min``, ``Mathlib/Analysis/Convex/Hull.lean``):
            the vertices of this polytope against the halfspaces of ``other``
            decide the subset relation, and a vertex that fails one of them is
            a point of this polytope that is not a point of ``other``.

            The polytopes are compared in the coordinate lattice that frames
            them, which is the category's parameter and the module their
            vertices are elements of, so ``other`` must be an object of this
            polytope's own :class:`ConvexPolytopes`, tested as ``other in C``.
            The polar dual is framed by the dual lattice, whose points are the
            functionals on this one and not its points, and no duality
            identifies the two spaces; a polytope of another lattice is
            therefore not one of these.  A subset of the ambient space that is
            not a polytope has no halfspace description to test, so the
            defining membership condition of such a subset decides it.
            """
            match other in ConvexPolytopes(self.ambient_lattice()):
                case True:
                    return all(
                        other.contains_point(vertex) for vertex in self.vertices()
                    )
                case False:
                    return super().is_contained_in(other)

        def is_equal_to(self, other) -> bool:
            r"""Return whether the two polytopes are the same subset of the ambient space.

            Two polytopes of one lattice are equal exactly when they have the
            same vertices: a polytope is the convex hull of its vertex set, and
            the vertices are the points of the polytope that are not a convex
            combination of other points of it, so the subset determines them.
            The lattice is read with the vertices, since they are elements of
            it: :meth:`_vertex_coordinate_set` reads them in the ambient space
            of that lattice, and a polytope framed by another lattice is
            another subset.  Containment agrees: :meth:`is_contained_in` tests
            the vertices of one polytope against the halfspaces of the other,
            so each polytope lies in the other exactly when their vertex sets
            are one set.
            """
            return (
                other.ambient_lattice() is self.ambient_lattice()
                and self._vertex_coordinate_set() == other._vertex_coordinate_set()
            )

        def __eq__(self, other):
            r"""Two polytopes of one lattice are equal when they have the same vertices.

            Equal sets are one factor of a product (`SET-05`), so equality
            reads the vertex set that :meth:`__hash__` hashes.  A polytope is
            its vertex set, which decides it, and which is the canonical form
            of the vertex and halfspace presentations that
            :meth:`is_contained_in` compares.  Membership in
            :class:`ConvexPolytopes` at this polytope's own lattice recognizes
            the other polytopes that are comparable; an operand of another kind
            -- a number, a set that is not a polytope, a polytope of another
            lattice -- is left to the inherited equality.
            """
            if self is other:
                return True
            if other in ConvexPolytopes(self.ambient_lattice()):
                return self.is_equal_to(other)
            return super().__eq__(other)

        @cached_method
        def __hash__(self) -> int:
            r"""Hash the lattice and the vertex set, which :meth:`__eq__` compares.

            A polytope is determined by its vertices, so their coordinates in
            the ambient space of its lattice are a complete invariant of the
            subset: equal polytopes have equal hashes, and the coordinates do
            not depend on the order the private exact polyhedron enumerated the
            vertices in.  Equality compares two polytopes framed by one lattice
            and hashes are equal only for equal polytopes, so the lattice is
            hashed beside the vertex set.  The hash is cached: a polytope is a
            factor of the interned finite products, whose store keys a family
            by its factors' hashes (`SET-05`), and the vertex set is computed
            from that polyhedron.
            """
            return hash((id(self.ambient_lattice()), self._vertex_coordinate_set()))

        def facets(self):
            r"""Return the codimension-one faces as owned polytopes."""
            return finite_ordered_set(
                tuple(
                    _convex_polytope(
                        engine_polyhedron=facet.as_polyhedron(),
                        lattice=self.ambient_lattice(),
                    )
                    for facet in self._engine_polyhedron().facets()
                )
            )

        @cached_method
        def _engine_face_lattice(self):
            r"""Return the faces of the private exact polyhedron, the empty face first.

            A face of a polyhedron is the set of points where a family of the
            defining inequalities is saturated; the face lattice orders them by
            inclusion, its bottom element is the empty face of dimension ``-1``
            and its top element is the whole polyhedron.  The faces are read off
            the exact polyhedron, which is the selected polyhedral computation
            (``sage.geometry.polyhedron.base4``, ``face_lattice``).
            """
            return tuple(self._engine_polyhedron().face_lattice())

        @cached_method
        def _engine_face_vertex_indices(self):
            r"""The ambient V-representation indices of each face, in face-lattice order.

            A face of a polytope is the convex hull of its vertices, so the set
            of vertices on a face identifies that face among the faces of this
            polytope, and the empty face is the face with no vertices.  The
            indices are those of the polyhedron's own V-representation, which is
            the order :meth:`_engine_vertex_coordinates` reads.
            """
            return tuple(
                frozenset(face.ambient_V_indices())
                for face in self._engine_face_lattice()
            )

        @cached_method
        def _engine_face_rank_by_vertex_indices(self):
            r"""The face-lattice position of the face spanned by each set of vertices."""
            return {
                vertices: rank
                for rank, vertices in enumerate(self._engine_face_vertex_indices())
            }

        @cached_method
        def _engine_vertex_coordinates(self):
            r"""The private coordinates of the ambient V-representation entries, in their order."""
            return tuple(
                tuple(SageQQ(coordinate) for coordinate in representation.vector())
                for representation in self._engine_polyhedron().Vrepresentation()
            )

        @cached_method
        def _embedded_vertex_coordinates(self):
            r"""The private coordinates of the owned vertices, in :meth:`vertices` order.

            A point of the ambient space and a lattice vertex are one point of
            it, so these are the coordinates of the very points :meth:`vertices`
            enumerates, read in the frame of :meth:`ambient_space`.
            """
            return tuple(
                tuple(SageQQ(coordinate) for coordinate in self._engine_coordinates(vertex))
                for vertex in self.vertices()
            )

        @cached_method
        def _engine_vertex_rank_in_vertices(self):
            r"""The rank in :meth:`vertices` of each ambient V-representation entry.

            The private polyhedron indexes its V-representation by its own order
            and the owned vertex set ranks the same points in its own order;
            this is the correspondence between the two, computed by coordinates
            rather than by position, so a polytope presented by halfspaces and
            one presented by its vertices agree on it.
            """
            owned = self._embedded_vertex_coordinates()
            ranks = []
            for representation, point in zip(
                self._engine_polyhedron().Vrepresentation(),
                self._engine_vertex_coordinates(),
                strict=True,
            ):
                assert representation.is_vertex(), (
                    f"the ambient V-representation of {self} holds the non-vertex {representation}, so its "
                    "entries are not the vertices of this polytope"
                )
                assert point in owned, (
                    f"the V-representation entry {representation} of {self} is at the private coordinates "
                    f"{point}, which are not the coordinates of an owned vertex; the owned vertices are at "
                    f"{owned}"
                )
                ranks.append(owned.index(point))
            return tuple(ranks)

        @cached_method
        def _owned_vertices_in_engine_order(self):
            r"""The owned vertices, in the private V-representation order."""
            vertices = tuple(self.vertices())
            return tuple(
                vertices[rank] for rank in self._engine_vertex_rank_in_vertices()
            )

        @cached_method
        def _engine_face_by_vertex_indices(self):
            r"""The private face on each set of ambient vertex indices."""
            return dict(
                zip(
                    self._engine_face_vertex_indices(),
                    self._engine_face_lattice(),
                    strict=True,
                )
            )

        @cached_method
        def _owned_face(self, vertices):
            r"""The owned polytope on the face with these ambient vertex indices.

            A face is a polytope in the same ambient lattice as this one; the
            private exact polyhedron's own face is what presents it, and no
            coordinate is read from any other space.
            """
            assert vertices in self._engine_face_by_vertex_indices(), (
                f"{set(vertices)} is not the vertex set of a face of {self}; the faces are spanned by "
                f"{tuple(sorted(self._engine_face_by_vertex_indices(), key=sorted))}"
            )
            return _convex_polytope(
                engine_polyhedron=self._engine_face_by_vertex_indices()[vertices].as_polyhedron(),
                lattice=self.ambient_lattice(),
            )

        @cached_method
        def _owned_faces(self):
            r"""The faces of this polytope as polytopes, the empty face first.

            The top face is the face spanned by all the vertices, which is this
            polytope, so the face poset retains the supplied polytope itself
            rather than an equal copy of it.
            """
            everything = frozenset(range(len(self._engine_vertex_coordinates())))
            return tuple(
                self if vertices == everything else self._owned_face(vertices)
                for vertices in self._engine_face_vertex_indices()
            )

        @cached_method
        def _face_poset_carrier(self):
            r"""The family of faces this polytope's face poset is carried by, in face-lattice order."""
            return finite_ordered_set(self._owned_faces())

        def faces(self, dimension):
            r"""The faces of the selected dimension, with their common ambient.

            Dimensions run from ``-1``, the empty face, to the dimension of this
            polytope.  A face of a polytope is again a polytope of the same
            ambient lattice, and the faces of one dimension are those the face
            lattice grades by it.
            """
            selected = int(dimension)
            return finite_ordered_set(
                tuple(
                    face
                    for face in self._owned_faces()
                    if int(face.dimension()) == selected
                )
            )

        def face_inclusion(self, face):
            r"""The selected face arrow from ``face`` into this polytope."""
            pass

        @cached_method
        def face_poset(self):
            r"""The exact finite graded poset of the faces of this polytope.

            The carrier is the family of faces as polytopes of this polytope's
            ambient lattice, the grading is the affine dimension of a face, the
            empty face being of dimension ``-1``, and the order is face
            inclusion.  A face is the convex hull of its vertices and a polytope
            is convex, so one face lies in another exactly when its vertices are
            among the other's, which is the incidence the face lattice records.

            This is the object an abstract polytope is
            (:class:`AbstractPolytopes`): the polytopes of one dimension are the
            faces of that rank, and the rank-preserving monotone self-maps of it
            are the polytope's combinatorial automorphisms.  Its automorphism
            group is realized by :meth:`abstract_automorphisms`, which this
            polytope's own exact face lattice computes.
            """
            vertices_of = dict(
                zip(
                    self._owned_faces(),
                    self._engine_face_vertex_indices(),
                    strict=True,
                )
            )
            order = PartiallyOrderedSets()(
                self._face_poset_carrier(),
                lambda face, other: vertices_of[face] <= vertices_of[other],
            )
            graded = FiniteGradedPosets().on(order, lambda face: face.dimension())
            return AbstractPolytopes().from_face_poset(graded)

        def facet_inclusion(self, facet):
            r"""The selected face arrow from ``facet`` into this polytope."""
            pass

        def boundary(self):
            pass

        def boundary_inclusion(self):
            pass

        @cached_method
        def _combinatorial_vertex_permutations(self):
            r"""The combinatorial automorphism generators, as permutations of the vertices.

            The combinatorial automorphism group of a polytope is computed as
            the automorphism group of the vertex-facet graph: the bipartite
            graph with one node per vertex and one per facet, and an edge
            between a vertex and a facet exactly when the vertex lies on the
            facet.  Its automorphisms are the incidence-preserving permutations
            of the vertices and facets, and that group is isomorphic to the
            automorphism group of the face lattice (Klee--Kleinschmidt,
            *Convex polytopes and related complexes*, Handbook of Combinatorics
            Vol. 1, Ch. 18, 1995, pp. 877--878, and Sage's
            ``combinatorial_automorphism_group``).  The vertex-edge graph alone
            does not determine the face lattice, so the incidence with the
            facets is what is read here.

            Each returned permutation is written on the vertices in the private
            V-representation order, and each of them is the vertex part of one
            generator of that group.  A face is the convex hull of its vertices
            and the incidence preserves which vertex sets span faces, so these
            permutations determine, and are determined by, the automorphisms of
            the face poset.
            """
            polyhedron = self._engine_polyhedron()
            representations = tuple(polyhedron.Vrepresentation())
            position = {
                representation: index
                for index, representation in enumerate(representations)
            }

            def images(generator):
                images_of_vertex = []
                for representation in representations:
                    image = generator(representation)
                    assert image in position, (
                        f"the combinatorial automorphism {generator} carries the vertex {representation} "
                        f"to {image}, which is not a vertex of {self}; the automorphisms of the "
                        "vertex-facet graph preserve its two kinds of node"
                    )
                    images_of_vertex.append(position[image])
                return tuple(images_of_vertex)

            return tuple(
                images(generator)
                for generator in polyhedron.combinatorial_automorphism_group().gens()
            )

        @cached_method
        def _restricted_vertex_permutations(self):
            r"""The restricted affine automorphism generators, as permutations of the vertices.

            The restricted automorphism group of a polytope is the subgroup of
            its affine automorphism group generated by permutations of the
            V-representation objects of one type; it is a subgroup of the
            combinatorial automorphism group, and it is generally smaller
            (Bremner--Dutour Sikiric--Schuermann, *Polyhedral representation
            conversion up to symmetries*, AMS/CRM Lecture Notes 48 (2009),
            45--71, arXiv:math/0702239; Sage's
            ``restricted_automorphism_group``).

            What is read here is that group's permutation action on the
            vertices, in the private V-representation order.  On a polytope of
            lower dimension than its ambient space, the affine realization the
            private engine also offers is an affine map that acts as the
            identity on a complement of the polytope's affine span; that
            complement is a choice, so the action on the vertices -- which span
            the polytope -- is what this polytope retains, and no action on an
            unused complement is claimed.
            """
            polyhedron = self._engine_polyhedron()
            indices = tuple(range(len(self._engine_vertex_coordinates())))
            return tuple(
                tuple(int(generator(index)) for index in indices)
                for generator in polyhedron.restricted_automorphism_group(
                    output="permutation"
                ).gens()
            )

        def _face_permutation_of_a_vertex_permutation(self, vertex_permutation):
            r"""The face each face goes to under a permutation of the vertices.

            A permutation of the vertices carries a face to the face spanned by
            the images of its vertices.  That image is a face exactly when the
            permutation preserves the incidence of the vertices with the
            facets, which is what a combinatorial automorphism does; a
            permutation that does not is refused here rather than sent to a
            chosen face.
            """
            ranks = self._engine_face_rank_by_vertex_indices()
            images = []
            for vertices in self._engine_face_vertex_indices():
                image = frozenset(vertex_permutation[index] for index in vertices)
                assert image in ranks, (
                    f"the vertex permutation {vertex_permutation} carries the face on the vertices "
                    f"{tuple(sorted(vertices))} to the vertices {tuple(sorted(image))}, which span no face of "
                    f"{self}, so it is not a combinatorial automorphism of this polytope"
                )
                images.append(ranks[image])
            return tuple(images)

        def _face_permutation_of_owned_vertex_permutation(self, element):
            r"""The faces' permutation induced by an element acting on the owned vertices."""
            index_of = self.vertices().ranking_map()
            engine_vertices = self._owned_vertices_in_engine_order()
            vertex_permutation = tuple(
                int(index_of(element(vertex))) for vertex in engine_vertices
            )
            return self._face_permutation_of_a_vertex_permutation(vertex_permutation)

        @cached_method
        def abstract_automorphisms(self):
            r"""The automorphism group of this polytope's face poset, acting on its faces.

            An abstract automorphism of a polytope is an automorphism of its
            face lattice: a rank-preserving monotone self-isomorphism of the
            finite graded poset of its faces
            (``lean-categories/LeanCategories/Orders/FiniteGradedPoset.lean``).
            The faces are retained as the polytopes they are, so this is the
            ``Aut`` of the face poset itself, computed by that owner: an element
            is a forward and an inverse rank-preserving order map of the faces,
            and applying it to a face is that face's image.
            """
            return self.face_poset().abstract_automorphisms()

        @cached_method
        def geometric_automorphisms(self):
            r"""The restricted affine automorphisms of this polytope, acting on its vertices.

            A geometric automorphism of a polytope is an affine automorphism of
            the ambient space carrying the polytope onto itself.  The group
            retained here is the restricted one: the subgroup generated by
            permutations of the V-representation objects of one type, which is
            how the private engine computes the affine automorphism group of a
            polytope exactly (Bremner--Dutour Sikiric--Schuermann, AMS/CRM
            Lecture Notes 48 (2009), 45--71).

            The action is on the vertices, in the polytope's own vertex set.  An
            affine map carrying a polytope onto itself is determined by its
            values on the vertices, and the vertices span the polytope, so this
            action is faithful; a matrix the private engine may also return for
            a polytope of lower dimension than its ambient space acts as the
            identity on a chosen complement, and that choice is not part of what
            this group states.
            """
            from sage_extensions.categories.group.groups import SymmetricGroups

            group = SymmetricGroups()(self.vertices())
            ranks = self._engine_vertex_rank_in_vertices()
            engine_index = [0] * len(ranks)
            for index, rank in enumerate(ranks):
                engine_index[rank] = index
            generators = tuple(
                group(
                    [
                        ranks[permutation[engine_index[rank]]] + 1
                        for rank in range(len(ranks))
                    ]
                )
                for permutation in self._restricted_vertex_permutations()
            )
            return group.subgroup(generators or (group.one(),))

        @cached_method
        def geometric_to_abstract_automorphisms(self):
            r"""The group map from the geometric to the abstract automorphisms.

            A geometric automorphism of this polytope is an affine automorphism
            of the ambient space carrying it onto itself, and it carries faces
            to faces: the image of the convex hull of a set of vertices is the
            convex hull of the images of those vertices, and an affine
            automorphism of the polytope permutes its vertices.  That induced
            permutation of the faces preserves the rank and the incidence of the
            face poset, so it is an abstract automorphism, and the assignment is
            a homomorphism because composing two affine maps composes the
            permutations they induce.

            Its target is the ``Aut`` of the face poset itself, so a value is an
            automorphism of the faces -- a forward rank-preserving order map and
            its inverse -- and not a permutation of them recorded beside the
            poset.  The map is an owned group morphism between the two owned
            groups, and its values on the source's generators are checked to
            satisfy the source's relations, so a group whose induced face maps do
            not satisfy them is refused here rather than represented.
            """
            from sage_extensions.categories.group.groups import OwnedGroups

            geometric = self.geometric_automorphisms()
            abstract = self.abstract_automorphisms()
            face_poset = self.face_poset()
            return OwnedGroups().Mor(geometric, abstract)(
                {
                    generator: face_poset.automorphism_from_positions(
                        self._face_permutation_of_owned_vertex_permutation(generator)
                    )
                    for generator in geometric.selected_subgroup_generators()
                },
                check=True,
            )

        def geometric_lifts_of_face_automorphism(self, face_automorphism):
            pass

        def triangulations(self):
            return ChosenTriangulations(self)

        def triangulate(self):
            pass

        def _engine_point_configuration(self):
            r"""Lower the owned vertices to a private Sage point configuration."""
            pass

        def _engine_normal_fan(self):
            r"""Return the private normal-fan computation object."""
            return self._engine_polyhedron().normal_fan(direction="inner")

        @cached_method
        def normal_fan(self):
            r"""Return the normal fan ``Sigma_P`` in ``N_R`` (CLS Def. 2.3.2).

            The polytope lives in ``M_R`` for ``M`` its coordinate lattice, so
            the normal fan lives in the dual lattice ``N``.  The cone of a face
            ``Q`` is spanned by the *inner* normals of the facets containing
            ``Q``, which is the convention under which ``X_{Sigma_P}`` carries
            ``P`` as the polytope of an ample divisor.
            """
            from sage_extensions.categories.schemes.toric.fans import (
                RationalPolyhedralFans,
            )

            assert int(self.dimension()) == int(
                self._engine_polyhedron().ambient_dim()
            ), (
                f"the normal fan of {self} is defined only for a full-dimensional polytope, but it "
                f"has dimension {self.dimension()} in a lattice of rank "
                f"{self._engine_polyhedron().ambient_dim()}"
            )
            cocharacters = self.ambient_lattice().dual_module()
            return RationalPolyhedralFans(cocharacters)._from_engine_fan(
                self._engine_normal_fan()
            )

        def volume(self):
            rationals = _owned_rationals()
            return _owned_engine_element(rationals,
                SageQQ(self._engine_polyhedron().volume())
            )

        def normalized_volume(self):
            r"""Volume normalized in the lattice parallel to the affine hull.

            For affine dimension ``d`` the measure is ``d!`` times lattice
            measure, so a unimodular simplex has volume one even when it
            lies in a larger ambient lattice. A rational polytope need not
            have integral normalized volume. The empty polytope has volume
            zero and a point has volume one.

            The full-dimensional case retains the existing exact ambient
            engine computation. In lower dimension the selected polyhedral
            engine must supply its exact ``induced_lattice`` measure; an
            unavailable relative-volume algorithm is a computation frontier.
            """
            polyhedron = self._engine_polyhedron()
            dimension = int(self.dimension())
            if dimension < 0:
                value = SageQQ.zero()
            elif dimension == 0:
                value = SageQQ.one()
            elif dimension == polyhedron.ambient_dim():
                value = factorial(dimension) * SageQQ(polyhedron.volume())
            else:
                value = SageQQ(polyhedron.volume(measure="induced_lattice"))
            target = SageZZ if self.is_lattice_polytope() else SageQQ
            return _owned_engine_element(target, target(value))

        @cached_method
        def integral_invariants(self):
            r"""The dimension, volumes and lattice-point counts of this polytope.

            These invariants require only a rational polytope in its chosen
            lattice. The ``volume`` entry uses ambient Lebesgue measure;
            ``normalized_volume`` uses the lattice parallel to the affine
            hull. Dimension is integral, volumes are rational (normalized
            volume is integral for a lattice polytope), and the counts are
            cardinals. The selected algorithms are those of the individual
            operations, with no toric or ADE hypothesis.
            """
            labels = finite_ordered_set(
                (
                    "dimension",
                    "volume",
                    "normalized_volume",
                    "n_integral_points",
                    "n_interior_points",
                    "n_boundary_points",
                )
            )
            values = {
                "dimension": self.dimension(),
                "volume": self.volume(),
                "normalized_volume": self.normalized_volume(),
                "n_integral_points": self.n_integral_points(),
                "n_interior_points": self.n_interior_points(),
                "n_boundary_points": self.n_boundary_points(),
            }
            return finite_indexed_family(
                labels, values.__getitem__, description=lambda self=self: f"Integral invariants of {self}"
            )

        def is_compact(self) -> bool:
            return True

        def _vertices_are_integral(self) -> bool:
            return _engine_vertices_are_integral(self._engine_polyhedron())

        def is_lattice_polytope(self) -> bool:
            return self._vertices_are_integral()

        def contains_point(self, point) -> bool:
            return bool(self._engine_polyhedron().contains(self._engine_coordinates(point)))

        def interior_contains_point(self, point) -> bool:
            return bool(
                self._engine_polyhedron().relative_interior_contains(
                    self._engine_coordinates(point)
                )
            )

        def normal_value(self, normal, point):
            r"""Return ``<point, normal>`` in the owned rational coordinate frame.

            The polytope lives in ``M_Q`` and an inner normal lives in the
            dual lattice ``N``.  This pairing is part of the mathematical
            polytope interface: consumers that need a supporting face do not
            need either the Sage polyhedron or its coordinate tuples.
            """
            rationals = _owned_rationals()
            dual = self.ambient_lattice().dual_module()
            point = self.rational_point(point)
            normal = dual(normal)
            point_coordinates = point.to_vector()
            normal_coordinates = normal.to_vector()
            zero = rationals.zero()
            point_labels = tuple(point.parent().module_generating_set().index_set())

            def source_label(dual_label):
                if any((dual_label == label) is True for label in point_labels):
                    return dual_label
                try:
                    # The character lattice is Hom(M, ZZ), whose matrix
                    # generator labels are (row, column). Evaluation on M
                    # uses the column label: the row is the basis label of
                    # the rank-one codomain ZZ, not a coordinate of M.
                    candidate = dual_label[1]
                except (TypeError, IndexError, KeyError):
                    candidate = None
                if any((candidate == label) is True for label in point_labels):
                    return candidate
                raise ValueError(
                    f"dual coordinate label {dual_label!r} does not identify a selected source basis "
                    f"label of {point.parent()}; dual labels are {normal_coordinates.support().domain()}"
                )

            return sum(
                (
                    rationals(normal_coordinates(label))
                    * rationals(point_coordinates(source_label(label)))
                    for label in normal_coordinates.support().domain()
                ),
                zero,
            )

        def normal_supports_point(self, normal, point) -> bool:
            r"""Whether ``point`` lies where the inner normal is minimized.

            If ``normal`` is the primitive inner normal of a facet, this says
            exactly that ``point`` lies on that facet.
            """
            value = SageQQ(_engine_element(_owned_rationals(), self.normal_value(normal, point)))
            values = (
                SageQQ(_engine_element(_owned_rationals(), self.normal_value(normal, vertex)))
                for vertex in self.vertices()
            )
            return value == min(values)

        def integral_points(self):

            engine_points = finite_ordered_set(
                tuple(self._engine_polyhedron().integral_points())
            )
            return FiniteOrderedSets().from_indexed(
                engine_points,
                lambda point: self.ambient_lattice()(
                    tuple(
                        self._owned_integral_coordinate(coordinate)
                        for coordinate in point
                    )
                ),
                name="Integral points",
            )

        def interior_integral_points(self):

            return self.integral_points().filtered(
                lambda point: self._engine_polyhedron().relative_interior_contains(
                    self._engine_coordinates(point)
                ),
                name="Interior integral points",
            )

        def boundary_integral_points(self):

            interior = self.interior_integral_points()
            return self.integral_points().filtered(
                lambda point: point not in interior,
                name="Boundary integral points",
            )

        def n_integral_points(self):
            return self.integral_points().cardinality()

        def n_interior_points(self):
            return self.interior_integral_points().cardinality()

        def n_boundary_points(self):
            return self.boundary_integral_points().cardinality()

        def is_reflexive(self) -> bool:
            if not self.is_lattice_polytope():
                return False
            if int(self.dimension()) != int(self._engine_polyhedron().ambient_dim()):
                return False
            origin = (SageQQ.zero(),) * int(self._engine_polyhedron().ambient_dim())
            if not self._engine_polyhedron().interior_contains(origin):
                return False
            polar = self._engine_polyhedron().polar()
            return all(
                coordinate in SageZZ
                for vertex in polar.vertices()
                for coordinate in vertex
            )

        def polar_dual(self):
            r"""Return the polar dual `P^\circ`, framed by the dual lattice.

            `P` lies in `M_R` for its coordinate lattice `M`, so
            `P^\circ = \{y \in M^*_R : \langle y, x\rangle \le 1
            \text{ for all } x \in P\}` lies in the dual `M^*_R`: a point of the
            polar is a functional on `M_R`, and the polar is a subset of
            another space, not of `M_R`.

            A lattice that is itself a dual has a primal, `M = L^*`, and then
            the polar's frame `(L^*)^*` is that primal `L` and not a third
            space: evaluation `x \mapsto (f \mapsto f(x))` is an isomorphism
            `L \to (L^*)^*` for a finite free `L` (Mathlib, `Module.evalEquiv`,
            `Mathlib/LinearAlgebra/Dual/Defs.lean`), which this library states
            as `Modules(R).dualization().double_dual_morphism(L)`, and it
            carries the basis of `L` into the dual basis of the dual basis,
            labelled by `L`'s own labels.  The polar dual of a polar dual is
            therefore a polytope of the primal lattice and is compared there;
            it is the primal polytope, since `P` lies in `P^{\circ\circ}`
            always (Mathlib, `LinearMap.subset_bipolar`,
            `Mathlib/Analysis/LocallyConvex/Polar.lean`) and the engine's
            second polar has `P`'s vertices.

            A lattice that is not a dual is not identified with anything: the
            polar dual is then framed by a new lattice, whose points are the
            functionals on this one.
            """
            assert int(self.dimension()) == int(
                self._engine_polyhedron().ambient_dim()
            ), (
                f"the polar dual of {self} is defined only for a full-dimensional polytope, but it "
                f"has dimension {self.dimension()} in a lattice of rank "
                f"{self._engine_polyhedron().ambient_dim()}"
            )
            origin = (SageQQ.zero(),) * int(self._engine_polyhedron().ambient_dim())
            assert self._engine_polyhedron().interior_contains(origin), (
                f"the polar dual of {self} is a polytope only when the origin is an interior point, "
                f"but the origin is not in the interior of {self}"
            )
            polar = self._engine_polyhedron().polar()
            lattice = self.ambient_lattice()
            primal = _primal_lattice_of_a_dual(lattice)
            if primal is None:
                return ConvexPolytopes(lattice.dual_module())(polar.vertices())
            from sage_extensions.categories.modules.pure.modules import Modules

            double_dual = lattice.dual_module()
            evaluation = Modules(lattice.base_ring()).dualization().double_dual_morphism(
                primal
            )
            assert evaluation.codomain() is double_dual, (
                f"the double dual of {primal} is {evaluation.codomain()}, but the polar dual of "
                f"{self} is framed by {double_dual}"
            )
            labels = tuple(primal.module_generating_set())
            assert labels == tuple(double_dual.module_generating_set()), (
                f"the evaluation isomorphism indexes the double dual {double_dual} by the labels "
                f"{labels} of {primal}, but its generating set is "
                f"{tuple(double_dual.module_generating_set())}"
            )
            assert all(
                evaluation(primal.module_generator(label))
                == double_dual.module_generator(label)
                for label in labels
            ), (
                f"the evaluation isomorphism {evaluation} does not carry the basis of {primal} to "
                f"the basis of {double_dual}, so the vertices of the polar dual are not read in "
                f"{primal}'s coordinates"
            )
            return ConvexPolytopes(primal)(polar.vertices())

        def is_smooth(self) -> bool:
            if not self.is_lattice_polytope():
                return False
            if int(self.dimension()) != int(self._engine_polyhedron().ambient_dim()):
                return False
            return bool(self._engine_normal_fan().is_smooth())

        def _repr_(self):
            noun = "Lattice " if self.is_lattice_polytope() else "Convex "
            noun += "Polygon" if int(self.dimension()) == 2 else "Polytope"
            return f"{noun} of dimension {self.dimension()} with {self.n_vertices()} vertices"


    class Integral(CategoryWithAxiom):
        r"""Convex polytopes all of whose vertices are lattice points."""

        def an_object(self):
            r"""The standard simplex in this category's coordinate lattice."""
            return self.base_category().an_object()

        @classmethod
        def _repr_object_names(cls):
            return "lattice polytopes"

        def _call_(self, vertices, lattice=None):
            r"""Construct the lattice polytope on the selected integral vertices."""
            return _polytope_in(self, vertices, lattice)

        class ParentMethods:
            def toric_variety(self, base_ring):
                r"""Return ``X_P`` with ``P`` retained as its polarizing lattice polytope."""
                return self.normal_fan().toric_variety(
                    base_ring,
                    polarizing_polytope=self,
                )

            def _dilate(self, scalar):
                integers = _owned_integers()
                scalar = integers(scalar)
                assert scalar >= integers.zero(), (
                    f"the dilate k P of {self} is taken here only for k >= 0, but k = {scalar}"
                )
                return ConvexPolytopes(self.ambient_lattice()).Integral()(
                    [tuple(scalar * coordinate for coordinate in vertex) for vertex in self.vertices()],
                )

            def ehrhart_polynomial(self, variable="t"):
                r"""Return the exact owned Ehrhart polynomial by interpolation."""
                rationals = _owned_rationals()
                integers = _owned_integers()
                polynomial_ring = rationals.polynomial_ring(variable)
                t = polynomial_ring.algebra_generator(variable)
                d = int(self.dimension())
                values = [
                    integers.one() if k == 0 else integers(int(self._dilate(k).n_integral_points()))
                    for k in range(d + 1)
                ]
                result = polynomial_ring.zero()
                for i, value in enumerate(values):
                    basis = polynomial_ring.one()
                    denominator = rationals.one()
                    for j in range(d + 1):
                        if i == j:
                            continue
                        basis *= t - j
                        denominator *= rationals(i - j)
                    result += rationals(value) / denominator * basis
                return result

            def h_star_vector(self):
                r"""Return the owned Ehrhart ``h*`` vector ``(h*_0,...,h*_d)``."""
                from math import comb

                integers = _owned_integers()
                d = int(self.dimension())
                counts = [
                    integers.one() if k == 0 else integers(int(self._dilate(k).n_integral_points()))
                    for k in range(d + 1)
                ]
                result = []
                for j in range(d + 1):
                    value = integers.zero()
                    for i in range(j + 1):
                        coefficient = integers(((-1) ** (j - i)) * comb(d + 1, j - i))
                        value += coefficient * counts[i]
                    result.append(value)

                return finite_family(result, name="h* vector")

        @cached_method
        def reflexive_polytopes(self, dimension):
            r"""The reflexive polytopes of the stated dimension, up to lattice equivalence.

            The classification is Kreuzer--Skarke's; Sage carries it in
            ``sage.geometry.lattice_polytope.ReflexivePolytopes``, with dimension
            two built in and dimension three behind its optional polytope
            database.  By Batyrev's theorem the toric variety of the normal fan of
            a reflexive polytope is Gorenstein Fano, so this is the finite list a
            session searches when it wants those.
            """
            from sage.geometry.lattice_polytope import ReflexivePolytopes

            dimension = int(dimension)
            assert dimension in (2, 3), (
                f"the classification of reflexive polytopes is available in dimensions 2 and 3, "
                f"not in dimension {dimension}"
            )
            assert int(self.ambient_lattice().module_rank()) == dimension, (
                f"reflexive polytopes of dimension {dimension} do not lie in the lattice "
                f"{self.ambient_lattice()} of rank {self.ambient_lattice().module_rank()}"
            )
            return finite_ordered_set(
                tuple(
                    self(
                        tuple(
                            tuple(int(coordinate) for coordinate in vertex)
                            for vertex in classified.vertices()
                        )
                    )
                    for classified in ReflexivePolytopes(dimension)
                )
            )

        class Polygon(CategoryWithAxiom):
            r"""Lattice polytopes of affine dimension two."""

            def an_object(self):
                r"""The standard triangle in the first two coordinates."""
                labels = tuple(self.ambient_lattice().module_generating_set())
                assert len(labels) >= 2, (
                    f"a polygon needs a lattice of rank at least 2, but {self.ambient_lattice()} "
                    f"has rank {len(labels)}"
                )
                return self(
                    (
                        tuple(0 for _label in labels),
                        tuple(1 if label == labels[0] else 0 for label in labels),
                        tuple(1 if label == labels[1] else 0 for label in labels),
                    )
                )

            @classmethod
            def _repr_object_names(cls):
                return "lattice polygons"

            def _call_(self, vertices, lattice=None):
                r"""Construct the two-dimensional lattice polytope on ``vertices``."""
                return _polytope_in(self, vertices, lattice)

    class Polygon(CategoryWithAxiom):
        r"""Convex polytopes of affine dimension two."""

        def an_object(self):
            r"""The triangle on ``0, e_1/2, e_2`` in the first two coordinates."""
            from sage.rings.rational import Rational

            labels = tuple(self.ambient_lattice().module_generating_set())
            assert len(labels) >= 2, (
                f"a polygon needs a lattice of rank at least 2, but {self.ambient_lattice()} "
                f"has rank {len(labels)}"
            )
            return self(
                (
                    tuple(0 for _label in labels),
                    tuple(Rational((1, 2)) if label == labels[0] else 0 for label in labels),
                    tuple(1 if label == labels[1] else 0 for label in labels),
                )
            )

        @classmethod
        def _repr_object_names(cls):
            return "convex polygons"

        def _call_(self, vertices, lattice=None):
            r"""Construct the two-dimensional convex polytope on ``vertices``."""
            return _polytope_in(self, vertices, lattice)

        class ParentMethods:
            def _repr_svg_(self):
                r"""Render this live polygon as a deterministic notebook SVG view.

                The mathematical object remains the exact owned polygon.  Floating
                point conversion is confined to this display boundary: the exact
                engine vertices are sorted cyclically about their centroid and
                affinely rescaled into a fixed SVG viewport.
                """
                vertices = tuple(
                    tuple(float(coordinate) for coordinate in vertex)
                    for vertex in self._engine_polyhedron().vertices_list()
                )
                if len(vertices) < 3:
                    return None

                center_x = sum(vertex[0] for vertex in vertices) / len(vertices)
                center_y = sum(vertex[1] for vertex in vertices) / len(vertices)
                ordered = tuple(
                    sorted(
                        vertices,
                        key=lambda vertex: atan2(
                            vertex[1] - center_y,
                            vertex[0] - center_x,
                        ),
                    )
                )
                minimum_x = min(vertex[0] for vertex in ordered)
                maximum_x = max(vertex[0] for vertex in ordered)
                minimum_y = min(vertex[1] for vertex in ordered)
                maximum_y = max(vertex[1] for vertex in ordered)
                span_x = maximum_x - minimum_x
                span_y = maximum_y - minimum_y
                scale = 260.0 / max(span_x, span_y, 1.0)
                margin = 30.0

                def screen_point(vertex):
                    x, y = vertex
                    return (
                        margin + (x - minimum_x) * scale,
                        margin + (maximum_y - y) * scale,
                    )

                points = " ".join(
                    f"{x:.6g},{y:.6g}" for x, y in map(screen_point, ordered)
                )
                width = 2 * margin + span_x * scale
                height = 2 * margin + span_y * scale
                return (
                    f'<svg xmlns="http://www.w3.org/2000/svg" '
                    f'viewBox="0 0 {width:.6g} {height:.6g}" '
                    f'width="{width:.6g}" height="{height:.6g}">'
                    '<polygon points="'
                    + points
                    + '" fill="none" stroke="currentColor" stroke-width="2"/>'
                    "</svg>"
                )


def LatticePolytopes(lattice) -> Category:
    r"""The category of lattice polytopes."""
    return ConvexPolytopes(lattice).Integral()


def ConvexPolygons(lattice) -> Category:
    r"""The category of convex polygons."""
    return ConvexPolytopes(lattice).Polygon()


def LatticePolygons(lattice) -> Category:
    r"""The category of lattice polygons."""
    return ConvexPolytopes(lattice).Integral().Polygon()


def _polytope_in(category, vertices, lattice):
    r"""The polytope on ``vertices``, which the caller asserts lies in ``category``."""
    if lattice is None:
        lattice = category.ambient_lattice()
    polytope = _convex_polytope(vertices, lattice=lattice)
    assert polytope in category, (
        f"the polytope {polytope} with vertices {vertices} is not an object of {category}; "
        f"it is in {polytope.category()}"
    )
    return polytope


def _primal_lattice_of_a_dual(lattice):
    r"""Return the lattice ``lattice`` is the linear dual of, when it is one.

    The dual of a lattice ``M`` is ``M^* = Hom(M, ZZ)``, which
    :meth:`Module.ParentMethods.dual_module` builds as the internal Mor of
    ``M`` into the regular module and places in ``LinearMorModules`` of the
    base ring.  Such a module records the module it dualizes and the module it
    takes values in, so ``M`` is recovered from ``M^*`` itself and not by
    searching for a lattice whose dual this one happens to be.

    ``None`` is returned when ``lattice`` is not a linear dual of this kind: the
    polar dual is then framed by a new lattice, and there is no primal space
    that the dual could be identified with.

    The double dual is the primal only through evaluation, which is an
    isomorphism for a finite free module and an injection otherwise, so the two
    ranks are required to agree before the identification is offered: the dual
    of a free module on an infinite basis is the product, which is not free
    (Baer--Specker), and ``M \to M^{**}`` is then not onto.
    """
    from sage_extensions.categories.modules.pure.modules import LinearMorModules

    ring = lattice.base_ring()
    match lattice in LinearMorModules(ring):
        case False:
            return None
        case True:
            pass
    match lattice.target_module() is ring.regular_module():
        case False:
            return None
        case True:
            pass
    primal = lattice.source_module()
    assert int(primal.module_rank()) == int(lattice.module_rank()), (
        f"{lattice} is the dual of {primal}, but their ranks "
        f"{lattice.module_rank()} and {primal.module_rank()} differ, so a free "
        "presentation of the double dual is not the primal lattice"
    )
    return primal


def _engine_vertices_are_integral(engine_polyhedron) -> bool:
    r"""Whether every vertex of the exact polyhedron is a lattice point."""
    return all(
        coordinate in SageZZ
        for vertex in engine_polyhedron.vertices()
        for coordinate in vertex
    )


def _convex_polytope(
    vertices=None,
    lattice=None,
    engine_polyhedron=None,
    defining_data=None,
):
    r"""The polytope on its data, constructed once in the category it lies in.

    A polytope is fixed by its vertices, by an owned polytope passed again, or
    by an exact polyhedron the private computation layer produced (from a
    face, a dilation, or a halfspace description); the third route is named
    rather than recognized.  Integrality of the vertices and affine dimension
    two are the two axioms the finer categories state, so they are decided on
    the polyhedron and the object is constructed in the category they select.
    """
    integers = _owned_integers()
    rationals = _owned_rationals()
    if engine_polyhedron is not None:
        polyhedron = engine_polyhedron
        if defining_data is None:
            defining_data = (
                "vertices",
                tuple(
                    tuple(_owned_rational(coordinate) for coordinate in vertex)
                    for vertex in polyhedron.vertices()
                ),
            )
    else:
        owned_vertices = tuple(
            tuple(_owned_rational(coordinate) for coordinate in vertex)
            for vertex in vertices
        )
        defining_data = ("vertices", owned_vertices)
        engine_vertices = [
            tuple(
                _engine_element(rationals, coordinate)
                for coordinate in vertex
            )
            for vertex in owned_vertices
        ]
        polyhedron = Polyhedron(vertices=engine_vertices, base_ring=SageQQ)

    ambient_dimension = int(polyhedron.ambient_dim())
    assert lattice is not None, (
        "a convex polytope must be given the lattice its vertices lie in, but none was given"
    )
    assert lattice.base_ring() is integers, (
        f"the vertices of a polytope lie in a lattice over ZZ, but {lattice} is a module over "
        f"{lattice.base_ring()}"
    )
    assert int(lattice.module_rank()) == ambient_dimension, (
        f"the vertices have {ambient_dimension} coordinates, but the lattice {lattice} has rank "
        f"{lattice.module_rank()}"
    )

    placement = ConvexPolytopes(lattice)
    if _engine_vertices_are_integral(polyhedron):
        placement = placement.Integral()
    if int(polyhedron.dim()) == 2:
        placement = placement.Polygon()
    ambient = ConvexPolytopes(lattice).ambient_space()
    labels = tuple(ambient.module_generating_set())

    def contains(point):
        point_coordinates = ambient(point).to_vector()
        coordinates = tuple(
            _engine_element(rationals, point_coordinates(label))
            for label in labels
        )
        return bool(polyhedron.contains(coordinates))

    subset = ambient.condition_set(contains)
    return Sets().Subobjects(ambient).object(
        subset.inclusion(),
        categories=(placement,),
        construction_data={
            "engine_polyhedron": polyhedron,
            "ambient_lattice": lattice,
            "defining_data": defining_data,
        },
    )


__all__ = [
    "AbstractPolytopes",
    "ConvexPolytopesIn",
    "ConvexPolygons",
    "ConvexPolytopes",
    "EuclideanPolytopesIn",
    "HyperbolicGeodesicPolytopesIn",
    "LatticePolytopesIn",
    "LatticePolygons",
    "LatticePolytopes",
    "RegularPolytopes",
    "SphericalGeodesicPolytopesIn",
]
