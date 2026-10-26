r"""Integral-affine structures on manifolds and on regular loci of spaces."""

from sage.categories.category import Category
from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.arrow_categories import (
    _FullSubcategoryOfArrows,
)
from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedCategory,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.manifold_dimension_strata import PureDimensionalManifolds
from sage_extensions.categories.manifolds import SmoothManifolds
from sage_extensions.categories.manifolds_with_boundary import (
    SmoothManifoldsWithBoundary,
    SmoothManifoldsWithCorners,
)
from sage_extensions.categories.topological_spaces import TopologicalSpaces
from sage_extensions.categories.rings.ring_foundation import _owned_integers
from sage_extensions.owned_category_bases import CategoryWithAxiom


for _axiom in (
    "Oriented",
    "StrictLatticePointAtlas",
    "FiniteSingularSet",
    "Sphere",
    "Disk",
    "RealProjectivePlane",
):
    if _axiom not in all_axioms:
        all_axioms.add(_axiom)


class IntegralAffineManifoldMor(CategoricalMor):
    r"""Locally integral-affine maps between selected affine manifolds."""

    class ElementMethods:
        def __init__(self, parent, smooth_map, local_affine_maps):
            Morphism.__init__(self, parent)
            self._smooth_map = smooth_map
            self._local_affine_maps = local_affine_maps

        def underlying_smooth_morphism(self):
            return self._smooth_map

        def local_affine_maps(self):
            return self._local_affine_maps

        def is_local_isomorphism(self):
            pass

        def _call_(self, point):
            return self._smooth_map(point)

        def __mul__(self, other):
            pass

    def _element_constructor_(self, smooth_map, local_affine_maps):
        pass

    @object_level
    def identity(self):
        pass


class IntegralAffineManifoldMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = IntegralAffineManifoldMor


class _LocalIntegralAffineIsomorphismArrows(_FullSubcategoryOfArrows):
    r"""Affine arrows whose chartwise linear parts are lattice isomorphisms."""

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.products import FiniteOrdinalCategory

        return [Cat().Mor(FiniteOrdinalCategory(2), self.base_category())]

    def admits_arrow(self, arrow):
        pass


