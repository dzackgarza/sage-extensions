r"""Native realizations of modules whose additive group is an owned ring.

The native ring is already a complete additive group before its R-module
structure is constructed. This representation supplies the scalar action to
Modules(R), not a category label in place of that action. Over itself its
chosen frame is F_R({0})->R, e_0 |-> 1; the inverse coordinate is r |-> r e_0.
Their composites are identities by the two unit laws, so this is a free
rank-one module, including over the zero ring. No change of scalar object
or second authoritative ring is involved.
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.modules.pure.modules import (
    Modules,
    _fix_selected_module_resolution,
)
from sage_extensions.categories.modules.framed.framed_free_modules import FramedFreeModules
from sage_extensions.refine import refine
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.sets.set_categories import Sets


class _NativeModuleFrame:
    r"""A native realization of an actual framed module, with inverse coordinates.

    The model is already constructed, with its free framing source and any
    relations.  Images of its generators and inverse coordinates identify
    it with the native realization.  Normalization is the model's, so a
    word quotient is not mistaken for the free module on its monomials.

    ``injective`` states whether the map from the source is also injective.
    When it is not, the source only spans, and the inverse coordinates of an
    element are those of one chosen preimage.
    """

    def __init__(self, source, images, coordinates, *, injective=True):
        assert source.has_selected_module_resolution(), (
            f"{source} cannot index a generating family: it must be a module with a chosen "
            f"generating family over {source.base_ring()}, but it is in {source.category()}"
        )
        self._source = source
        self._images = images
        self._coordinates = coordinates
        self._injective = injective

    def source(self):
        return self._source

    def image(self, label):
        return self._images(label)

    def coefficients(self, element):
        source = self.source()
        return source.framing_morphism().lift(source.linear_combination(self._coordinates(element)))

    def is_basis(self):
        r"""Whether the source is free and its map onto the module is also injective."""
        return self._injective and self._source in FramedFreeModules(self._source.base_ring())


class _NativeModuleBasis(_NativeModuleFrame):
    r"""The free case of the native frame, on an actual chosen basis."""

    def __init__(self, source, images, coordinates):
        assert source in FramedFreeModules(source.base_ring()), (
            f"{source} cannot index a basis: it must be a free module with a chosen basis "
            f"over {source.base_ring()}, but it is in {source.category()}"
        )
        super().__init__(source, images, coordinates)

    def coordinates(self, element):
        r"""The coordinates ``{i: c_i}`` of ``element = sum_i c_i b_i``, unique on a basis."""
        return self._coordinates(element)


def _power_module_basis(coefficient_ring, degree, power, coordinates):
    r"""The basis ``1, a, ..., a^{d-1}`` of ``k[x]/(p)`` over ``k``, ``a`` the class of ``x``.

    Let ``p`` in ``k[x]`` have degree ``d`` and unit leading coefficient.
    Division with remainder by ``p`` writes every class of ``k[x]/(p)``
    uniquely as ``sum_{i<d} c_i x^i``, so the powers ``a^i`` with ``i < d``
    are a ``k``-basis of ``k[x]/(p)`` along the coefficient map.

    ``power(i)`` is ``a^i`` in the ring, and ``coordinates(s)`` the ``d``
    remainder coefficients of ``s`` in the selected realization of that
    ring, raised here into ``coefficient_ring``.  Callers are the ring
    adapters whose realization performs that division.
    """
    labels = Sets.Δ[degree - 1]

    def basis_coordinates(element):
        # Polynomial and quotient representatives commonly omit trailing
        # zero coefficients (e.g. ``1`` is represented by ``[1]`` even when
        # the quotient basis has degree three). Missing high coordinates are
        # zero, not a malformed basis expansion. Reject only a backend that
        # returns more coefficients than the selected remainder degree.
        values = tuple(coordinates(element))
        # Some native quotient realizations retain explicit trailing zeros
        # in their coefficient list. These do not contribute to the class
        # and must be removed before checking the selected remainder degree;
        # never truncate a nonzero high coefficient, which would change the
        # represented element rather than normalize its coordinates.
        while len(values) > int(degree) and values[-1] == 0:
            values = values[:-1]
        assert len(values) <= int(degree), (
            f"the selected power-basis coordinates of {element} have length {len(values)}, "
            f"exceeding the quotient degree {degree}"
        )
        return {
            label: _owned_engine_element(coefficient_ring, coefficient)
            for label, coefficient in zip(labels, values)
            if coefficient != 0
        }

    return _NativeModuleBasis(
        coefficient_ring.free_module(labels),
        lambda exponent: power(int(exponent)),
        basis_coordinates,
    )


class _RingModulePresentation:
    r"""The native additive-group realization and its specified scalar action.

    Private constructor datum accepted only at Modules._call_. Suppliers are
    the ring computation adapters: the product, unit and scalar action must
    be the primitive operations of that ring, before its algebra classifier
    is formed. The ring-product classifier is derived from these operations,
    never supplied by a different constructor or inferred by sampling.

    The module and algebra owners may inspect this datum to retain the native
    realization of that exact product. A different multiplication on this
    same module takes the ordinary stronger-object construction instead.
    """

    def __init__(self, group, scalar_ring, product, unit, scalar_action, *, basis=None):
        self._group = group
        self._ring = scalar_ring
        self._product = product
        self._unit = unit
        self._scalar_action = scalar_action
        self._basis = basis

    def module(self):
        return self._group

    def base_ring(self):
        return self._ring

    def unit(self):
        return self._unit

    def scalar_multiple(self, scalar, element):
        return self.module()(self._scalar_action(self.base_ring()(scalar), self.module()(element)))

    def is_regular(self):
        return self.module() is self.base_ring()

    def construct(self, category):
        module = self.module()
        assert category.base_ring() is self.base_ring(), (
            f"{module} cannot be made an object of {category}: its scalar action is by "
            f"{self.base_ring()}, not by {category.base_ring()}"
        )
        assert module.base_ring() is self.base_ring(), (
            f"{module} cannot be made an {self.base_ring()}-module: it is already a module over "
            f"{module.base_ring()}"
        )
        assert Modules.ParentMethods._native_module_presentation(module) is None, (
            f"{module} already has a scalar action by {self.base_ring()}; it cannot be given a second one"
        )
        Modules.ParentMethods._retain_native_module_presentation(module, self)
        if self.is_regular():
            assert self._basis is None, (
                f"{module} is the regular module over itself; its basis is {{1}}, and no other basis may be given"
            )
            free = self.base_ring().free_module(1)
            label = next(iter(free.module_generating_set()))
            self._basis = _NativeModuleBasis(free, lambda _: self.unit(), lambda value: {label: module(value)})
        free_placement = None
        if self._basis is not None:
            source = self._basis.source()
            assert source.base_ring() is self.base_ring(), (
                f"the basis of {module} is indexed by {source}, a module over {source.base_ring()}, "
                f"but {module} is a module over {self.base_ring()}"
            )
            labels = source.module_generating_set()
            _fix_selected_module_resolution(
                module,
                self.base_ring(),
                labels,
                self._basis.image,
                lambda: source,
            )
            match self._basis.is_basis():
                case True:
                    placement = FramedFreeModules(self.base_ring())
                    if labels.cardinality().is_finite():
                        placement = placement.FinitelyGenerated()
                    free_placement = placement
        # Register the selected resolution before exposing the module to any
        # category realization hooks. The factory is lazy, so this retains the
        # framing data without constructing its augmentation Mor. First place
        # the module in Modules(R): its framing augmentation is an R-module Mor
        # whose endpoint checks require this membership. Only then add the
        # selected free-module refinement, whose hooks may request that Mor.
        match module in category:
            case True:
                pass
            case False:
                refine(module, category)
        if free_placement is not None and module not in free_placement:
            refine(module, free_placement)
        # Do not materialize R -> End_Ab(U(module)) here: building that
        # endomorphism ring can itself request module-Mor objects and recurse
        # into construction. Modules.scalar_action() constructs its typed map
        # lazily against the current canonical End parent.
        return module

    def module_basis(self):
        return self._basis

    def coefficients(self, element):
        assert self._basis is not None, (
            f"cannot take coordinates of {element} in {self.module()}: no basis of {self.module()} "
            f"over {self.base_ring()} was chosen"
        )
        return self._basis.coefficients(self.module()(element))

    @cached_method
    def multiplication(self):
        module = self.module()
        tensor = Modules(self.base_ring()).tensor_product((module, module))
        # The ring's product and the scalar action come from one ring datum,
        # so distributivity and compatibility with scalars are construction
        # data: the classifier is linear with no premise.
        mor = tensor.module_category().Mor(tensor, module)
        product = self._product
        match module.has_selected_module_resolution():
            case True:
                return mor._from_bilinear_evaluation(product, premises=())
            case False:
                return mor._from_constructed_element_map(
                    lambda value: tensor.underlying_set().evaluate(
                        tensor(value).underlying_element(),
                        module,
                        product,
                    )
                )
