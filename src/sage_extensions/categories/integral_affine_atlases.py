r"""Selected presentations of integral-affine atlases on smooth manifolds."""

from sage.misc.cachefunc import cached_method
from sage.categories.morphism import Morphism
from sage.rings.infinity import Infinity
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level
from sage_extensions.categories.abstract_categories.objects import Objects, OwnedCategory
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.integral_affine_manifolds import IntegralAffineManifolds
from sage_extensions.categories.manifolds import SmoothManifolds
from sage_extensions.categories.real_ck_atlases import RealCkAtlases
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of
from sage_extensions.owned_category_bases import CategoryWithAxiom


class IntegralAffineAtlasMor(CategoricalMor):
    r"""Smooth maps with compatible chartwise integral-affine maps."""

    class ElementMethods:
        def __init__(self, parent, smooth_map, chartwise_affine_maps):
            Morphism.__init__(self, parent)
            self._smooth_map = smooth_map
            self._chartwise_affine_maps = chartwise_affine_maps

        def underlying_smooth_morphism(self):
            return self._smooth_map

        def chartwise_affine_maps(self):
            return self._chartwise_affine_maps

        def _call_(self, point):
            return self._smooth_map(point)

        def integral_affine_morphism(self, source, target):
            r"""The affine map of the charts ``source`` and ``target``.

            The retained data are the chartwise affine maps, indexed by the pair of
            charts they are written in: the source chart of this arrow's domain
            atlas and the target chart of its codomain atlas.  A pair that is not
            retained is an error rather than a silent identity, because a map that
            is not affine in a pair of charts is not an integral-affine map of the
            atlases.
            """
            chartwise = self.chartwise_affine_maps()
            assert (source, target) in chartwise, (
                f"{self} retains no affine map of the charts {source} and {target}: its "
                f"chartwise maps are indexed by the pairs it is affine in, and this is "
                f"not one of them"
            )
            return chartwise[(source, target)]

        def smooth_atlas_morphism(self):
            r"""The arrow of smooth manifolds these two atlases are atlases of.

            An integral-affine atlas morphism is a smooth map together with its
            chartwise affine maps, so the smooth arrow is the map itself, which is
            also what :meth:`underlying_smooth_morphism` answers.
            """
            return self.underlying_smooth_morphism()

        def __mul__(self, other):
            r"""The composite, when ``other`` ends where this arrow starts.

            The composite is the composite of the two smooth maps, with the chart
            ``U`` of ``other``'s domain to the chart ``W`` of this arrow's codomain
            affine by the composite through every chart ``V`` that both arrows are
            written in.
            """
            if not isinstance(other, IntegralAffineAtlasMor.ElementMethods):
                return NotImplemented
            if other.codomain() is not self.domain():
                raise ValueError(
                    f"{other} ends at {other.codomain()} and {self} starts at "
                    f"{self.domain()}; these arrows do not compose"
                )
            composite = {}
            for (source, middle), left in other.chartwise_affine_maps().items():
                for (start, target), right in self.chartwise_affine_maps().items():
                    if start is not middle:
                        continue
                    composite[(source, target)] = right * left
            return self.parent()(self.underlying_smooth_morphism() * other.underlying_smooth_morphism(), composite)

    def _element_constructor_(self, smooth_map, chartwise_affine_maps):
        r"""Build the integral-affine atlas morphism these data state.

        The smooth map must be one between the manifolds the two atlases are
        atlases of: an integral-affine atlas morphism is added to a smooth map of
        that pair, and a map of another pair would give the arrow two authorities
        for its endpoints (``OWN-15``).  The chartwise affine maps are retained as
        given; what they are indexed by is stated by
        :meth:`IntegralAffineAtlasMor.ElementMethods.integral_affine_morphism`,
        which reads them by the pair of charts they are affine in.
        """
        if element_parent(smooth_map) is self:
            return smooth_map
        assert smooth_map.domain() is self.domain().underlying_smooth_manifold(), (
            f"{smooth_map} starts at {smooth_map.domain()}, not at the manifold "
            f"{self.domain()} is an atlas of"
        )
        assert smooth_map.codomain() is self.codomain().underlying_smooth_manifold(), (
            f"{smooth_map} ends at {smooth_map.codomain()}, not at the manifold "
            f"{self.codomain()} is an atlas of"
        )
        return self.element_class(self, smooth_map, chartwise_affine_maps)

    @object_level
    @cached_method
    def identity(self):
        r"""The identity arrow of this atlas: the identity map, affine in each chart.

        The smooth map is the manifold's identity and the chartwise data are the
        identity of the affine model at each chart's own pair, so the arrow answers
        :meth:`IntegralAffineAtlasMor.ElementMethods.integral_affine_morphism` at
        every chart of the atlas.
        """
        atlas = self.domain()
        manifold = atlas.underlying_smooth_manifold()
        model = atlas.affine_model()
        affine_identity = Sets().Mor(model, model).identity()
        return self(
            Sets().Mor(manifold, manifold).identity(),
            {(chart, chart): affine_identity for chart in atlas.affine_charts()},
        )


class IntegralAffineAtlasMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = IntegralAffineAtlasMor


class _AtlasUnderlyingManifoldFunctor(Functor):
    r"""Forget the atlas presentation on objects and maps."""

    def __init__(self, source):
        super().__init__(source, SmoothManifolds())

    def _apply_object(self, atlas):
        return atlas.underlying_smooth_manifold()

    def _apply_morphism(self, morphism):
        return morphism.underlying_smooth_morphism()


class _AtlasMaximalizationFunctor(Functor):
    r"""Pass from a compatible atlas to its selected maximal structure."""

    def __init__(self, source, target):
        super().__init__(source, target)

    def _apply_object(self, atlas):
        pass

    def _apply_morphism(self, morphism):
        pass


class _UnderlyingSmoothAtlasFunctor(Functor):
    def __init__(self, source):
        super().__init__(source, RealCkAtlases(Infinity))

    def _apply_object(self, atlas):
        return atlas.smooth_atlas()

    def _apply_morphism(self, morphism):
        return morphism.smooth_atlas_morphism()


class IntegralAffineAtlases(OwnedCategory):
    r"""Compatible charts into one selected real affine lattice model."""

    _MorCategory = IntegralAffineAtlasMorCategoryConstruction

    def super_categories(self):
        return [Objects()]

    @classmethod
    def _repr_object_names(cls):
        return "integral-affine atlas presentations"

    def an_object(self):
        pass

    def on(
        self,
        smooth_manifold,
        affine_model,
        chart_domains,
        chart_domain_inclusions,
        affine_charts,
        overlap_inclusions,
        transition_maps,
    ):
        r"""Select charts, their integral-affine maps and their transitions on the exact manifold.

        An integral-affine structure on a real surface is a family of charts
        into one affine model whose transition maps lie in
        ``GL(2,Z) ⋉ R^2``: they preserve the selected lattice and may reverse
        orientation.  Determinant one is the oriented structure, which is the
        case Alexeev--Engel state, on a real *oriented* surface (Alexeev--Engel,
        *Compactifications of moduli spaces of K3 surfaces with a nonsymplectic
        involution*, arXiv:2208.10383v2, Definition 6.11, p. 30); the
        reflection ``(x, y) |-> (x, -y)`` is a transition of the first kind and
        not of the second.

        Each chart has an open submanifold ``U_s`` of ``smooth_manifold``,
        carried into it by ``U_s -> smooth_manifold``, and an affine chart
        ``phi_s : U_s -> affine_model`` identifying it with a subset of the
        model.  The model overlap of ``U_s`` and ``U_t`` is ``phi_s(U_s cap
        U_t)``, and the transition is the coordinate change read in the model,

            ``tau_{st} = phi_t o phi_s^{-1} : phi_s(U_s cap U_t) -> phi_t(U_s cap U_t)``,

        with ``overlap_inclusions[s, t]`` the inclusion of that model overlap in
        the model.  So a transition is a map of the model, not a chart of the
        manifold restricted to an overlap, and the pair ``(s, t)`` names its
        direction.  On a triple overlap the gluings compose:

            ``tau_{tu} o tau_{st} = tau_{su}``.

        The four families of maps are indexed by the charts.  The construction
        retains them and computes nothing from them: whether the transitions
        are integral-affine and whether the domains cover the manifold are
        decisions the atlas answers
        (:meth:`ParentMethods.transitions_are_integral_affine`,
        :meth:`ParentMethods.chart_domains_cover`), never conditions a caller
        is charged for at construction (``OWN-22``).
        """
        assert smooth_manifold in SmoothManifolds(), (
            f"an integral-affine atlas is a family of charts on a smooth manifold, and "
            f"{smooth_manifold} is in {smooth_manifold.category()}"
        )
        return _object_of(
            self,
            smooth_manifold=smooth_manifold,
            affine_model=affine_model,
            chart_domains=chart_domains,
            chart_domain_inclusions=chart_domain_inclusions,
            affine_charts=affine_charts,
            overlap_inclusions=overlap_inclusions,
            transition_maps=transition_maps,
        )

    def transition_is_integral_affine(self, affine_model, transition_map):
        r"""Decide whether the transition preserves the model's selected lattice."""
        pass

    def refinement(self, finer_atlas, coarser_atlas, chartwise_maps):
        pass

    @cached_method
    def forget(self):
        return _AtlasUnderlyingManifoldFunctor(self)

    @cached_method
    def maximalization(self):
        return _AtlasMaximalizationFunctor(self, IntegralAffineManifolds())

    @cached_method
    def forget_affine_structure(self):
        return _UnderlyingSmoothAtlasFunctor(self)

    class ParentMethods:
        def __init__(
            self,
            smooth_manifold,
            affine_model,
            chart_domains,
            chart_domain_inclusions,
            affine_charts,
            overlap_inclusions,
            transition_maps,
            **rest,
        ):
            self._smooth_manifold = smooth_manifold
            self._affine_model = affine_model
            self._chart_domains = chart_domains
            self._chart_domain_inclusions = chart_domain_inclusions
            self._affine_charts = affine_charts
            self._overlap_inclusions = overlap_inclusions
            self._transition_maps = transition_maps
            super().__init__(**rest)

        def underlying_smooth_manifold(self):
            return self._smooth_manifold

        def affine_model(self):
            return self._affine_model

        def affine_group_action(self):
            return self.affine_model().integral_affine_group_action()

        def chart_domains(self):
            return self._chart_domains

        def chart_domain_inclusion(self, chart):
            r"""Return the selected open inclusion of a chart domain."""
            return self._chart_domain_inclusions[chart]

        def affine_charts(self):
            return self._affine_charts

        def affine_chart(self, chart):
            r"""Return the affine map from its exact open domain to the model."""
            return self._affine_charts[chart]

        def transition_maps(self):
            return self._transition_maps

        def overlap_inclusion(self, source_chart, target_chart):
            r"""Return the inclusion of the model overlap ``phi_s(U_s cap U_t)`` in the model."""
            return self._overlap_inclusions[source_chart, target_chart]

        def transition_map(self, source_chart, target_chart):
            r"""Return the coordinate change ``tau_{st} = phi_t o phi_s^{-1}`` on the model overlap.

            Its domain is ``phi_s(U_s cap U_t)`` and its codomain
            ``phi_t(U_s cap U_t)``; the direction is the pair's.
            """
            return self._transition_maps[source_chart, target_chart]

        def transition_linear_part(self, source_chart, target_chart):
            r"""Return the transition's linear part on the model.

            A transition that preserves the selected lattice has a linear part
            carrying the lattice into itself, and that lattice map is the one
            its own map reports beside it (:meth:`linear_part` here is the map
            of the model).
            """
            return self.transition_map(source_chart, target_chart).linear_part()

        def chart_domains_cover(self):
            r"""Decide whether the selected chart domains cover the manifold."""
            pass

        def transitions_are_integral_affine(self):
            r"""Decide whether every overlap map preserves the selected lattice."""
            pass

        def transition_cocycle_holds(self):
            r"""Decide the affine cocycle condition on each triple overlap."""
            pass

        def restrict(self, open_inclusion):
            pass

        def restriction_morphism(self, restricted_atlas):
            pass

        def maximal_atlas(self):
            pass

        def smooth_atlas(self):
            pass

        @cached_method
        def integral_affine_manifold(self):
            r"""Return the integral-affine manifold this atlas presents.

            The manifold is the exact smooth manifold the atlas is selected on,
            carrying this atlas (``OWN-15``): the atlas is the structure added
            to that manifold, so the presentation is built through
            ``IntegralAffineManifolds.on`` rather than as a second copy of the
            manifold (``OWN-02``, ``OWN-19``).
            """
            return IntegralAffineManifolds().on(self.underlying_smooth_manifold(), self)

    class Oriented(CategoryWithAxiom):
        r"""Atlases with determinant-one integral linear transitions."""

        @cached_method
        def maximalization(self):
            return _AtlasMaximalizationFunctor(self, IntegralAffineManifolds().Oriented())

    class StrictLatticePointAtlas(CategoryWithAxiom):
        r"""Atlases whose transitions preserve selected lattice points."""

        @cached_method
        def maximalization(self):
            return _AtlasMaximalizationFunctor(
                self, IntegralAffineManifolds().StrictLatticePointAtlas()
            )