class _UnderlyingSmoothManifoldFunctor(Functor):
    r"""Forget the selected affine atlas, on objects and local affine maps."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, manifold):
        return manifold.underlying_smooth_manifold()

    def _apply_morphism(self, morphism):
        return morphism.underlying_smooth_morphism()


class _UnderlyingAffineTopologicalSpaceFunctor(Functor):
    r"""Forget the affine and manifold structures on objects and maps."""

    def __init__(self, source):
        super().__init__(source, TopologicalSpaces())

    def _apply_object(self, manifold):
        pass

    def _apply_morphism(self, morphism):
        return morphism.underlying_smooth_morphism().underlying_topological_morphism()


class IntegralAffineManifolds(OwnedCategory):
    r"""Smooth real manifolds equipped with a selected integral-affine atlas.

    Forgetting the atlas changes the object and its morphisms, so the map to
    smooth manifolds is a functor rather than a supercategory inclusion.
    """

    _MorCategory = IntegralAffineManifoldMorCategoryConstruction

    @staticmethod
    def __classcall__(cls, dimension=None):
        if dimension is not None:
            return IntegralAffineManifoldsOfDimension(dimension)
        return Category.__classcall__(cls)

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "integral-affine manifolds"

    def an_object(self):
        pass

    def on(self, smooth_manifold, affine_atlas):
        r"""Equip the exact smooth manifold with a selected integral-affine atlas."""
        pass

    @cached_method
    def local_isomorphisms(self):
        r"""The wide subcategory on local integral-affine isomorphisms."""
        return self.WideSubcategory(_LocalIntegralAffineIsomorphismArrows(self))

    @cached_method
    def forget(self):
        return _UnderlyingSmoothManifoldFunctor(self, SmoothManifolds())

    @cached_method
    def forget_space(self):
        return _UnderlyingAffineTopologicalSpaceFunctor(self)

    class ParentMethods:
        def __init__(self, smooth_manifold, affine_atlas, **rest):
            self._smooth_manifold = smooth_manifold
            self._affine_atlas = affine_atlas
            super().__init__(**rest)

        def underlying_smooth_manifold(self):
            return self._smooth_manifold

        def dimension(self):
            return self.underlying_smooth_manifold().dimension()

        def affine_charts(self):
            return self.affine_atlas().affine_charts()

        def affine_atlas(self):
            return self._affine_atlas

        def integral_tangent_lattice_category(self):
            r"""Local systems of finite free integral modules on this manifold."""
            from sage_extensions.categories.modules.pure.modules import (
                FinitelyGeneratedFreeModules,
            )

            return self.underlying_smooth_manifold().local_systems(
                FinitelyGeneratedFreeModules(_owned_integers())
            )

        def integral_tangent_lattice(self):
            r"""The lattice local system transported along the fundamental groupoid."""
            pass

        def tangent_lattice_inclusion(self):
            r"""Return the lattice local system's inclusion in the tangent bundle."""
            pass

        def transition_derivative_comparison(self, source_chart, target_chart):
            r"""Compare the chart derivative with its integral lattice action."""
            pass

        def regular_open(self, open_inclusion):
            pass

        def regular_open_inclusion(self, open_affine_manifold):
            pass

        def product(self, other):
            pass

        def holonomy(self, base_point, affine_frame):
            pass

        def holonomy_conjugacy_class(self, base_point):
            pass

    class Oriented(CategoryWithAxiom):
        r"""Integral-affine structures whose linear transitions preserve orientation."""

    class StrictLatticePointAtlas(CategoryWithAxiom):
        r"""Selected atlases whose translations preserve the lattice points."""


class IntegralAffineManifoldsOfDimension(OwnedParameterizedCategory):
    r"""Full dimension-``n`` stratum of the general integral-affine category."""

    @staticmethod
    def __classcall__(cls, dimension):
        dimension = _owned_integers()(dimension)
        if dimension < 0:
            raise ValueError(f"an integral-affine dimension must be nonnegative, not {dimension}")
        return Category.__classcall__(cls, dimension)

    def dimension(self):
        return self.parameter()

    def super_categories(self):
        return [IntegralAffineManifolds()]

    def _repr_object_names(self):
        return f"integral-affine manifolds of dimension {self.dimension()}"

    def an_object(self):
        pass

    def on(self, smooth_manifold, affine_atlas):
        pass

    @cached_method
    def local_isomorphisms(self):
        r"""The wide local-isomorphism subcategory in this fixed dimension."""
        return self.WideSubcategory(_LocalIntegralAffineIsomorphismArrows(self))

    @cached_method
    def forget(self):
        return _UnderlyingSmoothManifoldFunctor(
            self,
            PureDimensionalManifolds(SmoothManifolds(), self.dimension()),
        )

    @cached_method
    def forget_space(self):
        return _UnderlyingAffineTopologicalSpaceFunctor(self)


class _StratifiedIntegralAffineMapMethods:
    def __init__(self, parent, smooth_stratified_map, interior_affine_map, local_affine_maps):
        Morphism.__init__(self, parent)
        self._smooth_stratified_map = smooth_stratified_map
        self._interior_affine_map = interior_affine_map
        self._local_affine_maps = local_affine_maps

    def underlying_smooth_stratified_map(self):
        return self._smooth_stratified_map

    def interior_affine_map(self):
        return self._interior_affine_map

    def local_affine_maps(self):
        return self._local_affine_maps

    def _call_(self, point):
        return self._smooth_stratified_map(point)

    def __mul__(self, other):
        pass


class _StratifiedIntegralAffineMor(CategoricalMor):
    ElementMethods = _StratifiedIntegralAffineMapMethods

    def _element_constructor_(self, smooth_stratified_map, interior_affine_map, local_affine_maps):
        pass

    @object_level
    def identity(self):
        pass


