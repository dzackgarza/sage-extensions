r"""Cell, polytopal, simplicial, Delta, and simplicial-set categories."""

from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.sets.set_categories import PartiallyOrderedSets
from sage_extensions.categories.topological_spaces import TopologicalSpaces
from sage_extensions.owned_category_bases import CategoryWithAxiom


for _axiom in ("RegularCW", "PLManifold", "Kan"):
    if _axiom not in all_axioms:
        all_axioms.add(_axiom)


class _ComplexMapMethods:
    def __mul__(self, other):
        pass

    def realization_map(self):
        pass

    def cellular_realization_map(self):
        pass

    def is_homotopic_to(self, other):
        pass

    def is_weak_equivalence(self):
        pass

    def is_embedding(self):
        pass


class _CellwiseComplexMapMethods(_ComplexMapMethods):
    def __init__(self, parent, cell_maps):
        Morphism.__init__(self, parent)
        self._cell_maps = cell_maps

    def underlying_map(self):
        return self._cell_maps

    def cell_maps(self):
        return self._cell_maps

    def cell_map(self, cell):
        return self._cell_maps[cell]


class _GradedComplexMapMethods(_ComplexMapMethods):
    def __init__(self, parent, degree_maps):
        Morphism.__init__(self, parent)
        self._degree_maps = degree_maps

    def underlying_map(self):
        return self._degree_maps

    def degree_maps(self):
        return self._degree_maps

    def degree_map(self, degree):
        return self._degree_maps[degree]


class _ComplexMor(CategoricalMor):
    @object_level
    def identity(self):
        pass


class CellComplexMor(_ComplexMor):
    r"""Cellular maps respecting characteristic and attaching maps."""

    ElementMethods = _CellwiseComplexMapMethods

    def _element_constructor_(self, cell_maps):
        pass


class PolytopalComplexMor(_ComplexMor):
    r"""Cellular maps respecting selected polytope face placements."""

    class ElementMethods(_CellwiseComplexMapMethods):
        def face_poset_map(self):
            pass

    def _element_constructor_(self, cell_maps):
        pass


class SimplicialComplexMor(_ComplexMor):
    r"""Simplicial maps respecting every face inclusion."""

    class ElementMethods(_ComplexMapMethods):
        def __init__(self, parent, vertex_map):
            Morphism.__init__(self, parent)
            self._vertex_map = vertex_map

        def underlying_map(self):
            return self._vertex_map

        def vertex_map(self):
            return self._vertex_map

        def face_poset_map(self):
            pass

    def _element_constructor_(self, vertex_map):
        pass


class DeltaComplexMor(_ComplexMor):
    r"""Maps commuting with the face identifications of a Delta-complex."""

    class ElementMethods(_GradedComplexMapMethods):
        def face_poset_map(self):
            pass

    def _element_constructor_(self, degree_maps):
        pass


class SimplicialSetMor(_ComplexMor):
    r"""Maps commuting with faces and degeneracies in every degree."""

    class ElementMethods(_GradedComplexMapMethods):
        def face_poset_map(self):
            pass

    def _element_constructor_(self, degree_maps):
        pass


class CellComplexMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = CellComplexMor


class PolytopalComplexMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = PolytopalComplexMor


class SimplicialComplexMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SimplicialComplexMor


class DeltaComplexMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = DeltaComplexMor


class SimplicialSetMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SimplicialSetMor


class _ComplexRealizationFunctor(Functor):
    r"""Send a represented complex and map to their selected realizations."""

    def __init__(self, source_category, target_category):
        super().__init__(source_category, target_category)

    def _apply_object(self, complex_):
        if self.codomain() is CellComplexes():
            return complex_.cellular_realization()
        return complex_.realization()

    def _apply_morphism(self, morphism):
        if self.codomain() is CellComplexes():
            return morphism.cellular_realization_map()
        return morphism.realization_map()


class _ComplexFacePosetFunctor(Functor):
    r"""Send a complex and its cellular maps to incidence posets."""

    def __init__(self, source_category):
        super().__init__(source_category, PartiallyOrderedSets())

    def _apply_object(self, complex_):
        return complex_.face_poset()

    def _apply_morphism(self, morphism):
        return morphism.face_poset_map()


class _OrderComplexFunctor(Functor):
    r"""Take chains of a poset and map them along monotone maps."""

    def __init__(self):
        super().__init__(PartiallyOrderedSets(), SimplicialComplexes())

    def _apply_object(self, poset):
        return self.codomain().order_complex(poset)

    def _apply_morphism(self, morphism):
        pass


