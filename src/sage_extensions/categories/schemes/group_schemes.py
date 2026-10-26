r"""Affine group schemes and their actions over an affine base.

A group scheme over ``S`` is a scheme ``G/S`` with multiplication, unit, and
inverse scheme morphisms satisfying the group diagrams.  An action on ``X/S``
is a morphism ``G x_S X -> X`` satisfying the associativity and unit diagrams;
equivariant morphisms are exactly the scheme maps for which the usual action
square commutes.  This is the scheme-valued notion of Stacks Project, Tags
022S and 022Z.  The affine specialization composes the common internal-group
owner ``Grp(AffineSchemes(R))`` and retains its actual structure maps.  It is
intentionally distinct from ``GObjects(G, Schemes(R))``:
the latter is an action of an abstract group through a functor ``BG -> Sch_R``.
"""

from sage.categories.morphism import Morphism
from sage.misc.classcall_metaclass import typecall

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    CategoryPacketMethods,
    MorCategoryConstruction,
    _precomposable,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.group.g_objects import Grp
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    _own_ring,
)
from sage_extensions.categories.schemes.schemes import (
    Schemes,
    _affine_morphism_from_pullback,
)
from sage_extensions.owned_category import _object_of
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class AffineGroupSchemeMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return AffineGroupSchemeMor


class AffineGroupSchemes(OwnedCategoryOverBaseRing):
    r"""Affine group schemes over ``Spec(R)``, represented by their structure maps."""

    def super_categories(self):
        return [Grp(Schemes(self.base_ring()).Affine())]

    def _repr_object_names(self):
        return f"affine group schemes over {self.base_ring()}"

    def _call_(self, scheme, multiplication, unit, inverse):
        internal_group = Grp(Schemes(self.base_ring()).Affine())(
            scheme,
            multiplication,
            unit,
            inverse,
        )
        return _object_of(
            self,
            _engine=(self, _AffineGroupSchemeEngine, None),
            internal_group_object=internal_group,
        )

    def roots_of_unity(self, degree: int):
        r"""Return the affine group scheme ``mu_degree`` over this base."""
        return _roots_of_unity_group_scheme(self.base_ring(), degree)

    def additive_group(self):
        r"""Return the additive affine group scheme over this base."""
        return _additive_group_scheme(self.base_ring())

    def multiplicative_group(self):
        r"""Return the multiplicative affine group scheme over this base."""
        return _multiplicative_group_scheme(self.base_ring())

    def an_object(self):
        return self.roots_of_unity(1)

    _MorCategory = AffineGroupSchemeMorCategoryConstruction


class _AffineGroupSchemeEngine:
    r"""One affine group scheme with actual scheme-theoretic structure morphisms."""

    def __init__(self, internal_group_object, **rest) -> None:
        self._internal_group_object = internal_group_object
        super().__init__(**rest)
        base = self.category().base_ring()
        if internal_group_object not in Grp(Schemes(base).Affine()):
            raise TypeError(
                f"{internal_group_object} is not a group object in affine schemes over {base}, "
                f"so it does not define an affine group scheme over {base}; it is in "
                f"{internal_group_object.category()}"
            )

    def internal_group_object(self):
        return self._internal_group_object

    def underlying_category(self):
        r"""The affine-scheme category in which this is an internal group."""
        return self.internal_group_object().underlying_category()

    def underlying_object(self):
        r"""The affine scheme underlying this internal group object."""
        return self.internal_group_object().underlying_object()

    def square_construction(self):
        r"""The selected product ``G x_S G`` retained by the internal group."""
        return self.internal_group_object().square_construction()

    def terminal_construction(self):
        r"""The selected terminal affine scheme retained by the internal group."""
        return self.internal_group_object().terminal_construction()

    def scheme(self):
        return self.internal_group_object().underlying_object()

    underlying_scheme = scheme

    def base_ring(self):
        return self.category().base_ring()

    def base_scheme(self):
        return self.unit_morphism().domain()

    def multiplication(self):
        return self.internal_group_object().multiplication()

    def unit_morphism(self):
        return self.internal_group_object().unit_morphism()

    def inverse_morphism(self):
        return self.internal_group_object().inverse_morphism()

    def actions(self):
        return AffineGroupSchemeActions(self)

    def Mor(self, target):
        return self.category().Mor(self, target)

    def _repr_(self):
        return f"Affine group scheme on {self.scheme()}"


class AffineGroupSchemeMorphism(Morphism):
    r"""A scheme morphism preserving affine group-scheme multiplication."""

    def __init__(self, parent, arrow) -> None:
        Morphism.__init__(self, parent)
        self._arrow = arrow

    def underlying_arrow(self):
        return self._arrow

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        return other.domain().Mor(self.codomain())(
            self.underlying_arrow() * other.underlying_arrow()
        )

    def _repr_(self):
        return f"Group-scheme morphism from {self.domain()} to {self.codomain()}"