class IntegralAffineBoundaryMor(_StratifiedIntegralAffineMor):
    r"""Local integral-affine maps preserving the specified boundary."""


class IntegralAffineCornerMor(_StratifiedIntegralAffineMor):
    r"""Local integral-affine maps preserving every corner-depth stratum."""


class IntegralAffineBoundaryMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = IntegralAffineBoundaryMor


class IntegralAffineCornerMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = IntegralAffineCornerMor


class _StratifiedAffineForgetfulFunctor(Functor):
    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, manifold):
        return manifold.underlying_smooth_stratified_manifold()

    def _apply_morphism(self, morphism):
        return morphism.underlying_smooth_stratified_map()


class _StratifiedAffineInteriorFunctor(Functor):
    def __init__(self, source):
        super().__init__(source, IntegralAffineManifolds())

    def _apply_object(self, manifold):
        pass

    def _apply_morphism(self, morphism):
        return morphism.interior_affine_map()


class _StratifiedAffineManifoldMethods:
    def underlying_smooth_stratified_manifold(self):
        pass

    def affine_atlas(self):
        pass

    def depth_stratum(self, depth):
        pass

    def interior_affine_manifold(self):
        pass

    def interior_inclusion(self):
        pass


class IntegralAffineManifoldsWithCorners(OwnedCategory):
    r"""Smooth corner manifolds with selected compatible integral-affine charts."""

    _MorCategory = IntegralAffineCornerMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "integral-affine manifolds with corners"

    def an_object(self):
        pass

    def on(self, smooth_corner_manifold, affine_atlas):
        pass

    @cached_method
    def forget(self):
        return _StratifiedAffineForgetfulFunctor(self, SmoothManifoldsWithCorners())

    @cached_method
    def interior(self):
        return _StratifiedAffineInteriorFunctor(self)

    class ParentMethods(_StratifiedAffineManifoldMethods):
        def __init__(self, smooth_stratified_manifold, affine_atlas, **rest):
            self._smooth_stratified_manifold = smooth_stratified_manifold
            self._affine_atlas = affine_atlas
            super().__init__(**rest)

        def underlying_smooth_stratified_manifold(self):
            return self._smooth_stratified_manifold

        def affine_atlas(self):
            return self._affine_atlas

        def depth_stratum(self, depth):
            pass

    class Oriented(CategoryWithAxiom):
        r"""Corner atlases with orientation-preserving integral transitions."""

    class StrictLatticePointAtlas(CategoryWithAxiom):
        r"""Corner atlases whose transitions preserve selected lattice points."""


class IntegralAffineManifoldsWithBoundary(OwnedCategory):
    r"""Smooth half-space manifolds with selected integral-affine charts."""

    _MorCategory = IntegralAffineBoundaryMorCategoryConstruction

    def super_categories(self):
        return [IntegralAffineManifoldsWithCorners()]

    @classmethod
    def _repr_object_names(cls):
        return "integral-affine manifolds with boundary"

    def an_object(self):
        pass

    def on(self, smooth_boundary_manifold, affine_atlas):
        pass

    @cached_method
    def forget(self):
        return _StratifiedAffineForgetfulFunctor(self, SmoothManifoldsWithBoundary())

    @cached_method
    def interior(self):
        return _StratifiedAffineInteriorFunctor(self)

    class ParentMethods(_StratifiedAffineManifoldMethods):
        def boundary(self):
            pass

        def boundary_inclusion(self):
            pass

    class Oriented(CategoryWithAxiom):
        r"""Boundary atlases with orientation-preserving integral transitions."""

    class StrictLatticePointAtlas(CategoryWithAxiom):
        r"""Boundary atlases whose transitions preserve selected lattice points."""


