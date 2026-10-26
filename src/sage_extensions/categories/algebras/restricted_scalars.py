r"""Restriction of scalars for algebras along a specified ring morphism.

For ``f : R -> S`` and an ``S``-algebra ``B=(M,m)``, restriction retains the
additive group and multiplication and lets ``r`` act as ``f(r)``. The
defining module is the exact ``Res_f(M)``. No associativity or unit is
inferred; these laws and the other absolute algebra identities are retained
only when the source supplies them. When both ``S/R`` and
``B/S`` carry the live commutative polynomial-quotient presentations, this
module also constructs an exact finite ``R``-presentation of the restricted
algebra.  That presentation is what makes the represented Mor surface and the
scalar-extension/restriction adjunction executable without replacing ``B`` by
a second authoritative ring implementation.
"""

from sage.categories.map import Map
from sage.structure.element import parent as element_parent

from sage_extensions.categories.algebras.algebras import (
    Algebras,
    AlgebrasWithChosenFinitePresentation,
    FinitelyPresentedAlgebras,
    _algebra_on_module,
    _fix_selected_algebra_presentation,
    _root_algebra_law_decisions,
)
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    _restricted_scalars_view,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedRings,
    _engine_element,
    _engine_ring,
    _owned_ring,
)
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.refine import RealizationHook

_RESTRICTED_SCALAR_ALGEBRAS = {}


class RestrictedScalarsAlgebras(OwnedCategoryOverBaseRing):
    r"""``R``-algebras obtained by restricting an algebra along ``R -> S``."""

    def an_object(self):
        r"""``Res_{id}(R[x])``: the polynomial algebra along the identity of ``R``.

        Restriction of scalars along \(\mathrm{id}: R\to R\) is the smallest
        specimen that still carries the chosen structure map the category is
        about.
        """


        ring = self.base_ring()
        algebra = ring.free_module(("x",)).symmetric_algebra()
        return algebra.restrict_scalars(
            ring.Mor(ring)(lambda element: element)
        )

    def _repr_object_names(self):
        return f"restricted-scalars algebras over {self.base_ring()}"

    def super_categories(self):
        return [Algebras(self.base_ring())]

    class ParentMethods:
        def __init__(
            self,
            algebra_over_extension,
            ring_map,
            restricted_scalar_generator_labels=None,
            restricted_algebra_generator_labels=None,
            **rest,
        ) -> None:
            self._algebra_over_extension = algebra_over_extension
            self._restricted_scalars_ring_map = ring_map
            self._restricted_scalar_generator_labels = restricted_scalar_generator_labels
            self._restricted_algebra_generator_labels = restricted_algebra_generator_labels
            super().__init__(**rest)

        def ring_map(self):
            r"""Return the selected scalar map ``R -> S``."""
            return self._restricted_scalars_ring_map

        def algebra_over_extension(self):
            r"""Return the original ``S``-algebra before scalar restriction."""
            return self._algebra_over_extension

        def extension_ring(self):
            return self.algebra_over_extension().base_ring()

        def restricted_scalar_generator_labels(self):
            return self._restricted_scalar_generator_labels

        def restricted_algebra_generator_labels(self):
            return self._restricted_algebra_generator_labels

        def _element_constructor_(self, value):
            r"""Read exact source-module data, or the selected unital coefficient input.

            The module realization continues to own coordinate syntax. An
            element of the original algebra is transported through its
            retained module, while a scalar of the new base enters a unital
            algebra through its selected restricted scalar action.
            """
            source = element_parent(value)
            if source is self:
                return value
            base = self.base_ring()
            if source in Modules(base) and self._built_on_the_same_data(source):
                return self._element_on_the_same_data(source, value)
            original = self.algebra_over_extension()
            original_module = original.unformed_module()
            module = self.unformed_module()
            if self in Algebras(base).Unital() and source is base:
                unit = module.wrap(original_module(original.one()))
                return self._element_from_unformed_module(
                    module.scalar_multiple(value, unit)
                )
            if source is original or source is original_module:
                return self._element_from_unformed_module(
                    module.wrap(original_module(value))
                )
            return super()._element_constructor_(value)

        def _element_from_unformed_module(self, element):
            r"""Transport a datum of ``Res_f(M)`` without applying ``f`` again."""
            if self.has_selected_module_resolution():
                return Algebras.ParentMethods._element_from_unformed_module(self, element)
            module = self.unformed_module()
            return self._element_from_underlying_set(
                module._underlying_additive_element(module(element))
            )

        @RealizationHook
        def _selected_engine_ring(self):
            r"""Supply the original ring's optional computation model.

            Protected OwnedRings realization contract. Only its engine
            dispatcher asks for this datum; a general nonring algebra has no
            ring model. The model supplies computation, never algebra laws.
            """
            original = self.algebra_over_extension()
            if original not in OwnedRings():
                return None
            return original._selected_engine_ring()

        def _engine_element(self, value):
            r"""Lower through ``Res_f(M)`` and the original algebra's ring adapter.

            This is the protected OwnedRings lowering contract, called only
            after its dispatcher has selected the original ring model.
            """
            original = self.algebra_over_extension()
            module_element = self.unformed_module()(self(value))
            return _engine_element(original, original(module_element.underlying_element()))

        def _from_engine_element(self, value):
            r"""Raise a ring computation through the exact restricted module.

            This is the protected OwnedRings raising contract. Its caller
            has already selected the original algebra's ring realization.
            """
            original = self.algebra_over_extension()
            original_value = _owned_engine_element(original, value)
            return self._element_from_unformed_module(
                self.unformed_module().wrap(original.unformed_module()(original_value))
            )


