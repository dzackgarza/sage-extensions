r"""Linearizations of projective line bundles under represented group actions.

A ``G``-linearization of a line bundle ``L`` over a ``G``-scheme is additional
data: isomorphisms ``lambda_g : g^*L -> L`` satisfying the cocycle.  Preserving
the isomorphism class of ``L`` does not select these maps.  For the standard
``O(d)`` on projective space, a projective-coordinate action canonically
identifies ``g^*O(d)`` with ``O(d)``; multiplying that identification by a
character gives the familiar character twists.

The induced *left* action on global sections is

``g . s = lambda_g((g^{-1})^* s)``.

The inverse is essential: pullback is contravariant.  The resulting section
space is constructed as the existing module over the group algebra, so
invariants and isotypic components are those of the common group-module owner.
"""

from sage.misc.cachefunc import cached_function, cached_method

from sage_extensions.categories.functors.group_actions import GroupActionFunctor
from sage_extensions.categories.group.g_objects import GObjects
from sage_extensions.categories.group.groups import OwnedGroups
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.schemes.ringed_spaces import QuasiCoherentSheaves
from sage_extensions.categories.schemes.schemes import (
    Schemes,
    _affine_morphism_from_pullback,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
    indexed_family,
)


class _ProjectiveActionFunctor(GroupActionFunctor):
    r"""Private realization data for one represented projective ``G``-action."""

    def __init__(
        self,
        acting_group,
        category,
        obj,
        action,
        *,
        coordinate_weights=None,
        local_automorphisms=None,
    ) -> None:
        self._acting_group = acting_group
        self._coordinate_weights = coordinate_weights
        self._local_automorphisms = local_automorphisms
        super().__init__(acting_group, category, obj, action)

    def acting_group(self):
        return self._acting_group

    def action_functor(self):
        return self

    def coordinate_weights(self):
        assert self._coordinate_weights is not None, (
            f"the action of {self.acting_group()} on {self} is not given by scalar weights on "
            "the homogeneous coordinates"
        )
        return self._coordinate_weights

    def local_automorphisms(self):
        assert self._local_automorphisms is not None, (
            f"the action of {self.acting_group()} on {self} is not given by automorphisms of "
            "its standard affine charts"
        )
        return self._local_automorphisms

    def local_automorphism(self, chart_index):
        return self.local_automorphisms()[chart_index]


def _line_bundle_scalar_morphism(line_bundle, scalar):
    r"""The QCoh endomorphism of ``line_bundle`` multiplying every local basis by ``scalar``."""

    sheaves = QuasiCoherentSheaves(line_bundle.scheme())
    local_maps = {}
    for index in line_bundle.gluing_datum().chart_index_set():
        module = line_bundle.local_module(index)
        label = next(iter(module.module_generating_set()))
        coefficient = module.base_ring()(scalar)
        local_maps[index] = module.module_category().Mor(module, module)(
            {
                label: module.scalar_multiple(
                    coefficient,
                    module.module_generator(label),
                )
            }
        )
    return sheaves.Mor(line_bundle, line_bundle)(local_maps)


def _line_bundle_scalar_isomorphism(line_bundle, scalar):
    r"""The scalar automorphism of a represented trivialized line bundle."""

    scalar = line_bundle.scheme().scheme_base_ring()(scalar)
    assert scalar.is_unit(), (
        f"multiplication by {scalar} is not an automorphism of {line_bundle}: "
        f"{scalar} is not a unit of {scalar.parent()}"
    )
    sheaves = QuasiCoherentSheaves(line_bundle.scheme())
    forward = _line_bundle_scalar_morphism(line_bundle, scalar)
    inverse = _line_bundle_scalar_morphism(line_bundle, scalar.inverse_of_unit())
    return sheaves.Core().Mor(line_bundle, line_bundle)(forward, inverse)