class SingularIntegralAffineSpaceMor(CategoricalMor):
    r"""Maps preserving the singular set and the affine regular structure."""

    class ElementMethods:
        def __init__(self, parent, topological_map, singular_locus_map, regular_affine_map):
            Morphism.__init__(self, parent)
            self._topological_map = topological_map
            self._singular_locus_map = singular_locus_map
            self._regular_affine_map = regular_affine_map

        def underlying_topological_morphism(self):
            return self._topological_map

        def singular_locus_morphism(self):
            return self._singular_locus_map

        def regular_affine_morphism(self):
            return self._regular_affine_map

        def _call_(self, point):
            return self._topological_map(point)

        def __mul__(self, other):
            pass

    def _element_constructor_(self, topological_map, singular_locus_map, regular_affine_map):
        pass

    @object_level
    def identity(self):
        pass


class SingularIntegralAffineSpaceMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SingularIntegralAffineSpaceMor


class _UnderlyingSingularTopologicalSpaceFunctor(Functor):
    r"""Forget the singular affine structure, on objects and morphisms."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, space):
        return space.underlying_topological_space()

    def _apply_morphism(self, morphism):
        return morphism.underlying_topological_morphism()


class _RegularIntegralAffineLocusFunctor(Functor):
    r"""Restrict a singular affine space and its maps to the regular loci."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, space):
        return space.regular_affine_manifold()

    def _apply_morphism(self, morphism):
        return morphism.regular_affine_morphism()


class _SingularLocusSubobjectFunctor(Functor):
    r"""Send each singular locus to its selected topological inclusion."""

    def __init__(self, source):
        super().__init__(source, TopologicalSpaces().MonomorphismArrowCategory())

    def _apply_object(self, space):
        return self.codomain().object(space.singular_locus_inclusion())

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return self.codomain().Mor(source, target)(
            morphism.singular_locus_morphism(),
            morphism.underlying_topological_morphism(),
        )


class _RegularLocusSubobjectFunctor(Functor):
    r"""Send each regular complement to its selected topological inclusion."""

    def __init__(self, source):
        super().__init__(source, TopologicalSpaces().MonomorphismArrowCategory())

    def _apply_object(self, space):
        return self.codomain().object(space.regular_locus_inclusion())

    def _apply_morphism(self, morphism):
        pass