def _lift_polynomial(relation, coefficient_lift, target_variables, target_ring):
    r"""Lift a polynomial exactly after lifting each coefficient."""
    variable_count = int(target_variables.cardinality())
    if variable_count == 0:
        return target_ring(coefficient_lift(relation))
    if variable_count == 1:
        variable = target_variables[0]
        return sum(
            (
                coefficient_lift(coefficient) * variable**exponent
                for exponent, coefficient in enumerate(relation.list())
            ),
            target_ring.zero(),
        )
    return sum(
        (
            coefficient_lift(coefficient)
            * target_ring.prod(
                target_variables[position] ** int(exponent)
                for position, exponent in enumerate(exponents)
            )
            for exponents, coefficient in relation.dict().items()
        ),
        target_ring.zero(),
    )


def _chosen_restriction_presentation(algebra, extension_ring, base_ring):
    r"""Construct the selected polynomial presentation of ``Res(B)`` over ``R``."""
    extension_labels = extension_ring.algebra_generating_set()
    algebra_labels = algebra.algebra_generating_set()
    tagged_labels = Sets().coproduct(
        indexed_family(
            Sets.Δ[1],
            lambda index: extension_labels if int(index) == 0 else algebra_labels,
        )
    )
    presentation_ring = base_ring.free_module(tagged_labels).symmetric_algebra()
    combined_labels = presentation_ring.algebra_generating_set()
    presentation_engine = _engine_ring(presentation_ring)

    scalar_variables = indexed_family(
        extension_labels,
        lambda label: _engine_element(
            presentation_ring,
            presentation_ring.algebra_generator(tagged_labels(0, label)),
        ),
        name="Restricted-scalar presentation variables",
    )
    algebra_variables = indexed_family(
        algebra_labels,
        lambda label: _engine_element(
            presentation_ring,
            presentation_ring.algebra_generator(tagged_labels(1, label)),
        ),
        name="Restricted-algebra presentation variables",
    )

    extension_presentation_engine = _engine_ring(extension_ring.presentation_ring())
    # Private finite backend serialization required by Sage's polynomial-Hom constructor.
    extension_presentation_map = extension_presentation_engine.hom(
        list(scalar_variables),
        presentation_engine,
    )
    extension_presentation_ring = extension_ring.presentation_ring()
    extension_relations = extension_ring.relations()
    algebra_relations = algebra.relations()
    relation_indices = Sets().coproduct(indexed_family(Sets.Δ[1], lambda index: (
            extension_relations.index_set()
            if int(index) == 0
            else algebra_relations.index_set()
        )))

    extension_engine = _engine_ring(extension_ring)

    def coefficient_lift(coefficient):
        representative = _engine_element(
            extension_presentation_ring,
            extension_ring.lift_to_presentation(
                _owned_engine_element(extension_ring, extension_engine(coefficient))
            ),
        )
        return presentation_engine(extension_presentation_map(representative))

    algebra_presentation_ring = algebra.presentation_ring()

    def relation_value(tagged):
        if int(tagged.summand_index()) == 0:
            relation = extension_relations[tagged.summand_element()]
            backend = presentation_engine(
                extension_presentation_map(
                    _engine_element(extension_presentation_ring, relation)
                )
            )
        else:
            relation = algebra_relations[tagged.summand_element()]
            backend = _lift_polynomial(
                _engine_element(algebra_presentation_ring, relation),
                coefficient_lift,
                algebra_variables,
                presentation_engine,
            )
        return _owned_engine_element(presentation_ring, presentation_engine(backend))

    selected_relations = indexed_family(
        relation_indices,
        relation_value,
        name="Restricted-algebra defining relations",
    )
    # Private finite backend serialization required by Sage's ideal constructor.
    presentation_ideal = presentation_engine.ideal(
        [_engine_element(presentation_ring, relation) for relation in selected_relations]
    )

    structure_map = algebra.algebra_structure_morphism()

    def generator_value(label):
        tagged = combined_labels(label)
        if int(tagged.summand_index()) == 0:
            value = structure_map(
                extension_ring.algebra_generator(tagged.summand_element())
            )
        else:
            value = algebra.algebra_generator(tagged.summand_element())
        return algebra(value)

    def lift_to_presentation(element):
        representative = _engine_element(
            algebra_presentation_ring,
            algebra.lift_to_presentation(algebra(element)),
        )
        return _lift_polynomial(
            representative,
            coefficient_lift,
            algebra_variables,
            presentation_engine,
        )

    return (
        combined_labels,
        presentation_ring,
        selected_relations,
        presentation_ideal,
        generator_value,
        lift_to_presentation,
        extension_labels,
        algebra_labels,
    )


