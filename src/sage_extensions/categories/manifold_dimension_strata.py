r"""Dimension filtrations and pure strata of the represented manifold categories."""

from sage.categories.category import Category
from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.manifolds import (
    ComplexManifolds,
    DifferentiableManifolds,
    SmoothManifolds,
    TopologicalManifolds,
    _ComplexRealificationFunctor,
)
from sage_extensions.categories.manifolds_with_boundary import (
    RealCkManifoldsWithBoundary,
    RealCkManifoldsWithCorners,
    SmoothManifoldsWithBoundary,
    SmoothManifoldsWithCorners,
    TopologicalManifoldsWithBoundary,
    TopologicalManifoldsWithCorners,
)
from sage_extensions.categories.real_ck_manifolds import RealCkManifolds
from sage_extensions.categories.rings.ring_foundation import _owned_integers


def _manifold_dimension_parameters(base_category, dimension):
    if base_category not in (
        TopologicalManifolds(),
        DifferentiableManifolds(),
        SmoothManifolds(),
        ComplexManifolds(),
        TopologicalManifoldsWithBoundary(),
        SmoothManifoldsWithBoundary(),
        TopologicalManifoldsWithCorners(),
        SmoothManifoldsWithCorners(),
    ) and not isinstance(
        base_category,
        (RealCkManifolds, RealCkManifoldsWithBoundary, RealCkManifoldsWithCorners),
    ):
        raise TypeError(f"{base_category} is not a selected manifold category")
    dimension = _owned_integers()(dimension)
    if dimension < 0:
        raise ValueError(f"a manifold dimension must be nonnegative, not {dimension}")
    return base_category, dimension


class ManifoldsOfDimensionAtMost(OwnedCategory):
    r"""The full subcategory whose component dimensions do not exceed ``n``."""

    @staticmethod
    def __classcall__(cls, base_category, dimension):
        base_category, dimension = _manifold_dimension_parameters(base_category, dimension)
        return Category.__classcall__(cls, base_category, dimension)

    def __init__(self, base_category, dimension):
        self._base_category = base_category
        self._dimension_bound = dimension
        super().__init__()

    def base_category(self):
        return self._base_category

    def dimension_bound(self):
        return self._dimension_bound

    def super_categories(self):
        return [self.base_category()]

    def __contains__(self, manifold):
        return manifold in self.base_category() and manifold.dimension() <= self.dimension_bound()

    def _repr_object_names(self):
        return f"{self.base_category()} of dimension at most {self.dimension_bound()}"

    def an_object(self):
        pass

    def on(self, manifold):
        r"""Place the exact base manifold under the componentwise bound."""
        if manifold not in self:
            raise TypeError(f"{manifold} does not have dimension at most {self.dimension_bound()}")
        return manifold


class PureDimensionalManifolds(OwnedCategory):
    r"""The full subcategory of manifolds pure of dimension ``n``.

    The dimension is real except when the selected base is
    ``ComplexManifolds()``, where it is complex dimension. Morphisms are
    exactly those of the selected base category between objects in this
    stratum; restricting objects does not change a hom set.
    """

    @staticmethod
    def __classcall__(cls, base_category, dimension):
        base_category, dimension = _manifold_dimension_parameters(base_category, dimension)
        return Category.__classcall__(cls, base_category, dimension)

    def __init__(self, base_category, dimension):
        self._base_category = base_category
        self._dimension = dimension
        super().__init__()

    def base_category(self):
        return self._base_category

    def dimension(self):
        return self._dimension

    def super_categories(self):
        return [ManifoldsOfDimensionAtMost(self.base_category(), self.dimension())]

    def __contains__(self, manifold):
        return manifold in self.base_category() and manifold.dimension() == self.dimension()

    def _repr_object_names(self):
        return f"pure {self.dimension()}-dimensional {self.base_category()}"

    def an_object(self):
        pass

    def on(self, manifold):
        r"""Place the exact base manifold in its pure-dimension stratum."""
        if manifold not in self:
            raise TypeError(f"{manifold} is not pure of dimension {self.dimension()}")
        return manifold

    @cached_method
    def realification(self):
        r"""Realify a complex ``m``-manifold into real dimension ``2m``."""
        if self.base_category() is not ComplexManifolds():
            raise TypeError("realification requires the pure complex-manifold stratum")
        target = PureDimensionalManifolds(SmoothManifolds(), 2 * self.dimension())
        return _ComplexRealificationFunctor(self, target)