class CellComplexes(OwnedCategory):
    r"""CW complexes with selected cells and attaching maps."""

    _MorCategory = CellComplexMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "cell complexes"

    def an_object(self):
        pass

    def from_attaching_maps(self, cells, attaching_maps):
        pass

    def regularization(self, complex_):
        r"""Replace nonembedded attaching maps by mapping cylinders."""
        pass

    def from_intersection_strata(self, component_inclusions, intersection_strata):
        r"""Select the dual complex of connected component intersections."""
        pass

    def _categorical_coproduct_construction(self, factors):
        r"""Select a disjoint complex with its cellwise inclusion cocone."""
        pass

    def _categorical_coequalizer_construction(self, left_morphism, right_morphism):
        r"""Select the cellular quotient and its universal cocone."""
        pass

    def colimit(self, diagram):
        r"""Select a complex colimit with its universal cocone."""
        pass

    def face_gluing_diagram(self, pieces, paired_faces, face_isomorphisms):
        r"""Present the finite face-pairing data as a diagram in this category."""
        pass

    def from_face_gluing_diagram(self, diagram, colimit_cocone):
        r"""Select the quotient complex with every piece-to-quotient arrow."""
        pass

    def surgery(self, region_inclusion, replacement, boundary_isomorphism):
        r"""Select the pushout of a region complement and a boundary-matched replacement."""
        pass

    def boundary_surgery_span(self, region_inclusion, replacement, boundary_isomorphism):
        r"""Select the boundary-matched span of the complement and replacement."""
        pass

    @cached_method
    def realization(self):
        return _ComplexRealizationFunctor(self, TopologicalSpaces())

    class ParentMethods:
        def __init__(self, cell_family, attaching_maps, **rest):
            self._cell_family = cell_family
            self._attaching_maps = attaching_maps
            super().__init__(**rest)

        def cell_family(self):
            return self._cell_family

        def attaching_maps(self):
            return self._attaching_maps

        def attaching_map(self, cell):
            return self._attaching_maps[cell]

        def skeleton(self, dimension):
            r"""The subcomplex formed by cells of dimension at most the bound."""
            pass

        def skeleton_inclusion(self, dimension):
            r"""The selected inclusion of that skeleton into this complex."""
            pass

        def is_regular(self):
            pass

        def is_simplicial(self):
            pass

        def is_delta_complex(self):
            pass

        def regularization(self):
            pass

        def regularization_comparison(self, regularization):
            r"""Map a selected mapping-cylinder regularization to this complex."""
            pass

        def characteristic_map(self, cell):
            r"""Return the selected map from the closed cell to this complex."""
            pass

        def cell_inclusion(self, cell):
            r"""Return the cell's inclusion with its exact source and target."""
            pass

        def cells(self, dimension):
            pass

        def face_poset(self):
            pass

        def star(self, cell):
            pass

        def star_inclusion(self, cell):
            pass

        def link(self, cell):
            pass

        def link_inclusion(self, cell):
            pass

        def subdivision(self):
            pass

        def subdivision_comparison(self, subdivision):
            pass

        def triangulations(self):
            from sage_extensions.categories.triangulations import ChosenTriangulations

            return ChosenTriangulations(self)

        def triangulate(self):
            pass

        def face_inclusion(self, face, cell):
            pass

        def subcomplex(self, cells):
            r"""Select the subcomplex closed under attaching faces of ``cells``."""
            pass

        def subcomplex_inclusion(self, subcomplex):
            r"""Return the cellular inclusion from ``subcomplex`` into ``self``."""
            pass

        def face_gluing_diagram(self):
            pass

        def gluing_cocone(self):
            pass

        def piece_inclusion(self, piece):
            pass

        def surgery_span(self):
            pass

        def surgery_cocone(self):
            pass

        def realization(self):
            pass

        def underlying_space(self):
            pass

    class RegularCW(CategoryWithAxiom):
        r"""Cell complexes with embedded closed cells."""

    class PLManifold(CategoryWithAxiom):
        r"""Cell complexes with the required PL sphere and ball links."""

        class ParentMethods:
            def boundary(self):
                pass

            def boundary_inclusion(self):
                pass


