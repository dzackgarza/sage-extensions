r"""The contravariant affine spectrum functor on commutative algebras.

``Spec_R : CAlg_R^op -> AffSch_R`` sends an algebra ``A`` to the object
``Schemes(R).Affine()(A)``, the one entry of the affine schemes over ``R``, and
an algebra morphism ``phi : A -> B`` to the scheme morphism
``Spec B -> Spec A`` whose coordinate pullback is ``phi``.
"""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.algebras.algebras import Algebras
from sage_extensions.categories.rings.ring_foundation import _owned_ring
from sage_extensions.categories.schemes.schemes import (
    Schemes,
    _affine_spec_morphism,
)


class _AffineSpecFunctor(Functor):
    r"""The contravariant functor ``Spec_R: CAlg_R -> AffSch_R``."""

    def __init__(self, base_ring) -> None:
        base = _owned_ring(base_ring)
        self._base_ring = base
        algebras = Algebras(base).Associative().Unital().Commutative()
        super().__init__(algebras.opposite(), Schemes(base).Affine())

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, opposite_algebra):
        return self.codomain()(opposite_algebra.underlying_object())

    def _apply_morphism(self, opposite_morphism):
        return _affine_spec_morphism(opposite_morphism.underlying_arrow())

    def _repr_(self) -> str:
        return f"Affine spectrum functor over {self.base_ring()}"


@cached_function
def _affine_spec_functor(base_ring):
    return _AffineSpecFunctor(base_ring)


__all__ = []
