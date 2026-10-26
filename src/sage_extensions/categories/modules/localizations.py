r"""Modules equipped as localizations of modules over the source ring."""

from sage.structure.element import ModuleElement, parent as element_parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.group.magmas import AdditiveGroups
from sage_extensions.categories.modules.general_modules import _module_element_scalar_action

from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
    _relation_morphism,
    _SelectedFinitePresentationModules,
)
from sage_extensions.categories.modules.pure.modules import (
    FinitelyGeneratedModules,
    FinitelyPresentedModules,
    Modules,
    ModuleSubobjects,
    ModulesWithChosenFinitePresentation,
)
from sage_extensions.categories.rings.ring_foundation import (
    IntegralDomains,
    OwnedCategoryOverBaseRing,
)
from sage_extensions.logic import AtomicProposition, Propositions, conjunction, negation
from sage_extensions.owned_category import _object_of, owned_category_join




class LocalizedModules(OwnedCategoryOverBaseRing):
    r"""Modules represented as ``S^{-1}M`` for a chosen localization ``S^{-1}R``."""

    def an_object(self):
        r"""``S^{-1}(R^2)`` for ``S^{-1}R`` this category's ring."""
        from sage_extensions.categories.rings.commutative_algebra import LocalizationRings
        from sage_extensions.categories.sets.set_categories import finite_ordinal_set

        localization_ring = self.base_ring()
        match localization_ring in LocalizationRings():
            case True:
                pass
            case False:
                raise TypeError(
                    f"{self} has no example localized module: its base ring {localization_ring} is not "
                    f"constructed as a localization S^(-1)R of a ring R, but is in {localization_ring.category()}"
                )
        source = localization_ring.localization_source().free_module(finite_ordinal_set(2))
        return localization_ring.localize_module(source)

    def super_categories(self):

        return [Modules(self.base_ring())]

    class ElementMethods(ModuleElement):
        r"""A represented fraction ``m/s`` in ``S^{-1}M``."""

        def __init__(self, parent, numerator, denominator) -> None:
            ModuleElement.__init__(self, parent)
            self._numerator = numerator
            self._denominator = denominator

        def numerator(self):
            return self._numerator

        def denominator(self):
            return self._denominator

        def _add_(self, other):
            # ``m/s + m'/s' = (s'm + sm')/(ss')``; ``ss'`` lies in ``S`` because
            # ``S`` is multiplicatively closed.
            parent = self.parent()
            source = parent.numerator_module()
            numerator = (
                source.scalar_multiple(other.denominator(), self.numerator())
                + source.scalar_multiple(self.denominator(), other.numerator())
            )
            return parent.element_class(
                parent,
                numerator,
                self.denominator() * other.denominator(),
            )

        def _neg_(self):
            parent = self.parent()
            return parent.element_class(parent, -self.numerator(), self.denominator())

        def _lmul_(self, scalar):
            return self.parent().scalar_multiple(scalar, self)

        def _rmul_(self, scalar):
            return self.parent().scalar_multiple(scalar, self)

        def _acted_upon_(self, actor, self_on_left):
            return _module_element_scalar_action(self, actor, self_on_left)

        def equality_status(self, other):
            r"""Return ``True``, ``False``, or the proposition ``equal(x, y)`` for fraction equality."""
            if other.parent() is not self.parent():
                return False
            return self.parent()._fraction_equality_status(self, other)

        def _richcmp_(self, other, op):
            if op not in (op_EQ, op_NE):
                return NotImplemented
            status = self.equality_status(other)
            match status:
                case _ if status in Propositions:
                    return status if op == op_EQ else negation(status)
                case _:
                    return bool(status) if op == op_EQ else not bool(status)

        def _repr_(self):
            if (self.denominator() == self.parent().source_ring().one()) is True:
                return repr(self.numerator())
            return f"({self.numerator()})/({self.denominator()})"

    class ParentMethods:
        _derived_construction_parameters = frozenset(
            {"base_ring", "module_generating_set", "module_generator_function"}
        )

        def __init__(
            self,
            numerator_module,
            localization_ring,
            localization_functor,
            framing_source=None,
            **rest,
        ) -> None:
            r"""Construct ``S^{-1}M`` from ``M``, ``S^{-1}R`` and the localization functor.

            When ``M`` is framed, localization chooses no new framing: it
            carries the framing of ``M`` to its images ``m_s/1``, so the
            framed localization installs that framing once the fractions of
            this module exist.
            """
            self._numerator_module = numerator_module
            self._localization_ring = localization_ring
            self._localization_functor = localization_functor
            framing = {}
            if framing_source is not None:
                framing.update(
                    module_generating_set=framing_source.module_generating_set(),
                    module_generator_function=lambda label: self.fraction(
                        numerator_module.module_generator(label)
                    ),
                    framing_source=framing_source,
                )
            super().__init__(base_ring=localization_ring, **framing, **rest)

        def _selected_module_coefficients(self, element):
            r"""Return the coefficients of ``m/s`` in the framing carried from ``M``.

            ``m = sum_s c_s m_s`` in ``M`` gives ``m/s = sum_s (c_s/s) (m_s/1)``.
            """
            element = self(element)
            source_coordinates = self.numerator_module().framing_morphism().lift(element.numerator())
            localization_map = self.localization_ring().localization_map()
            denominator = localization_map(element.denominator())
            denominator_inverse = denominator.inverse_of_unit()
            return {
                label: localization_map(coefficient) * denominator_inverse
                for label, coefficient in source_coordinates.parent()._selected_module_coefficients(source_coordinates).items()
            }

        def base_ring(self):
            return self.localization_ring()

        def base(self):
            return self.base_ring()

        def source_ring(self):
            return self.localization_ring().localization_source()

        def fraction(self, numerator, denominator=None):
            r"""Return the fraction ``m/s`` of ``m`` in ``M`` and ``s`` in ``S``.

            ``s`` names a denominator exactly when its image in ``S^{-1}R`` is
            a unit, that is when it lies in the saturation of ``S``, whose
            fractions are the fractions of ``S^{-1}R``.
            """
            source_module = self.numerator_module()
            numerator = source_module(numerator)
            source = self.source_ring()
            denominator = source.one() if denominator is None else source(denominator)
            status = self.localization_ring().localization_map()(denominator).is_unit()
            match status:
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"{numerator}/{denominator} is not an element of {self}: the denominator {denominator} "
                        f"does not become a unit in {self.localization_ring()}"
                    )
                case _:
                    raise ValueError(
                        f"cannot form {numerator}/{denominator} in {self}: it is not known whether the "
                        f"denominator {denominator} becomes a unit in {self.localization_ring()}"
                    )
            return self.element_class(self, numerator, denominator)

        def _element_constructor_(self, value):
            match value:
                case _ if element_parent(value) is self:
                    return value
                case (numerator, denominator):
                    return self.fraction(numerator, denominator)
                case _:
                    return self.fraction(value)

        def zero(self):
            return self.fraction(self.numerator_module().zero())

        def _fraction_equality_status(self, left, right):
            r"""Decide ``m/s = m'/s'``: some ``u`` in ``S`` kills ``d = s'm - sm'``.

            That holds exactly when ``Ann_R(d)`` meets ``S``. The selected
            finite-presentation owner computes that ideal when its kernel
            computation applies. A finite module has a finite orbit
            under a selected finite generating family of ``S``; the search
            applies when zero and repeated-point comparisons are decided.
            A torsion-free module over a domain has ``Ann_R(d) = 0`` when
            ``d`` is proved nonzero. For a free module over a represented
            quotient or exact coefficient presentation, localization kills
            ``d`` exactly when it kills every stored source coordinate. The
            localized zero ideal already owns this source membership test.

            A source coordinate proved to be ``1`` or ``-1`` gives
            ``Ann_R(d) = 0`` directly, without a general unit computation.
            This also keeps the coordinate test nonrecursive: constructing
            the localized zero ideal may transport its unit relation and
            compare ``1`` with ``0`` in the localized coefficient ring. That
            comparison is settled over the source before constructing any
            localized zero ideal. Outside these computations the answer is
            the proposition ``equal(x, y)``.
            """
            from sage_extensions.categories.modules.framed.framed_free_modules import (
                FramedFreeModules,
            )
            from sage_extensions.categories.rings.commutative_algebra import (
                QuotientRings,
                _submonoid_contains_zero_in_domain,
            )

            source = self.numerator_module()
            source_ring = self.source_ring()
            cross_difference = (
                source.scalar_multiple(right.denominator(), left.numerator())
                - source.scalar_multiple(left.denominator(), right.numerator())
            )
            zero_status = cross_difference == source.zero()
            if zero_status is True:
                return True
            match source:
                case _ if source in _SelectedFinitePresentationModules(source_ring):
                    return self.localization_ring().inverted_submonoid_meets(
                        source.annihilator_of(cross_difference)
                    )
                case _ if (
                    source.is_finite() is True
                    and self.localization_submonoid()._selected_representation_kind() == "generators"
                ):
                    generators = tuple(self.inverted_elements())
                    pending = [cross_difference]
                    seen = []
                    while pending:
                        current = pending.pop()
                        current_zero = current == source.zero()
                        if current_zero is True:
                            return True
                        if current_zero is not False:
                            return AtomicProposition("equal", left, right)
                        comparisons = tuple(current == old for old in seen)
                        if any(comparison is True for comparison in comparisons):
                            continue
                        if any(comparison is not False for comparison in comparisons):
                            return AtomicProposition("equal", left, right)
                        seen.append(current)
                        pending.extend(
                            source.scalar_multiple(generator, current)
                            for generator in generators
                        )
                    return False
                case _ if (
                    zero_status is False
                    and source_ring in IntegralDomains()
                    and source.is_torsion_free() is True
                ):
                    return _submonoid_contains_zero_in_domain(
                        source_ring, self.localization_submonoid()
                    )
                case _ if (
                    source in FramedFreeModules(source_ring)
                    and (
                        source_ring in QuotientRings()
                        or source_ring._has_selected_exact_coefficient_presentation() is True
                    )
                ):
                    coefficients = source._selected_module_coefficients(cross_difference)
                    localization = self.localization_ring()
                    zero_ideal = source_ring.ideal(source_ring.zero())
                    one = source_ring.one()
                    if any(
                        (coefficient == one) is True or (coefficient == -one) is True
                        for coefficient in coefficients.values()
                    ):
                        return localization.inverted_submonoid_meets(zero_ideal)
                    localized_zero = zero_ideal.extension_to_localization(localization)
                    localization_map = localization.localization_map()
                    return conjunction(
                        localized_zero.contains_ambient_element(localization_map(coefficient))
                        for coefficient in coefficients.values()
                    )
                case _:
                    return AtomicProposition("equal", left, right)

        def inverted_elements(self):
            r"""Return the chosen generators of the submonoid ``S`` inverted here."""
            return self.localization_ring().inverted_elements()

        def _owned_scalar_multiple(self, scalar, element):
            r"""Apply the fraction action ``(a/t)(m/s) = (am)/(ts)`` defining this module."""
            element = self(element)
            numerator, denominator = self.localization_ring().localization_fraction_data(scalar)
            source = self.numerator_module()
            return self.element_class(
                self,
                source.scalar_multiple(numerator, element.numerator()),
                denominator * element.denominator(),
            )

        def _finiteness_decision(self):
            r"""Finite numerator modules have finite localizations.

            Localizing a finite module is a quotient of its finite underlying
            set.  An infinite numerator may become zero, so its infinitude
            alone does not imply infinitude after localization.
            """
            if self.numerator_module().is_finite() is True:
                return True
            if self.is_zero() is True:
                return True
            return AtomicProposition("is_finite", self)

        def is_zero(self):
            r"""Decide whether ``S^{-1}M = 0``.

            A finitely generated ``M`` localizes to zero exactly when some
            element of ``S`` kills all of it, that is when ``Ann_R(M)`` meets
            ``S``, which is an ideal computation.  A finite ``M`` localizes to
            zero exactly when each of its elements does.
            """
            source = self.numerator_module()
            match source:
                case _ if source in FinitelyGeneratedModules(self.source_ring()):
                    return self.localization_ring().inverted_submonoid_meets(source.annihilator())
                case _ if source.is_finite() is True:
                    statuses = tuple(
                        self.fraction(element).equality_status(self.zero())
                        for element in source
                    )
                    if any(status in Propositions for status in statuses):
                        return AtomicProposition("is_zero", self)
                    return all(status is True for status in statuses)
                case _:
                    return AtomicProposition("is_zero", self)

        def _represented_annihilator_ideal(self):
            r"""Localize the annihilator of a represented finite source module.

            For finitely generated M,
            ``Ann_(S^-1 A)(S^-1 M) = S^-1 Ann_A(M)``
            (Stacks, Tag 07T8). Finiteness is essential: a common
            denominator can be chosen for the finitely many generators.
            The public module annihilator and the selected-presentation
            provider delegate here; no conductor-specific calculation is
            introduced. Return ``NotImplemented`` outside this source regime.
            """
            source = self.numerator_module()
            if source not in FinitelyGeneratedModules(self.source_ring()):
                return NotImplemented
            annihilator = source._represented_annihilator_ideal()
            if annihilator is NotImplemented:
                return NotImplemented
            return annihilator.extension_to_localization(self.localization_ring())

        def _repr_(self):
            return (
                f"{self.numerator_module()} localized along "
                f"{self.localization_ring().localization_map()}"
            )

        def numerator_module(self):
            r"""The module the numerators of these fractions lie in: the ``M`` this is ``S^{-1}M`` of."""
            return self._numerator_module

        def localization_ring(self):
            return self._localization_ring

        def localization_submonoid(self):
            return self.localization_ring().localization_submonoid()

        def localization_functor(self):
            return self._localization_functor

        def localization_unit(self):
            return self.localization_functor().unit(
                self.numerator_module(),
                localized=self,
            )

        def restriction_to(self, target_ring):
            r"""Return ``S^{-1}M -> T^{-1}M`` over the ring restriction ``S^{-1}R -> T^{-1}R``.

            Both localizations are built on the same source module and keep its
            framing, so the restriction carries a generator to the generator of
            the same name: as fractions it is ``m/s`` to ``m/s``.  It is
            ``S^{-1}R``-linear into the restriction of scalars of ``T^{-1}M``,
            which is where a map between modules over different rings lives.

            This is the sheaf restriction of ``M~`` along ``D(g) <= D(f)``, and
            at a prime it is the map from a section to its germ in the stalk.
            """

            source_module = self.numerator_module()
            target = target_ring.localize_module(source_module)
            restriction = self.localization_ring().restriction_to(target_ring)
            restricted = target.restrict_scalars(restriction)
            return self.module_category().Mor(self, restricted)(
                lambda label: restricted(target.module_generator(label))
            )

        def localization_prime_point(self):
            r"""Return the point of ``Spec(R)`` whose local ring this localizes at.

            ``M_p`` is the localization along ``R -> R_p``, and ``R_p`` names
            the prime it inverts the complement of, so the point is read from
            the localization ring rather than recorded a second time here.
            """
            from sage_extensions.categories.rings.commutative_algebra import (
                PrimeLocalizations,
            )

            localization_ring = self.localization_ring()
            match localization_ring in PrimeLocalizations():
                case True:
                    pass
                case False:
                    raise TypeError(
                        f"{localization_ring} does not invert the complement of a prime, so "
                        f"{self} is not the localization of a module at a point of a spectrum"
                    )
            return self.source_ring().spectrum()(localization_ring.localized_prime())


