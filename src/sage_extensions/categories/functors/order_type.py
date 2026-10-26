r"""The order-type functor from well-orders and order isomorphisms to ``Ord``."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.sets.cardinals import Ordinals
from sage_extensions.categories.sets.set_categories import WellOrderedSets


class _OrderTypeFunctor(Functor):
    r"""Send a represented well-order to its ordinal order type.

    The domain is the core of well-ordered sets: a morphism is therefore an
    order isomorphism, not an arbitrary bijection of underlying sets.  Equal
    well-order types map to the identity comparison in the thin category
    ``Ord``.

    Unverified source specimen::

        sage: from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
        sage: from sage_extensions.categories.sets.set_categories import finite_ordinal_set
        sage: labels = finite_ordered_set(("a", "b", "c"))
        sage: three = finite_ordinal_set(3)
        sage: well_orders = WellOrderedSets()
        sage: forward = well_orders.Mor(labels, three)(lambda point: labels.ranking_map()(point))
        sage: inverse = well_orders.Mor(three, labels)(lambda position: labels.ranking_map().inverse()(position))
        sage: isomorphism = well_orders.Core().Mor(labels, three)(forward, inverse)
        sage: order_type = well_orders.order_type_functor()
        sage: order_type(labels) == order_type(three) == Ordinals()(3)
        True
        sage: order_type(isomorphism) == Ordinals().Mor(3, 3).identity()
        True
    """

    def __init__(self) -> None:
        super().__init__(WellOrderedSets().Core(), Ordinals())

    def _apply_object(self, well_order):
        return well_order.order_type()

    def _apply_morphism(self, isomorphism):
        source = self(isomorphism.domain())
        target = self(isomorphism.codomain())
        return self.codomain().Mor(source, target).unique_morphism()

    def _repr_(self) -> str:
        return "Order type: core(WellOrd) -> Ord"


@cached_function
def _order_type_functor() -> _OrderTypeFunctor:
    return _OrderTypeFunctor()


__all__ = []
