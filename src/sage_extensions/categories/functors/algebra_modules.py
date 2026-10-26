r"""The forgetful functor \(U\colon R\text{-}\mathbf{Alg}\to R\text{-}\mathbf{Mod}\).

An algebra is a module equipped with a multiplication, so \(U\) is the
identity on objects: it changes which operations an object answers to, never
the object.  An algebra built by ``Algebras(R)(M, m)`` is a module constructed
through ``Modules(R)`` on the data of \(M\), and its module operations are
inherited from that construction.  On a morphism \(U\) is the underlying
linear map.
"""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.algebras.algebras import Algebras
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.modules.pure.modules import (
    Modules,
)
from sage_extensions.categories.rings.ring_foundation import (
    _owned_ring,
)


class _AlgebraUnderlyingModuleFunctor(Functor):
    r"""\(U\colon\mathbf{Alg}_R\to\mathbf{Mod}_R\)."""

    def __init__(self, base_ring, algebra_category=None) -> None:
        self._base_ring = _owned_ring(base_ring)
        domain = (
            Algebras(self._base_ring) if algebra_category is None else algebra_category
        )
        assert domain.is_subcategory(Algebras(self._base_ring)), (
            f"the underlying-module functor starts at a category of {self._base_ring}-algebras, but "
            f"{domain} is not a subcategory of {Algebras(self._base_ring)}"
        )
        super().__init__(domain, Modules(self._base_ring))

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, algebra):
        r"""Return the underlying \(R\)-module of one algebra: the algebra itself."""
        return algebra

    def _apply_morphism(self, morphism):
        r"""Return the algebra morphism read as a module morphism between the same objects.

        \(U\) changes neither an element nor its image; it changes which
        operations the map answers to.  An \(R\)-algebra morphism is
        \(R\)-linear by definition, under the same retained linearity
        premise as the admitted arrow. Forgetting multiplication does not
        decide an unresolved premise.
        """
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return source.module_category().Mor(source, target)._from_constructed_element_map(
            lambda element: morphism(element), premises=(morphism,)
        )

    def _repr_(self):
        return f"Underlying-module functor on {self.base_ring()}-algebras"


@cached_function
def _algebra_underlying_module_functor(
    base_ring,
    algebra_category=None,
) -> _AlgebraUnderlyingModuleFunctor:
    return _AlgebraUnderlyingModuleFunctor(base_ring, algebra_category)


__all__ = []