def _line_bundle_linearization(line_bundle, scheme_action, character):
    r"""Construct a standard projective linearization as a ``G``-object in ``QCoh(X)``.

    The private linearization class realizes the functor object; it does not
    define a category of all outputs of this construction.
    """

    from sage_extensions.categories.schemes.schemes import (
        ProductProjectiveSpaces,
        ProjectiveSpaces,
    )

    group = scheme_action.acting_group()
    scheme = scheme_action.action_functor().underlying_object()
    base = scheme.scheme_base_ring()
    assert scheme_action in GObjects(group, Schemes(base)), (
        f"cannot linearize {line_bundle} along {scheme_action}: a linearization needs an "
        f"action of {group} on the scheme {scheme}, and this is not a {group}-scheme"
    )
    match scheme:
        case _ if scheme in ProjectiveSpaces(base):
            assert line_bundle.projective_space() is scheme, (
                f"cannot linearize {line_bundle} along the action of {group} on {scheme}: the "
                f"line bundle lives on {line_bundle.projective_space()}, not on {scheme}"
            )
            engine = _ProjectiveLineBundleLinearization
        case _ if scheme in ProductProjectiveSpaces(base):
            assert line_bundle.projective_product() is scheme, (
                f"cannot linearize {line_bundle} along the action of {group} on {scheme}: the "
                f"line bundle lives on {line_bundle.projective_product()}, not on {scheme}"
            )
            engine = _ProductProjectiveLineBundleLinearization
        case _:
            assert False, (
                f"cannot linearize {line_bundle} on {scheme}: linearizations are implemented "
                "only on projective spaces and products of projective spaces"
            )

    return engine(line_bundle, scheme_action, character)


class _ProjectiveLineBundleLinearizationIsomorphism:
    r"""Private computation of one selected ``lambda_g : g^*L -> L``."""

    def __init__(self, linearization, group_element) -> None:
        self._linearization = linearization
        self._group_element = linearization.acting_group()(group_element)

    def linearization(self):
        return self._linearization

    def group_element(self):
        return self._group_element

    def pullback_morphism(self):
        return self.linearization().scheme_action_of(self.group_element())

    def domain(self):
        return self.linearization().line_bundle()

    def codomain(self):
        return self.linearization().line_bundle()

    def scalar(self):
        return self.linearization().character_value(self.group_element())

    def morphism(self):
        return _line_bundle_scalar_isomorphism(self.domain(), self.scalar())

    def inverse(self):
        return _ProjectiveLineBundleLinearizationIsomorphism(
            self.linearization(),
            self.group_element().inverse(),
        ).morphism()

    def _repr_(self):
        return (
            f"Linearization isomorphism for {self.group_element()} on "
            f"{self.linearization().line_bundle()} with scalar {self.scalar()}"
        )


class _EigensectionDivisorEngine:
    r"""Private realization data on a closed subscheme cut out by an eigensection."""

    def __init__(
        self,
        eigensection_linearization,
        eigensection_section,
        eigensection_character,
        **rest,
    ) -> None:
        self._eigensection_linearization = eigensection_linearization
        self._eigensection_section = eigensection_section
        self._eigensection_character = eigensection_character
        super().__init__(**rest)

    def linearization(self):
        return self._eigensection_linearization

    def section(self):
        return self._eigensection_section

    def character(self):
        return self._eigensection_character


