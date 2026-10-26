r"""The free-module/underlying-set adjunction ``F_R ⊣ U``."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import _owned_ring
from sage_extensions.categories.sets.set_categories import Sets


class _FreeModuleFunctor(Functor):
    r"""``F_R : Set -> Mod_R``."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(Sets(), Modules(self._base_ring))

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, set_object):
        return self.base_ring().free_module(set_object)

    def _apply_morphism(self, set_morphism):
        source = self(set_morphism.domain())
        target = self(set_morphism.codomain())
        return source.module_category().Mor(source, target)(
            lambda label: target.module_generator(set_morphism(label))
        )

    def _repr_(self):
        return f"Free {self.base_ring()}-module functor"


class _UnderlyingSetFunctor(Functor):
    r"""``U : Mod_R -> Set``; a module is already a set object."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(Modules(self._base_ring), Sets())

    def _apply_object(self, module):
        return module

    def _apply_morphism(self, module_morphism):
        r"""``U(f)`` is the function ``f`` computes on points (``CON-17``)."""
        return Sets().Mor(
            module_morphism.domain(), module_morphism.codomain()
        )(lambda element: module_morphism(element))

    def _repr_(self):
        return f"Underlying-set functor on {self._base_ring}-modules"


class _FreeForgetfulAdjunction(Adjunction):
    r"""``F_R ⊣ U`` between sets and ``R``-modules."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            _FreeModuleFunctor(self._base_ring),
            _UnderlyingSetFunctor(self._base_ring),
        )

    def _unit_component(self, set_object):
        free = self.left_adjoint()(set_object)
        return Sets().Mor(set_object, free)(
            lambda element: free.module_generator(element)
        )

    def _counit_component(self, module):
        free = self.left_adjoint()(self.right_adjoint()(module))
        return free.module_category().Mor(free, module)(lambda element: element)


    def _repr_(self):
        return f"Free/underlying-set adjunction over {self._base_ring}"


@cached_function
def _free_module_functor(base_ring) -> _FreeModuleFunctor:
    return _FreeModuleFunctor(base_ring)


@cached_function
def _underlying_set_functor(base_ring) -> _UnderlyingSetFunctor:
    return _UnderlyingSetFunctor(base_ring)


@cached_function
def _free_forgetful_adjunction(base_ring) -> _FreeForgetfulAdjunction:
    return _FreeForgetfulAdjunction(base_ring)
