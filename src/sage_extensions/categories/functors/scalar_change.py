r"""Scalar extension, restriction and coextension along a specified ring morphism.

For ``f: R -> S`` the three functors ``S tensor_R -``, ``Res_f`` and
``Hom_R(S, -)`` form the adjoint triple ``S tensor_R - -| Res_f -| Hom_R(S, -)``
(Weibel, *An Introduction to Homological Algebra*, Proposition 2.3.10 and
Exercise 2.3.6).  Induction, restriction and coinduction along a subgroup
``H <= G`` are these functors along ``R[H] -> R[G]``; their transversal
realization lives in ``group_induction``.
"""

from sage.misc.cachefunc import cached_function, cached_method

from sage_extensions.categories.algebras.group_algebras import GroupAlgebras
from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.modules.base_change import _base_change_element

from sage_extensions.categories.modules.pure.modules import (
    FinitelyGeneratedModules,
    Modules,
    RestrictedScalarsModules,
)
from sage_extensions.categories.rings.ring_foundation import (
    _engine_ring,
    _owned_ring,
)


def _scalar_extension_comparison(source, direct, iterated):
    r"""Return ``T tensor_R M ~= T tensor_S (S tensor_R M)``.

    The currently represented scalar extensions preserve the selected framing
    of ``M``.  The associativity comparison is therefore the unique linear
    isomorphism carrying each directly extended generator to the iterated
    generator with the same source label.  This is the scalar-extension
    pseudofunctor comparison; downstream semilinear categories consume it
    rather than owning another associator.
    """
    source_ring = source.base_ring()
    target_ring = direct.base_ring()
    match (
        source.has_selected_module_resolution(),
        direct.has_selected_module_resolution(),
        iterated.has_selected_module_resolution(),
    ):
        case (True, True, True):
            pass
        case _:
            raise TypeError(
                f"the comparison T (x)_R M = T (x)_S (S (x)_R M) for M = {source} is computed only when "
                f"{source}, {direct} and {iterated} have chosen generating sets"
            )
    modules = Modules(target_ring)
    forward = modules.Mor(direct, iterated)(
        lambda label: iterated.module_generator(label)
    )
    inverse = modules.Mor(iterated, direct)(
        lambda label: direct.module_generator(label)
    )
    return modules.Core().Mor(direct, iterated)(forward, inverse)


class _ScalarExtensionFunctor(Functor):
    r"""``S tensor_R - : Mod_R -> Mod_S`` along ``f:R -> S``.

    The mathematical functor is defined on every module.  The live computation
    presently materializes the represented framed/free/presented cases for
    which the module layer has an exact constructor.
    """

    def __init__(self, ring_map) -> None:
        self._ring_map = ring_map
        self._source_ring = _owned_ring(ring_map.domain())
        self._target_ring = _owned_ring(ring_map.codomain())
        super().__init__(Modules(self._source_ring), Modules(self._target_ring))

    def ring_map(self):
        return self._ring_map

    def _apply_object(self, module):
        # Restriction of scalars does not erase relations.  In particular
        # S tensor_R Res_f(M) cannot be replaced by a free module merely
        # because a generating family of Res_f(M) was selected.
        match self.ring_map():
            case ring_map if ring_map.is_identity() is True:
                return module
            case _:
                return module.base_change(self.ring_map())

    def _apply_morphism(self, morphism):
        match self.ring_map():
            case ring_map if ring_map.is_identity() is True:
                return morphism
            case _:
                pass
        source_module = morphism.domain()
        target_module = morphism.codomain()
        assert source_module.has_selected_module_resolution(), (
            f"scalar extension of the morphism {morphism} needs a chosen generating set of its domain "
            f"{source_module}"
        )
        assert target_module.has_selected_module_resolution(), (
            f"scalar extension of the morphism {morphism} needs a chosen generating set of its codomain "
            f"{target_module}"
        )
        source = self(source_module)
        target = self(target_module)

        def image(label):
            original = source_module.module_generator(label)
            return _base_change_element(
                target_module,
                target,
                self.ring_map(),
                morphism(original),
            )

        mor = source.module_category().Mor(source, target)
        return mor._from_scalar_extension(morphism, image, self)

    def identity_comparison(self, module):
        r"""Return the canonical comparison ``id_* M ~= M`` for an identity scalar map."""
        match self.ring_map().is_identity():
            case True:
                pass
            case False:
                raise ValueError(
                    f"the comparison id_* M = M exists only for scalar extension along an identity map, but "
                    f"{self.ring_map()} is not an identity"
                )
        changed = self(module)
        match changed is module:
            case True:
                identity = module.module_category().Mor(module, module).identity()
                return module.module_category().Core().Mor(module, module)(identity, identity)
            case False:
                raise ArithmeticError(
                    f"scalar extension along the identity {self.ring_map()} sent {module} to a different module"
                )

    @cached_method(key=lambda self, second_ring_map: id(second_ring_map))
    def composite_ring_map(self, second_ring_map):
        r"""Return the selected composite ``R -> S -> T`` for this extension."""
        match second_ring_map.domain() is self.ring_map().codomain():
            case True:
                return second_ring_map * self.ring_map()
            case False:
                raise ValueError(
                    f"cannot compose {second_ring_map} after {self.ring_map()}: the first ends at "
                    f"{self.ring_map().codomain()}, but the second starts at {second_ring_map.domain()}"
                )

    def composition_comparison(self, second_ring_map, module):
        r"""Return ``(second * self)_* M ~= second_* (self_* M)``.

        ``self`` is extension along ``R -> S`` and ``second_ring_map`` is
        ``S -> T``.  The result is the specified associativity comparison of
        scalar extension, not an equality inferred from rank or presentation.
        """
        first = self(module)
        second = Modules(second_ring_map.domain()).scalar_extension(second_ring_map)
        iterated = second(first)
        composite = self.composite_ring_map(second_ring_map)
        direct = Modules(self.ring_map().domain()).scalar_extension(composite)(module)
        return _scalar_extension_comparison(module, direct, iterated)

    def _repr_(self):
        return f"Scalar extension along {self.ring_map()}"