class SingularIntegralAffineSpaces(OwnedCategory):
    r"""Spaces with a selected singular locus and affine regular complement."""

    _MorCategory = SingularIntegralAffineSpaceMorCategoryConstruction

    @staticmethod
    def __classcall__(cls, dimension=None):
        if dimension is not None:
            return SingularIntegralAffineSpacesOfDimension(dimension)
        return Category.__classcall__(cls)

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "singular integral-affine spaces"

    def an_object(self):
        pass

    def PureDimension(self, dimension):
        return SingularIntegralAffineSpacesOfDimension(dimension)

    def on(
        self,
        topological_space,
        singular_locus_inclusion,
        regular_locus_inclusion,
        regular_affine_manifold,
    ):
        r"""Select the singular subobject and affine structure on its exact complement."""
        pass

    def from_face_gluing(self, gluing_cocone, singular_locus_inclusion, affine_collars):
        r"""Select an affine structure from a complex quotient and collar data."""
        pass

    def surgery(
        self,
        region_inclusion,
        replacement,
        boundary_isomorphism,
        affine_collars,
    ):
        pass

    def symington_surgery(self, cut_inclusion, size, affine_regluing, affine_collars):
        r"""Select a cut, size, and affine regluing through the surgery construction."""
        pass

    def basis_triangle_surgery(
        self,
        source_space,
        point,
        tangent_lattice_basis,
        replacement,
        boundary_isomorphism,
        affine_collars,
    ):
        r"""Select the unimodular triangle at a point and its boundary gluing."""
        pass

    @cached_method
    def forget(self):
        return _UnderlyingSingularTopologicalSpaceFunctor(self, TopologicalSpaces())

    @cached_method
    def regular_locus(self):
        return _RegularIntegralAffineLocusFunctor(self, IntegralAffineManifolds())

    @cached_method
    def singular_locus_functor(self):
        return _SingularLocusSubobjectFunctor(self)

    @cached_method
    def regular_locus_inclusions(self):
        return _RegularLocusSubobjectFunctor(self)

    class ParentMethods:
        def __init__(
            self,
            topological_space,
            singular_locus_inclusion,
            regular_locus_inclusion,
            regular_affine_manifold,
            **rest,
        ):
            self._topological_space = topological_space
            self._singular_locus_inclusion = singular_locus_inclusion
            self._regular_locus_inclusion = regular_locus_inclusion
            self._regular_affine_manifold = regular_affine_manifold
            super().__init__(**rest)

        def underlying_topological_space(self):
            return self._topological_space

        def singular_locus(self):
            return self.singular_locus_inclusion().domain()

        def singular_locus_inclusion(self):
            return self._singular_locus_inclusion

        def regular_locus(self):
            return self.regular_locus_inclusion(), self.regular_affine_manifold()

        def regular_locus_inclusion(self):
            return self._regular_locus_inclusion

        def regular_affine_manifold(self):
            return self._regular_affine_manifold

        def gluing_cocone(self):
            pass

        def affine_collars(self):
            pass

        def local_monodromy(self, singular_point, loop, affine_frame):
            pass

        def triangulations(self):
            from sage_extensions.categories.triangulations import ChosenTriangulations

            return ChosenTriangulations(self)

        def triangulation_is_compatible_with_singular_locus(self, triangulation):
            pass

        def triangulate(self):
            pass

        def triangulation_preserving_automorphisms(self, triangulation):
            r"""Affine automorphisms preserving the selected triangulation."""
            pass

        def action_on_face_poset(self, triangulation):
            r"""Map triangulation-preserving affine automorphisms to face automorphisms."""
            pass

        def lift_face_action(self, abstract_action, realization_map, affine_chart_maps):
            r"""Lift a face action through the selected realization to this affine space."""
            pass

    class FiniteSingularSet(CategoryWithAxiom):
        r"""Singular affine spaces whose selected singular locus is finite."""

        def PureDimension(self, dimension):
            return Cat().meet((self, SingularIntegralAffineSpacesOfDimension(dimension)))

    class Sphere(CategoryWithAxiom):
        r"""Singular integral-affine spaces whose underlying space is a sphere."""

    class Disk(CategoryWithAxiom):
        r"""Singular integral-affine spaces whose underlying space is a closed ball."""

    class RealProjectivePlane(CategoryWithAxiom):
        r"""Dimension-two singular affine spaces with underlying real projective plane."""


class SingularIntegralAffineSpacesOfDimension(OwnedParameterizedCategory):
    r"""Full dimension-``n`` stratum with specified singular local models."""

    @staticmethod
    def __classcall__(cls, dimension):
        dimension = _owned_integers()(dimension)
        if dimension < 1:
            raise ValueError(f"a singular affine dimension must be positive, not {dimension}")
        return Category.__classcall__(cls, dimension)

    def dimension(self):
        return self.parameter()

    @cached_method
    def local_model_category(self):
        return SingularIntegralAffineLocalModels(self.dimension())

    def super_categories(self):
        return [SingularIntegralAffineSpaces()]

    def _repr_object_names(self):
        return f"singular integral-affine spaces of dimension {self.dimension()}"

    def an_object(self):
        pass

    def on(
        self,
        topological_space,
        singular_locus_inclusion,
        regular_locus_inclusion,
        regular_affine_manifold,
        local_models=None,
    ):
        r"""Select the exact regular locus and, in higher dimension, local models."""
        pass

    def from_face_gluing(
        self,
        gluing_cocone,
        singular_locus_inclusion,
        affine_collars,
        local_models,
    ):
        pass

    def surgery(
        self,
        region_inclusion,
        replacement,
        boundary_isomorphism,
        affine_collars,
        local_models,
    ):
        pass

    @cached_method
    def forget(self):
        return _UnderlyingSingularTopologicalSpaceFunctor(self, TopologicalSpaces())

    @cached_method
    def regular_locus(self):
        return _RegularIntegralAffineLocusFunctor(self, IntegralAffineManifolds(self.dimension()))

    @cached_method
    def singular_locus_functor(self):
        return _SingularLocusSubobjectFunctor(self)

    @cached_method
    def regular_locus_inclusions(self):
        return _RegularLocusSubobjectFunctor(self)

    class ParentMethods:
        def __init__(self, local_models, **rest):
            self._local_models = local_models
            super().__init__(**rest)

        def local_models(self):
            return self._local_models

        def local_model_at(self, singular_point):
            pass


