r"""Functorial Set constructions: exponentials and finite/power subsets."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.sets.set_categories import NN, Sets


class _ExponentialFunctor(Functor):
    r"""The internal-Mor functor ``Set^op x Set -> Set``."""

    def __init__(self) -> None:
        self._opposite_sets = Sets().opposite()
        self._product_category = Cat().product((self._opposite_sets, Sets()))
        super().__init__(self._product_category, Sets())

    def opposite_sets(self):
        return self._opposite_sets

    def pair(self, exponent, codomain):
        return self.domain()(self.opposite_sets()(exponent), codomain)

    def _apply_object(self, pair):
        return pair.second().exponential(pair.first().underlying_object())

    def _apply_morphism(self, pair_morphism):
        source = self(pair_morphism.domain())
        target = self(pair_morphism.codomain())
        precompose = pair_morphism.first().underlying_arrow()
        postcompose = pair_morphism.second()
        return Sets().Mor(source, target)(
            lambda function: target(
                lambda element: postcompose(function(precompose(element)))
            ),
        )

    def morphism(self, precompose, postcompose):
        r"""Return the product-category morphism induced by ``precompose`` and ``postcompose``."""
        source = self.pair(precompose.codomain(), postcompose.domain())
        target = self.pair(precompose.domain(), postcompose.codomain())
        opposite = self.opposite_sets().Mor(source.first(), target.first())(precompose)
        return self.domain().Mor(source, target)(opposite, postcompose)

    def _repr_(self):
        return "Exponential bifunctor (X, Y) |-> Y^X"


class _InverseImagePowerSetFunctor(Functor):
    r"""The contravariant power-set functor on the opposite of Set."""

    # If f != g then f(x) != g(x) for some x, and x lies in f^{-1}{f(x)} but
    # not in g^{-1}{f(x)}.
    _faithful = True

    def __init__(self) -> None:
        self._opposite_sets = Sets().opposite()
        super().__init__(self._opposite_sets, Sets())

    def opposite_sets(self):
        return self._opposite_sets

    def _apply_object(self, opposite_set):
        return opposite_set.underlying_object().power_set()

    def _apply_morphism(self, opposite_morphism):
        source = self(opposite_morphism.domain())
        return source.inverse_image_morphism(opposite_morphism.underlying_arrow())

    def opposite_morphism(self, morphism):
        return self.domain().Mor(
            self.domain()(morphism.codomain()),
            self.domain()(morphism.domain()),
        )(morphism)

    def _repr_(self):
        return "Contravariant power-set functor (inverse image)"


class _FinitePowerSetFunctor(Functor):
    r"""The covariant finite-power-set functor under direct image."""

    # If f != g then f(x) != g(x) for some x, and the direct images of the
    # finite subset {x} are {f(x)} != {g(x)}.
    _faithful = True

    def __init__(self) -> None:
        super().__init__(Sets(), Sets())

    def _apply_object(self, source):
        return source.finite_subsets()

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return Sets().Mor(source, target)(
            lambda subset: target(tuple(morphism(member) for member in subset)),
        )

    def _repr_(self):
        return "Finite power-set functor (direct image)"


class _FixedCardinalitySubsetFunctor(Functor):
    r"""Direct image on ``k``-element subsets, defined on injective set maps."""

    def __init__(self, subset_cardinality) -> None:
        # The size of a subset is a natural number; NN's element constructor
        # admits exactly those.
        self._subset_cardinality = NN(subset_cardinality)
        injections = Sets().MonomorphismArrowCategory()
        super().__init__(Sets().WideSubcategory(injections), Sets())

    def subset_cardinality(self):
        return self._subset_cardinality

    def _apply_object(self, source):
        return source.subsets_of_size(int(self.subset_cardinality()))

    def _apply_morphism(self, morphism):
        if not self.domain().admits(morphism):
            raise TypeError(
                f"the direct image on k-element subsets needs an injective map, but {morphism} is not known to "
                "be injective"
            )
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return Sets().Mor(source, target)(
            lambda subset: target(tuple(morphism(member) for member in subset)),
        )

    def _repr_(self):
        return f"Direct image on subsets of cardinality {self.subset_cardinality()}"


@cached_function
def _exponential_functor() -> _ExponentialFunctor:
    return _ExponentialFunctor()


@cached_function
def _inverse_image_power_set_functor() -> _InverseImagePowerSetFunctor:
    return _InverseImagePowerSetFunctor()


@cached_function
def _finite_power_set_functor() -> _FinitePowerSetFunctor:
    return _FinitePowerSetFunctor()


@cached_function
def _fixed_cardinality_subset_functor(subset_cardinality) -> _FixedCardinalitySubsetFunctor:
    return _FixedCardinalitySubsetFunctor(subset_cardinality)


__all__ = []