class _RestrictionOfScalarsFunctor(Functor):
    r"""``Res_f : Mod_S -> Mod_R`` along ``f:R -> S``."""

    def __init__(self, ring_map) -> None:
        self._ring_map = ring_map
        self._source_ring = _owned_ring(ring_map.domain())
        self._target_ring = _owned_ring(ring_map.codomain())
        super().__init__(Modules(self._target_ring), Modules(self._source_ring))

    def ring_map(self):
        return self._ring_map

    # Along an identity ``R -> R`` restriction is the identity functor, as
    # scalar extension along it is.  Along ``R -> R[G]`` an ``R[G]``-module is
    # an ``R``-module with a chosen action, and restriction forgets the
    # action: the image is the module the action was stated on, and elements
    # pass to it by coercion.  Along any other map the image is the
    # restricted-scalars view.

    def _restricts_group_modules(self) -> bool:
        return self._target_ring in GroupAlgebras(self._source_ring)

    def _apply_object(self, module):
        if self.ring_map().is_identity() is True:
            return module
        if self._restricts_group_modules():
            return module.unformed_module()
        return RestrictedScalarsModules(self._source_ring)(module, self.ring_map())

    def _restricted_element(self, source_module, restricted, element):
        r"""Read an element of ``source_module`` in its restriction ``restricted``."""
        return restricted(element)

    def _extension_element(self, source_module, restricted, element):
        r"""Read an element of ``restricted`` back in ``source_module``.

        The restricted-scalars module of ``M`` holds each element of ``M``
        as its underlying element.  The restriction of an algebra, and the
        underlying ``R``-module of an ``R[G]``-module, are built on the
        elements of ``M`` itself, which ``M`` reads directly.
        """
        if self.ring_map().is_identity() is True:
            return element
        match restricted:
            case _ if restricted in RestrictedScalarsModules(self._source_ring):
                return element.underlying_element()
            case _:
                return source_module(element)

    def _apply_morphism(self, morphism):
        # Restriction changes which ring acts and never the underlying map, so
        # ``Res_f(g)`` is ``g``: its element action is the original one read
        # through the restricted parents, and its ``R``-linearity is the
        # ``S``-linearity of ``g`` along ``f``, not a runtime condition.  A
        # framing of the source is therefore not part of the statement.
        if self.ring_map().is_identity() is True:
            return morphism
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return source.module_category().Mor(source, target)._from_constructed_element_map(
            lambda element: self._restricted_element(
                morphism.codomain(),
                target,
                morphism(
                    self._extension_element(morphism.domain(), source, element)
                ),
            ),
            premises=(morphism,),
        )

    def _repr_(self):
        return f"Restriction of scalars along {self.ring_map()}"