class PolytopalComplexes(OwnedCategory):
    r"""Complexes built from placed polytopes and their face maps."""

    _MorCategory = PolytopalComplexMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "polytopal complexes"

    def an_object(self):
        pass

    def from_cells(self, polytopes, face_maps):
        pass

    def _from_engine_polyhedral_complex(self, engine_complex, cell_map, face_maps):
        r"""Raise Sage's polyhedral complex with owned cells and face arrows."""
        pass

    @cached_method
    def face_posets(self):
        return _ComplexFacePosetFunctor(self)

    @cached_method
    def cellular_realization(self):
        return _ComplexRealizationFunctor(self, CellComplexes())

    @cached_method
    def realization(self):
        return self.cellular_realization().then(CellComplexes().realization())

    class ParentMethods:
        def __init__(self, polytopes, face_maps, **rest):
            self._polytopes = polytopes
            self._face_maps = face_maps
            super().__init__(**rest)

        def placed_polytopes(self):
            return self._polytopes

        def cells(self, dimension):
            pass

        def face_maps(self):
            return self._face_maps

        def _engine_polyhedral_complex(self):
            r"""Lower selected placed cells and face maps to Sage privately."""
            pass

        def face_map(self, face, cell):
            return self._face_maps[face, cell]

        def face_poset(self):
            pass

        def face_inclusion(self, face, cell):
            pass

        def star(self, cell):
            pass

        def star_inclusion(self, cell):
            pass

        def link(self, cell):
            pass

        def link_inclusion(self, cell):
            pass

        def subdivision(self):
            pass

        def subdivision_comparison(self, subdivision):
            pass

        def subcomplex(self, cells):
            r"""Select the placed polytopes and all their incident faces."""
            pass

        def subcomplex_inclusion(self, subcomplex):
            pass

        def cellular_realization(self):
            pass

        def realization(self):
            r"""Realize the selected polytopal cells as a topological space."""
            pass

        def triangulations(self):
            from sage_extensions.categories.triangulations import ChosenTriangulations

            return ChosenTriangulations(self)

        def triangulate(self):
            pass


class SimplicialComplexes(OwnedCategory):
    r"""Complexes of simplices closed under faces, with simplicial maps."""

    _MorCategory = SimplicialComplexMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "simplicial complexes"

    def an_object(self):
        pass

    def from_simplices(self, vertices, simplices):
        pass

    def _from_engine_simplicial_complex(self, engine_complex, vertex_map):
        r"""Raise Sage's simplicial complex with owned vertices and face maps."""
        pass

    def order_complex(self, poset):
        r"""Construct the nerve of a poset from its chains."""
        pass

    @cached_method
    def order_complex_functor(self):
        return _OrderComplexFunctor()

    @cached_method
    def face_posets(self):
        return _ComplexFacePosetFunctor(self)

    @cached_method
    def cellular_realization(self):
        return _ComplexRealizationFunctor(self, CellComplexes())

    @cached_method
    def realization(self):
        return self.cellular_realization().then(CellComplexes().realization())

    class ParentMethods:
        def __init__(self, vertices, defining_simplices, **rest):
            self._vertices = vertices
            self._defining_simplices = defining_simplices
            super().__init__(**rest)

        def vertices(self):
            return self._vertices

        def defining_simplices(self):
            return self._defining_simplices

        def _engine_simplicial_complex(self):
            r"""Lower selected vertices and simplices to Sage privately."""
            pass

        def simplices(self, dimension):
            pass

        def face_poset(self):
            pass

        def link(self, simplex):
            pass

        def link_inclusion(self, simplex):
            pass

        def star(self, simplex):
            pass

        def star_inclusion(self, simplex):
            pass

        def subdivision(self):
            pass

        def subdivision_comparison(self, subdivision):
            pass

        def barycentric_subdivision(self):
            r"""The order complex of this complex's face poset."""
            pass

        def barycentric_subdivision_comparison(self, subdivision):
            r"""The realization map from the barycentric subdivision to this complex."""
            pass

        def simplex_inclusion(self, face, simplex):
            pass

        def subcomplex(self, simplices):
            r"""Select the simplices together with all their faces."""
            pass

        def subcomplex_inclusion(self, subcomplex):
            pass

        def cellular_realization(self):
            pass

        def realization(self):
            r"""Realize the selected simplices as a topological space."""
            pass

        def triangulations(self):
            from sage_extensions.categories.triangulations import ChosenTriangulations

            return ChosenTriangulations(self)

        def triangulate(self):
            pass


