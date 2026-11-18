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
from sage_extensions.owned_category import _object_of
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
        r"""Equip the exact smooth manifold with a selected integral-affine atlas.

        An integral-affine manifold is a smooth manifold whose charts are
        integral-affine, i.e. whose transition maps lie in ``GL(2,Z) ⋉ R^2``:
        they preserve the selected lattice, and determinant one -- the
        orientation-preserving case -- is the axiom ``Oriented``.  Alexeev--Engel
        state the oriented case, on a real oriented surface (Alexeev--Engel,
        *Compactifications of moduli spaces of K3 surfaces with a nonsymplectic
        involution*, arXiv:2208.10383v2, Definition 6.11, p. 30).  The added
        datum is the atlas, whose own construction is
        :meth:`IntegralAffineAtlases.on`; the manifold retains that atlas and
        the smooth manifold it is an atlas of, and introduces no further
        structure (``OWN-15``, ``OWN-19``).

        The atlas must be an atlas of this manifold: an integral-affine
        structure is added to the manifold the charts are selected on, so
        passing another manifold, even an equal one, would give the object two
        authorities for what it forgets to (``OWN-15``).
        """
        from sage_extensions.categories.integral_affine_atlases import IntegralAffineAtlases

        assert smooth_manifold in SmoothManifolds(), (
            f"an integral-affine manifold is a smooth manifold with a selected "
            f"integral-affine atlas, and {smooth_manifold} is in "
            f"{smooth_manifold.category()}"
        )
        assert affine_atlas in IntegralAffineAtlases(), (
            f"the added structure of an integral-affine manifold is an integral-affine "
            f"atlas, and {affine_atlas} is in {affine_atlas.category()}"
        )
        assert affine_atlas.underlying_smooth_manifold() is smooth_manifold, (
            f"the atlas {affine_atlas} is an atlas of "
            f"{affine_atlas.underlying_smooth_manifold()}, not of {smooth_manifold}: an "
            f"integral-affine structure is added to the manifold that atlas is selected on"
        )
        return _object_of(
            self,
            smooth_manifold=smooth_manifold,
            affine_atlas=affine_atlas,
        )

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