class _CoextensionOfScalarsFunctor(Functor):
    r"""``Hom_R(S, -) : Mod_R -> Mod_S`` along ``f: R -> S``, the right adjoint of ``Res_f``.

    ``S`` acts on ``Hom_R(S, M)`` through its right regular action,
    ``(s . phi)(t) = phi(t s)``.  The Mor is represented when ``S`` is a
    finitely framed ``R``-module; ``Hom_ZZ(ZZ[x], M)`` is a countable product
    the module layer does not build, and is refused.
    """

    def __init__(self, ring_map) -> None:
        self._ring_map = ring_map
        self._source_ring = _owned_ring(ring_map.domain())
        self._target_ring = _owned_ring(ring_map.codomain())
        super().__init__(Modules(self._source_ring), Modules(self._target_ring))

    def ring_map(self):
        return self._ring_map

    def scalars_as_module(self):
        r"""``S`` as an ``R``-module, the domain of every ``Hom_R(S, M)``."""
        scalars, ring = self._target_ring, self._source_ring
        assert scalars in Modules(ring), (
            f"Mor_R(S, -) needs S = {scalars} to be a module over R = {ring}, but it is not one"
        )
        assert scalars.has_selected_module_resolution() and scalars in FinitelyGeneratedModules(ring), (
            f"Mor_R(S, -) is computed only for S finitely generated over R with a chosen generating set, "
            f"but {scalars} is not one over {ring}"
        )
        return scalars

    def _right_multiplication(self, scalar):
        scalars = self.scalars_as_module()
        return scalars.module_category().Mor(scalars, scalars)(
            {
                label: scalars.module_generator(label) * scalar
                for label in scalars.module_generating_set()
            }
        )

    # A coextended module over a group algebra is a group module built on
    # ``Hom_R(S, M)``, whose elements pass to it by coercion; over any other
    # ring it is the general module built on ``Hom_R(S, M)``.

    def _coextends_to_group_modules(self) -> bool:
        return self._target_ring in GroupAlgebras(self._source_ring)

    def _mor_element(self, coextended, element):
        r"""Read an element of ``Hom_R(S, M)`` off the coextended module."""
        if self._coextends_to_group_modules():
            return coextended.unformed_module()(element)
        return element.underlying_element()

    def _coextended_element(self, coextended, mor_element):
        return coextended(mor_element)

    def _linear_map(self, domain, codomain, function):
        r"""The ``S``-linear map given elementwise by ``function``."""
        if self._coextends_to_group_modules():
            source_module = domain.unformed_module()
            target_module = codomain.unformed_module()
            underlying = source_module.module_category().Mor(
                source_module, target_module
            )._from_constructed_element_map(
                lambda element: target_module(function(domain(element))),
            )
            return domain.Mor(codomain)._from_equivariant_images(underlying)
        return domain.module_category().Mor(domain, codomain)._from_constructed_element_map(function)

    def _apply_object(self, module):
        scalars = self.scalars_as_module()
        mor = scalars.module_category().Mor(scalars, module)
        identity = module.module_category().Mor(module, module).identity()
        endomorphisms = Modules(self._source_ring).End(mor)
        action = self._target_ring.Mor(endomorphisms)(
            lambda scalar: self._right_multiplication(scalar).internal_mor_map(
                identity,
                source_internal_mor=mor,
                target_internal_mor=mor,
            ),
        )
        return Modules(self._target_ring)(mor, action)

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        scalars = self.scalars_as_module()
        identity = scalars.module_category().Mor(scalars, scalars).identity()
        postcomposition = identity.internal_mor_map(
            morphism,
            source_internal_mor=scalars.module_category().Mor(
                scalars, morphism.domain()
            ),
            target_internal_mor=scalars.module_category().Mor(
                scalars, morphism.codomain()
            ),
        )
        if self._coextends_to_group_modules():
            return source.Mor(target)._from_equivariant_images(postcomposition)
        return source.module_category().Mor(source, target)._from_constructed_element_map(
            lambda element: self._coextended_element(
                target,
                postcomposition(self._mor_element(source, element)),
            ),
            premises=(postcomposition,),
        )

    def _repr_(self):
        return f"Coextension of scalars along {self.ring_map()}"