class SingularIntegralAffineLocalModelMor(CategoricalMor):
    r"""Pointed local maps preserving the affine regular loci."""

    class ElementMethods:
        def __init__(self, parent, pointed_map, singular_locus_map, regular_affine_map):
            Morphism.__init__(self, parent)
            self._pointed_map = pointed_map
            self._singular_locus_map = singular_locus_map
            self._regular_affine_map = regular_affine_map

        def underlying_pointed_map(self):
            return self._pointed_map

        def singular_locus_morphism(self):
            return self._singular_locus_map

        def regular_affine_morphism(self):
            return self._regular_affine_map

        def _call_(self, point):
            return self._pointed_map(point)

        def underlying_singular_affine_morphism(self):
            pass

        def __mul__(self, other):
            pass

    def _element_constructor_(self, pointed_map, singular_locus_map, regular_affine_map):
        pass

    @object_level
    def identity(self):
        pass


class SingularIntegralAffineLocalModelMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = SingularIntegralAffineLocalModelMor


class _UnpointedSingularLocalModelFunctor(Functor):
    r"""Forget the selected singular point on a local model and map."""

    def __init__(self, source):
        super().__init__(source, SingularIntegralAffineSpaces(source.dimension()))

    def _apply_object(self, model):
        return model.underlying_singular_affine_space()

    def _apply_morphism(self, morphism):
        return morphism.underlying_singular_affine_morphism()


class SingularIntegralAffineLocalModels(OwnedParameterizedCategory):
    r"""Pointed dimension-``n`` neighbourhoods with affine regular complements."""

    _MorCategory = SingularIntegralAffineLocalModelMorCategoryConstruction

    @staticmethod
    def __classcall__(cls, dimension):
        dimension = _owned_integers()(dimension)
        if dimension < 1:
            raise ValueError(f"a singular affine local-model dimension must be positive, not {dimension}")
        return Category.__classcall__(cls, dimension)

    def dimension(self):
        return self.parameter()

    def super_categories(self):
        return [Objects()]

    def _repr_object_names(self):
        return f"singular integral-affine local models of dimension {self.dimension()}"

    def an_object(self):
        pass

    def on(
        self,
        topological_neighborhood,
        singular_locus_inclusion,
        regular_locus_inclusion,
        regular_affine_manifold,
        singular_point,
    ):
        pass

    @cached_method
    def forget_point(self):
        return _UnpointedSingularLocalModelFunctor(self)

    class ParentMethods:
        def __init__(self, singular_space, singular_point, **rest):
            self._singular_space = singular_space
            self._singular_point = singular_point
            super().__init__(**rest)

        def underlying_singular_affine_space(self):
            return self._singular_space

        def topological_neighborhood(self):
            return self._singular_space.underlying_topological_space()

        def singular_locus_inclusion(self):
            return self._singular_space.singular_locus_inclusion()

        def regular_locus_inclusion(self):
            return self._singular_space.regular_locus_inclusion()

        def regular_affine_manifold(self):
            return self._singular_space.regular_affine_manifold()

        def singular_point(self):
            return self._singular_point

        def link(self):
            pass

        def link_inclusion(self):
            r"""The selected link as a subspace of the local neighborhood."""
            pass

        def monodromy(self, loop, affine_frame):
            pass