def _surgery_data(region_inclusion, replacement, boundary_isomorphism, affine_collars):
    r"""Return the four selected data of the surgery the arguments state.

    Cutting the region out and sewing the replacement in along its boundary does not
    change the ambient surface as a smooth manifold or as a topological space -- the
    base of a Symington surgery is the surface it was cut from (Alexeev--Engel,
    *Compactifications of moduli spaces of K3 surfaces with a nonsymplectic
    involution*, arXiv:2208.10383v2, Construction 6.16, pp. 31--32) -- so the result
    is the ambient space, the replacement's singular locus, the region as regular
    locus, and the replacement's structure restricted to the region and reglued by the
    collar charts.  The general category and its fixed-dimension stratum state the
    result from these data; the construction is written once, here.
    """
    ambient = region_inclusion.codomain()
    assert region_inclusion.domain() in SmoothManifolds(), (
        f"the region {region_inclusion.domain()} is an open submanifold of the ambient "
        f"surface, and it is in {region_inclusion.domain().category()}"
    )
    assert replacement in SingularIntegralAffineSpaces(), (
        f"a surgery glues a singular integral-affine space along the region's "
        f"boundary, and {replacement} is in {replacement.category()}"
    )
    assert replacement.underlying_topological_space() is ambient, (
        f"the replacement is glued into the ambient surface: its underlying space is "
        f"{replacement.underlying_topological_space()}, not {ambient}"
    )
    from sage_extensions.categories.integral_affine_atlases import IntegralAffineAtlases
    from sage_extensions.categories.integral_affine_collars import IntegralAffineCollars
    from sage_extensions.categories.sets.set_categories import Sets

    source_collar, target_collar = affine_collars
    for collar in (source_collar, target_collar):
        assert collar in IntegralAffineCollars(), (
            f"a surgery's regluing is read through its collars, and {collar} is in "
            f"{collar.category()}"
        )
    assert boundary_isomorphism.domain() is source_collar.face(), (
        f"the boundary isomorphism starts at {boundary_isomorphism.domain()}, not at "
        f"the source collar's face {source_collar.face()}"
    )
    assert boundary_isomorphism.codomain() is target_collar.face(), (
        f"the boundary isomorphism ends at {boundary_isomorphism.codomain()}, not at "
        f"the target collar's face {target_collar.face()}"
    )
    restricted = replacement.regular_affine_manifold().affine_atlas().restrict(
        region_inclusion
    )
    model = restricted.affine_model()
    chart_domains = dict(restricted.chart_domains())
    chart_domain_inclusions = {
        chart: restricted.chart_domain_inclusion(chart) for chart in chart_domains
    }
    affine_charts = {
        chart: restricted.affine_chart(chart) for chart in chart_domains
    }
    for collar in (source_collar, target_collar):
        collar_chart = collar.collar_chart()
        assert collar_chart.codomain() is model, (
            f"the collar chart {collar_chart} is read in {collar_chart.codomain()}, not "
            f"in the affine model {model} of the surface the surgery reglues"
        )
        neighbourhood = collar_chart.domain()
        chart_domains[collar] = neighbourhood
        chart_domain_inclusions[collar] = (
            Sets().Mor(neighbourhood, region_inclusion.domain()).identity()
            if neighbourhood is region_inclusion.domain()
            else region_inclusion.domain().open_submanifold_inclusion(neighbourhood)
        )
        affine_charts[collar] = collar_chart
    reglued = IntegralAffineAtlases().on(
        region_inclusion.domain(),
        model,
        chart_domains,
        chart_domain_inclusions,
        affine_charts,
        {},
        {},
    )
    return {
        "topological_space": ambient,
        "singular_locus_inclusion": replacement.singular_locus_inclusion(),
        "regular_locus_inclusion": region_inclusion,
        "regular_affine_manifold": reglued.integral_affine_manifold(),
    }


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
        r"""Select the singular subobject and affine structure on its exact complement.

        A singular integral-affine space is one topological space with two selected
        parts: a singular locus, and the integral-affine structure of the exact
        complement of that locus.  The four stated data are exactly that selection --
        the space, one inclusion per part, and the affine manifold on the regular
        part -- and nothing is reconstructed from them (``OWN-15``).

        Each inclusion is a selection into *this* space, and the regular part's
        inclusion is a selection of the manifold the affine structure is added to:
        passing a map into another space, even an equal one, would give the object
        two authorities for what it is a selection into, and passing a regular part
        that is not the affine manifold's own underlying manifold would give the
        affine structure a domain it is not selected on.  Whether the two parts
        exhaust the space and meet only in the singular locus is a question about
        the space, answered by the reader of the topology, and it is not re-decided
        here.
        """
        assert topological_space in TopologicalSpaces(), (
            f"a singular integral-affine space is a topological space with a selected "
            f"singular locus, and {topological_space} is in "
            f"{topological_space.category()}"
        )
        for inclusion in (singular_locus_inclusion, regular_locus_inclusion):
            assert inclusion.codomain() is topological_space, (
                f"{inclusion} selects into {inclusion.codomain()}, not into "
                f"{topological_space}: a singular integral-affine space's parts are "
                f"selected in the space itself"
            )
        assert singular_locus_inclusion.domain() is not regular_locus_inclusion.domain(), (
            f"the singular locus {singular_locus_inclusion.domain()} and the regular "
            f"locus {regular_locus_inclusion.domain()} are one object; an integral-affine "
            f"structure on the complement of the singular locus is not added to the "
            f"singular locus"
        )
        assert regular_affine_manifold in IntegralAffineManifolds(), (
            f"the regular locus of a singular integral-affine space carries an "
            f"integral-affine manifold, and {regular_affine_manifold} is in "
            f"{regular_affine_manifold.category()}"
        )
        assert (
            regular_locus_inclusion.domain()
            is regular_affine_manifold.underlying_smooth_manifold()
        ), (
            f"the affine structure is selected on "
            f"{regular_affine_manifold.underlying_smooth_manifold()}, but the regular "
            f"locus of {topological_space} is {regular_locus_inclusion.domain()}"
        )
        return _object_of(
            self,
            topological_space=topological_space,
            singular_locus_inclusion=singular_locus_inclusion,
            regular_locus_inclusion=regular_locus_inclusion,
            regular_affine_manifold=regular_affine_manifold,
        )

    def surgery(
        self,
        region_inclusion,
        replacement,
        boundary_isomorphism,
        affine_collars,
    ):
        r"""Glue the replacement into the ambient space along the boundary of the region.

        The region is the part of the ambient integral-affine surface that survives the
        cut, selected by ``region_inclusion``: the inclusion of an open submanifold
        ``V`` of the ambient smooth manifold ``X``.  Cutting the region out and sewing
        the replacement in along its boundary does not change ``X`` as a smooth
        manifold or as a topological space -- the base of a Symington surgery is the
        surface it was cut from -- so the result's underlying space is ``X`` itself,
        its singular locus is the replacement's, and its regular locus is the region.

        The integral-affine structure of the result is ``X``'s, restricted to the
        region (``IntegralAffineAtlases.restrict``) and reglued by the collar charts:
        the two collars of ``affine_collars`` are the source and the target of the
        gluing, ``boundary_isomorphism`` identifies their faces, and each collar's
        chart is a chart of the result on its neighbourhood, into the same affine
        model.  The chartwise affine gluing of the two collars is what makes the result
        integral-affine rather than only topological (Alexeev--Engel, *Compactifications
        of moduli spaces of K3 surfaces with a nonsymplectic involution*,
        arXiv:2208.10383v2, Construction 6.16, pp. 31--32).

        The replacement supplies the singular locus and the ambient affine structure;
        it is a singular integral-affine space on ``X``, whose regular affine manifold
        is the structure this surgery restricts.  Nothing is rebuilt: the result
        retains the replacement's singular inclusion, the region's inclusion, and the
        restricted structure's own charts (``OWN-15``).
        """
        return self.on(
            **_surgery_data(
                region_inclusion, replacement, boundary_isomorphism, affine_collars
            )
        )

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
        r"""Select the exact regular locus of a space of this dimension, and its local models.

        The four data are the general category's -- one topological space, the
        singular locus selected in it, the regular locus selected in it, and the
        integral-affine manifold on that regular locus -- together with the local
        models of the singularities, which the fixed-dimension stratum adds.  The
        affine structure must be one of this dimension: a dimension-``n`` space's
        regular locus is ``n``-dimensional, and an atlas of another dimension would
        state the space twice (``OWN-15``).

        Whether the parts exhaust the space and meet only in the singular locus is a
        question about the space, not re-decided here; and a stratum with no singular
        models selected passes none, which is what the general category states.
        """
        assert topological_space in TopologicalSpaces(), (
            f"a singular integral-affine space is a topological space with a selected "
            f"singular locus, and {topological_space} is in "
            f"{topological_space.category()}"
        )
        for inclusion in (singular_locus_inclusion, regular_locus_inclusion):
            assert inclusion.codomain() is topological_space, (
                f"{inclusion} selects into {inclusion.codomain()}, not into "
                f"{topological_space}: a singular integral-affine space's parts are "
                f"selected in the space itself"
            )
        assert singular_locus_inclusion.domain() is not regular_locus_inclusion.domain(), (
            f"the singular locus {singular_locus_inclusion.domain()} and the regular "
            f"locus {regular_locus_inclusion.domain()} are one object; an integral-affine "
            f"structure on the complement of the singular locus is not added to the "
            f"singular locus"
        )
        assert regular_affine_manifold in IntegralAffineManifolds(), (
            f"the regular locus of a singular integral-affine space carries an "
            f"integral-affine manifold, and {regular_affine_manifold} is in "
            f"{regular_affine_manifold.category()}"
        )
        assert (
            regular_locus_inclusion.domain()
            is regular_affine_manifold.underlying_smooth_manifold()
        ), (
            f"the affine structure is selected on "
            f"{regular_affine_manifold.underlying_smooth_manifold()}, but the regular "
            f"locus of {topological_space} is {regular_locus_inclusion.domain()}"
        )
        assert regular_affine_manifold.dimension() == self.dimension(), (
            f"a singular integral-affine space of dimension {self.dimension()} has an "
            f"integral-affine regular locus of that dimension, and {regular_affine_manifold} "
            f"has dimension {regular_affine_manifold.dimension()}"
        )
        if local_models is not None:
            assert local_models in self.local_model_category(), (
                f"the singular local models of a dimension-{self.dimension()} space are "
                f"objects of {self.local_model_category()}, and {local_models} is in "
                f"{local_models.category()}"
            )
        return _object_of(
            self,
            topological_space=topological_space,
            singular_locus_inclusion=singular_locus_inclusion,
            regular_locus_inclusion=regular_locus_inclusion,
            regular_affine_manifold=regular_affine_manifold,
            local_models=local_models,
        )

    def surgery(
        self,
        region_inclusion,
        replacement,
        boundary_isomorphism,
        affine_collars,
        local_models,
    ):
        r"""Glue the replacement into a space of this dimension along the region's boundary.

        The construction is the general category's (``_surgery_data``): the result is
        the ambient space, the replacement's singular locus, the region as regular
        locus, and the replacement's structure restricted to the region and reglued by
        the collar charts.  The fixed-dimension stratum states the same result with its
        dimension and the singular local models it is given.
        """
        return self.on(
            **_surgery_data(
                region_inclusion, replacement, boundary_isomorphism, affine_collars
            ),
            local_models=local_models,
        )

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