class AffineGroupSchemeMor(CategoricalMor):
    r"""Morphisms of affine group schemes over one represented base."""

    Element = AffineGroupSchemeMorphism

    def _element_constructor_(self, arrow):
        source = self.domain()
        target = self.codomain()
        internal = source.internal_group_object().Mor(
            target.internal_group_object()
        )(arrow)
        return self.element_class(self, internal.underlying_arrow())

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity morphism from {self.domain()} to the different group "
                f"scheme {self.codomain()}; the identity exists only when domain and codomain agree"
            )
        return self(self.domain().scheme().categorical_identity_morphism())


_ACTION_CATEGORIES = {}


class AffineGroupSchemeActionMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return AffineGroupSchemeActionMor


class AffineGroupSchemeActions(CategoryPacketMethods, OwnedCategory):
    r"""Affine schemes over the same base with an action of one affine group scheme."""

    @staticmethod
    def __classcall__(cls, group_scheme):
        key = id(group_scheme)
        cached = _ACTION_CATEGORIES.get(key)
        if cached is not None and cached.group_scheme() is group_scheme:
            return cached
        category = typecall(cls, group_scheme)
        _ACTION_CATEGORIES[key] = category
        return category

    def __init__(self, group_scheme) -> None:
        self._group_scheme = group_scheme
        OwnedCategory.__init__(self)

    def group_scheme(self):
        return self._group_scheme

    def super_categories(self):
        return [self.group_scheme().internal_group_object().actions()]

    def _repr_object_names(self):
        return f"affine schemes acted on by {self.group_scheme()}"

    def _call_(self, scheme, action_morphism):
        internal_action = self.group_scheme().internal_group_object().actions()(
            scheme,
            action_morphism,
        )
        return _object_of(
            self,
            _engine=(self, _AffineGroupSchemeActionEngine, None),
            internal_action=internal_action,
        )

    def an_object(self):
        group = self.group_scheme()
        base = group.base_scheme()
        product = base.scheme_category().product((group.scheme(), base))
        action = product.projection(1)
        return self(base, action)

    _MorCategory = AffineGroupSchemeActionMorCategoryConstruction


class _AffineGroupSchemeActionEngine:
    r"""An affine ``G``-scheme represented by ``a: G x_S X -> X``."""

    def __init__(self, internal_action, **rest) -> None:
        self._internal_action = internal_action
        super().__init__(**rest)
        group = self.category().group_scheme()
        self._group_scheme = group
        base = group.base_ring()
        if internal_action.group_object() is not group.internal_group_object():
            raise ValueError(
                f"the action {internal_action} is an action of {internal_action.group_object()}, "
                f"not of the group scheme {group}"
            )
        if internal_action.underlying_object() not in Schemes(base).Affine():
            raise TypeError(
                f"the scheme {internal_action.underlying_object()} acted on by {group} must be an "
                f"affine scheme over {base}, but it is in "
                f"{internal_action.underlying_object().category()}"
            )
        if internal_action.underlying_object().base_scheme() is not group.base_scheme():
            raise ValueError(
                f"the group scheme {group} lies over {group.base_scheme()}, but the scheme it acts "
                f"on, {internal_action.underlying_object()}, lies over "
                f"{internal_action.underlying_object().base_scheme()}; they must have the same base"
            )

    def internal_action(self):
        return self._internal_action

    def group_object(self):
        r"""The internal group object whose action this affine action refines."""
        return self.internal_action().group_object()

    def underlying_object(self):
        r"""The affine scheme acted on, as the underlying internal-action object."""
        return self.internal_action().underlying_object()

    def action_product_construction(self):
        r"""The selected product ``G x_S X`` retained by the internal action."""
        return self.internal_action().action_product_construction()

    def scheme(self):
        return self.internal_action().underlying_object()

    underlying_scheme = scheme

    def group_scheme(self):
        return self._group_scheme

    def action_morphism(self):
        return self.internal_action().action_morphism()

    def Mor(self, target):
        return self.category().Mor(self, target)

    def _repr_(self):
        return f"{self.scheme()} with action of {self.group_scheme()}"


class AffineGroupSchemeEquivariantMorphism(Morphism):
    r"""A scheme morphism commuting with one affine group-scheme action."""

    def __init__(self, parent, arrow) -> None:
        Morphism.__init__(self, parent)
        self._arrow = arrow

    def underlying_arrow(self):
        return self._arrow

    def __mul__(self, other):
        if not _precomposable(self, other):
            return NotImplemented
        return other.domain().Mor(self.codomain())(
            self.underlying_arrow() * other.underlying_arrow()
        )

    def _repr_(self):
        return f"Equivariant morphism from {self.domain()} to {self.codomain()}"


