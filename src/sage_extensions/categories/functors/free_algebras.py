r"""Tensor and symmetric algebra adjunctions, plus exterior-algebra functoriality."""

from collections.abc import Callable
from typing import ClassVar

from sage.categories.category import Category
from sage.misc.cachefunc import cached_function
from sage.structure.parent import Parent

from sage_extensions.categories.algebras.algebras import (
    Algebras,
)
from sage_extensions.categories.algebras.framed_free_algebras import (
    _symmetric_algebra_of,
    _tensor_algebra_of,
)
from sage_extensions.categories.algebras.free_algebras import (
    AlternatingAlgebras,
    DividedPowerAlgebras,
)
from sage_extensions.categories.algebras.power_algebras import (
    _alternating_algebra_of,
    _divided_power_algebra_of,
)
from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import _owned_ring


class _ModuleAlgebraFunctor(Functor):
    r"""A free algebra functor on ``R``-modules, fixed by its object construction.

    A specialization states the construction ``M |-> A(M)`` and the category
    of algebras it lands in; the morphism action, extending a linear map
    along the degree-one generators, is common to all of them.
    """

    _constructor: ClassVar[Callable[[Parent], Parent]]
    _codomain_category: ClassVar[Callable[[Parent], Category]]
    _name = "free algebra"

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            Modules(self._base_ring),
            self._codomain_category(self._base_ring),
        )

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, module):
        return self._constructor(module)

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target_module = morphism.codomain()
        target = self(target_module)

        def image(label):
            return target.from_component(
                1,
                morphism(morphism.domain().module_generator(label)),
            )

        mor = source.Mor(target)
        return mor._from_degree_preserving_generator_map(image)

    def _repr_(self):
        return f"{self._name} functor on {self.base_ring()}-modules"


class _TensorAlgebraFunctor(_ModuleAlgebraFunctor):
    r"""The functor \(T_R:\mathbf{Mod}_R\to\mathbf{Alg}_R\)."""

    _constructor = staticmethod(_tensor_algebra_of)
    _codomain_category = Algebras
    _name = "Tensor algebra"


class _SymmetricAlgebraFunctor(_ModuleAlgebraFunctor):
    r"""The functor \(\operatorname{Sym}_R:\mathbf{Mod}_R\to\mathbf{CAlg}_R\)."""

    _constructor = staticmethod(_symmetric_algebra_of)
    _codomain_category = staticmethod(
        lambda base_ring: Algebras(base_ring).Associative().Unital().Commutative()
    )
    _name = "Symmetric algebra"


def _lift_algebra_morphism(functor, morphism):
    """Apply the free-algebra construction to both endpoints and lift the arrow."""
    source = functor(morphism.domain())
    target = functor(morphism.codomain())
    return source.Mor(target)(morphism)


class _AlternatingAlgebraFunctor(Functor):
    r"""Exterior-algebra functor on represented modules.

    No ordinary free/forgetful adjunction is asserted for this construction.
    """

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            Modules(self._base_ring),
            AlternatingAlgebras(self._base_ring),
        )

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, module):
        return _alternating_algebra_of(module)

    def _apply_morphism(self, morphism):
        return _lift_algebra_morphism(self, morphism)

    def _repr_(self):
        return f"Alternating algebra functor on {self.base_ring()}-modules"


class _DividedPowerAlgebraFunctor(Functor):
    r"""The divided-power algebra functor ``Gamma_R : Mod_R -> DPAlg_R``."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            Modules(self._base_ring),
            DividedPowerAlgebras(self._base_ring),
        )

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, module):
        return _divided_power_algebra_of(module)

    def _apply_morphism(self, morphism):
        return _lift_algebra_morphism(self, morphism)

    def _repr_(self):
        return f"Divided-power algebra functor on {self.base_ring()}-modules"


@cached_function
def _tensor_algebra_functor(base_ring) -> _TensorAlgebraFunctor:
    return _TensorAlgebraFunctor(base_ring)


@cached_function
def _symmetric_algebra_functor(base_ring) -> _SymmetricAlgebraFunctor:
    return _SymmetricAlgebraFunctor(base_ring)


class _ModuleAlgebraAdjunction(Adjunction):
    r"""A free algebra functor ``F`` with its underlying-module right adjoint ``U``.

    A specialization states the free functor over a base ring; the unit is
    the degree-one inclusion and the counit the evaluation map.
    """

    _left_functor_factory: ClassVar[Callable[[Parent], _ModuleAlgebraFunctor]]
    _name = "module-algebra"

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        left = self._left_functor_factory(self._base_ring)
        right = left.codomain().underlying_module()
        super().__init__(left, right)

    def base_ring(self):
        return self._base_ring

    def _unit_component(self, module):
        r"""The degree-one inclusion \(M\to U(F(M))\)."""
        free_algebra = self.left_adjoint()(module)
        underlying = self.right_adjoint()(free_algebra)
        return module.module_category().Mor(module, underlying)(
            free_algebra.algebra_generator
        )

    def _counit_component(self, algebra):
        r"""Evaluation \(F(U(A))\to A\) when ``U(A)`` is represented."""
        module = self.right_adjoint()(algebra)
        free_algebra = self.left_adjoint()(module)
        mor = free_algebra.Mor(algebra)

        return mor._from_degree_preserving_generator_map(module.module_generator)


    def _repr_(self):
        return f"{self._name} adjunction over {self.base_ring()}"


class _TensorAlgebraAdjunction(_ModuleAlgebraAdjunction):
    r"""The adjunction \(T_R\dashv U:\mathbf{Mod}_R\leftrightarrows\mathbf{Alg}_R\)."""

    _left_functor_factory = staticmethod(_tensor_algebra_functor)
    _name = "Tensor-algebra/underlying-module"


class _SymmetricAlgebraAdjunction(_ModuleAlgebraAdjunction):
    r"""The adjunction \(\operatorname{Sym}_R\dashv U\) for commutative algebras."""

    _left_functor_factory = staticmethod(_symmetric_algebra_functor)
    _name = "Symmetric-algebra/underlying-module"


@cached_function
def _alternating_algebra_functor(base_ring) -> _AlternatingAlgebraFunctor:
    return _AlternatingAlgebraFunctor(base_ring)


@cached_function
def _divided_power_algebra_functor(base_ring) -> _DividedPowerAlgebraFunctor:
    return _DividedPowerAlgebraFunctor(base_ring)


@cached_function
def _tensor_algebra_adjunction(base_ring) -> _TensorAlgebraAdjunction:
    return _TensorAlgebraAdjunction(base_ring)


@cached_function
def _symmetric_algebra_adjunction(base_ring) -> _SymmetricAlgebraAdjunction:
    return _SymmetricAlgebraAdjunction(base_ring)


__all__ = []