def _restrict_algebra_scalars(algebra, ring_map):
    r"""Return ``Res_f(B)`` for ``f : R -> S`` and an ``S``-algebra ``B``.

    If ``B=(M,m)``, the defining module is ``Res_f(M)`` and the product is
    ``m`` on its unchanged underlying additive elements. Since ``m`` is
    ``S``-bilinear it is ``R``-bilinear for the action ``r*x=f(r)*x``.
    Every retained associative, unit, commutative, alternating and Jacobi law
    is the very same equation in those elements. No additional law follows
    from restriction. The stronger chosen finite presentation is retained only
    when it can be constructed from chosen presentations of both ``S/R`` and
    ``B/S`` along the selected structure map of ``S``.
    """
    if not isinstance(ring_map, Map):
        raise TypeError(
            f"restriction of scalars of {algebra} is along a ring morphism, but {ring_map!r} is not a map"
        )

    extension_ring = algebra.algebra_base_ring()
    base_ring = _owned_ring(ring_map.domain())
    if ring_map.codomain() is not extension_ring:
        raise ValueError(
            f"restriction of scalars for {algebra} requires a map into the exact coefficient ring "
            f"{extension_ring}, got codomain {ring_map.codomain()}"
        )
    if base_ring not in OwnedRings().Commutative():
        raise TypeError(
            f"restriction of an algebra to {base_ring} requires a commutative coefficient ring"
        )
    if ring_map not in OwnedRings().Mor(base_ring, extension_ring):
        raise TypeError(
            f"restriction of scalars requires an owned unital ring map {base_ring} -> {extension_ring}"
        )

    cache_key = (id(algebra), id(ring_map))
    cached = _RESTRICTED_SCALAR_ALGEBRAS.get(cache_key)
    if (
        cached is not None
        and cached.algebra_over_extension() is algebra
        and cached.ring_map() is ring_map
    ):
        return cached

    original_module = algebra.unformed_module()
    # A native algebra may realize its own module. Select the module owner
    # directly, so its stronger algebra method cannot recurse into this one.
    module = _restricted_scalars_view(original_module, ring_map)
    original_multiplication = algebra.multiplication()
    multiplication = module.tensor_product(module).from_bilinear_map(
        module,
        lambda left, right: module.wrap(
            original_multiplication(left.underlying_element(), right.underlying_element())
        ),
    )
    source_algebras = Algebras(extension_ring)
    target_algebras = Algebras(base_ring)
    placement = [RestrictedScalarsAlgebras(base_ring)]
    for source, target in (
        (source_algebras.Associative(), target_algebras.Associative()),
        (source_algebras.Unital(), target_algebras.Unital()),
        (source_algebras.Commutative(), target_algebras.Commutative()),
        (source_algebras.Lie(), target_algebras.Lie()),
    ):
        if algebra in source:
            placement.append(target)
    unit = (
        module.wrap(original_module(algebra.one()))
        if algebra in source_algebras.Unital()
        else None
    )
    construction_data = {
        "algebra_over_extension": algebra,
        "ring_map": ring_map,
    }

    from sage_extensions.categories.algebras.free_algebras import (
        SymmetricAlgebras,
    )
    from sage.rings.polynomial.multi_polynomial_ring_base import MPolynomialRing_base
    from sage.rings.polynomial.polynomial_ring import PolynomialRing_generic

    # The represented transport below substitutes polynomial variables in
    # both selected covers. Commutativity of the two quotients alone does
    # not supply polynomial covers: either may retain a tensor presentation.
    has_selected_presentation = (
        extension_ring in AlgebrasWithChosenFinitePresentation(base_ring)
        and algebra in AlgebrasWithChosenFinitePresentation(extension_ring)
        and extension_ring in Algebras(base_ring).Associative().Unital().Commutative()
        and algebra in Algebras(extension_ring).Associative().Unital().Commutative()
        and extension_ring.presentation_ring() in SymmetricAlgebras(base_ring)
        and algebra.presentation_ring() in SymmetricAlgebras(extension_ring)
        and isinstance(
            _engine_ring(extension_ring.presentation_ring()),
            (PolynomialRing_generic, MPolynomialRing_base),
        )
        and isinstance(
            _engine_ring(algebra.presentation_ring()),
            (PolynomialRing_generic, MPolynomialRing_base),
        )
        and ring_map is extension_ring.algebra_structure_morphism()
    )
    if has_selected_presentation:
        (
            labels,
            presentation_ring,
            selected_relations,
            presentation_ideal,
            generator_values,
            lift_to_presentation,
            restricted_scalar_labels,
            restricted_algebra_labels,
        ) = _chosen_restriction_presentation(algebra, extension_ring, base_ring)
        placement.extend(
            (
                FinitelyPresentedAlgebras(base_ring),
                AlgebrasWithChosenFinitePresentation(base_ring),
            )
        )
        construction_data.update(
            algebra_generating_family=indexed_family(
                labels,
                lambda label: module.wrap(original_module(generator_values(label))),
                name="Restricted algebra generators",
            ),
            algebra_framing_source=presentation_ring,
            restricted_scalar_generator_labels=restricted_scalar_labels,
            restricted_algebra_generator_labels=restricted_algebra_labels,
        )

    restricted = _algebra_on_module(
        module,
        multiplication,
        placement=tuple(placement),
        categories=tuple(
            category for category in algebra.category().all_super_categories()
            if OwnedRings()._with_axioms(category.axioms()) is category
            or Sets()._with_axioms(category.axioms()) is category
        ),
        unit=unit,
        construction_data=construction_data,
        law_decisions=_root_algebra_law_decisions(algebra),
    )
    if has_selected_presentation:
        _fix_selected_algebra_presentation(
            restricted,
            presentation_ring,
            selected_relations,
            presentation_ideal,
            lambda element: lift_to_presentation(
                module(restricted(element)).underlying_element()
            ),
        )
    _RESTRICTED_SCALAR_ALGEBRAS[cache_key] = restricted
    return restricted


__all__ = ["RestrictedScalarsAlgebras"]