class _ProjectiveLineBundleLinearization(GroupActionFunctor):
    r"""A character-twisted linearization of ``O(d)`` under a projective action."""

    def __init__(self, line_bundle, scheme_action, character, **rest) -> None:
        self._line_bundle = line_bundle
        self._scheme_action = scheme_action
        scheme = self.section_scheme()
        base = scheme.scheme_base_ring()
        scheme_action_functor = scheme_action.action_functor()
        group = scheme_action.acting_group()
        assert scheme_action in GObjects(group, Schemes(base)), (
            f"cannot linearize {line_bundle} along {scheme_action}: a linearization needs an "
            f"action of {group} on {scheme}, and this is not a {group}-scheme"
        )
        assert scheme_action_functor.underlying_object() is scheme, (
            f"cannot linearize {line_bundle} along the action of {group}: the group acts on "
            f"{scheme_action_functor.underlying_object()}, but the line bundle lives on {scheme}"
        )
        assert group.is_finite() is True, (
            f"cannot linearize {line_bundle} along the action of {group}: checking that the "
            "twist is a character is implemented only for finite groups, and this group is "
            "not known to be finite"
        )
        self._group = group
        self._character = character
        self._validate_character()
        def lift(group_element):
            scalar = base(character(group(group_element)))
            assert scalar.is_unit(), (
                f"the character does not take values in the units of {base}: it sends "
                f"{group_element} to {scalar}"
            )
            return _line_bundle_scalar_morphism(line_bundle, scalar)

        super().__init__(group, QuasiCoherentSheaves(scheme), line_bundle, lift)

    def line_bundle(self):
        return self._line_bundle

    underlying_line_bundle = line_bundle

    def projective_space(self):
        return self.line_bundle().projective_space()

    def section_scheme(self):
        return self.projective_space()

    def acting_group(self):
        return self._group

    def scheme_action_functor(self):
        return self._scheme_action.action_functor()

    def scheme_action(self):
        return self._scheme_action

    @cached_method
    def acted_scheme(self):
        r"""Return the owned ``G``-scheme carrying this linearization."""
        return self.scheme_action()

    def character_value(self, group_element):
        base = self.section_scheme().scheme_base_ring()
        value = base(self._character(self.acting_group()(group_element)))
        assert value.is_unit(), (
            f"the character of {self} does not take values in the units of {base}: it "
            f"sends {group_element} to {value}"
        )
        return value

    def _validate_character(self) -> None:
        group = self.acting_group()
        base = self.section_scheme().scheme_base_ring()
        assert self.character_value(group.one()) == base.one(), (
            f"the twist of {self} is not a character of {group}: it sends the identity to "
            f"{self.character_value(group.one())}, not to 1"
        )
        elements = tuple(group)
        for left in elements:
            for right in elements:
                assert self.character_value(left * right) == (
                    self.character_value(left) * self.character_value(right)
                ), (
                    f"the twist of {self} is not a character of {group}: it is not "
                    f"multiplicative on the pair {left}, {right}"
                )

    def scheme_action_of(self, group_element):
        group_element = self.acting_group()(group_element)
        action = self.scheme_action_functor()
        point = action.domain().an_object()
        arrow = action.domain().Mor(point, point)(group_element)
        return action(arrow)

    @cached_method
    def linearization_isomorphism(self, group_element):
        return _ProjectiveLineBundleLinearizationIsomorphism(
            self,
            group_element,
        ).morphism()

    def cocycle_holds(self, left, right) -> bool:
        r"""Check the character part of ``lambda_{gh}=lambda_g o g^*lambda_h``.

        The untwisted ``O(d)`` lift is functorial pullback of homogeneous
        coordinates.  Hence the only additional cocycle condition for a twist
        is multiplicativity of its scalar character, which is recorded here.
        """
        left = self.acting_group()(left)
        right = self.acting_group()(right)
        return self.character_value(left * right) == (
            self.character_value(left) * self.character_value(right)
        )

    @cached_method
    def section_action_of(self, group_element):
        r"""Return ``s |-> chi(g) (g^-1)^*s`` on ``H^0(P,O(d))``."""
        group_element = self.acting_group()(group_element)
        sections = self.line_bundle().global_sections()
        inverse_action = self.scheme_action_of(group_element.inverse())
        pullback = sections.pullback_by_projective_automorphism(inverse_action)
        scalar = self.character_value(group_element)
        return sections.Mor(sections).scalar_multiple(scalar, pullback)

    @cached_method
    def section_group_module(self):
        r"""Return the actual module over ``R[G]`` induced by this linearization."""
        base = self.section_scheme().scheme_base_ring()
        group_algebra = OwnedGroups().group_algebra(base)(self.acting_group())
        sections = self.line_bundle().global_sections()
        return Modules(group_algebra)(
            sections,
            lambda group_element, section: self.section_action_of(group_element)(section),
        )

    def invariant_sections(self):
        return self.section_group_module().module_invariants()

    def isotypic_decomposition(self):
        return self.section_group_module().isotypic_decomposition()

    @cached_method
    def coherent_cohomology_group_module(self, degree):
        r"""Return the induced ``G``-action on represented ``H^degree(P,O(d))``.

        For ``d >= 0`` on projective space, the represented global-section
        module is ``H^0``.  On a projective line the only other coherent
        cohomology group is ``H^1``, which vanishes in this nonnegative regime;
        its zero module carries the unique trivial action.  Negative-degree
        nonzero higher cohomology is left to the later general projective
        cohomology owner rather than inferred from a dimension formula here.
        """
        degree = int(degree)
        if degree < 0:
            raise ValueError(
                f"H^{degree}({self.line_bundle()}) is undefined: cohomology degrees are nonnegative"
            )
        supported_h1 = (
            int(self.projective_space().relative_dimension()) == 1
            and degree == 1
            and self.line_bundle().degree() >= 0
        )
        assert degree == 0 or supported_h1, (
            f"the action of {self.acting_group()} on H^{degree}({self.line_bundle()}) is "
            "implemented only on H^0, and on H^1 of O(d) with d >= 0 on P^1, where it vanishes"
        )
        if degree == 0:
            return self.section_group_module()
        base = self.section_scheme().scheme_base_ring()
        zero = base._fresh_free_module_on(finite_ordered_set(()))
        return Modules(base).trivial_action(self.acting_group())(zero)

    def equivariant_section_restriction(self, divisor):
        r"""Restrict sections equivariantly to an invariant eigensection divisor.

        The underlying map is the exact image-valued section restriction.  The
        divisor is invariant because it is the zero locus of an eigensection,
        so its restriction kernel is stable.  Acting on a target section means
        choosing any source preimage, acting there, and restricting again;
        stability of the kernel makes that independent of the preimage.
        """
        if not self.is_eigensection_divisor(divisor):
            raise ValueError(
                f"cannot restrict sections of {self.line_bundle()} equivariantly to {divisor}: "
                "equivariant restriction is implemented only to the zero divisor of an "
                "eigensection of this linearization"
            )
        restriction = self.line_bundle().restriction_map(divisor)
        source = self.section_group_module()
        target_unacted = restriction.codomain()
        group_algebra = source.group_algebra()

        def target_action(group_element, element):
            preimage = restriction.preimage(element)
            return restriction(
                self.section_action_of(group_element)(preimage)
            )

        target = Modules(group_algebra)(target_unacted, target_action)
        images = {
            label: target(restriction(source.unformed_module().module_generator(label)))
            for label in source.module_generating_set()
        }
        return source.Mor(target)(images)

    def is_eigensection(self, section, character) -> bool:
        sections = self.line_bundle().global_sections()
        section = sections(section)
        base = sections.base_ring()
        return all(
            self.section_action_of(group_element)(section)
            == sections.scalar_multiple(base(character(group_element)), section)
            for group_element in self.acting_group()
        )

    def eigensection_divisor(self, section, character):
        r"""Return the invariant zero divisor of a selected eigensection."""
        sections = self.line_bundle().global_sections()
        section = sections(section)
        assert self.is_eigensection(section, character), (
            f"{section} is not an eigensection of {self} for the given character, so its zero "
            "divisor is not known to be invariant"
        )
        polynomial = sections.homogeneous_polynomial(section)
        return self.projective_space().closed_subscheme(
            polynomial,
            _object_engine=_EigensectionDivisorEngine,
            construction_data={
                "eigensection_linearization": self,
                "eigensection_section": section,
                "eigensection_character": character,
            },
        )

    def eigensection_divisor_construction(self, divisor):
        r"""Return the selected eigensection datum defining ``divisor`` for this lift."""
        match divisor:
            case _EigensectionDivisorEngine() if divisor.linearization() is self:
                return divisor
            case _:
                assert False, (
                    f"{divisor} is not the zero divisor of an eigensection of {self}"
                )

    def is_eigensection_divisor(self, divisor) -> bool:
        r"""Return whether ``divisor`` was constructed from an eigensection of this lift."""
        match divisor:
            case _EigensectionDivisorEngine() if divisor.linearization() is self:
                return True
            case _:
                return False

    @staticmethod
    def _normalized_projective_coordinates(point):
        coordinates = tuple(point.point_coordinates())
        base = point.codomain().scheme_base_ring()
        pivot = next(
            (coordinate for coordinate in coordinates if coordinate != base.zero()),
            None,
        )
        if pivot is None:
            raise ValueError(
                f"{point} is not a point of projective space: its homogeneous coordinates "
                f"{coordinates} all vanish"
            )
        inverse = pivot.inverse_of_unit()
        return tuple(coordinate * inverse for coordinate in coordinates)

    def point_is_fixed(self, point) -> bool:
        if point.codomain() is not self.projective_space():
            raise ValueError(
                f"cannot ask whether {point} is fixed by {self.acting_group()}: it is a point "
                f"of {point.codomain()}, not of {self.projective_space()}"
            )
        selected = self._normalized_projective_coordinates(point)
        for group_element in self.acting_group():
            image = self.scheme_action_of(group_element).image_of_point(point)
            if self._normalized_projective_coordinates(image) != selected:
                return False
        return True

    @cached_method
    def fixed_point_fiber_evaluation(self, point):
        r"""Return the equivariant evaluation ``H^0(P,L) -> L|_p`` at a fixed point."""
        if not self.point_is_fixed(point):
            raise ValueError(
                f"cannot evaluate sections of {self.line_bundle()} equivariantly at {point}: "
                f"the point is not fixed by {self.acting_group()}"
            )
        source = self.section_group_module()
        sections = source.unformed_module()
        evaluation = self.line_bundle().jet_evaluation(point, 1)
        fiber = evaluation.codomain()
        group_algebra = source.group_algebra()
        target = Modules(group_algebra)(
            fiber,
            lambda group_element, vector: fiber.scalar_multiple(
                self.character_value(group_element),
                vector,
            ),
        )
        images = {
            label: target(evaluation(sections.module_generator(label)))
            for label in source.module_generating_set()
        }
        return source.Mor(target)(images)

    def twist(self, character):
        return _line_bundle_linearization(
            self.line_bundle(),
            self.scheme_action(),
            lambda group_element: self.character_value(group_element)
            * self.section_scheme().scheme_base_ring()(character(group_element)),
        )

    def _repr_(self) -> str:
        return f"Linearization of {self.line_bundle()} by {self.acting_group()}"