class AffineGroupSchemeActionMor(CategoricalMor):
    r"""Equivariant morphisms between two actions of the same affine group scheme."""

    Element = AffineGroupSchemeEquivariantMorphism

    def __init__(self, family, domain, codomain) -> None:
        if domain.group_scheme() is not codomain.group_scheme():
            raise ValueError(
                f"equivariant morphisms from {domain} to {codomain} need one acting group scheme, "
                f"but they are acted on by {domain.group_scheme()} and {codomain.group_scheme()}"
            )
        CategoricalMor.__init__(self, family, domain, codomain)

    def _element_constructor_(self, arrow):
        internal = self.domain().internal_action().Mor(
            self.codomain().internal_action()
        )(arrow)
        return self.element_class(self, internal.underlying_arrow())

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity morphism from {self.domain()} to the different scheme "
                f"with action {self.codomain()}; the identity exists only when domain and codomain agree"
            )
        return self(self.domain().scheme().categorical_identity_morphism())


def _additive_group_scheme(base_ring):
    r"""Return the additive group scheme with coordinate Hopf algebra R[x]."""
    base = _own_ring(base_ring)
    algebra = base.polynomial_ring("x")
    x = algebra.algebra_generator("x")
    scheme = algebra.affine_spectrum(base_ring=base)
    square = scheme.scheme_category().product((scheme, scheme))
    square_algebra = square.coordinate_algebra()
    first_pullback = square.projection(0).coordinate_algebra_morphism()
    second_pullback = square.projection(1).coordinate_algebra_morphism()
    multiplication = _affine_morphism_from_pullback(
        square,
        scheme,
        algebra.Mor(square_algebra)(
            {"x": first_pullback(x) + second_pullback(x)}
        ),
    )
    base_scheme = scheme.base_scheme()
    unit = _affine_morphism_from_pullback(
        base_scheme,
        scheme,
        algebra.Mor(base)({"x": base.zero()}),
    )
    inverse = _affine_morphism_from_pullback(
        scheme,
        scheme,
        algebra.Mor(algebra)({"x": -x}),
    )
    return AffineGroupSchemes(base)(scheme, multiplication, unit, inverse)


def _multiplicative_group_scheme(base_ring):
    r"""Return the multiplicative group scheme with coordinate Hopf algebra R[u,u^-1]."""
    base = _own_ring(base_ring)
    algebra = base.laurent_polynomial_ring("u")
    u = algebra.algebra_generator("u")
    scheme = algebra.affine_spectrum(base_ring=base)
    square = scheme.scheme_category().product((scheme, scheme))
    square_algebra = square.coordinate_algebra()
    first_pullback = square.projection(0).coordinate_algebra_morphism()
    second_pullback = square.projection(1).coordinate_algebra_morphism()
    multiplication = _affine_morphism_from_pullback(
        square,
        scheme,
        algebra.Mor(square_algebra)(
            {"u": first_pullback(u) * second_pullback(u)}
        ),
    )
    base_scheme = scheme.base_scheme()
    unit = _affine_morphism_from_pullback(
        base_scheme,
        scheme,
        algebra.Mor(base)({"u": base.one()}),
    )
    inverse = _affine_morphism_from_pullback(
        scheme,
        scheme,
        algebra.Mor(algebra)({"u": u**-1}),
    )
    return AffineGroupSchemes(base)(scheme, multiplication, unit, inverse)


def _roots_of_unity_group_scheme(base_ring, degree: int):
    r"""Return ``mu_degree = Spec(R[u]/(u^degree - 1))`` over ``Spec(R)``.

    The construction is valid over every represented commutative base ring;
    no primitive root of unity and no invertibility hypothesis on ``degree`` is
    imposed.  The multiplication, unit, and inverse are the actual scheme maps
    dual to ``u |-> u_1 u_2``, ``u |-> 1``, and ``u |-> u^(degree-1)``.
    """
    if degree < 1:
        raise ValueError(f"the group scheme mu_n of n-th roots of unity needs n >= 1, got n = {degree}")
    base = _own_ring(base_ring)
    presentation = base.polynomial_ring("u")
    u_presentation = presentation.algebra_generator("u")
    algebra = (presentation).quotient_by_relations((u_presentation**degree - presentation.one(),),
    )
    u = algebra.algebra_generator("u")
    scheme = (algebra).affine_spectrum(base_ring=base)
    square = scheme.scheme_category().product((scheme, scheme))
    square_algebra = square.coordinate_algebra()
    first_pullback = square.projection(0).coordinate_algebra_morphism()
    second_pullback = square.projection(1).coordinate_algebra_morphism()
    multiplication_pullback = algebra.Mor(square_algebra)(
        {"u": first_pullback(u) * second_pullback(u)}
    )
    multiplication = _affine_morphism_from_pullback(
        square,
        scheme,
        multiplication_pullback,
    )

    base_scheme = scheme.structure_morphism().codomain()
    unit_pullback = algebra.Mor(base)({"u": base.one()})
    unit = _affine_morphism_from_pullback(base_scheme, scheme, unit_pullback)
    inverse_pullback = algebra.Mor(algebra)({"u": u ** (degree - 1)})
    inverse = _affine_morphism_from_pullback(scheme, scheme, inverse_pullback)
    return AffineGroupSchemes(base)(scheme, multiplication, unit, inverse)
