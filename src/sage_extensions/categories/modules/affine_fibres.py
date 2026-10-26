r"""Affine inverse images of module subobjects, with their translation action.

For an R-linear map A:P->V, an offset c in V, and an inclusion j:M->V,
the parameter set is {p : c+A(p) in j(M)}. Its translation module is
A^-1(j(M)), including any non-finitely-generated part of that module.
The set pullback, the module inclusion, and the map to M are retained.

Distinguishing mathematical specimens (source phase, DEV-58):

* For A:QQ^2->QQ, A(s,t)=s+t, and ZZ->QQ, the translation
  module is ZZ(1,0)+QQ(1,-1). Every rational multiple of (1,-1)
  belongs to it. A finite ZZ-span of rational vectors cannot equal it.
* For A:QQ->QQ^2, A(t)=(t,0), and ZZ^2->QQ^2, offset (0,1/2)
  gives an empty inverse image. Offset (1/2,0) gives 1/2+ZZ.
* For A:ZZ^2->ZZ, A(s,t)=2s+3t, the fibre over 1 is nonempty
  with translation module ZZ(3,-2); the fibre of multiplication by
  2 over 1 is empty. No chosen image basis identifies source coefficients.
* For X->X+transpose(X) on rational 2 by 2 matrices, the fibre over
  diag(2,0) is diag(1,0)+QQ(E12-E21). Its intersection with integral
  matrices is diag(1,0)+ZZ(E12-E21).
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.modules.general_modules import GeneralModules
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    ModuleSubobjects,
    RestrictedScalarsModules,
)
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of


class ModuleInverseImages(OwnedCategoryOverBaseRing):
    r"""Module subobjects defined by the inverse image of an inclusion."""

    def super_categories(self):
        return [GeneralModules(self.base_ring()), ModuleSubobjects(self.base_ring())]

    def _call_(self, linear_map, target_inclusion):
        if linear_map.codomain() is not target_inclusion.codomain():
            raise ValueError("an inverse image needs a map and inclusion with the same codomain")
        if linear_map.domain().base_ring() is not self.base_ring():
            raise ValueError("the inverse image must use the map's scalar ring")
        return _object_of(self, linear_map=linear_map, target_inclusion=target_inclusion)

    class ParentMethods:
        _derived_construction_parameters = ("base_ring",)

        def __init__(self, linear_map, target_inclusion, **rest):
            self._linear_map = linear_map
            self._target_inclusion = target_inclusion
            ambient = linear_map.domain()
            points = ambient.condition_set(
                lambda point: target_inclusion.is_in_image(linear_map(point))
            )

            def inclusion(submodule):
                arrow = Modules(ambient.base_ring()).Mor(submodule, ambient)._from_constructed_element_map(
                    lambda element: element.underlying_element()
                )
                return Modules(ambient.base_ring()).Mono(submodule, ambient)._subobject_inclusion(
                    arrow,
                    lift=lambda value: submodule(value) if value in points else None,
                )

            super().__init__(
                base_ring=ambient.base_ring(),
                underlying_set=points,
                addition=lambda left, right: left + right,
                zero=ambient.zero(),
                negation=lambda value: -value,
                scalar_action=lambda scalar, value: ambient.scalar_multiple(scalar, value),
                subobject_ambient=ambient,
                subobject_inclusion_factory=inclusion,
                **rest,
            )

        def defining_morphism(self):
            return self._linear_map

        def target_inclusion(self):
            return self._target_inclusion

        @cached_method
        def map_to_target(self):
            r"""The other pullback map, satisfying ``j*k = A*i``."""
            inclusion = self.target_inclusion()
            return Modules(self.base_ring()).Mor(self, inclusion.domain())._from_constructed_element_map(
                lambda element: inclusion.lift(self.defining_morphism()(self.inclusion()(element)))
            )

        def _repr_(self):
            return f"Inverse image of {self.target_inclusion().domain()} under {self.defining_morphism()}"


class AffineModuleFibres(OwnedCategoryOverBaseRing):
    r"""Affine inverse images of represented module inclusions."""

    def super_categories(self):
        return [Sets()]

    def _call_(self, linear_map, target_inclusion, offset, *, parameter_inclusion=None):
        if linear_map.codomain() is not target_inclusion.codomain():
            raise ValueError("the affine map and target inclusion must have the same codomain")
        if linear_map.domain().base_ring() is not self.base_ring():
            raise ValueError("the affine inverse image must use its parameter scalar ring")
        offset = linear_map.codomain()(offset)
        return _object_of(
            self, linear_map=linear_map, target_inclusion=target_inclusion,
            offset=offset, parameter_inclusion=parameter_inclusion,
        )

    class ParentMethods:
        def __init__(self, linear_map, target_inclusion, offset, parameter_inclusion, **rest):
            self._linear_map = linear_map
            self._target_inclusion = target_inclusion
            self._offset = offset
            self._parameter_inclusion = parameter_inclusion
            self._points = linear_map.domain().condition_set(
                lambda point: target_inclusion.is_in_image(offset + linear_map(point))
            )
            super().__init__(facade=self._points, **rest)

        def base_ring(self):
            return self.parameter_module().base_ring()

        def parameter_inclusion(self):
            r"""Return the specified inclusion of integral parameters, when supplied."""
            return self._parameter_inclusion

        def linear_part(self):
            return self._linear_map

        def offset(self):
            return self._offset

        def target_inclusion(self):
            return self._target_inclusion

        def parameter_module(self):
            return self.linear_part().domain()

        def point_set(self):
            return self._points

        def _emptiness_decision(self):
            r"""Decide finite-free affine feasibility by module-image membership.

            For the datum c+A(p) in j(M), a point exists precisely when
            -c lies in the image of (A,-j): P direct_sum M -> V.
            Reuse the module owner's exact preimage solver over a PID.
            Outside this finite-free route retain the emptiness proposition;
            failure of a point-finding procedure never means empty.

            EXAMPLES::

                sage: P = ZZ ** 2
                sage: A = P.Mor(ZZ)(lambda label: ZZ(2) if label == P.module_generating_set()[0] else ZZ(3))
                sage: F = A.solution_fibre(ZZ(1))
                sage: assert F.is_empty() is False
                sage: assert A(F.base_point()) == ZZ(1)
                sage: D = ZZ.Mor(ZZ)(lambda label: ZZ(2))
                sage: assert D.solution_fibre(ZZ(1)).is_empty() is True
                sage: assert D.solution_fibre(ZZ(0)).is_empty() is False
            """
            from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
                _has_finite_free_framing,
            )
            from sage_extensions.categories.rings.ring_foundation import PrincipalIdealDomains

            ring = self.base_ring()
            linear = self.linear_part()
            target = self.target_inclusion()
            if ring not in PrincipalIdealDomains():
                return None
            source, values = linear.domain(), linear.codomain()
            if source in RestrictedScalarsModules(ring) and values in RestrictedScalarsModules(ring):
                field = ring.fraction_field()
                if source.extension_ring() is not field or values.extension_ring() is not field:
                    return None
                if not all(_has_finite_free_framing(module) for module in (
                    source.module_over_extension(), values.module_over_extension(), target.domain()
                )):
                    return None
                _rational_map, equation, rhs = self._fraction_field_lifting_equation()
                return not equation.is_in_image(rhs)
            if not all(
                _has_finite_free_framing(module)
                for module in (linear.domain(), target.domain(), linear.codomain())
            ):
                return None
            product = Modules(ring).biproduct((linear.domain(), target.domain()))
            difference = product.from_summands(linear, -target)
            return not difference.is_in_image(-self.offset())

        def __contains__(self, point):
            return point in self.point_set()

        def _element_constructor_(self, point):
            return self.point_set()(point)

        @cached_method
        def inclusion(self):
            return Sets().Mor(self, self.parameter_module())(lambda point: point)

        @cached_method
        def evaluation(self):
            return Sets().Mor(self, self.target_inclusion().domain())(
                lambda point: self.target_inclusion().lift(self.offset() + self.linear_part()(point))
            )

        @cached_method
        def pullback_construction(self):
            r"""Retain the set-theoretic pullback and both its projections."""
            linear = self.linear_part()
            target = self.target_inclusion()
            product = Sets().product_construction((linear.domain(), target.domain()))
            shape = product.diagram().domain()
            left = product.structure_morphism(shape(0))
            right = product.structure_morphism(shape(1))
            return Sets().equalizer_construction(
                Sets().Mor(product.object(), linear.codomain())(
                    lambda pair: self.offset() + linear(left(pair))
                ),
                Sets().Mor(product.object(), linear.codomain())(
                    lambda pair: target(right(pair))
                ),
            )

        @cached_method
        def translation_module(self):
            return ModuleInverseImages(self.base_ring())(self.linear_part(), self.target_inclusion())

        @cached_method
        def image_translation_module(self):
            r"""Return the translations of the affine image inside the target module.

            For ``A:P -> V`` over ``K=Frac(R)``, with ``j:M -> V``,
            this is ``ker(M -> V/im(A))``. Unlike the parameter module,
            it contains no copy of ``ker(A)``. This distinction includes
            the constant affine map, whose image has zero translations.
            """
            linear = self.linear_part()
            target = self.target_inclusion()
            ring = self.base_ring()
            source, values = linear.domain(), linear.codomain()
            if source in RestrictedScalarsModules(ring) and values in RestrictedScalarsModules(ring):
                field = ring.fraction_field()
                if source.extension_ring() is not field or values.extension_ring() is not field:
                    raise NotImplementedError("image translations require restriction from the fraction field")
                rational_map = Modules(field).Mor(
                    source.module_over_extension(), values.module_over_extension()
                )._from_constructed_element_map(
                    lambda point: linear(source(point)).underlying_element()
                )
                quotient = rational_map.cokernel_projection()
                restrict = Modules(field).restriction_of_scalars(source.ring_map())
                return (restrict(quotient) * target).kernel()
            return (linear.cokernel_projection() * target).kernel()

        @cached_method
        def image_point_set(self):
            r"""The affine image, retained separately from its parameter fibre."""
            if self.image_translation_module().module_rank() == 0:
                from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

                match self.is_empty():
                    case True:
                        points = finite_ordered_set(())
                    case False:
                        points = finite_ordered_set((self.base_point(),))
                    case _:
                        raise NotImplementedError(
                            f"cannot enumerate the constant affine image of {self}: emptiness remains undecided"
                        )
                evaluation = self.evaluation()
                return Sets().Mor(points, evaluation.codomain())(
                    lambda point: evaluation(point)
                ).image()
            return self.evaluation().image()

        @cached_method
        def _fraction_field_lifting_equation(self):
            r"""The equation in the cokernel over the fraction field for mixed-scalar feasibility.

            For p in a fraction-field vector space and m in the supplied
            R-submodule, c+A(p)=j(m) is soluble precisely when the class
            of c in coker(A) is in the image of m |-> class(j(m)).
            Keep A as well, to recover p after solving that equation.
            """
            linear = self.linear_part()
            target = self.target_inclusion()
            ring = self.base_ring()
            source, values = linear.domain(), linear.codomain()
            field = ring.fraction_field()
            if source.extension_ring() is not field or values.extension_ring() is not field:
                raise NotImplementedError("affine point finding here requires restriction from the fraction field")
            rational_source = source.module_over_extension()
            rational_values = values.module_over_extension()
            rational_map = Modules(field).Mor(rational_source, rational_values)._from_constructed_element_map(
                lambda point: linear(source(point)).underlying_element()
            )
            quotient = rational_map.cokernel_projection()
            restricted_quotient = quotient.codomain().restrict_scalars(source.ring_map())
            integral_equation = Modules(ring).Mor(target.domain(), restricted_quotient)(
                lambda label: restricted_quotient(quotient(target(target.domain().module_generator(label)).underlying_element()))
            )
            rhs = restricted_quotient(quotient(self.offset().underlying_element()))
            return rational_map, integral_equation, rhs

        @cached_method
        def base_point(self):
            r"""Select a point by module-image lifting; raise ``ValueError`` for an empty fibre.

            In the mixed-scalar case, first solve the integral equation in
            the rational cokernel. Lift its residual through the rational
            map. The rational kernel stays in ``translation_module``.
            """
            linear = self.linear_part()
            target = self.target_inclusion()
            ring = self.base_ring()
            source = linear.domain()
            values = linear.codomain()
            if source in RestrictedScalarsModules(ring) and values in RestrictedScalarsModules(ring):
                rational_map, integral_equation, rhs = self._fraction_field_lifting_equation()
                integral_value = integral_equation.preimage(rhs)
                residual = target(integral_value).underlying_element() - self.offset().underlying_element()
                return self(source(rational_map.preimage(residual)))
            product = Modules(ring).biproduct((source, target.domain()))
            difference = product.from_summands(linear, -target)
            solution = difference.preimage(-self.offset())
            return self(product.projection(0)(solution))

        @cached_method
        def torsor(self):
            r"""The nonempty fibre as a torsor under its complete translation module."""
            from sage_extensions.categories.group.g_sets import Torsors

            origin = self.base_point()
            kernel = self.translation_module()
            exponential = kernel.multiplicative_group_identification()
            group = exponential.codomain()
            forward = Sets().Mor(group, self)(
                lambda element: self(origin + kernel.inclusion()(exponential.inverse()(element)))
            )
            backward = Sets().Mor(self, group)(
                lambda point: exponential(kernel.inclusion().lift(point - origin))
            )
            # Translation by the origin and subtraction of the origin are
            # inverse; the inclusion's exact lift identifies their difference.
            trivialization = Sets().Core().Mor(group, self)._from_known_inverse_pair(forward, backward)
            return Torsors(group).from_trivialization(trivialization)

        def integral_members(self, integral_parameters):
            r"""Intersect a linear solution fibre with a chosen integral parameter inclusion.

            ``integral_parameters`` maps into the restriction of the rational
            parameter module. The result retains that parameter inclusion.
            This operation requires the target submodule to be zero.
            """
            if not self.target_inclusion().domain().is_zero():
                raise ValueError("integral_members on a solution fibre requires a fixed right-hand side")
            ring = integral_parameters.domain().base_ring()
            field_map = ring.fraction_field_map()
            restrict = Modules(field_map.codomain()).restriction_of_scalars(field_map)
            if integral_parameters.codomain() is not restrict(self.parameter_module()):
                raise ValueError("the integral parameter inclusion has the wrong rational ambient module")
            linear = restrict(self.linear_part()) * integral_parameters
            values = linear.codomain()
            zero = values.zero_subobject()
            result = AffineModuleFibres(ring)(
                linear, zero.inclusion(), values(self.offset()),
                parameter_inclusion=integral_parameters,
            )
            return result

        def _repr_(self):
            return f"Affine inverse image of {self.target_inclusion().domain()} under {self.linear_part()} with offset {self.offset()}"