class _ProductProjectiveLineBundleLinearization(_ProjectiveLineBundleLinearization):
    r"""A C2 coordinate linearization of ``O(d_1,...,d_r)`` on a projective product.

    The scheme action stores the scalar weight of every homogeneous coordinate.
    The induced action on a monomial section is the product of those weights to
    its exponent vector, followed by the selected character twist.  Thus the
    eigenspace decomposition is obtained from the represented action on the
    common group-module owner rather than from a dimension formula.
    """

    def __init__(self, line_bundle, scheme_action, character, **rest) -> None:
        super().__init__(line_bundle, scheme_action, character, **rest)
        scheme = self.projective_product()
        assert int(self.acting_group().order()) == 2, (
            f"cannot linearize {line_bundle} along the action of {self.acting_group()}: "
            "coordinate-weight linearizations of products of projective spaces are "
            "implemented only for groups of order 2"
        )
        weights = scheme_action.coordinate_weights()
        assert weights.index_set() is scheme.factors().index_set(), (
            f"the coordinate weights of the action on {scheme} are indexed by "
            f"{weights.index_set()}, not by the factors {scheme.factors().index_set()} of "
            "the product"
        )
        self._coordinate_action = scheme_action

    def projective_product(self):
        return self.line_bundle().projective_product()

    def section_scheme(self):
        return self.projective_product()

    def coordinate_action_construction(self):
        return self._coordinate_action

    def coordinate_weights(self):
        return self.coordinate_action_construction().coordinate_weights()

    def local_chart_automorphism(self, group_element, chart_index):
        group_element = self.acting_group()(group_element)
        atlas = self.projective_product().standard_affine_atlas()
        chart_index = atlas.normalize_chart_index(chart_index)
        if group_element == self.acting_group().one():
            return atlas.chart(chart_index).categorical_identity_morphism()
        return self.coordinate_action_construction().local_automorphism(chart_index)

    def local_jacobian_scalar(self, group_element, chart_index):
        r"""Return the determinant of the diagonal action on affine chart coordinates."""
        group_element = self.acting_group()(group_element)
        base = self.section_scheme().scheme_base_ring()
        if group_element == self.acting_group().one():
            return base.one()
        atlas = self.projective_product().standard_affine_atlas()
        chart_index = atlas.normalize_chart_index(chart_index)
        choice = chart_index
        factors = self.projective_product().factors()
        labels = tuple(factors.index_set())
        result = base.one()
        for position, label in enumerate(labels):
            selected = choice[position]
            weights = self.coordinate_weights()[label]
            other = 1 - int(selected)
            result *= base(weights[other]) * base(weights[selected]).inverse_of_unit()
        return result

    @cached_method
    def section_action_of(self, group_element):
        group_element = self.acting_group()(group_element)
        sections = self.line_bundle().global_sections()
        base = sections.base_ring()
        scalar_twist = self.character_value(group_element)
        if group_element == self.acting_group().one():
            endomorphisms = sections.Mor(sections)
            return endomorphisms.scalar_multiple(
                scalar_twist,
                endomorphisms.identity(),
            )
        factor_labels = tuple(self.projective_product().factors().index_set())
        weights = self.coordinate_weights()
        images = {}
        for monomial in sections.module_generating_set():
            weight = base.one()
            for factor_label, block in zip(
                factor_labels,
                sections.monomial_exponents(monomial),
                strict=True,
            ):
                factor_weights = weights[factor_label]
                for coordinate_weight, exponent in zip(factor_weights, block, strict=True):
                    if exponent:
                        weight *= base(coordinate_weight) ** int(exponent)
            images[monomial] = sections.scalar_multiple(
                scalar_twist * weight,
                sections.module_generator(monomial),
            )
        return sections.Mor(sections)(images)

    def coherent_cohomology_group_module(self, degree):
        r"""Return the represented action on ``H^0`` of this multiprojective line bundle."""
        degree = int(degree)
        if degree < 0:
            raise ValueError(
                f"H^{degree}({self.line_bundle()}) is undefined: cohomology degrees are nonnegative"
            )
        assert degree == 0, (
            f"the action of {self.acting_group()} on H^{degree}({self.line_bundle()}) is "
            "implemented only in degree 0 on a product of projective spaces"
        )
        return self.section_group_module()