class DeltaComplexes(OwnedCategory):
    r"""Delta-complexes with selected face identifications."""

    _MorCategory = DeltaComplexMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "Delta-complexes"

    def an_object(self):
        pass

    def from_faces(self, simplices, face_maps):
        pass

    def _from_engine_delta_complex(self, engine_complex, simplex_map):
        r"""Raise Sage's Delta-complex with owned simplices and face maps."""
        pass

    @cached_method
    def face_posets(self):
        return _ComplexFacePosetFunctor(self)

    @cached_method
    def cellular_realization(self):
        return _ComplexRealizationFunctor(self, CellComplexes())

    @cached_method
    def realization(self):
        return self.cellular_realization().then(CellComplexes().realization())

    class ParentMethods:
        def __init__(self, defining_simplices, face_maps, **rest):
            self._defining_simplices = defining_simplices
            self._face_maps = face_maps
            super().__init__(**rest)

        def defining_simplices(self):
            return self._defining_simplices

        def simplices(self, dimension):
            pass

        def face_maps(self):
            return self._face_maps

        def _engine_delta_complex(self):
            r"""Lower selected simplices and face maps to Sage privately."""
            pass

        def face_map(self, simplex, index):
            return self._face_maps[simplex, index]

        def face_poset(self):
            pass

        def subcomplex(self, simplices):
            r"""Select simplices closed under the given face identifications."""
            pass

        def subcomplex_inclusion(self, subcomplex):
            pass

        def star(self, simplex):
            pass

        def star_inclusion(self, simplex):
            pass

        def link(self, simplex):
            pass

        def link_inclusion(self, simplex):
            pass

        def subdivision(self):
            pass

        def subdivision_comparison(self, subdivision):
            pass

        def cellular_realization(self):
            pass

        def realization(self):
            r"""Realize the selected face identifications as a topological space."""
            pass

        def triangulations(self):
            from sage_extensions.categories.triangulations import ChosenTriangulations

            return ChosenTriangulations(self)

        def triangulate(self):
            pass


class SimplicialSets(OwnedCategory):
    r"""Graded simplices with face and degeneracy operators."""

    _MorCategory = SimplicialSetMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "simplicial sets"

    def an_object(self):
        pass

    def from_face_degeneracy_maps(self, simplices, faces, degeneracies):
        r"""Select graded ``simplices[n]`` and operators ``faces[n,i]``, ``degeneracies[n,i]``."""
        pass

    def _from_engine_simplicial_set(self, engine_simplicial_set, simplex_map):
        r"""Raise Sage's simplicial set with owned face and degeneracy maps."""
        pass

    def nerve(self, category):
        r"""Construct the simplicial nerve of a small category."""
        pass

    def standard_simplex(self, dimension):
        r"""The representable simplicial set on the ordinal of this dimension."""
        pass

    @cached_method
    def face_posets(self):
        return _ComplexFacePosetFunctor(self)

    @cached_method
    def realization(self):
        return _ComplexRealizationFunctor(self, TopologicalSpaces())

    class ParentMethods:
        def __init__(self, defining_simplices, defining_faces, defining_degeneracies, **rest):
            self._defining_simplices = defining_simplices
            self._defining_faces = defining_faces
            self._defining_degeneracies = defining_degeneracies
            super().__init__(**rest)

        def defining_simplices(self):
            return self._defining_simplices

        def defining_faces(self):
            return self._defining_faces

        def defining_degeneracies(self):
            return self._defining_degeneracies

        def _engine_simplicial_set(self):
            r"""Lower selected face and degeneracy operators to Sage privately."""
            pass

        def _engine_kenzo_simplicial_set(self):
            r"""Lower a finite selected simplicial set through Sage's ``KFiniteSimplicialSet``."""
            pass

        def simplices(self, dimension):
            return self._defining_simplices[dimension]

        def simplex_map(self, dimension, simplex):
            r"""The simplicial map from the standard simplex selected by ``simplex``."""
            pass

        def simplex_category(self):
            pass

        def face_poset(self):
            r"""Order nondegenerate simplices by the face relation."""
            pass

        def barycentric_subdivision(self):
            pass

        def barycentric_subdivision_comparison(self, subdivision):
            r"""Return the last-vertex map from a selected subdivision."""
            pass

        def face_map(self, dimension, index):
            return self._defining_faces[dimension, index]

        def degeneracy_map(self, dimension, index):
            return self._defining_degeneracies[dimension, index]

        def realization(self):
            pass

    class Kan(CategoryWithAxiom):
        r"""Simplicial sets satisfying the horn-filling condition."""
