r"""The cardinality functor ``# : core(Set) -> Card``."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.sets.cardinals import (
    Cardinalities,
    cardinal,
)
from sage_extensions.categories.sets.set_categories import (
    CartesianProductsOfSets,
    CoproductsOfSets,
    PowerSets,
    Sets,
)


class _CardinalityFunctor(Functor):
    r"""Send a set to its cardinal and a set isomorphism to the unique order arrow.

    Isomorphic sets have equal cardinality, so the image of a bijection is the
    identity of that cardinal in the thin category ``Card``; ``Card``'s Mor object
    supplies it.
    """

    def __init__(self) -> None:
        super().__init__(Sets().Core(), Cardinalities())

    def _apply_object(self, set_object):
        return set_object.cardinality()

    def _apply_morphism(self, isomorphism):
        source = self(isomorphism.domain())
        target = self(isomorphism.codomain())
        return self.codomain().Mor(source, target).unique_morphism()

    def morphism_image(self, morphism):
        r"""Act on an arrow of ``core(Set)``, or on a set map read as one.

        A set map that is not already an arrow of the core is read through
        the set Mor it belongs to and presented there as an isomorphism; that
        presentation is the one that decides whether it is a bijection.
        """
        core_mor = self.domain().Mor(morphism.domain(), morphism.codomain())
        match morphism:
            case _ if morphism in core_mor:
                isomorphism = morphism
            case _:
                set_mor = Sets().Mor(morphism.domain(), morphism.codomain())
                if not set_mor.accepts(morphism):
                    raise TypeError(f"{morphism} is not a set map; apply the underlying-set functor first")
                isomorphism = morphism.as_isomorphism()
        return super().morphism_image(isomorphism)

    def cartesian_product_comparison(self, product):
        r"""Return ``prod_i #X_i -> #(prod_i X_i)`` for a represented set product."""
        assert product in CartesianProductsOfSets(), (
            f"the comparison prod_i #X_i -> #(prod_i X_i) needs a Cartesian product of sets, but {product} "
            "is not one"
        )
        expected = self.codomain().indexed_product(
            product.index_set(), lambda index: self(product.factor(index))
        )
        return self.codomain().Mor(expected, self(product)).unique_morphism()

    def coproduct_comparison(self, coproduct):
        r"""Return ``sum_i #X_i -> #(coprod_i X_i)`` for a represented set coproduct."""
        assert coproduct in CoproductsOfSets(), (
            f"the comparison sum_i #X_i -> #(coprod_i X_i) needs a coproduct of sets, but {coproduct} is not one"
        )
        expected = self.codomain().indexed_sum(
            coproduct.index_set(), lambda index: self(coproduct.cofactor(index))
        )
        return self.codomain().Mor(expected, self(coproduct)).unique_morphism()

    def power_set_comparison(self, power_set):
        r"""Return ``2^(#X) -> #P(X)`` for a represented power set."""
        assert power_set in PowerSets(), (
            f"the comparison 2^#X -> #P(X) needs a power set P(X), but {power_set} is not one"
        )
        expected = self.codomain().power(cardinal(2), self(power_set.base_set()))
        return self.codomain().Mor(expected, self(power_set)).unique_morphism()

    def _repr_(self):
        return "Cardinality functor # : core(Set) -> Card"


@cached_function
def _cardinality_functor() -> _CardinalityFunctor:
    return _CardinalityFunctor()


__all__ = []