__all__ = [
    "LocalizedModules",
]


def _localized_module(
    numerator_module,
    localization_ring,
    localization_functor,
    *,
    subobject_ambient=None,
    subobject_generator_images=None,
    subobject_lift=None,
    subobject_inclusion_factory=None,
    extra_categories=(),
    extra_construction_data=None,
    selected_presentation_data=None,
):
    r"""Return ``S^{-1}M``, placed by what the source module already is.

    A localized module is a subobject when the construction selects an
    inclusion, and is framed, finitely generated, or finitely presented exactly
    when its source is: localization is exact, so a presentation of ``M`` maps
    to a presentation of ``S^{-1}M`` under ``R -> S^{-1}R``.
    """
    # Localization preserves the abelian addition of the source module.
    # Materialize this inherited axiom at the construction owner because
    # owned category joins do not guarantee it on the concrete parent, while
    # native scalar-action construction requires it explicitly.
    placement = [
        LocalizedModules(localization_ring),
        AdditiveGroups().AdditiveCommutative(),
        *tuple(extra_categories),
    ]
    data = {
        "numerator_module": numerator_module,
        "localization_ring": localization_ring,
        "localization_functor": localization_functor,
    }
    if extra_construction_data is not None:
        data.update(extra_construction_data)

    if subobject_inclusion_factory is not None or (
        subobject_ambient is not None and subobject_generator_images is not None
    ):
        placement.append(ModuleSubobjects(localization_ring))
        if subobject_ambient is not None:
            placement.append(Modules(localization_ring).Subobjects(subobject_ambient))
        data.update(
            subobject_ambient=subobject_ambient,
            subobject_generator_images=subobject_generator_images,
            subobject_lift=subobject_lift,
            subobject_inclusion_factory=subobject_inclusion_factory,
        )

    source_ring = localization_ring.localization_source()
    if numerator_module.has_selected_module_resolution():
        framing_source = localization_ring.free_module(
            numerator_module.module_generating_set()
        )
        if numerator_module in FinitelyGeneratedModules(source_ring):
            placement.append(FinitelyGeneratedModules(localization_ring))
        if numerator_module in ModulesWithChosenFinitePresentation(source_ring):
            transported = _transported_presentation(numerator_module, localization_ring)
            data.update(transported)
            if selected_presentation_data is not None:
                data.update(selected_presentation_data)
            framing_source = data["presentation"].codomain()
            placement.extend(
                [
                    FinitelyPresentedModules(localization_ring),
                    ModulesWithChosenFinitePresentation(localization_ring),
                    _SelectedFinitePresentationModules(localization_ring),
                ]
            )
        data["framing_source"] = framing_source

    return _object_of(owned_category_join(placement), **data)


def _transported_presentation(numerator_module, localization_ring):
    r"""Return the presentation of ``S^{-1}M`` induced by one of ``M``.

    Localization is exact, so applying ``R -> S^{-1}R`` to the relation
    morphism ``r: F_1 -> F_0`` of ``M``, coefficient by coefficient, gives
    ``S^{-1}r``, which presents ``S^{-1}M`` on the images of the same
    generators.
    """
    relations = _relation_morphism(numerator_module)
    localization_map = localization_ring.localization_map()
    free_relations = localization_ring.free_module(relations.domain().module_generating_set())
    free_generators = localization_ring.free_module(numerator_module.module_generating_set())

    def localized_relation(relation_label):
        relation = relations(relations.domain().module_generator(relation_label)).to_vector()
        return free_generators.linear_combination(
            {
                label: localization_map(coefficient)
                for label, coefficient in relation.parent()._selected_module_coefficients(relation).items()
            }
        )

    return {
        "presentation": free_relations.module_category().Mor(free_relations, free_generators)(localized_relation),
    }
