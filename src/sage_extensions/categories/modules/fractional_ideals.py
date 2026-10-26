r"""Ideals and fractional ideals as modules represented by their inclusions."""

from functools import reduce

from sage.misc.cachefunc import cached_function
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.element import ModuleElement
from sage.structure.element import parent as element_parent
from sage.structure.richcmp import richcmp

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    ModuleSubobjects,
)
from sage_extensions.categories.rings.commutative_ideals import (
    CommutativeIdeals,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedIntegralDomains,
    OwnedOrders,
    OwnedRings,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_ring,
    _owned_integers,
    _owned_rationals,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.owned_category import _object_of
from sage_extensions.tensors.tensor import (
    _engine_component_vector,
    tensor,
)


class FractionalIdeals(OwnedCategoryOverBaseRing):
    r"""Fractional ideals of an integral domain, as modules in its fraction field."""

    def parameter_category(self):
        r"""The coefficient ring is a nonzero commutative domain."""
        return OwnedIntegralDomains()

    def an_object(self):
        r"""The fractional ideal (2) of the base ring."""
        return self.base_ring().fractional_ideal(2)

    def _repr_object_names(self):
        return f"fractional ideals over {self.base_ring()}"

    def super_categories(self):
        r"""A fractional ideal is a framed submodule of the fraction field.

        a generic selected-generator category because this level chooses the spanning values and
        hands them up as the framing.  Declaring the level that consumes a
        datum is what puts it after this one in the linearization; listing it
        beside this category in a join leaves the order to C3, which ran the
        framing level first and left the framing keyword with nothing to
        consume it.
        """
        ring = self.base_ring()
        return [Modules(ring), ModuleSubobjects(ring)]

    class ElementMethods(ModuleElement):
        def __init__(self, parent, value) -> None:
            ModuleElement.__init__(self, parent)
            self._value = _engine_ring(parent.fraction_field())(value)

        def _inclusion_value(self):
            r"""Protected representation contract of this module's fractional-ideal constructions: the value in ``K``."""
            return self._value

        def _add_(self, other):
            return self.parent()(self._value + other._value)

        def _neg_(self):
            return self.parent()(-self._value)

        def _lmul_(self, scalar):
            return self.parent().scalar_multiple(scalar, self)

        def _richcmp_(self, other, op):
            return richcmp(self._value, other._value, op)

        def _repr_(self):
            return repr(_owned_engine_element(self.parent().fraction_field(), self._value))

    class ParentMethods:
        def __init__(
            self,
            base_ring,
            fraction_field,
            module_generator_values,
            **rest,
        ) -> None:
            r"""Construct the ``R``-submodule of ``K = Frac(R)`` spanned by a finite family.

            The datum is the fraction field and the spanning family of its
            elements; the family frames the ideal and the inclusion into ``K``
            read over ``R`` is its subobject structure.
            """
            ring = _owned_ring(base_ring)
            self._fraction_field = _owned_ring(fraction_field)
            self._module_generator_values = tuple(module_generator_values)
            super().__init__(
                base_ring=ring,
                module_generating_set=finite_ordered_set(
                    range(len(self._module_generator_values))
                ),
                module_generator_function=self._generator_of_selected_value,
                subobject_inclusion_factory=_fractional_ideal_inclusion,
                **rest,
            )

        def _generator_of_selected_value(self, label):
            r"""Return the chosen spanning element indexed by ``label``."""
            labels = self.module_generating_set()
            return self.element_class(
                self,
                self._module_generator_values[labels.ranking_map()(label)],
            )

        def _selected_module_coefficients(self, element):
            r"""Coordinates in the spanning family, over the integers.

            A fractional ideal of ``ZZ`` is spanned by one value ``g``, and
            ``x = (x/g) g`` with ``x/g`` integral exactly when ``x`` lies in the
            ideal.  Over an order the spanning family need not be a basis, so
            its coordinates are a choice this representation does not make.
            """
            assert _engine_ring(self.base_ring()) is SageZZ, (
                f"coordinates of an element of {self} in its generators are computed only over ZZ, where "
                f"a fractional ideal is principal; {self} is over {self.base_ring()}, where the "
                f"generators need not be a basis and coordinates are not unique"
            )
            element = self(element)
            value = element._inclusion_value()
            if not self._module_generator_values:
                assert value == 0, (
                    f"{value} has no coordinates in {self}: that is the zero ideal, and {value} is nonzero"
                )
                return {}
            labels = self.module_generating_set()
            (principal,) = self._module_generator_values
            if principal == 0:
                assert value == 0, (
                    f"{value} has no coordinates in {self}: that is the zero ideal, and {value} is nonzero"
                )
                return {}
            coefficient = SageQQ(value / principal)
            assert coefficient.denominator() == 1, (
                f"{value} has no coordinates in {self}: it is {coefficient} times the generator "
                f"{principal}, and {coefficient} is not an integer"
            )
            integers = self.base_ring()
            return (
                {}
                if coefficient == 0
                else {labels[0]: _owned_engine_element(integers, SageZZ(coefficient))}
            )

        def _element_constructor_(self, value):
            if isinstance(value, self.element_class) and value.parent() is self:
                return value
            parent = element_parent(value)
            if parent is not None and parent in OwnedRings():
                candidate = _engine_element(parent, value)
            else:
                candidate = _engine_ring(self._fraction_field)(value)
            if candidate not in self:
                # Sage's element-construction protocol: a value outside the
                # parent is rejected with ``ValueError``.
                raise ValueError(f"{candidate} is not in {self}")
            return self.element_class(self, candidate)

        def __contains__(self, value) -> bool:
            if isinstance(value, self.element_class) and value.parent() is self:
                return True
            parent = element_parent(value)
            match parent:
                case _ if parent is not None and parent in OwnedRings():
                    candidate = _engine_element(parent, value)
                case _ if value in _engine_ring(self._fraction_field):
                    candidate = _engine_ring(self._fraction_field)(value)
                case _:
                    return False
            if _engine_ring(self.base_ring()) is SageZZ:
                principal = _zz_fractional_generator(self._module_generator_values)
                if principal == 0:
                    return candidate == 0
                return SageQQ(candidate / principal).denominator() == 1
            return bool(
                _engine_component_vector(_order_coordinate_vector(self.base_ring(), candidate))
                in _integer_coordinate_submodule(self)
            )

        def zero(self):
            return self(self._fraction_field.zero())

        def an_element(self):
            if self._module_generator_values:
                return self(self._module_generator_values[0])
            return self.zero()

        def fraction_field(self):
            return self._fraction_field

        def ring(self):
            r"""Return the coefficient ring ``R`` of this fractional ideal."""
            return self.base_ring()

        def ideal_generators(self):
            r"""Return the selected generators of this fractional ideal."""
            return self.module_generators()

        def scalar_multiple(self, scalar, element):
            if element.parent() is not self:
                element = self(element)
            scalar = self.base_ring()(scalar)
            value = (
                _engine_element(self.base_ring(), scalar)
                * element._inclusion_value()
            )
            return self.element_class(self, value)

        def is_principal(self) -> bool:
            if _engine_ring(self.base_ring()) is SageZZ:
                return True
            return _principal_generator_from_order_values(
                self.base_ring(),
                self._module_generator_values,
            ) is not None

        def projectivity_decision(self) -> bool:
            ring = _engine_ring(self.base_ring())
            if ring is SageZZ:
                return True
            return bool(ring.is_maximal()) or self.is_principal()

        def principal_generator(self):
            r"""Return ``a`` with ``I=aR`` when this ideal is principal."""
            assert self.is_principal(), f"{self} is not principal"
            if _engine_ring(self.base_ring()) is SageZZ:
                return _owned_engine_element(self.fraction_field(),
                    _zz_fractional_generator(self._module_generator_values)
                )
            return _owned_engine_element(self.fraction_field(),
                _principal_generator_from_order_values(
                    self.base_ring(),
                    self._module_generator_values,
                )
            )

        def inverse(self):
            r"""Return ``I^{-1}={x in K : xI subseteq R}`` for an invertible ideal."""
            if _engine_ring(self.base_ring()) is SageZZ:
                value = self.principal_generator()
                assert value != 0, f"{self} has no inverse: it is the zero ideal, and only nonzero fractional ideals are invertible"
                return self.base_ring().fractional_ideal(value**-1)
            assert any(value != 0 for value in self._module_generator_values), (
                f"{self} has no inverse: it is the zero ideal, and only nonzero fractional ideals are invertible"
            )
            return _inverse_order_fractional_ideal(self)

        def __invert__(self):
            r"""Return the inverse fractional ideal ``I^{-1}``."""
            return self.inverse()

        def sum(self, other):
            r"""Return ``I+J`` inside the common fraction field."""
            assert self.base_ring() is other.base_ring(), (
                f"the sum {self} + {other} is not defined: both must be fractional ideals of one ring, "
                f"but they are over {self.base_ring()} and {other.base_ring()}"
            )
            other = _in_fraction_field(self.base_ring(), other)
            field = self.fraction_field()
            values = tuple(
                _owned_engine_element(field, value)
                for value in (
                    self._module_generator_values
                    + other._module_generator_values
                )
            )
            return self.base_ring().fractional_ideal(*values)

        def __add__(self, other):
            r"""Return the sum fractional ideal ``I+J``."""
            if other not in FractionalIdeals(self.base_ring()) and other not in CommutativeIdeals(self.base_ring()):
                return NotImplemented
            return self.sum(other)

        def intersection(self, other):
            r"""Return ``I intersect J`` inside the common fraction field."""
            assert self.base_ring() is other.base_ring(), (
                f"the intersection of {self} and {other} is not defined: both must be fractional ideals "
                f"of one ring, but they are over {self.base_ring()} and {other.base_ring()}"
            )
            other = _in_fraction_field(self.base_ring(), other)
            if _engine_ring(self.base_ring()) is SageZZ:
                field = self.fraction_field()
                left = self.principal_generator()
                right = other.principal_generator()
                if left == field.zero() or right == field.zero():
                    return self.base_ring().fractional_ideal(field.zero())
                ratio = _engine_element(field, left / right)
                numerator = _owned_engine_element(field, abs(ratio.numerator()))
                denominator = _owned_engine_element(field, ratio.denominator())
                return self.base_ring().fractional_ideal(left * denominator, right * numerator)
            integer_submodule = _integer_coordinate_submodule(self).intersection(
                _integer_coordinate_submodule(other)
            )
            values = _order_integer_submodule_values(
                self.base_ring(), integer_submodule
            )
            return _fractional_ideal_from_order_values(self.base_ring(), values)

        def __mul__(self, other):
            r"""Return the product fractional ideal ``IJ``."""
            if other not in FractionalIdeals(self.base_ring()) and other not in CommutativeIdeals(self.base_ring()):
                return NotImplemented
            other = _in_fraction_field(self.base_ring(), other)
            if _engine_ring(self.base_ring()) is SageZZ:
                return self.base_ring().fractional_ideal(
                    self.principal_generator() * other.principal_generator()
                )
            values = tuple(
                left * right
                for left in self._module_generator_values
                for right in other._module_generator_values
            )
            return _fractional_ideal_from_order_values(self.base_ring(), values)

        def _repr_(self):
            listed = ", ".join(str(value) for value in self._module_generator_values)
            return f"Fractional ideal ({listed}) of {self.base_ring()}"


def _regular_module_coefficient(regular_module, element):
    r"""The scalar ``r`` with ``element = r * 1`` in a rank-one regular module."""
    (label,) = tuple(regular_module.module_generating_set())
    return element.to_vector()(label)


def _fraction_field_value(fractional_ideal, element):
    r"""The element of ``Frac(R)`` that an element of a fractional ideal is."""
    embedded = fractional_ideal.inclusion()(element).underlying_element()
    return _regular_module_coefficient(
        fractional_ideal.fraction_field().regular_module(), embedded
    )


def _in_fraction_field(ring, ideal):
    r"""``ideal`` as a fractional ideal of ``ring``; an integral ideal is extended along ``R -> Frac(R)``."""
    if ideal in FractionalIdeals(ring):
        return ideal
    assert ideal in CommutativeIdeals(ring), f"{ideal} is not an ideal or fractional ideal of {ring}"
    return CommutativeIdeals(ring).extension_to_fraction_field()(ideal)


class _FractionalIdealExtension(Functor):
    r"""``CommutativeIdeals(R) -> FractionalIdeals(R)``: an ideal as the ``R``-submodule of ``Frac(R)`` it spans."""

    _faithful = True

    def __init__(self, ideals) -> None:
        super().__init__(ideals, FractionalIdeals(ideals.base_ring()))

    def _apply_object(self, ideal):
        ring = ideal.base_ring()
        regular = ring.regular_module()
        return ring.fractional_ideal(
            *(
                _regular_module_coefficient(regular, ideal.inclusion()(generator))
                for generator in ideal.module_generators()
            )
        )

    def _apply_morphism(self, morphism):
        domain_ideal = morphism.domain()
        codomain_ideal = morphism.codomain()
        source = self.object_image(domain_ideal)
        target = self.object_image(codomain_ideal)
        codomain_regular = codomain_ideal.base_ring().regular_module()

        def image(label):
            value = _fraction_field_value(source, source.module_generator(label))
            moved = codomain_ideal.inclusion()(morphism(domain_ideal(value)))
            return target(_regular_module_coefficient(codomain_regular, moved))

        return source.module_category().Mor(source, target)(
            {label: image(label) for label in source.module_generating_set()}
        )

    def _repr_(self) -> str:
        return f"Extension of ideals of {self.domain().base_ring()} to fractional ideals"


@cached_function
def _fraction_field_as_module(base_ring):
    r"""Return ``Frac(R)`` restricted to an ``R``-module along ``R -> Frac(R)``."""

    ring = _owned_ring(base_ring)
    scalar_map = ring.fraction_field_map()
    field = scalar_map.codomain()
    return field.regular_module().restrict_scalars(scalar_map)


def _fractional_ideal_inclusion(ideal):
    r"""The inclusion of a fractional ideal into ``Frac(R)`` read as an ``R``-module.

    An ``R``-submodule of ``K`` includes into ``K`` read over ``R``, so the
    map is linear and injective by that construction.  An element of ``K``
    lies in the ideal exactly when its value does, and then that value is its
    preimage.
    """
    target = _fraction_field_as_module(ideal.base_ring())
    extension_module = target.module_over_extension()
    (unit_label,) = tuple(extension_module.module_generating_set())
    unit = extension_module.module_generator(unit_label)

    def include(element):
        scalar = _owned_engine_element(target.extension_ring(), element._inclusion_value())
        return target.wrap(extension_module.scalar_multiple(scalar, unit))

    def preimage(element):
        if element.parent() is not target:
            element = target(element)
        value = extension_module.framing_morphism().lift(element.underlying_element())(unit_label)
        match value in ideal:
            case False:
                return None
            case True:
                return ideal(value)

    return ideal.Mono(target)._from_constructed_embedding(
        include,
        lift=preimage,
        lift_is_section=True,
    )


def _fraction_field_backend_value(base_ring, value):
    r"""Cross a preamble/internal scalar to the private fraction-field engine."""
    ring = _owned_ring(base_ring)
    field = ring.fraction_field()
    engine_field = _engine_ring(field)
    value_parent = element_parent(value)
    if value_parent in OwnedRings():
        return engine_field(_engine_element(value_parent, value))
    return engine_field(value)


def _zz_fractional_generator(module_generator_values):
    integers = _owned_integers()
    values = tuple(
        SageQQ(_fraction_field_backend_value(integers, value))
        for value in module_generator_values
    )
    if not values or all(value == 0 for value in values):
        return SageQQ.zero()
    denominator = reduce(
        lambda current, value: current.lcm(value.denominator()),
        values,
        SageZZ.one(),
    )
    integral_ideal = SageZZ.ideal(
        tuple(SageZZ(denominator * value) for value in values)
    )
    return SageQQ(integral_ideal.gen()) / denominator


def _order_coordinate_vector(base_ring, value):

    ring = _owned_ring(base_ring)
    rationals = _owned_rationals()
    backend_value = _fraction_field_backend_value(ring, value)
    return tensor.vector(
        rationals,
        tuple(
            _owned_engine_element(rationals, SageQQ(coefficient))
            for coefficient in backend_value.vector()
        ),
    )


def _integer_coordinate_submodule(ideal):
    r"""Materialize ``Res_ZZ^O(I)`` inside ``K``'s rational coordinate space."""
    return _integer_coordinate_submodule_from_values(
        ideal.base_ring(),
        ideal._module_generator_values,
    )


def _integer_coordinate_submodule_from_values(base_ring, module_generator_values):
    r"""Materialize the underlying integer lattice from selected ``O``-generators."""
    from sage.modules.free_module import span

    ring = _owned_ring(base_ring)
    order = _engine_ring(ring)
    field = _engine_ring(ring.fraction_field())
    rows = [
        _order_coordinate_vector(
            ring,
            field(order_basis) * _fraction_field_backend_value(ring, value),
        )
        for value in module_generator_values
        for order_basis in order.basis()
    ]
    if not rows:
        rationals = _owned_rationals()
        rows = [tensor.vector(rationals, [rationals.zero()] * int(order.module_rank()))]
    return span([_engine_component_vector(row) for row in rows], SageZZ)


def _order_integer_submodule_values(base_ring, integer_submodule):
    ring = _owned_ring(base_ring)
    field = _engine_ring(ring.fraction_field())
    return tuple(
        field(row) for row in integer_submodule.basis_matrix().rows()
    )


def _fractional_ideal_object(ring, fraction_field, values, *, projective=False):
    r"""Return the fractional ideal spanned by ``values`` in ``fraction_field``."""
    categories = [FractionalIdeals(ring), Modules(ring).FinitelyGenerated()]
    match projective:
        case True:
            categories.append(Modules(ring).Projective())
        case False:
            pass
    return _object_of(
        Cat().meet(categories),
        base_ring=ring,
        fraction_field=fraction_field,
        module_generator_values=values,
    )


def _fractional_ideal_from_order_values(base_ring, module_generator_values):
    ring = _owned_ring(base_ring)
    order = _engine_ring(ring)
    values = tuple(
        _fraction_field_backend_value(ring, value)
        for value in module_generator_values
    )

    projective = bool(order.is_maximal()) or (
        _principal_generator_from_order_values(ring, values) is not None
    )
    return _fractional_ideal_object(
        ring,
        ring.fraction_field(),
        values,
        projective=projective,
    )


def _principal_generator_from_order_values(base_ring, module_generator_values):
    r"""Return a generator of an order fractional ideal from its selected generators."""

    ring = _owned_ring(base_ring)
    order = _engine_ring(ring)
    field = _engine_ring(ring.fraction_field())
    basis_values = _order_integer_submodule_values(
        ring,
        _integer_coordinate_submodule_from_values(ring, module_generator_values),
    )
    if not basis_values:
        return field.zero()

    rationals = _owned_rationals()
    rank = int(order.module_rank())
    # The map QQ^rank -> K sending e_j to the j-th basis element of the order,
    # written in the power basis of K.
    basis_map_space = rationals.matrix_space(rank, rank)
    power_basis = basis_map_space.codomain()
    power_basis_labels = tuple(power_basis.module_generating_set())

    def power_basis_coordinates(value):
        return power_basis.linear_combination(
            {
                label: _owned_engine_element(rationals, SageQQ(coefficient))
                for label, coefficient in zip(power_basis_labels, field(value).vector(), strict=True)
                if coefficient
            }
        )

    basis_map = basis_map_space(
        tuple(power_basis_coordinates(basis_element) for basis_element in order.basis())
    )
    denominator = SageZZ.one()
    for value in basis_values:
        target = power_basis_coordinates(value)
        coordinates = basis_map.domain()(basis_map.solve_right(target)).to_vector()
        for label in coordinates.support().domain():
            denominator = denominator.lcm(
                _engine_element(rationals, coordinates(label)).denominator()
            )

    integral_values = tuple(
        order(denominator * value) for value in basis_values
    )
    integral_ideal = order.ideal(integral_values)
    if not bool(integral_ideal.is_principal()):
        return None
    reduced = tuple(integral_ideal.gens_reduced())
    if not reduced:
        return field.zero()
    return field(reduced[0]) / denominator


def _inverse_order_fractional_ideal(ideal):
    r"""Return ``(R:I)`` by intersecting ``g^{-1}R`` for an ``R``-generating set."""
    ring = ideal.base_ring()
    field = _engine_ring(ideal.fraction_field())
    nonzero_values = tuple(
        field(value)
        for value in ideal._module_generator_values
        if field(value) != 0
    )
    assert nonzero_values, (
        f"{ideal} has no inverse: it is the zero ideal, and only nonzero fractional ideals are invertible"
    )

    inverse_integer_submodule = _integer_coordinate_submodule(
        ring.fractional_ideal(nonzero_values[0] ** -1)
    )
    for value in nonzero_values[1:]:
        inverse_integer_submodule = inverse_integer_submodule.intersection(
            _integer_coordinate_submodule(ring.fractional_ideal(value**-1))
        )
    values = _order_integer_submodule_values(ring, inverse_integer_submodule)
    return _fractional_ideal_from_order_values(
        ring,
        values,
    )


def _fractional_ideal_from_backend(base_ring, backend):
    ring = _owned_ring(base_ring)
    assert _engine_ring(ring) is SageZZ
    principal = SageQQ(backend)
    values = () if principal == 0 else (principal,)
    return _fractional_ideal_object(
        ring,
        _owned_rationals(),
        values,
        projective=True,
    )


@cached_function
def _fractional_ideal(ring, values):
    r"""Return the one fractional ideal of ``R`` spanned by this family.

    A fractional ideal is determined by its ring and its elements, so two
    calls that write the same family name one submodule and get one object.
    The key is the family as written, which is what the ring and quotient and
    localization constructors are also interned on: ``(2)`` and ``(2,4)`` span
    one module of the integers but reach two entries here, and they compare
    equal afterwards.
    """
    engine = _engine_ring(ring)
    if engine is SageZZ:
        return _fractional_ideal_from_backend(ring, _zz_fractional_generator(values))
    assert ring in OwnedOrders(), (
        f"fractional ideals of {ring} are constructed here only for ZZ and for orders in number fields, "
        f"but {ring} is in {ring.category()}"
    )
    field_values = tuple(
        _fraction_field_backend_value(ring, value) for value in values
    )
    return _fractional_ideal_from_order_values(ring, field_values)


__all__ = [
    "FractionalIdeals",
]