class _BaseChangeAdjunction(Adjunction):
    r"""``S tensor_R - ⊣ Res_f``."""

    _extension_functor = _ScalarExtensionFunctor
    _restriction_functor = _RestrictionOfScalarsFunctor

    def __init__(self, ring_map) -> None:
        self._ring_map = ring_map
        super().__init__(
            self._extension_functor(ring_map),
            self._restriction_functor(ring_map),
        )

    def _unit_component(self, module):
        extended = self.left_adjoint()(module)
        restricted = self.right_adjoint()(extended)
        return module.module_category().Mor(module, restricted)(
            lambda label: restricted(extended.module_generator(label))
        )

    def _counit_component(self, module):
        r"""``epsilon_N : S tensor_R Res_f(N) -> N``, ``s tensor n |-> s n``.

        On a chosen generating set of ``Res_f(N)`` the counit is fixed by the
        generator images ``1 tensor n_i |-> n_i``.  Otherwise it is the map
        the tensor quotient classifies from the ``R``-bilinear evaluation
        ``(s, n) |-> phi_n(s)``, where ``phi_n : S -> N`` is the ``S``-linear
        map with ``phi_n(1) = n``.
        """
        restricted = self.right_adjoint()(module)
        extended = self.left_adjoint()(restricted)
        mor = extended.module_category().Mor(extended, module)
        match restricted.has_selected_module_resolution():
            case True:
                return mor(
                    lambda label: self.right_adjoint()._extension_element(
                        module, restricted, restricted.module_generator(label)
                    )
                )
            case False:
                pass
        restriction = self.right_adjoint()
        regular = _owned_ring(self._ring_map.codomain()).regular_module()
        module_maps = module.module_category().Mor(regular, module)

        def acting(scalar, element):
            image = restriction._extension_element(module, restricted, element)
            through = module_maps(
                {label: image for label in regular.module_generating_set()}
            )
            return restriction(through)(scalar)

        return mor._from_constructed_element_map(
            lambda value: restriction._extension_element(
                module,
                restricted,
                extended.underlying_set().evaluate(
                    extended(value).underlying_element(), restricted, acting
                ),
            ),
        )


    def _repr_(self):
        return f"Scalar-extension/restriction adjunction along {self._ring_map}"


class _RestrictionCoextensionAdjunction(Adjunction):
    r"""``Res_f ⊣ Hom_R(S, -)``.

    The unit sends ``n`` to ``s |-> s n`` and the counit evaluates at ``1``.
    """

    _restriction_functor = _RestrictionOfScalarsFunctor
    _coextension_functor = _CoextensionOfScalarsFunctor

    def __init__(self, ring_map) -> None:
        self._ring_map = ring_map
        super().__init__(
            self._restriction_functor(ring_map),
            self._coextension_functor(ring_map),
        )

    def _unit_component(self, module):
        restricted = self.left_adjoint()(module)
        coextended = self.right_adjoint()(restricted)
        scalars = self.right_adjoint().scalars_as_module()
        mor = scalars.module_category().Mor(scalars, restricted)

        def image(element):
            return self.right_adjoint()._coextended_element(
                coextended,
                mor(
                    {
                        label: self.left_adjoint()._restricted_element(
                            restricted,
                            module.scalar_multiple(scalars.module_generator(label), element),
                        )
                        for label in scalars.module_generating_set()
                    }
                ),
            )

        return self.right_adjoint()._linear_map(module, coextended, image)

    def _counit_component(self, module):
        coextended = self.right_adjoint()(module)
        restricted = self.left_adjoint()(coextended)
        one = self.right_adjoint().scalars_as_module().one()
        return restricted.module_category().Mor(restricted, module)._from_constructed_element_map(
            lambda element: self.right_adjoint()._mor_element(
                coextended, self.left_adjoint()._extension_element(restricted, element)
            )(one),
        )

    def _repr_(self):
        return f"Restriction/coextension adjunction along {self._ring_map}"


@cached_function(key=lambda ring_map: id(ring_map))
def _base_change_adjunction(ring_map) -> _BaseChangeAdjunction:
    return _BaseChangeAdjunction(ring_map)


@cached_function(key=lambda ring_map: id(ring_map))
def _restriction_coextension_adjunction(ring_map) -> _RestrictionCoextensionAdjunction:
    return _RestrictionCoextensionAdjunction(ring_map)