@cached_function(
    key=lambda projective_product, group=None: (
        id(projective_product),
        id(OwnedGroups().C(2) if group is None else group),
    )
)
def _c2_diagonal_product_projective_action(projective_product, group=None):
    r"""Return the diagonal sign action ``[x0:x1] |-> [x0:-x1]`` on every P1 factor."""
    base = projective_product.scheme_base_ring()
    factors = projective_product.factors()
    indices = factors.index_set()
    for label in indices:
        if int(factors[label].relative_dimension()) != 1:
            raise TypeError(
                f"the diagonal sign action is defined only on products of projective lines, "
                f"but the factor {factors[label]} of {projective_product} has dimension "
                f"{factors[label].relative_dimension()}"
            )
    group = OwnedGroups().C(2) if group is None else group
    if int(group.order()) != 2:
        raise ValueError(
            f"the diagonal sign action on {projective_product} needs a group of order 2, "
            f"but {group} has order {group.order()}"
        )
    weights = finite_indexed_family(
        indices,
        lambda _label: (base.one(), -base.one()),
        name="Homogeneous coordinate weights of the diagonal sign action",
    )
    factor_automorphisms = {}
    for label in indices:
        factor = factors[label]
        ring = factor.O(1).global_sections().homogeneous_coordinate_ring()
        coordinate_labels = tuple(ring.algebra_generating_set())
        coordinates = tuple(ring.algebra_generator(name) for name in coordinate_labels)
        factor_automorphisms[label] = factor.projective_morphism_from_coordinates(
            factor,
            (coordinates[0], -coordinates[1]),
        )
    nontrivial = projective_product.from_product_cone(
        indexed_family(
            indices,
            lambda label: factor_automorphisms[label] * projective_product.projection(label),
            name="Factor legs of the diagonal sign involution",
        )
    )
    atlas = projective_product.standard_affine_atlas()
    positions = {label: position for position, label in enumerate(tuple(indices))}
    local_automorphisms = {}
    for choice in atlas.chart_indices():
        chart = atlas.chart(choice)
        local_factors = chart.factors()
        local_factor_automorphisms = {}
        for label in indices:
            factor_chart = local_factors[label]
            algebra = factor_chart.coordinate_algebra()
            coordinate_label = next(iter(algebra.algebra_generating_set()))
            coordinate = algebra.algebra_generator(coordinate_label)
            selected = int(choice[positions[label]])
            other = 1 - selected
            factor_weights = weights[label]
            scalar = base(factor_weights[other]) * base(factor_weights[selected]).inverse_of_unit()
            local_factor_automorphisms[label] = _affine_morphism_from_pullback(
                factor_chart,
                factor_chart,
                algebra.Mor(algebra)({coordinate_label: algebra(scalar) * coordinate}),
            )
        local_automorphisms[choice] = chart.from_product_cone(
            indexed_family(
                indices,
                lambda label, chart=chart: (
                    local_factor_automorphisms[label] * chart.projection(label)
                ),
                name="Affine factor legs of the diagonal sign involution",
            )
        )

    identity = projective_product.categorical_identity_morphism()
    return _ProjectiveActionFunctor(
        group,
        Schemes(base),
        projective_product,
        lambda element: identity if element == group.one() else nontrivial,
        coordinate_weights=weights,
        local_automorphisms=finite_indexed_family(
            atlas.chart_index_set(),
            lambda index: local_automorphisms[index],
            name="Affine-chart automorphisms of the diagonal sign action",
        ),
    )



@cached_function(key=lambda projective_line, group=None: (id(projective_line), id(OwnedGroups().C(2) if group is None else group)))
def _projective_line_coordinate_swap_action(projective_line, group=None):
    r"""Return the ``C2`` action on ``P^1`` interchanging its two coordinates."""
    base = projective_line.scheme_base_ring()
    if int(projective_line.relative_dimension()) != 1:
        raise TypeError(
            f"the coordinate-swap action is defined only on P^1, but {projective_line} has "
            f"dimension {projective_line.relative_dimension()}"
        )
    group = OwnedGroups().C(2) if group is None else group
    if int(group.order()) != 2:
        raise ValueError(
            f"the coordinate-swap action on {projective_line} needs a group of order 2, "
            f"but {group} has order {group.order()}"
        )
    ring = projective_line.O(1).global_sections().homogeneous_coordinate_ring()
    labels = tuple(ring.algebra_generating_set())
    if len(labels) != 2:
        raise ArithmeticError(
            f"{projective_line} should have 2 homogeneous coordinates, but its coordinate "
            f"ring {ring} has {len(labels)}"
        )
    left = ring.algebra_generator(labels[0])
    right = ring.algebra_generator(labels[1])
    identity = projective_line.projective_morphism_from_coordinates(
        projective_line,
        (left, right),
    )
    swap = projective_line.projective_morphism_from_coordinates(
        projective_line,
        (right, left),
    )
    return _ProjectiveActionFunctor(
        group,
        Schemes(base),
        projective_line,
        lambda group_element: identity if group_element == group.one() else swap,
    )



__all__ = []
