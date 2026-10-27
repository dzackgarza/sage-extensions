r"""Modules equipped with exact bilinear or quadratic forms."""

from collections.abc import Iterable
from typing import TYPE_CHECKING

from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.richcmp import op_EQ

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MonoCategoryConstruction,
    MorCategories,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoricalArrow,
    object_level,
)
from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
)
from sage_extensions.categories.forms.forms import (
    _is_bilinear_form as _form_is_bilinear,
)
from sage_extensions.categories.forms.forms import (
    _is_quadratic_form as _form_is_quadratic,
)
from sage_extensions.categories.modules.base_change import (
    _base_change_codomain,
    _base_change_element,
    _base_change_scalar,
)
from sage_extensions.categories.modules.framed.finitely_generated.finitely_presented_modules import (
    _relation_images,
)
from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
    CokernelTorsionFormModules,
    TorsionBilinearFormIsoCategoryConstruction,
    TorsionFormTwistFunctor,
    TorsionQuadraticFormIsoCategoryConstruction,
    _bilinear_descends,
    _coerced_gram,
    _even_lattice_genus_exists,
    _forms_are_isomorphic,
    _invariant_factor_form_isomorphism,
    _p_adic_jordan_decomposition,
    _p_adic_jordan_form,
    _p_adic_jordan_module_generators,
    _quadratic_descends,
    _regenerate_form_on_generators,
    _representative_gram,
    _torsion_form_all_subobjects,
    _torsion_form_automorphism_group,
    _torsion_form_element_action,
    _torsion_form_isotropic_subobjects,
    _torsion_form_lagrangian_subobjects,
    _torsion_form_maximal_isotropic_subobjects,
    _torsion_form_orthogonal_subobject,
    _torsion_form_primary_part,
    _torsion_form_subobject_on,
    _torsion_form_subobject_orbits,
    _torsion_form_subquotient,
)
from sage_extensions.categories.modules.framed.fraction_field_quotients import (
    FractionFieldQuotients,
)
from sage_extensions.categories.modules.framed.framed_free_modules import (
    FramedFreeModules,
    _module_subobject_spanning,
    _span_basis_elements,
)
from sage_extensions.categories.modules.hodge import (
    _algebraic_correlation_morphism,
    _correlation_isomorphism,
    _hodge_discriminant,
    _hodge_star,
    _hodge_star_over_fraction_field,
    _multivector_hodge_star,
)
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    ModuleMorphismMethods,
)
from sage_extensions.categories.modules.pure.modules import (
    MatrixSpaces,
    Modules,
    ModulesWithChosenFinitePresentation,
    RestrictedScalarsModules,
    TensorProductModules,
    VectorSpaces,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedFields,
    OwnedIntegralDomains,
    OwnedRings,
    _engine_element,
    _engine_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import Sets as OwnedSets
from sage_extensions.logic import AtomicProposition, Predicate, conjunction, negation
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.tensors.tensor import tensor
from sage_extensions.validation import validator

if TYPE_CHECKING:
    from sage.categories.category import Category

    from sage_extensions.owned_category import ConstructionData

for _form_axiom in ("Symmetric", "Nondegenerate", "Unimodular", "Even"):
    if _form_axiom not in all_axioms:
        all_axioms.add(_form_axiom)


def _is_bilinear_form(form) -> bool:

    return _form_is_bilinear(form)


def _is_quadratic_form(form) -> bool:

    return _form_is_quadratic(form)


def _has_finite_framing(module) -> bool:
    ring = module.base_ring()
    return (
        module.has_selected_module_resolution()
        and module.module_generating_set().cardinality().is_finite()
    )


def _relation_morphism(ring, relation_rows):
    r"""Return ``r: F(relations) -> F(module_generators)`` for a family of relation rows.

    Each row writes one relation by its coordinates in the module
    generators, so ``r`` sends the ``i``-th relation generator to the
    linear combination the ``i``-th row states.  This is the one place
    where relation rows enter as data; the presented module is ``coker(r)``.
    """

    rows = tuple(tuple(row) for row in relation_rows)
    target = ring.free_module(len(rows[0]) if rows else 0)
    source = ring.free_module(len(rows))
    return source.module_category().Mor(source, target)(
        {
            relation: target.linear_combination(
                {
                    label: ring(coefficient)
                    for label, coefficient in zip(
                        target.module_generating_set(), row, strict=True
                    )
                    if coefficient
                }
            )
            for relation, row in zip(source.module_generating_set(), rows, strict=True)
        }
    )


@cached_function(key=lambda formed_module: id(formed_module))
def _represented_value_module(formed_module):
    r"""Return the actual module object underlying a form's public value object."""
    return _represented_module(formed_module.value_module(), formed_module.base_ring())


@cached_function(key=lambda value, ring: (id(value), id(ring)))
def _represented_module(value, ring):
    r"""Return the ``ring``-module underlying the value object ``value`` of a pairing.

    A scalar-valued pairing publicly takes values in the ring ``R``.  When
    ``R`` is already carrying its canonical self-module structure it is
    returned directly; otherwise ``R.regular_module()`` supplies the canonical
    rank-one realization over itself.  Genuine module values are unchanged.
    """

    if value is ring:
        return ring.regular_module()
    if value in Modules(ring):
        return value
    if value in OwnedRings():
        try:
            scalar_map = OwnedRings().Mor(ring, value)(lambda scalar: value(scalar))
            return value.regular_module().restrict_scalars(scalar_map)
        except (TypeError, ValueError, NotImplementedError) as error:
            raise TypeError(
                f"the form value ring {value} does not carry the required represented {ring}-module structure"
            ) from error
    raise TypeError(
        f"a pairing takes values in {value}, which is neither an "
        f"{ring}-module nor a ring receiving a map from {ring}, so it cannot serve as a value module"
    )


def _value_as_module_element(formed_module, value):
    return _as_module_element(
        formed_module.value_module(), formed_module.base_ring(), value
    )


def _as_module_element(values, ring, value):
    r"""Return the pairing value ``value`` in ``values`` as an element of its represented ``ring``-module."""
    represented = _represented_module(values, ring)
    if represented is values:
        return represented(value)
    if values is ring:
        unit_label = represented.module_generating_set()[0]
        return represented.linear_combination({unit_label: ring(value)})
    extension = represented.module_over_extension()
    unit_label = extension.module_generating_set()[0]
    return represented.wrap(extension.linear_combination({unit_label: values(value)}))


def _value_from_module_element(formed_module, element):
    r"""Read a value through its actual regular or restricted-module realization."""
    represented = _represented_value_module(formed_module)
    values = formed_module.value_module()
    if represented is values:
        return represented(element)
    if values is formed_module.base_ring():
        coordinates = represented.framing_morphism().lift(represented(element))
        unit_label = represented.module_generating_set()[0]
        return values(coordinates(unit_label))

    extension = represented.module_over_extension()
    restricted_element = represented(element)
    coordinates = extension.framing_morphism().lift(
        restricted_element.underlying_element()
    )
    unit_label = extension.module_generating_set()[0]
    return values(coordinates(unit_label))


def _mapped_value(domain, codomain, value_morphism, value):
    r"""Return ``h(v)`` for a form value ``v`` of ``domain`` and the value map ``h``."""
    return _value_from_module_element(
        codomain, value_morphism(_value_as_module_element(domain, value))
    )


def _form_square_commutes(
    domain, codomain, module_morphism, value_morphism
) -> bool | Predicate:
    r"""Whether ``h(b_M(x, y)) = b_N(f(x), f(y))`` for the pair ``(f, h)`` from ``M`` to ``N``.

    When both forms are bilinear with values in the same R-algebra S,
    regarded as an R-module by restriction of scalars, ``h`` is the identity and
    ``f`` is a map of framed free modules of finite rank, the square is the
    tensor equation ``f^* G_N = G_M``: the Gram tensor of ``N`` pulled back
    along ``f`` is the Gram tensor of ``M``, and :meth:`Tensor.pullback` owns
    that contraction (``OWN-24``).  Otherwise no Gram tensor states the
    square, and a selected finite spanning family supplies the equations:
    a bilinear form is determined by its values on pairs of generators,
    and a quadratic form ``q`` by ``q(s)`` and ``q(s + t)``.  These finite
    equations prove the universal equation when both maps are known linear.
    A failed equation refutes it without that premise.  Missing finite data
    or unestablished linearity retains the form-square proposition; no
    infinite generating family or undecided equality is Boolean-coerced.
    """
    source_form = domain.form()
    target_form = codomain.form()
    values = value_morphism.domain()
    kind = _is_bilinear_form(source_form), _is_quadratic_form(source_form)
    match kind:
        case True, _ if not _is_bilinear_form(target_form):
            raise TypeError(
                f"{domain} has a bilinear form, so a morphism out of it must land in a "
                f"module with a bilinear form, but {codomain} has form {target_form}"
            )
        case _, True if not _is_quadratic_form(target_form):
            raise TypeError(
                f"{domain} has a quadratic form, so a morphism out of it must land in a "
                f"module with a quadratic form, but {codomain} has form {target_form}"
            )
        case (True, _) | (_, True):
            pass
        case _:
            raise TypeError(
                f"a morphism of formed modules requires a bilinear or quadratic form on its domain, "
                f"but {domain} has form {source_form}"
            )

    module_mor = domain.module_category().Mor(domain, codomain)
    value_identity = (
        values.module_category().Mor(values, values).identity()
        if value_morphism.codomain() is values
        else None
    )
    if (
        domain is codomain
        and module_morphism is module_mor.identity()
        and value_morphism is value_identity
    ):
        return True
    undecided = AtomicProposition(
        "form_square_commutes", domain, codomain, module_morphism, value_morphism
    )
    if not domain.has_selected_module_resolution():
        return undecided
    if domain.module_generating_set().is_finite() is not True:
        return undecided
    source_generators = tuple(domain.module_generators())
    established_linear = (
        isinstance(module_morphism, ModuleMorphismMethods)
        and isinstance(value_morphism, ModuleMorphismMethods)
        and module_morphism.linearity_decision() is True
        and value_morphism.linearity_decision() is True
    )
    algebra_values = source_form.codomain() in OwnedRings() or (
        source_form.codomain() in RestrictedScalarsModules(domain.base_ring())
        and source_form.codomain().module_over_extension() in OwnedRings()
    )
    match kind:
        case True, _ if (
            algebra_values
            and value_morphism is value_identity
            and module_mor in MatrixSpaces(domain.base_ring())
            and established_linear
        ):
            # Ordinary Mor admission retains stronger arrows.  The tensor
            # supplier requires the actual ordinary matrix realization.
            ordinary_map = module_morphism
            if module_morphism.parent() is not module_mor:
                ordinary_map = module_mor._from_constructed_element_map(
                    module_morphism, premises=(module_morphism,)
                )
            source_gram = domain.gram_tensor()
            pulled_back = codomain.gram_tensor().pullback(ordinary_map)
            rows, columns = map(int, source_gram.tensor_shape())
            equations = conjunction(
                pulled_back[row, column] == source_gram[row, column]
                for row in range(rows)
                for column in range(columns)
            )
        case True, _:
            equations = conjunction(
                _mapped_value(domain, codomain, value_morphism, domain.b(left, right))
                == codomain.b(module_morphism(left), module_morphism(right))
                for left in source_generators
                for right in source_generators
            )
        case _, True:
            probes = source_generators + tuple(
                left + right
                for index, left in enumerate(source_generators)
                for right in source_generators[index + 1 :]
            )
            equations = conjunction(
                _mapped_value(domain, codomain, value_morphism, domain.norm(element))
                == codomain.norm(module_morphism(element))
                for element in probes
            )
    if equations is False or established_linear:
        return equations
    return undecided


def _formed_component_map(domain, codomain, module_morphism):
    r"""Realize an underlying-module component on its formed endpoints."""
    if module_morphism.domain() is domain and module_morphism.codomain() is codomain:
        return module_morphism
    source_module = domain.unformed_module()
    target_module = codomain.unformed_module()
    if (
        module_morphism.domain() is not source_module
        or module_morphism.codomain() is not target_module
    ):
        raise ValueError(
            f"a formed-module component {domain} -> {codomain} must be a module map "
            f"{source_module} -> {target_module}, but {module_morphism} is "
            f"{module_morphism.domain()} -> {module_morphism.codomain()}"
        )
    return (
        domain.module_category()
        .Mor(domain, codomain)
        ._from_constructed_element_map(
            lambda element: codomain._element_from_unformed_module(
                module_morphism(domain._element_of_unformed_module(element))
            ),
            premises=(module_morphism,),
        )
    )


class FormedModuleMorphism:
    r"""A morphism of formed modules in one coefficient-ring fiber.

    The datum is a pair ``(f,h)`` with a module map on the underlying modules
    and a module map on the value objects that preserves the forms,
    ``h(b(x,y)) = b'(f(x),f(y))``.  Construction states this equation and does
    not compute it (``OWN-22``); :meth:`preserves_forms` computes it when asked.
    :meth:`preserves_form_exactly` asks whether ``h`` is the identity.
    This does not imply injectivity: the zero map on a nonzero module with
    zero form, together with the identity value map, preserves that form.
    """

    def __init__(self, parent, module_morphism, value_morphism) -> None:
        domain = parent.domain()
        codomain = parent.codomain()
        realized_module_morphism = _formed_component_map(
            domain, codomain, module_morphism
        )
        source_values = _represented_value_module(domain)
        target_values = _represented_value_module(codomain)
        if value_morphism.domain() is not source_values:
            raise ValueError(
                f"the value map {value_morphism} must start at the value module {source_values} of "
                f"{self.domain()}, but starts at {value_morphism.domain()}"
            )
        if value_morphism.codomain() is not target_values:
            raise ValueError(
                f"the value map {value_morphism} must end at the value module {target_values} of "
                f"{self.codomain()}, but ends at {value_morphism.codomain()}"
            )
        self._form_module_morphism = module_morphism
        self._value_morphism = value_morphism
        super().__init__(
            parent,
            lambda element: realized_module_morphism(element),
            elementwise=True,
            linearity_premises=(realized_module_morphism,),
        )

    def module_morphism(self):
        r"""Return the retained first component ``f`` of the defining pair ``(f,h)``.

        Its endpoints are the literal formed-module objects.  An admitted
        stronger module map keeps its original parent; the forgetful functor
        owns realization of this component in its ordinary module Mor.
        """
        return self._form_module_morphism

    def value_morphism(self):
        return self._value_morphism

    def preserves_form_exactly(self) -> bool | Predicate:
        r"""Return whether the value-object map is the identity."""
        value_morphism = self.value_morphism()
        values = value_morphism.domain()
        if value_morphism.codomain() is not values:
            return False
        if (
            hasattr(value_morphism, "is_identity")
            and value_morphism.is_identity() is True
        ):
            return True
        if value_morphism.parent().identity() is value_morphism:
            return True
        identity = values.module_category().Mor(values, values).identity()
        if value_morphism is identity:
            return True
        return value_morphism == identity

    def map_value(self, value):
        return _mapped_value(
            self.domain(), self.codomain(), self.value_morphism(), value
        )

    def base_change(
        self, ring_map: Morphism | CategoricalArrow
    ) -> "FormedModuleMorphism":
        r"""Extend both the module map and the value map along ``R -> S``.

        A formed morphism is a pair ``(f,h)`` satisfying the form square.
        Tensoring that square extends both components, as in
        ``Lattices/Valued/BaseChange.lean:baseChangeBilWForm``. The existing
        object construction currently computes scalar-valued forms. For
        these, the value map is multiplication by ``h(1)``, so its extension
        is multiplication by the image of ``h(1)`` in S. The result retains
        the literal scalar-extended endpoints and the module component's
        original map and scalar-extension functor.

        The result is a formed morphism. Tensoring need not preserve an
        embedding: a nonflat scalar change can destroy injectivity. The
        isometry specialization separately transports its inverse pair.
        Value-module extensions outside the existing object computation
        remain unsupported; they are not replaced by scalar values.

        EXAMPLES::

            sage: L = Lattices(ZZ)([[1]])
            sage: values = ZZ.regular_module()
            sage: f = L.module_category().Mor(L, L)(lambda label: 2*L.module_generator(label))
            sage: h = values.module_category().Mor(values, values)(lambda label: 4*values.module_generator(label))
            sage: a = FormModules(ZZ).Mor(L, L)((f, h))
            sage: scalar_map = ZZ.fraction_field_map()
            sage: b = a.base_change(scalar_map)
            sage: V = L.base_change(scalar_map)
            sage: assert b.domain() is V and b.codomain() is V
            sage: assert b.map_value(QQ(1)) == QQ(4)
            sage: assert b.module_morphism().scalar_extension_of() is a.module_morphism()
            sage: assert b.preserves_forms() is True
            sage: assert (a*a).base_change(scalar_map) == b*b
            sage: S = ZZ.quotient_ring(ZZ.ideal(2))
            sage: T = Lattices(ZZ)([[4]])
            sage: j = T.Emb(L)((2*L.module_generators()[0],))
            sage: reduced = j.base_change(S.quotient_map())
            sage: assert reduced.map_value(S.one()) == S.one()
            sage: assert reduced.is_injective() is False
            sage: assert reduced.preserves_forms() is True
        """
        source, target = self.domain(), self.codomain()
        ring = source.base_ring()
        if target.base_ring() is not ring or ring_map.domain() is not ring:
            raise ValueError(
                "a formed morphism is extended along a map out of its common scalar ring"
            )
        if ring_map.is_identity() is True:
            return self
        extension = Modules(ring).scalar_extension(ring_map)
        changed_source, changed_target = extension(source), extension(target)
        module_map = extension(self.module_morphism())
        multiplier = _base_change_scalar(ring_map, self.map_value(ring.one()))
        values = _represented_value_module(changed_source)
        value_map = values.module_category().Mor(values, values)(
            lambda label: values.scalar_multiple(
                multiplier, values.module_generator(label)
            )
        )
        return FormModules(ring_map.codomain()).Mor(changed_source, changed_target)(
            (module_map, value_map)
        )

    def is_injective(self) -> bool:
        r"""Return injectivity of the retained underlying-module component."""
        return self.module_morphism().is_injective()

    def preserves_forms(self) -> bool | Predicate:
        r"""Return whether ``h(b(x,y)) = b'(f(x),f(y))`` on the module generators.

        The caller's diagnostic of ``OWN-22``: construction does not compute
        it, and its answer is an untrusted computation.
        """
        return _form_square_commutes(
            self.domain(), self.codomain(), self, self.value_morphism()
        )

    @validator
    def validate_form_preservation(self) -> None:
        r"""Reject a false square; name the computation frontier when undecided."""
        decision = self.preserves_forms()
        if decision is False:
            raise ValueError(
                f"({self}, {self.value_morphism()}) is not a morphism of formed modules "
                f"{self.domain()} -> {self.codomain()}: the value map applied to the source form "
                f"is not the target form pulled back along the module map"
            )
        assert decision is True, (
            f"cannot decide form preservation of {self}: the retained form-square "
            "equations need a selected finite spanning computation and decided comparisons"
        )

    def __eq__(self, other) -> bool | Predicate:
        r"""A formed morphism is the pair ``(f,h)``; both components decide."""
        if not isinstance(other, FormedModuleMorphism):
            return False
        if self is other:
            return True
        if self.parent() is not other.parent():
            return False
        module_equal = ModuleMorphismMethods._richcmp_(self, other, op_EQ)
        return conjunction(
            (module_equal, self.value_morphism() == other.value_morphism())
        )

    def __ne__(self, other) -> bool | Predicate:
        return negation(self == other)

    __hash__ = None

    def __mul__(self, other):
        if not isinstance(other, FormedModuleMorphism):
            modules = Modules(self.domain().base_ring())
            ordinary = modules.Mor(
                self.domain(), self.codomain()
            )._from_constructed_element_map(self, premises=(self,))
            return ordinary * other
        if other.codomain() is not self.domain():
            raise ValueError(
                f"cannot compose {self} after {other}: the codomain {other.codomain()} of {other} "
                f"is not the domain {self.domain()} of {self}"
            )
        if self.parent().identity() is self:
            return other
        if other.parent().identity() is other:
            return self
        source = other.domain()
        target = self.codomain()
        modules = source.module_category()
        # The two actual identity components prove the unit law, including
        # on modules without a selected finite spanning family.
        for factor, remainder in ((self, other), (other, self)):
            if factor.domain() is factor.codomain():
                values = _represented_value_module(factor.domain())
                if (
                    factor._form_module_morphism
                    is modules.Mor(factor.domain(), factor.domain()).identity()
                    and factor.value_morphism()
                    is values.module_category().Mor(values, values).identity()
                ):
                    return remainder
        module_composite = modules.Mor(source, target)._from_constructed_element_map(
            lambda element: self(other(element)), premises=(self, other)
        )
        return FormModules(source.base_ring()).Mor(source, target)(
            (
                module_composite,
                self.value_morphism() * other.value_morphism(),
            )
        )


class FormEmbedding:
    r"""A form-preserving morphism whose module map is a monomorphism."""

    def __init__(
        self,
        parent,
        module_morphism,
        value_morphism,
        *,
        quadratic: bool | None = None,
        denominator_clearing=None,
    ) -> None:
        super().__init__(parent, module_morphism, value_morphism)
        if quadratic is None:
            domain = parent.domain()
            quadratic = domain in QuadraticFormModules(domain.base_ring())
        self._quadratic = bool(quadratic)
        self._denominator_clearing = denominator_clearing

    def scale(self):
        r"""The least positive denominator factor of a retained rational isometry."""
        if self._denominator_clearing is None:
            raise ValueError("this embedding has no denominator-clearing construction")
        return self._denominator_clearing[2]

    def rational_isometry(self):
        r"""The rational isometry from which this integral similarity was obtained."""
        if self._denominator_clearing is None:
            raise ValueError("this embedding has no denominator-clearing construction")
        return self._denominator_clearing[0]

    def clearing_ideal(self):
        if self._denominator_clearing is None:
            raise ValueError("this embedding has no denominator-clearing construction")
        return self._denominator_clearing[1]

    def multiplier(self):
        r"""The scalar multiplying the form, distinct from a denominator factor."""
        ring = self.domain().base_ring()
        if (
            self.domain().value_module() is not ring
            or self.codomain().value_module() is not ring
        ):
            raise TypeError(
                "a scalar multiplier requires forms valued in their common scalar ring"
            )
        return self.map_value(ring.one())

    @validator
    def validate_denominator_clearing(self):
        r"""Check the retained normalization and its defining scalar-extension equation."""
        if self._denominator_clearing is None:
            return
        rational, ideal, scale = self._denominator_clearing
        source, target = self.domain(), self.codomain()
        ring = source.base_ring()
        if scale <= ring.zero() or ideal != rational.denominator_ideal(source, target):
            raise ValueError(
                "the retained ideal must be the denominator ideal of the rational map"
            )
        if ring.ideal(scale) != ideal or self.multiplier() != scale * scale:
            raise ValueError(
                "the clearing factor must generate the denominator ideal and square to the multiplier"
            )
        fraction_map = ring.fraction_field_map()
        restrict = Modules(fraction_map.codomain()).restriction_of_scalars(fraction_map)
        from sage_extensions.categories.modules.pure.modules import (
            ModulesOverIntegralDomains,
        )

        extended = (
            restrict(rational)
            * ModulesOverIntegralDomains(ring)(source).generic_fibre_map()
        )
        integral = ModulesOverIntegralDomains(ring)(target).generic_fibre_map()
        for vector in source.module_generators():
            if integral(self(vector)) != extended.codomain().scalar_multiple(
                scale, extended(vector)
            ):
                raise ValueError(
                    "the embedding must equal the clearing factor times its retained rational map"
                )

    def is_quadratic(self) -> bool:
        return self._quadratic

    @validator
    def validate_injectivity(self) -> None:
        r"""Check the first component's injectivity, retaining an unresolved decision."""
        domain = self.domain()
        codomain = self.codomain()
        injective = self.module_morphism().is_injective()
        if injective is False:
            raise ValueError(
                f"{self} is not a form-preserving embedding {domain} -> {codomain}: "
                "its module map is not injective"
            )
        assert injective is True, (
            f"cannot decide injectivity of the module component of {self}: "
            "its selected injectivity computation remains unresolved"
        )

    @cached_method
    def orthogonal_complement(self):
        r"""Return the orthogonal complement of this embedded formed submodule.

        For ``i:S -> M`` this is the kernel of the pairing morphism
        ``M -> S^vee``, ``x |-> (s |-> b_M(x,i(s)))``.  The kernel computation
        belongs to the module-morphism owner; its image in ``M`` is then
        equipped with the restricted form by ``M.subobject_on``.
        """
        source = self.domain()
        target = self.codomain()
        if source not in FreeFormModules(source.base_ring()).FinitelyGenerated():
            raise TypeError(
                f"the orthogonal complement of {self} is computed only for a finitely generated free "
                f"formed domain, but {source} is in {source.category()}"
            )
        if target not in FreeFormModules(target.base_ring()).FinitelyGenerated():
            raise TypeError(
                f"the orthogonal complement of {self} is computed only in a finitely generated free "
                f"formed module, but {target} is in {target.category()}"
            )
        if source.value_module() is not source.base_ring():
            raise TypeError(
                f"the orthogonal complement of {self} is computed only for forms valued in the base ring "
                f"{source.base_ring()}, but the form on {source} takes values in {source.value_module()}"
            )
        if target.value_module() is not target.base_ring():
            raise TypeError(
                f"the orthogonal complement of {self} is computed only for forms valued in the base ring "
                f"{target.base_ring()}, but the form on {target} takes values in {target.value_module()}"
            )
        if source.base_ring() is not target.base_ring():
            raise TypeError(
                f"the orthogonal complement of {self} needs source and target over one base ring, "
                f"but {source} is over {source.base_ring()} and {target} is over {target.base_ring()}"
            )

        dual = source.dual_module()
        images = {}
        source_labels = tuple(source.module_generating_set())
        for target_label in target.module_generating_set():
            target_generator = target.module_generator(target_label)
            images[target_label] = dual.linear_combination(
                {
                    source_label: coefficient
                    for source_label in source_labels
                    if (
                        coefficient := target.b(
                            target_generator,
                            self(source.module_generator(source_label)),
                        )
                    )
                }
            )
        pairing = target.module_category().Mor(target, dual)(images)
        kernel = pairing.kernel()
        kernel_inclusion = kernel.inclusion()
        return target.subobject_on(
            tuple(
                kernel_inclusion(generator) for generator in kernel.module_generators()
            )
        )


class FormEmbeddingMor(CategoricalMor):
    r"""The form-preserving monomorphisms between two formed modules."""

    ElementMethods = FormEmbedding

    def __init__(self, mor_family, domain, codomain) -> None:
        ring = domain.base_ring()
        formed = FormModules(ring)
        if (
            codomain.base_ring() is not ring
            or domain not in formed
            or codomain not in formed
        ):
            raise TypeError(
                f"form-preserving embeddings {domain} -> {codomain} need two modules with forms over one "
                f"base ring {ring}, but they lie in {domain.category()} and {codomain.category()}"
            )
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def __call__(self, images, *, value_morphism=None, **kwargs):
        if (
            isinstance(images, (Morphism, CategoricalArrow))
            and value_morphism is not None
        ):
            return super().__call__((images, value_morphism), **kwargs)
        return super().__call__(images, value_morphism=value_morphism, **kwargs)

    def _element_constructor_(
        self,
        images,
        *,
        quadratic: bool | None = None,
        value_morphism=None,
        denominator_clearing=None,
        check=False,
    ):
        domain = self.domain()
        codomain = self.codomain()
        if (
            isinstance(images, tuple)
            and len(images) == 2
            and all(isinstance(part, (Morphism, CategoricalArrow)) for part in images)
        ):
            images, value_morphism = images
        elif isinstance(images, (Morphism, CategoricalArrow)):
            if self._already_parented_arrow(images):
                images.validate_form_preservation(check=check)
                images.validate_injectivity(check=check)
                images.validate_denominator_clearing(check=check)
                return images
            raise TypeError(
                f"{images} is not an arrow of {self}; give the module and value maps as defining data"
            )

        if quadratic is None:
            ring = domain.base_ring()
            quadratic = domain in QuadraticFormModules(ring)
        values = _represented_value_module(domain)
        if _represented_value_module(codomain) is not values:
            raise TypeError(
                f"a form-preserving embedding {domain} -> {codomain} needs both forms valued in one module, "
                f"but they take values in {values} and {_represented_value_module(codomain)}"
            )
        module_morphism = domain.module_category().Mor(domain, codomain)(images)
        if value_morphism is None:
            value_morphism = values.module_category().Mor(values, values).identity()
        embedding = self.element_class(
            self,
            module_morphism,
            value_morphism,
            quadratic=quadratic,
            denominator_clearing=denominator_clearing,
        )
        embedding.validate_form_preservation(check=check)
        embedding.validate_injectivity(check=check)
        embedding.validate_denominator_clearing(check=check)
        return embedding

    def super_categories(self):
        packet = self.base_category().category_packet()
        source = self.domain()
        target = self.codomain()
        inherited = [
            superpacket.Monos().Of(source, target)
            for superpacket in packet.super_packets()
            if source in superpacket.C() and target in superpacket.C()
        ]
        return [packet.Mors().Of(source, target), *inherited]

    def _repr_(self):
        return f"Emb_Form({self.domain()}, {self.codomain()})"


class FormedModuleMor(CategoricalMor):
    ElementMethods = FormedModuleMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        if domain.base_ring() != codomain.base_ring():
            raise ValueError(
                f"morphisms of formed modules {domain} -> {codomain} need one base ring, but {domain} is "
                f"over {domain.base_ring()} and {codomain} is over {codomain.base_ring()}"
            )
        CategoricalMor.__init__(
            self,
            mor_family,
            domain,
            codomain,
        )

    def _element_constructor_(self, datum, *, check=False):

        explicit_pair = (
            isinstance(datum, tuple)
            and len(datum) == 2
            and all(isinstance(part, (Morphism, CategoricalArrow)) for part in datum)
        )
        if (
            not explicit_pair
            and not isinstance(datum, FormedModuleMorphism)
            and not isinstance(datum, ModuleMorphismMethods)
        ):
            domain = self.domain()
            codomain = self.codomain()
            module_morphism = domain.module_category().Mor(domain, codomain)(datum)
            source_values = _represented_value_module(domain)
            target_values = _represented_value_module(codomain)
            if source_values is not target_values:
                raise TypeError(
                    f"{self} requires an explicit value map between {source_values} and {target_values}"
                )
            datum = (
                module_morphism,
                source_values.module_category()
                .Mor(source_values, target_values)
                .identity(),
            )

        if isinstance(datum, (Morphism, CategoricalArrow)):
            if self._already_parented_arrow(datum):
                datum.validate_form_preservation(check=check)
                return datum
            raise TypeError(
                f"{datum} is not an arrow of {self}; give the module and value maps as defining data"
            )
        module_morphism, value_morphism = datum
        morphism = self.element_class(self, module_morphism, value_morphism)
        morphism.validate_form_preservation(check=check)
        return morphism

    def preserves_forms(self, module_morphism) -> bool | Predicate:
        r"""Whether the module map ``f: M -> N`` preserves the forms: ``b_N(f(x), f(y)) = b_M(x, y)``.

        These are the module maps that underlie the elements of this Mor
        object whose value map is the identity, so the answer says whether
        ``self(f)`` exists.  Both forms take values in one module.
        """
        domain = self.domain()
        codomain = self.codomain()
        assert (
            module_morphism.domain() is domain
            and module_morphism.codomain() is codomain
        ), (
            f"{self} preserves forms along module maps {domain} -> {codomain}, but {module_morphism} is "
            f"{module_morphism.domain()} -> {module_morphism.codomain()}"
        )
        values = _represented_value_module(domain)
        assert _represented_value_module(codomain) is values, (
            f"the forms of {domain} and {codomain} take values in {values} and "
            f"{_represented_value_module(codomain)}, so a module map alone does not compare them"
        )
        return _form_square_commutes(
            domain,
            codomain,
            module_morphism,
            values.module_category().Mor(values, values).identity(),
        )

    @object_level
    @cached_method
    def identity(self):

        domain = self.domain()
        values = _represented_value_module(domain)
        return self(
            (
                domain.module_category().Mor(domain, domain).identity(),
                values.module_category().Mor(values, values).identity(),
            )
        )


class FormedModuleMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return FormedModuleMor


class FormedModuleMonoCategoryConstruction(MonoCategoryConstruction):
    r"""The form-preserving monomorphisms of formed modules."""

    def fixed_category_class(self):
        return FormEmbeddingMor


class FiberedFormedModuleMorphism:
    r"""A formed-module morphism over a coefficient-ring map ``g:S1 -> S2``.

    The actual linear data live in the target fiber, exactly as required by
    the Grothendieck/fibered-category formulation:

    ``module_morphism : S2 tensor_S1 L1 -> L2`` and
    ``value_morphism  : S2 tensor_S1 W1 -> W2``.

    The represented scalar-extension computation currently materializes this for the
    scalar-valued finite-free formed objects supported by ``FormModules(R)``'s
    ``base_change`` method.  Unsupported scalar extensions fail at object
    construction rather than being represented by a semilinear fiction.
    """

    def __init__(self, parent, module_morphism, value_morphism) -> None:
        domain = parent.domain()
        codomain = parent.codomain()
        changed = parent.base_changed_domain()
        realized_module_morphism = _formed_component_map(
            changed, codomain, module_morphism
        )
        source_values = _represented_value_module(changed)
        target_values = _represented_value_module(codomain)
        if value_morphism.domain() is not source_values:
            raise ValueError(
                f"the value map {value_morphism} must start at the value module {source_values} of the "
                f"scalar extension {changed}, but starts at {value_morphism.domain()}"
            )
        if value_morphism.codomain() is not target_values:
            raise ValueError(
                f"the value map {value_morphism} must end at the value module {target_values} of "
                f"{codomain}, but ends at {value_morphism.codomain()}"
            )
        self._form_module_morphism = module_morphism
        self._value_morphism = value_morphism
        module_mor = parent.module_mor()
        compatible = module_mor.base_change_adjunction(
            parent.ring_map()
        ).mor_set_isomorphism_forward(
            realized_module_morphism,
            domain,
        )
        super().__init__(parent, parent.ring_map(), compatible)

    def ring_map(self):
        return self.parent().ring_map()

    def base_changed_domain(self):
        return self.parent().base_changed_domain()

    def value_morphism(self):
        return self._value_morphism

    def module_morphism(self):
        r"""Return the retained module component of the defining pair."""
        return self._form_module_morphism

    def underlying_semilinear_morphism(self):
        r"""Return this arrow with only its semilinear module structure read."""
        from sage_extensions.categories.modules.fibered_modules import (
            ModulesOverCommutativeRings,
        )

        source = self.domain().unformed_module()
        target = self.codomain().unformed_module()
        mor = ModulesOverCommutativeRings().Mor(source, target)
        return mor._from_linearization(self.ring_map(), self.module_morphism())

    def preserves_form_exactly(self) -> bool | Predicate:
        r"""Return whether the retained value component is an identity."""
        value_morphism = self.value_morphism()
        values = value_morphism.domain()
        if value_morphism.codomain() is not values:
            return False
        if (
            hasattr(value_morphism, "is_identity")
            and value_morphism.is_identity() is True
        ):
            return True
        if value_morphism.parent().identity() is value_morphism:
            return True
        identity = values.module_category().Mor(values, values).identity()
        if value_morphism is identity:
            return True
        return value_morphism == identity

    def __eq__(self, other) -> bool | Predicate:
        r"""Compare both the semilinear and value components of a formed pair."""
        if not isinstance(other, FiberedFormedModuleMorphism):
            return False
        if self is other:
            return True
        if self.parent() is not other.parent():
            return False
        from sage_extensions.categories.modules.fibered_modules import (
            SemilinearModuleMorphism,
        )

        module_equal = SemilinearModuleMorphism._richcmp_(self, other, op_EQ)
        return conjunction(
            (module_equal, self.value_morphism() == other.value_morphism())
        )

    def __ne__(self, other) -> bool | Predicate:
        return negation(self == other)

    __hash__ = None

    def map_value(self, value):
        changed = self.base_changed_domain()
        source_element = _value_as_module_element(changed, value)
        return _value_from_module_element(
            self.codomain(), self.value_morphism()(source_element)
        )

    def preserves_forms(self) -> bool | Predicate:
        r"""Return whether ``h(b(x,y)) = b'(f(x),f(y))`` on generators of the scalar extension.

        The caller's diagnostic of ``OWN-22``: construction does not compute
        it, and its answer is an untrusted computation.
        """
        return _form_square_commutes(
            self.base_changed_domain(),
            self.codomain(),
            self.linearization(),
            self.value_morphism(),
        )

    @validator
    def validate_form_preservation(self):
        r"""Reject a false scalar-extended square; retain its computation frontier."""
        decision = self.preserves_forms()
        if decision is False:
            raise ValueError(
                f"({self.linearization()}, {self.value_morphism()}) is not a morphism of formed modules "
                f"{self.base_changed_domain()} -> {self.codomain()} over {self.ring_map()}: the value map "
                f"applied to the source form is not the target form pulled back along the module map"
            )
        return decision

    def __mul__(self, other):
        if not isinstance(other, FiberedFormedModuleMorphism):
            return NotImplemented
        if other.codomain() is not self.domain():
            raise ValueError(
                f"cannot compose {self} after {other}: the codomain {other.codomain()} of {other} "
                f"is not the domain {self.domain()} of {self}"
            )
        if getattr(self, "_preamble_fibered_formed_identity", False):
            return other
        if getattr(other, "_preamble_fibered_formed_identity", False):
            return self
        composite_ring_map = self.ring_map() * other.ring_map()
        mor = other.domain().fibered_formed_mor(self.codomain(), composite_ring_map)

        direct_changed = mor.base_changed_domain()
        middle_changed = self.base_changed_domain()
        from sage_extensions.categories.modules.fibered_modules import (
            SemilinearModuleMorphism,
        )

        module_semilinear = SemilinearModuleMorphism.__mul__(self, other)
        module_map = module_semilinear.linearization()
        if module_map.domain() is not direct_changed:
            raise ValueError(
                f"composing {self} after {other}: the linearized module map starts at "
                f"{module_map.domain()}, not at the scalar extension {direct_changed} of {other.domain()} "
                f"along {composite_ring_map}"
            )

        other_values = _represented_value_module(other.base_changed_domain())
        middle_values = _represented_value_module(self.domain())
        lifted_middle_values = _represented_value_module(middle_changed)
        direct_values = _represented_value_module(direct_changed)
        target_values = _represented_value_module(self.codomain())
        value_images = {}
        for label in direct_values.module_generating_set():
            # All currently materialized cross-fiber value objects are the
            # rank-one scalar module, but retain the generic framed spelling.
            source_value = other_values.module_generator(label)
            middle_value = other.value_morphism()(source_value)
            lifted_value = _base_change_element(
                middle_values,
                lifted_middle_values,
                self.ring_map(),
                middle_value,
            )
            value_images[label] = self.value_morphism()(lifted_value)
        value_map = direct_values.module_category().Mor(direct_values, target_values)(
            value_images
        )
        return mor((module_map, value_map))


class FiberedFormedModuleMor(CategoricalMor):
    ElementMethods = FiberedFormedModuleMorphism

    def __init__(self, domain, codomain, ring_map) -> None:

        target_ring = _base_change_codomain(domain, ring_map)
        if target_ring != codomain.base_ring():
            raise ValueError(
                f"the ring map {ring_map} sends {domain.base_ring()} to {target_ring}, "
                f"not to the base ring {codomain.base_ring()} of {codomain}"
            )
        from sage_extensions.categories.modules.fibered_modules import (
            ModulesOverCommutativeRings,
        )

        self._ring_map = ring_map
        self._module_mor = ModulesOverCommutativeRings().Mor(domain, codomain)
        self._base_changed_domain = self._module_mor.extended_domain(ring_map)
        # The endpoints sit over different base rings; the Mor is filed under
        # the Mor category of the source fibre.
        CategoricalMor.__init__(
            self,
            FormModules(domain.base_ring()).MorCategory(),
            domain,
            codomain,
            category=MorCategories(),
        )

    def ring_map(self):
        return self._ring_map

    def base_changed_domain(self):
        return self._base_changed_domain

    def module_mor(self):
        r"""Return the underlying Mor in the varying-ring module category."""
        return self._module_mor

    def super_categories(self):
        r"""The lower arrow theory is the varying-ring semilinear module Mor.

        EXAMPLES::

            sage: L = Lattices(ZZ)("U")
            sage: C = FiberedFormedModuleMor(L, L.vector_space(), ZZ.fraction_field_map())
            sage: C.super_categories()[0] is C.module_mor()
            True
            sage: C.domain() is L and C.codomain() is L.vector_space()
            True
        """
        return [self.module_mor()]

    def _element_constructor_(self, datum, *, check=False):
        if isinstance(datum, FiberedFormedModuleMorphism) and datum.parent() is self:
            datum.validate_form_preservation(check=check)
            return datum
        module_morphism, value_morphism = datum
        morphism = self.element_class(self, module_morphism, value_morphism)
        morphism.validate_form_preservation(check=check)
        return morphism

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"{self} has no identity: its domain {self.domain()} differs from its codomain {self.codomain()}"
            )
        identity_decision = self.ring_map().is_identity()
        if identity_decision is False:
            raise ValueError(
                f"{self} has no identity: it lies over the ring map {self.ring_map()}, "
                "which is not the identity"
            )
        assert identity_decision is True, (
            f"constructing the identity of {self} requires deciding whether {self.ring_map()} is the identity"
        )

        changed = self.base_changed_domain()
        module_map = self.module_mor().identity().linearization()
        if module_map.domain() is not changed:
            raise ValueError(
                f"the identity of {self} linearizes to a module map starting at {module_map.domain()}, "
                f"not at the scalar extension {changed} of {self.domain()} along {self.ring_map()}"
            )
        source_values = _represented_value_module(changed)
        target_values = _represented_value_module(self.domain())
        value_map = source_values.module_category().Mor(source_values, target_values)(
            {
                label: target_values.module_generator(label)
                for label in source_values.module_generating_set()
            }
        )
        identity = self((module_map, value_map))
        identity._preamble_fibered_formed_identity = True
        return identity


def _value_module_of(value_object):
    r"""The module a pairing takes values in; a ring names its regular module."""
    if value_object in OwnedRings():
        return value_object.regular_module()
    return value_object


class PairingObjects(OwnedCategoryOverBaseRing):
    r"""Module objects carrying one represented pairing ``X tensor_R Y -> W``."""

    def _repr_object_names(self):
        return f"pairing-bearing module objects over {self.base_ring()}"

    def an_object(self):
        return PairedModules(self.base_ring()).an_object()

    def super_categories(self):
        return [Modules(self.base_ring())]

    class ParentMethods:
        def pairing(self, left, right):
            r"""Evaluate this object's selected pairing on ``(left,right)``."""
            return self._pairing_value(left, right)

        def left_module(self):
            r"""Return the left module of the selected pairing."""
            return self._pairing_left_module()

        def right_module(self):
            r"""Return the right module of the selected pairing."""
            return self._pairing_right_module()

        def value_module(self):
            r"""Return the value module of the selected pairing."""
            return self._pairing_value_module()

        def is_base_ring_valued(self) -> bool:
            r"""Decide whether the selected finite pairing tensor has entries in the base ring.

            Bilinearity makes the generator-pair values sufficient.  For a
            scalar-valued form, these values are *already* its defining
            covariant tensor: testing its entries must not evaluate the
            classifying Hom on all pairs of generators a second time.
            """
            match (
                self.left_module() is self.right_module() and self.left_module() is self
            ):
                case True:
                    pass
                case False:
                    raise TypeError(
                        f"base-ring-valuedness here is defined for a formed module pairing itself, but {self} pairs {self.left_module()} and {self.right_module()}"
                    )
            match self.module_rank().is_finite():
                case True:
                    ring = self.base_ring()
                    form = self.form()
                    if _is_bilinear_form(form):
                        from sage_extensions.tensors.tensor import Tensor

                        gram = form._as_numerical_tensor()
                        if not isinstance(gram, Tensor):
                            return all(
                                self.b(left, right) in ring
                                for left in self.module_generators()
                                for right in self.module_generators()
                            )
                        size = int(self.module_rank())
                        return all(
                            gram[i, j] in ring for i in range(size) for j in range(size)
                        )
                    generators = tuple(self.module_generators())
                    return all(
                        self.b(left, right) in ring
                        for left in generators
                        for right in generators
                    )
                case False:
                    raise ValueError(
                        f"cannot decide whether the form on {self} is base-ring-valued from a finite framing: the module has infinite rank"
                    )

        @cached_method
        def left_curry(self):
            r"""Return ``X -> Hom_R(Y,W)``, ``x |-> (y |-> b(x,y))``."""
            left = self.left_module()
            right = self.right_module()
            pairing_values = self._pairing_value_module()
            ring = self.base_ring()
            values = _represented_module(pairing_values, ring)
            internal_mor = right.module_category().Mor(right, values)
            return (
                left.module_category()
                .Mor(left, internal_mor)
                ._from_constructed_element_map(
                    lambda left_element: internal_mor._from_constructed_element_map(
                        lambda right_element: _as_module_element(
                            pairing_values,
                            ring,
                            self.pairing(left_element, right_element),
                        )
                    )
                )
            )

        @cached_method
        def right_curry(self):
            r"""Return ``Y -> Hom_R(X,W)``, ``y |-> (x |-> b(x,y))``."""
            left = self.left_module()
            right = self.right_module()
            pairing_values = self._pairing_value_module()
            ring = self.base_ring()
            values = _represented_module(pairing_values, ring)
            internal_mor = left.module_category().Mor(left, values)
            return (
                right.module_category()
                .Mor(right, internal_mor)
                ._from_constructed_element_map(
                    lambda right_element: internal_mor._from_constructed_element_map(
                        lambda left_element: _as_module_element(
                            pairing_values,
                            ring,
                            self.pairing(left_element, right_element),
                        )
                    )
                )
            )

        @cached_method
        def left_radical(self):
            r"""Return ``ker(X -> Hom_R(Y,W))`` for the selected pairing."""
            return self.left_curry().kernel()

        @cached_method
        def right_radical(self):
            r"""Return ``ker(Y -> Hom_R(X,W))`` for the selected pairing."""
            return self.right_curry().kernel()


class PairedModules(OwnedParameterizedCategory):
    r"""Pairings \(X\otimes_R Y\to W\), the comma category of the tensor functor over ``W``.

    An object is a morphism ``X (x) Y -> W`` of ``Modules(R)``, so its
    underlying arrow is an object of the slice ``Modules(R)/W``.  A ring
    given as the parameter names its regular module.  Equipping ``X`` with
    a pairing ``X (x) X -> W`` is :class:`FormModules`.
    """

    @staticmethod
    def __classcall__(cls, value_module):
        return OwnedParameterizedCategory.__classcall__(
            cls, _value_module_of(value_module)
        )

    @classmethod
    def _repr_object_names(cls):
        return "paired modules"

    def parameter_category(self):
        return Modules(self.base_ring())

    def base_ring(self):
        return self.base().base_ring()

    def super_categories(self):
        return [
            Modules(self.base_ring()).SliceOver(self.base()),
            PairingObjects(self.base_ring()),
        ]

    def an_object(self):
        r"""``R (x) R -> W`` sending the pure tensor of the units to a chosen element of ``W``."""
        ring = self.base_ring()
        regular = ring.regular_module()
        square = Modules(ring).tensor_product((regular, regular))
        value = self.base()
        return self(
            square.module_category().Mor(square, value)(
                {label: value.an_element() for label in square.module_generating_set()}
            )
        )

    def _call_(self, pairing):
        r"""The pairing classified by a morphism out of a represented tensor product.

        A ring-valued pairing ``X x Y -> R`` arrives as the form object of
        ``X.pairings_with(Y, R)``; its arrow into the regular module ``R`` is
        built here from its values on the tensor generators.
        """
        ring = self.base_ring()
        value = self.base()
        assert _value_module_of(pairing.codomain()) is value, (
            f"a pairing in {self} takes values in {value}, not {pairing.codomain()}"
        )
        if pairing.codomain() is not value:
            square = Modules(ring).tensor_product(
                (pairing.left_module(), pairing.right_module())
            )
            left, right = square.tensor_factor(0), square.tensor_factor(1)
            pairing = square.module_category().Mor(square, value)(
                lambda pair: value(
                    (
                        pairing(
                            left.module_generator(pair.component(0)),
                            right.module_generator(pair.component(1)),
                        ),
                    )
                )
            )
        assert pairing.parent().mor_category().is_subcategory(Modules(ring)), (
            f"a pairing in {self} is a morphism of {Modules(ring)}; {pairing} is not one: "
            f"it lies in {pairing.parent()}"
        )
        assert pairing.domain() in TensorProductModules(ring), (
            f"a pairing in {self} is a morphism out of a tensor product of {ring}-modules, "
            f"but {pairing} has domain {pairing.domain()} in {pairing.domain().category()}"
        )
        # A paired module is the tensor product ``X (x) Y`` with its arrow
        # to ``W``: the module owner constructs it on that tensor product.
        return Modules(ring).SliceOver(value).object(pairing, categories=(self,))

    class ParentMethods:
        def _pairing_value(self, left, right):
            return self.arrow()(self.arrow().domain().pure_tensor(left, right))

        def _pairing_left_module(self):
            return self.arrow().domain().tensor_factor(0)

        def _pairing_right_module(self):
            return self.arrow().domain().tensor_factor(1)

        def _pairing_value_module(self):
            return self.arrow().codomain()

        def _repr_(self) -> str:
            return (
                f"Pairing {self.left_module()} ⊗ {self.right_module()} "
                f"-> {self.value_module()}"
            )


def _base_changed_scalar_gram(source, ring_map):
    r"""Map a finite scalar Gram along the selected map, including noncanonical maps."""
    rank = int(source.module_rank())
    gram = source.gram_tensor()
    return tensor(
        ring_map.codomain(),
        (),
        (rank, rank),
        (
            _base_change_scalar(ring_map, gram[i, j])
            for i in range(rank)
            for j in range(rank)
        ),
    )


@cached_function(key=lambda source, ring_map: (id(source), id(ring_map)))
def _formed_module_base_change(self, ring_map):
    r"""Base-change a scalar-valued finite free form along ``R -> S``."""

    assert self.value_module() is self.base_ring()
    target_ring = _base_change_codomain(self, ring_map)
    if ring_map.is_identity() is True:
        return self
    source = self
    source_labels = source.module_generating_set()
    form = self.form()
    changed = form.module().base_change(ring_map)

    def equip(changed_form):
        from sage_extensions.categories._lattice import _BaseChangedGram
        from sage_extensions.categories.lattices import Lattices

        categories = [FormBaseChanges(target_ring)]
        data = dict(base_change_source=source, base_change_ring_map=ring_map)
        if _has_finite_framing(form.module()):
            if source in FormModules(source.base_ring()).Unimodular():
                # In a finite basis the determinant is a unit, and its
                # image under every unital ring map remains a unit.
                categories.append(FormModules(target_ring).Unimodular())
            elif (
                source in FormModules(source.base_ring()).Nondegenerate()
                and target_ring in OwnedIntegralDomains()
                and _base_change_scalar(ring_map, source.determinant())
                != target_ring.zero()
            ):
                # Over a domain, the nonzero image of this finite Gram
                # determinant is the exact target nondegeneracy witness.
                categories.append(FormModules(target_ring).Nondegenerate())
        if source in BilinearFormModules(source.base_ring()).Symmetric():
            categories.append(BilinearFormModules(target_ring).Symmetric())
        if source in Lattices(source.base_ring()):
            categories.append(Lattices(target_ring))
            data["gram_tensor"] = (
                _base_changed_scalar_gram(source, ring_map)
                if source.module_rank().is_finite()
                else _BaseChangedGram(
                    changed, source.gram_tensor(), ring_map, changed_form
                )
            )
        return _form_module(
            changed_form, _extra_categories=categories, _extra_construction_data=data
        )

    if _is_bilinear_form(form):
        target_values = _represented_module(target_ring, target_ring)
        if _has_finite_framing(form.module()):
            changed_values = form.coordinate_values().map(
                lambda value: _as_module_element(
                    target_ring,
                    target_ring,
                    _base_change_scalar(
                        ring_map, _value_from_module_element(source, value)
                    ),
                ),
                name="Base-changed bilinear coordinate values",
            )
            return equip(changed.bilinear_forms(target_values)(changed_values))

        def changed_bilinear_value(left, right):
            left_coordinates = changed(left).to_vector()
            right_coordinates = changed(right).to_vector()
            result = target_ring.zero()
            for left_label in left_coordinates.support().domain():
                source_left = form.module().module_generator(left_label)
                for right_label in right_coordinates.support().domain():
                    source_right = form.module().module_generator(right_label)
                    result += (
                        left_coordinates(left_label)
                        * right_coordinates(right_label)
                        * _base_change_scalar(
                            ring_map,
                            _value_from_module_element(
                                source, form(source_left, source_right)
                            ),
                        )
                    )
            return _as_module_element(target_ring, target_ring, result)

        return equip(changed.bilinear_forms(target_values)(changed_bilinear_value))

    if not _is_quadratic_form(form):
        raise TypeError(
            f"base change along {ring_map} is defined for bilinear and quadratic forms, "
            f"but the form {form} on {self} is neither"
        )

    source_form = self.form()
    target_values = _represented_module(target_ring, target_ring)
    if source_form.has_selected_bilinear_lift():
        changed_lift_values = source_form.lift_coordinate_values().map(
            lambda value: _as_module_element(
                target_ring,
                target_ring,
                _base_change_scalar(
                    ring_map, _value_from_module_element(source, value)
                ),
            ),
            name="Base-changed quadratic-lift coordinate values",
        )
        return equip(changed.quadratic_forms(target_values)(changed_lift_values))

    def changed_quadratic_value(element):
        coordinates = changed(element).to_vector()
        result = target_ring.zero()
        for left_label in coordinates.support().domain():
            source_left = form.module().module_generator(left_label)
            result += coordinates(left_label) ** 2 * _base_change_scalar(
                ring_map, _value_from_module_element(source, form(source_left))
            )
            left_rank = source_labels.ranking_map()(left_label)
            for right_label in coordinates.support().domain():
                if source_labels.ranking_map()(right_label) <= left_rank:
                    continue
                source_right = form.module().module_generator(right_label)
                result += (
                    coordinates(left_label)
                    * coordinates(right_label)
                    * _base_change_scalar(
                        ring_map,
                        _value_from_module_element(
                            source, form.b(source_left, source_right)
                        ),
                    )
                )
        return _as_module_element(target_ring, target_ring, result)

    return equip(changed.quadratic_map(target_values, changed_quadratic_value))


class FormModules(OwnedCategoryOverBaseRing):
    r"""Modules over ``R`` equipped with a form.

    ``FormModules(R)(b)`` for a form ``b`` stated on ``M`` is the one entry:
    the formed module is built on the data of ``M``, retains ``M`` as its
    datum and answers ``unformed_module()`` with it, and elements pass
    between the two by coercion, ``F(m)`` and ``M(f)``.
    """

    def an_object(self):
        r"""Return the bilinear owner's formed-module witness over this base."""
        return BilinearFormModules(self.base_ring()).an_object()

    def _repr_object_names(self):
        return f"form modules over {self.base_ring()}"

    def super_categories(self):
        return [
            Modules(self.base_ring()),
            PairingObjects(self.base_ring()),
        ]

    def _call_(
        self,
        form,
        *,
        _extra_categories=(),
        _extra_construction_data=None,
        _subobject_ambient=None,
        _subobject_generator_images=None,
        _subobject_lift=None,
        _subobject_inclusion_factory=None,
    ):
        r"""Equip the module classified by ``form`` with that selected form."""
        # A formed module is the pair (M,b), where b is already an element
        # of Hom_R(M tensor M,W) or Hom_R(Gamma^2 M,W).  Bare tensors,
        # functions and other maps do not construct this pair: their owner
        # is the relevant Mor's element constructor.
        from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
            ModuleMorphismMethods,
        )

        if not isinstance(form, ModuleMorphismMethods):
            raise TypeError(
                f"{self} takes an already constructed module Hom element b, not a callable or tensor: "
                f"first construct b in M.bilinear_hom_space(W)"
            )
        if form.codomain() not in Modules(self.base_ring()):
            raise TypeError(
                f"the value object {form.codomain()} of {form} is not an {self.base_ring()}-module"
            )
        if _is_bilinear_form(form):
            module = form.module()
            if form.parent() is not module.bilinear_hom_space(form.codomain()):
                raise TypeError(
                    f"{form} is not an element of the chosen bilinear Hom of {module}"
                )
        elif _is_quadratic_form(form):
            module = form.module()
        else:
            raise TypeError(f"{form} is not a bilinear or quadratic module-Hom element")
        if module.base_ring() is not self.base_ring():
            raise ValueError(
                f"{self} is over {self.base_ring()}, but the form {form} is on {module}, "
                f"which is over {module.base_ring()}"
            )
        return _form_module(
            form,
            _extra_categories=(self, *tuple(_extra_categories)),
            _extra_construction_data=_extra_construction_data,
            _subobject_ambient=_subobject_ambient,
            _subobject_generator_images=_subobject_generator_images,
            _subobject_lift=_subobject_lift,
            _subobject_inclusion_factory=_subobject_inclusion_factory,
        )

    _MorCategory = FormedModuleMorCategoryConstruction
    _MonoCategory = FormedModuleMonoCategoryConstruction

    class ParentMethods:
        def __init__(
            self,
            source_form,
            source_form_computation=None,
            radical_quotient_cokernel_projection=None,
            radical_quotient_basis_map=None,
            **rest,
        ) -> None:
            r"""Retain the selected form, or its defining-data computation."""
            assert (source_form is None) != (source_form_computation is None), (
                "a formed module needs exactly one selected form or form computation"
            )
            self._preamble_form = source_form
            self._preamble_form_computation = source_form_computation
            self._preamble_radical_quotient_cokernel_projection = (
                radical_quotient_cokernel_projection
            )
            self._preamble_radical_quotient_basis_map = radical_quotient_basis_map
            super().__init__(**rest)

        def _added_structure(
            self, construction_data: dict[str, "ConstructionData"]
        ) -> tuple[tuple["Category", ...], dict[str, "ConstructionData"]]:
            r"""The form this level adds, kept when the module is constructed again (``OWN-05``; see ``Objects``)."""
            categories, data = super()._added_structure(construction_data)
            return categories, {"source_form": self.form(), **data}

        def form(self):
            r"""Return the selected form datum, stated on the unformed module."""
            if self._preamble_form is None:
                self._preamble_form = self._preamble_form_computation()
                self._preamble_form_computation = None
            return self._preamble_form

        @validator
        def validate_form_placement(self):
            r"""Check the declared form properties against the defining pairing."""
            from sage_extensions.refine import check_certifying_predicates

            check_certifying_predicates(
                self, self.category(), self.unformed_module().category()
            )

        def algebraic_correlation_morphism(self):
            r"""Return ``b^flat : M -> Hom_R(M,R)`` for this scalar-valued polar pairing."""
            injective = self in FormModules(self.base_ring()).Nondegenerate()
            return _algebraic_correlation_morphism(self, injective=injective)

        def is_unimodular(self):
            r"""Whether the polar correlation is an isomorphism.

            Declared unimodularity supplies the property without querying its
            own certifying predicate.  The selected finite free scalar-valued
            computation uses the actual correlation; otherwise retain the
            proposition.  Symmetry is not required.
            """
            ring = self.base_ring()
            if self.category().is_subcategory(FormModules(ring).Unimodular()):
                return True
            return self._unimodularity_decision()

        @cached_method
        def _unimodularity_decision(self):
            r"""Decide perfection from the correlation, independently of placement."""
            ring = self.base_ring()
            if (
                self.value_module() is not ring
                or ring not in OwnedRings().Commutative()
                or self not in FramedFreeModules(ring)
                or self.module_generating_set().is_finite() is not True
            ):
                return AtomicProposition("is_unimodular", self)
            correlation = _algebraic_correlation_morphism(self, injective=False)
            return conjunction(
                (correlation.is_injective(), correlation.is_surjective())
            )

        def correlation_isomorphism(self):
            r"""Return the perfect scalar polar correlation and its inverse.

            The current inverse computation uses a selected finite free
            framing; other represented perfect pairings retain that named
            computation frontier.
            """
            return _correlation_isomorphism(self)

        def hodge_discriminant(self, volume):
            r"""Return the determinant of ``b`` divided by the squared volume.

            For a quadratic form, ``b`` is its polar pairing.  The existing
            Gram-determinant supplier retains the actual ring of values.
            """
            return _hodge_discriminant(self, volume)

        def hodge_star(self, volume, degree):
            r"""Return ``PD_volume o Lambda^degree(b^flat)^(-1)`` on forms.

            This uses a perfect scalar-valued pairing and an actual volume
            isomorphism; it does not require the pairing to be symmetric.
            """
            return _hodge_star(self, volume, degree)

        def hodge_star_over_fraction_field(self, volume, degree):
            r"""Return the covariant Hodge isomorphism after scalar extension.

            The current computation is over the fraction field of a declared
            integral domain and requires the extended pairing to be perfect.
            """
            return _hodge_star_over_fraction_field(self, volume, degree)

        def multivector_hodge_star(self, volume, degree):
            r"""Return ``PD_volume^(-1) o Lambda^degree(b^flat)`` on vectors.

            This scalar-valued construction does not require a perfect or
            symmetric pairing and need not be invertible.
            """
            return _multivector_hodge_star(self, volume, degree)

        @cached_method
        def ideal_dual(self, modulus):
            r"""Return the rational vectors whose polar pairings lie in the principal ideal ``(modulus)``."""
            from sage_extensions.categories.modules.ideal_duals import IdealMetricDuals

            return IdealMetricDuals(self.base_ring())(self, modulus)

        @cached_method
        def scale_submodule(self):
            r"""Return the span of values of the retained defining form.

            For a bilinear form this is the span of ``b(x,y)``; for a
            quadratic form it is the span of ``q(x)``, in its own value
            module.  A quadratic form and its polar pairing can have
            different value spans and even different value modules.

            Selected finite module generators suffice.  Quadratic values
            on generators and their pairwise sums give generators of this
            span without division by two.  The existing ideal or module
            subobject owner computes the resulting span.
            """
            ring = self.base_ring()
            form = self.form()
            module = form.module()
            values = form.codomain()
            assert (
                module.has_selected_module_resolution()
                and module.module_generating_set().is_finite() is True
            ), (
                f"cannot compute the value span of {form}: its module {module} "
                "needs a selected finite spanning family"
            )
            generators = tuple(module.module_generators())
            if _is_bilinear_form(form):
                value_generators = tuple(
                    form(left, right) for left in generators for right in generators
                )
            else:
                diagonal = tuple(form(element) for element in generators)
                value_generators = diagonal + tuple(
                    form(left + right) - diagonal[i] - diagonal[j]
                    for i, left in enumerate(generators)
                    for j, right in enumerate(generators[i + 1 :], start=i + 1)
                )
            if values is ring and ring in OwnedRings().Commutative():
                return ring.ideal(*value_generators)
            if ring in OwnedIntegralDomains() and values is ring.fraction_field():
                return ring.fractional_ideal(*value_generators)
            represented_values = _represented_module(values, ring)
            return represented_values.subobject_on(
                tuple(
                    _as_module_element(values, ring, value)
                    for value in value_generators
                )
            )

        def pullback_form(self, morphism):
            r"""Pull back this formed module's form along a map into this module."""
            if morphism.codomain() is not self:
                raise ValueError(
                    "the form pullback requires a map into this formed module"
                )
            return self._formed_form().pullback(morphism)

        @cached_method
        def _formed_form(self):
            r"""The selected form read on this module.

            This module is built on the framing of the unformed module, so a
            bilinear form with values in a ring on a finite framing reads here
            with the same Gram tensor.  Otherwise its arguments coerce to the
            unformed module.
            """
            form = self.form()
            module = self.unformed_module()
            if form.module() is self:
                return form
            if (
                _is_bilinear_form(form)
                and form.codomain() in OwnedRings()
                and _has_finite_framing(module)
            ):
                return self.bilinear_forms(self.value_module())(form.gram_tensor())
            if _is_quadratic_form(form):
                return self.quadratic_map(
                    self.value_module(),
                    lambda element: form(module(element)),
                )
            return self.bilinear_forms(form.codomain())(
                lambda left, right: form(module(left), module(right))
            )

        def unformed_module(self):
            r"""Return the module the form was stated on: the datum this module is built on."""
            return self.form().module()

        def _element_of_unformed_module(self, element):
            r"""The element of :meth:`unformed_module` with the coefficients ``element`` has here.

            A formed module is built on the framing of the module its form was
            stated on: the same generating set and, for a presented module,
            the same presentation.  So an element reads there with the same
            coefficients.
            """
            coordinates = self._framing_lift(self(element))
            return self.unformed_module().linear_combination(
                {label: coordinates(label) for label in coordinates.support().domain()}
            )

        def _element_from_unformed_module(self, element):
            r"""The element of this module with the coefficients ``element`` has in :meth:`unformed_module`."""
            coordinates = self.unformed_module().framing_morphism().lift(element)
            return self.linear_combination(
                {label: coordinates(label) for label in coordinates.support().domain()}
            )

        def _pairing_value(self, left, right):
            return self.b(left, right)

        def _pairing_left_module(self):
            return self

        def _pairing_right_module(self):
            return self

        def _pairing_value_module(self):
            return self.form().codomain()

        def is_nondegenerate(self) -> bool:
            r"""Return whether both radicals of this form are zero."""
            match self in FormModules(self.base_ring()).Nondegenerate():
                case True:
                    return True
                case False:
                    return self._nondegeneracy_decision()

        @cached_method
        def _nondegeneracy_decision(self):
            r"""Decide vanishing of both radicals from the pairing itself."""
            ring = self.base_ring()
            if (
                self.value_module() is ring
                and ring in OwnedIntegralDomains()
                and self in FramedFreeModules(ring)
                and self.module_generating_set().is_finite() is True
            ):
                return self.determinant() != ring.zero()
            return conjunction(
                (self.left_curry().is_injective(), self.right_curry().is_injective())
            )

        @object_level
        def Mono(self, codomain):
            r"""Return the form-preserving monomorphisms into ``codomain``."""
            return FormModules(self.base_ring()).Mono(self, codomain)

        def formed_mor(self, module_morphism, value_morphism):
            r"""Construct the general fixed-fiber formed morphism ``(f,h)``."""
            target = module_morphism.codomain()
            if target is self.unformed_module():
                target = self
            return FormModules(self.base_ring()).Mor(self, target)(
                (module_morphism, value_morphism)
            )

        def fibered_formed_mor(
            self,
            codomain,
            ring_map,
            module_morphism=None,
            value_morphism=None,
        ):
            r"""Return, or construct in, the formed Mor over ``ring_map``."""
            mor = FiberedFormedModuleMor(self, codomain, ring_map)
            if module_morphism is None and value_morphism is None:
                return mor
            if module_morphism is None or value_morphism is None:
                raise TypeError(
                    "a fibered formed arrow needs both its module and value components"
                )
            return mor((module_morphism, value_morphism))

        def _Hom_(self, codomain, category=None):
            ring = self.base_ring()
            formed = FormModules(ring)
            if codomain in formed and (
                category is None or category.is_subcategory(formed)
            ):
                return FormModules(ring).Mor(self, codomain)

            return self.module_category().Mor(self, codomain)

        def b(self, left, right):
            r"""Evaluate the (polar) bilinear form on two elements of this module.

            On a finite framing with values in a ring, ``b(x, y)`` is one
            contraction ``G(x, y) = sum_{i,j} G_{ij} x^i y^j`` of the Gram
            tensor with the coordinate vectors of ``x`` and ``y`` (`OWN-24`).
            """
            if left not in self or right not in self:
                raise TypeError(
                    f"the form on {self} pairs two of its elements, but {left} or {right} is not in {self}"
                )
            form = self.form()
            match _is_quadratic_form(form):
                case False if form.codomain() in OwnedRings() and _has_finite_framing(
                    self
                ):
                    # This module is constructed on the framing of the form's
                    # module, so its coordinates are the Gram tensor's indices.
                    framing = self.framing_morphism()
                    values = form.codomain()
                    return form.gram_tensor().contract(
                        tensor.vector(values, tuple(framing.lift(left))),
                        tensor.vector(values, tuple(framing.lift(right))),
                    )
                case is_quadratic:
                    module = form.module()
                    if module is not self:
                        left, right = module(left), module(right)
                    return form.b(left, right) if is_quadratic else form(left, right)

        def norm(self, element):
            r"""Return ``q(x)`` for a quadratic form, else ``b(x, x)``."""
            if element not in self:
                raise TypeError(
                    f"the norm on {self} is defined on its elements, but {element} is not in {self}"
                )
            form = self.form()
            if form.module() is not self:
                element = self.unformed_module()(element)
            if _is_quadratic_form(form):
                return form(element)
            return form(element, element)

        def q(self, element):
            r"""Return the selected quadratic/norm value of ``element``."""
            return self.norm(element)

        def is_isotropic(self) -> bool | Predicate:
            r"""Whether the selected norm vanishes at a nonzero element.

            This is the negation of anisotropy in
            ``LeanCategories/Modules/Bilinear/Valued/Witt.lean``,
            ``BilinModuleCat.IsAnisotropic``, applied to the selected norm.
            The nonzero zero-fibre defines the question without a framing,
            a countability hypothesis, or an enumeration. A specialized
            formed module may decide it; otherwise the set owner retains
            the undecided emptiness proposition.
            """
            zero = self.zero()
            null_vectors = self.elements_of_norm(self.value_module().zero())
            return negation(
                null_vectors.condition_set(lambda vector: vector != zero).is_empty()
            )

        def is_anisotropic(self) -> bool | Predicate:
            r"""Whether zero is the only element of selected norm zero.

            This complements the same isotropy question, including any
            exact specialized decision, rather than interpreting a search
            that has not found a vector as a proof of anisotropy. An
            undecided isotropy proposition stays a proposition.

            EXAMPLES::

                sage: U = Lattices(ZZ)("U")
                sage: assert U.is_anisotropic() is False
                sage: A = Lattices(ZZ)([[1, 0], [0, -2]])
                sage: assert A.is_anisotropic() is True
                sage: assert (U + U).is_anisotropic() is False
            """
            return negation(self.is_isotropic())

        def vector_of_sign(self, sign):
            r"""Return a vector whose selected norm has sign ``-1`` or ``1``, or ``None``.

            The vector belongs to this formed module. For a represented
            submodule its inclusion supplies the ambient vector. Exact
            diagonalization supplies the computation over ``QQ``, ``ZZ``
            and ``AA`` with a finite framing and scalar form values;
            the integral result is primitive. For a lattice over represented
            exact ``RR``, its retained diagonalization and decided signs
            supply a normalized witness of square +1 or -1. A bilinear form uses its
            diagonal function, and a quadratic form retains its own norm.

            EXAMPLES::

                sage: V = Lattices(AA)([[1, 0], [0, -2]])
                sage: p, n = V.positive_vector(), V.negative_vector()
                sage: p.parent() is V and n.parent() is V
                True
                sage: p.q() > AA(0) and n.q() < AA(0)
                True
                sage: Lattices(AA)([[1]]).negative_vector() is None
                True
                sage: U = Lattices(ZZ)("U")
                sage: S = U.subobject_on((U.basis_vector(0) - U.basis_vector(1),))
                sage: v = S.vector_of_sign(-1)
                sage: v.parent() is S and S.inclusion()(v).q() < ZZ(0)
                True
                sage: S.vector_of_sign(1) is None
                True
                sage: T = U.subobject_on((U.basis_vector(0) + U.basis_vector(1), U.basis_vector(0) - U.basis_vector(1)))
                sage: p, n = T.positive_vector(), T.negative_vector()
                sage: p.parent() is T and n.parent() is T
                True
                sage: p.q() > 0 and n.q() < 0
                True
                sage: T.inclusion()(p).q() == p.q() and T.inclusion()(n).q() == n.q()
                True
            """
            if sign not in (-1, 1):
                raise ValueError("a signed-vector request requires sign -1 or 1")
            from sage_extensions.categories.lattice_engines import (
                _signed_vector_witness,
            )

            return _signed_vector_witness(self, sign)

        def positive_vector(self):
            r"""Return a positive-norm vector, or ``None`` if none exists."""
            return self.vector_of_sign(1)

        def negative_vector(self):
            r"""Return a negative-norm vector, or ``None`` if none exists."""
            return self.vector_of_sign(-1)

        @cached_method
        def signature_pair(self):
            r"""Return cardinal inertia of the selected norm in its chosen ordering."""
            value_module = self.value_module()
            if value_module not in OwnedRings():
                if not hasattr(value_module, "regular_module_identification"):
                    raise TypeError(
                        f"the signature of {self} needs ordered scalar values, not {value_module}"
                    )
                # This is not a coordinate projection: the selected value
                # module must be literally the restriction of its extension
                # ring's regular module along the selected algebra structure
                # morphism. The identification supplies the exact scalar Gram.
                value_module.regular_module_identification()
            from sage_extensions.categories._lattice import (
                _signature_pair_of_gram,
            )

            form = self.form()
            if _is_quadratic_form(form) and not form.has_selected_bilinear_lift():
                assert _has_finite_framing(self), (
                    f"the polar Gram computation of {self} needs finite selected spanning data; "
                    "no infinite quadratic Gram inertia is supplied"
                )
                gram = form.polar_form().gram_tensor()
            else:
                gram = self.gram_tensor()
            signature = _signature_pair_of_gram(gram)
            assert signature is not None, (
                f"cannot compute the inertia of {self}: its selected norm supplies no exact inertia computation"
            )
            return signature

        def signature(self):
            r"""Return the inertia pair of this selected norm."""
            return self.signature_pair()

        def definiteness(self):
            r"""Return the sign type at finite rank from the exact inertia pair."""
            assert self.module_rank().is_finite() is True, (
                f"the definiteness of {self} is decided here only at finite rank; "
                f"its exact inertia {self.signature_pair()} does not determine an infinite-dimensional radical"
            )
            signature = self.signature_pair()
            positive, negative = signature.first(), signature.second()
            rank = self.module_rank()
            if positive == 0 and negative == 0:
                return "zero"
            if negative == 0:
                return (
                    "positive_definite" if positive == rank else "positive_semidefinite"
                )
            if positive == 0:
                return (
                    "negative_definite" if negative == rank else "negative_semidefinite"
                )
            return "indefinite"

        @cached_method
        def orthogonal_group(self):
            r"""Return the module automorphisms preserving this form with identity value map."""
            automorphisms = Modules(self.base_ring()).Aut(self)
            formed_mor = FormModules(self.base_ring()).Mor(self, self)
            return automorphisms.predicate_subgroup(
                lambda automorphism: formed_mor.preserves_forms(
                    automorphism.as_morphism()
                ),
                f"Isometries of {self}",
            )

        O = orthogonal_group

        @cached_method
        def square_fibre(self, square):
            r"""The fibre of the selected norm ``v |-> q(v)`` at ``square``.

            When the supplied value is decided zero, retain the module's
            zero as a point of this fibre. The identity q(0)=0 provides
            this point without searching or enumerating the module.
            """
            values = self.value_module()
            square = values(square)
            fibre = OwnedSets().equalizer_construction(
                OwnedSets().Mor(self, values)(lambda vector: self.norm(vector)),
                OwnedSets().Mor(self, values)(lambda vector: square),
            )
            if (square == values.zero()) is True:
                fibre.object()(self.zero())
            else:
                from sage_extensions.categories.lattices import Lattices
                from sage_extensions.categories.rings.ring_foundation import (
                    _owned_rationals,
                    _owned_real_algebraic_numbers,
                )
                from sage_extensions.rings.real import RR

                ring = self.base_ring()
                if (
                    self in Lattices(ring)
                    and values is ring
                    and ring
                    in (
                        _owned_integers(),
                        _owned_rationals(),
                        _owned_real_algebraic_numbers(),
                        RR,
                    )
                    and self.module_rank().is_finite()
                    and int(self.module_rank()) > 0
                    and self in FormModules(ring).Nondegenerate()
                ):
                    locus = fibre.object()

                    def point():
                        # The solver supplies a solution of this exact
                        # equation; admission retains that actual point
                        # without trying to decide its scalar equation again.
                        return self.representation_vector(square)

                    locus._retain_point_computation(point)
            return fibre

        def elements_of_norm(self, value):
            r"""Return the full norm fibre as a set with its inclusion.

            Unlike ``square_fibre``, which returns the selected equalizer
            construction, this returns its object. The fibre includes zero
            when ``value`` is zero and exists over uncountable rings as
            well as countable ones. Its ability to enumerate points is
            supplied by the underlying set construction, not inferred from
            the norm equation. Values lie in ``value_module()``, including
            quotient-valued forms.

            EXAMPLES::

                sage: U = Lattices(ZZ)("U")
                sage: null_vectors = U.elements_of_norm(ZZ.zero())
                sage: e, f = U.basis_vector(0), U.basis_vector(1)
                sage: assert null_vectors.inclusion()(null_vectors(e)) == e
                sage: assert U.zero() in null_vectors
                sage: assert null_vectors.is_parent_of(e + f) is False
                sage: from sage_extensions.rings.real import RR
                sage: V = Lattices(RR)([[1]])
                sage: null_vectors = V.elements_of_norm(RR.zero())
                sage: assert null_vectors.an_element() == V.zero()
                sage: assert null_vectors.inclusion()(null_vectors.an_element()) == V.zero()
                sage: assert null_vectors.is_empty() is False
                sage: assert V.square_fibre(RR.zero()).object() is null_vectors
                sage: F = V.elements_of_norm(RR.pi())
                sage: point = F(V.representation_vector(RR.pi()))
                sage: assert F.an_element() == point
                sage: assert V.q(F.inclusion()(F.an_element())) == RR.pi()
                sage: W = Lattices(RR).Nondegenerate()([[1]])
                sage: fresh = W.elements_of_norm(RR(3))
                sage: point = fresh.an_element()
                sage: assert point.parent() is W
                sage: assert W.q(fresh.inclusion()(point)) == RR(3)
                sage: assert fresh.is_empty() is False
                sage: assert fresh.an_element() is point
                sage: excluded = W.elements_of_norm(RR(-1))
                sage: excluded.an_element()  # doctest: +ELLIPSIS
                Traceback (most recent call last):
                ...
                ValueError: ... does not represent -1
                sage: from sage_extensions.logic import Predicate
                sage: assert isinstance(excluded.is_empty(), Predicate)
                sage: Z = Lattices(RR).Nondegenerate()(0)
                sage: empty = Z.square_fibre(RR.one()).object()
                sage: assert empty.inclusion().codomain() is Z
                sage: assert empty.is_parent_of(Z.zero()) is False
                sage: from sage_extensions.categories.rings.ring_foundation import _owned_integers
                sage: ZZ = _owned_integers()
                sage: P = Lattices(ZZ).Nondegenerate()([[1, 0], [0, -2]])
                sage: shell = P.elements_of_norm(ZZ(4))
                sage: v = shell.an_element()
                sage: assert v.parent() is P and P.q(v) == ZZ(4)
                sage: assert shell.inclusion()(v) == v
                sage: assert shell.an_element() is v
                sage: absent = P.elements_of_norm(ZZ(3))
                sage: absent.an_element()  # doctest: +ELLIPSIS
                Traceback (most recent call last):
                ...
                ValueError: ... does not represent 3
            """
            return self.square_fibre(value).object()

        def square_fibre_action(self, square, *, orbit_relation=None):
            r"""The identity-value isometry action on the complete norm fibre."""
            from sage_extensions.categories.group.g_objects import GObjects

            points = self.square_fibre(square).object()
            return GObjects(self.orthogonal_group(), OwnedSets()).on_set(
                points,
                lambda isometry, vector: isometry(vector),
                orbit_relation=orbit_relation,
            )

        def gram_tensor(self):
            r"""Return the scalar Gram as its intrinsic type-``(0,2)`` tensor."""
            form = self.form()
            numerical_coordinates = getattr(form, "_as_numerical_tensor", None)
            if numerical_coordinates is not None:
                return numerical_coordinates()
            return form.gram_tensor()

        def raise_index(self, tensor, slot=0):
            r"""Raise one lower tensor index using this formed module.

            The tensor owns the contraction algorithm.  This method is the
            formed-module-facing spelling of that same construction and does
            not introduce a second index-raising implementation.
            """
            return tensor.raise_index(self, slot)

        def lower_index(self, tensor, slot=0):
            r"""Lower one upper tensor index using this formed module."""
            return tensor.lower_index(self, slot)

        def twist(self, scalar):
            r"""This module with the form scaled by ``scalar``: Gram tensor ``m G`` when it has one."""
            return FormValueScalings(self.base_ring())(self, scalar)

        def base_change(self, ring_map):
            r"""Extend the form through its source-retaining scalar-change construction."""
            return FormBaseChanges(ring_map.codomain())(self, ring_map)

    class ElementMethods:
        @cached_method
        def b(self, other):
            r"""Return the polar bilinear value ``b(self, other)``."""
            return self.parent().b(self, other)

        @cached_method
        def q(self):
            r"""Return the represented quadratic/norm value of this element."""
            return self.parent().norm(self)

        def is_isotropic(self) -> bool | Predicate:
            r"""Return the zero-norm equation, retaining undecided predicates.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: from sage_extensions.categories.sets.set_categories import NN, Sets
                sage: from sage_extensions.rings.real import RR
                sage: from sage_extensions.categories.rings.ring_foundation import _owned_rationals
                sage: from sage_extensions.logic import Predicate
                sage: QQ = _owned_rationals()
                sage: a = Sets().Mor(NN, QQ)(lambda n: QQ(1)/QQ(2)**int(n))
                sage: z = RR.of_cauchy(a)
                sage: V = Lattices(RR)([[z]])
                sage: v = V.module_generators()[0]
                sage: assert isinstance(v.is_isotropic(), Predicate)
                sage: assert isinstance(v.is_orthogonal_to(v), Predicate)
                sage: assert isinstance(v.represents(RR.zero()), Predicate)
                sage: assert isinstance(V.is_unimodular(), Predicate)
                sage: U = Lattices(QQ)("U")
                sage: assert U.module_generators()[0].is_isotropic() is True
            """
            return self.q() == self.parent().value_module().zero()

        def is_orthogonal_to(self, other) -> bool | Predicate:
            r"""Return the polar/bilinear zero equation, possibly undecided."""
            pairing = self.b(other)
            return pairing == pairing.parent().zero()

        def represents(self, value) -> bool | Predicate:
            r"""Return whether this element has represented norm ``value``.

            This is the elementwise statement ``q(self)=value``.  It does not
            answer the distinct existential question whether the whole formed
            module represents a selected value.
            """
            parent = self.parent()
            return self.q() == parent.value_module()(value)

    class SubcategoryMethods:
        def Nondegenerate(self):
            r"""Return this category with the axiom that both radicals of the form are zero."""
            return self._with_axiom("Nondegenerate")

        def Unimodular(self):
            r"""Return this category with the axiom that the correlation of the form is an isomorphism."""
            return self._with_axiom("Unimodular")

    class Nondegenerate(CategoryWithAxiom):
        r"""Form modules whose left and right radicals are zero."""

        _certifying_predicate = "_nondegeneracy_decision"

        def an_object(self):
            r"""The hyperbolic plane U, whose form is unimodular."""
            from sage_extensions.categories.lattices import Lattices

            return Lattices(self.base_ring())("U")

    class Unimodular(CategoryWithAxiom):
        r"""Form modules whose correlation morphism is an isomorphism."""

        _certifying_predicate = "_unimodularity_decision"

        def an_object(self):
            r"""The hyperbolic plane U."""
            from sage_extensions.categories.lattices import Lattices

            return Lattices(self.base_ring())("U")

        def extra_super_categories(self):
            return [FormModules(self.base_ring()).Nondegenerate()]

    class FinitelyPresented(CategoryWithAxiom):
        r"""Form modules admitting a finite presentation."""

        def an_object(self):
            r"""The discriminant group of U."""
            from sage_extensions.categories.lattices import Lattices

            return Lattices(self.base_ring())("U").discriminant_group()

        class ParentMethods:
            def base_change(self, ring_map):
                return FormBaseChanges(ring_map.codomain())(self, ring_map)

        class Torsion(CategoryWithAxiom):
            r"""Finitely presented torsion modules carrying a bilinear or quadratic form."""

            def extra_super_categories(self):
                return [Modules(self.base_ring()).FinitelyPresented().Torsion()]

            def an_object(self):
                ring = self.base_ring()
                zero = ring.free_module(0)
                presentation = zero.module_category().Mor(zero, zero).identity()
                module = Modules(ring).FinitelyPresented().Torsion()(presentation)
                form = module.bilinear_forms(ring)(lambda left, right: ring.zero())
                return FormModules(ring)(form, _extra_categories=(self,))

            class ParentMethods:
                def _torsion_form_is_quadratic(self) -> bool:
                    return _is_quadratic_form(self.form())

                def subobject_generated_by(self, generators):
                    return _torsion_form_subobject_on(
                        self,
                        generators,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def primary_part(self, prime):
                    return _torsion_form_primary_part(
                        self,
                        prime,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                @cached_method
                def isotropic_subobjects(self):
                    return _torsion_form_isotropic_subobjects(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                @cached_method
                def maximal_isotropic_subobjects(self):
                    return _torsion_form_maximal_isotropic_subobjects(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def form_vanishes_on(self, elements) -> bool:
                    elements = tuple(elements)
                    zero = self.value_module().zero()
                    if self._torsion_form_is_quadratic():
                        return all(self.q(element) == zero for element in elements)
                    return all(
                        self.b(left, right) == zero
                        for left in elements
                        for right in elements
                    )

                def gram_matrix(self):
                    representative = _representative_gram(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )
                    rows, columns = map(int, representative.tensor_shape())
                    return (
                        representative.base_ring()
                        .matrix_space(rows, columns)
                        .from_rows(
                            tuple(
                                tuple(
                                    representative[row, column]
                                    for column in range(columns)
                                )
                                for row in range(rows)
                            )
                        )
                    )

                @cached_method(
                    key=lambda self, generators: tuple(
                        id(generator) for generator in generators
                    )
                )
                def reframing_isometry(self, generators):
                    return _regenerate_form_on_generators(
                        self,
                        tuple(generators),
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def regenerate(self, generators):
                    return self.reframing_isometry(generators).codomain()

                @cached_method
                def primary_components(self):
                    return _primary_form_component_family(self)

                def primary_decomposition(self, *args, **kwargs):
                    return self.primary_components(*args, **kwargs)

                @cached_method
                def subobjects(self):
                    return _torsion_form_all_subobjects(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def orbit(self, element, group=None):
                    return _finite_form_orbit(self, element, group)

                @cached_method
                def orbits(self, group=None):
                    return _finite_form_orbits(self, group)

                def orbits_on_subobjects(self, group=None):
                    return _finite_form_subobject_orbits(self, group=group)

                def orbits_on_isotropic_subobjects(self, group=None):
                    return _finite_form_subobject_orbits(
                        self, isotropic=True, group=group
                    )

                def is_anisotropic(self) -> bool:
                    zero = self.zero()
                    return all(
                        not self.form_vanishes_on((element,))
                        for element in self.elements()
                        if element != zero
                    )

                def orthogonal_subobject(self, subobject):
                    return _torsion_form_orthogonal_subobject(
                        self,
                        subobject,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                @cached_method
                def lagrangian_subobjects(self):
                    return _torsion_form_lagrangian_subobjects(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def is_metabolic(self) -> bool:
                    return self.lagrangian_subobjects().cardinality() != 0

                def metabolizer(self):
                    return _finite_form_metabolizer(self)

                def restricted_form(self, subobject):
                    if subobject.inclusion().codomain() is not self:
                        raise ValueError(
                            f"the form of {self} restricts only to a submodule of {self}, but {subobject} "
                            f"is included into {subobject.inclusion().codomain()}"
                        )
                    return subobject

                def subquotient_form(self, subobject, over):
                    return _torsion_form_subquotient(
                        self,
                        subobject,
                        over,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def orthogonal_quotient(self, subobject):
                    perpendicular = self.orthogonal_subobject(subobject)
                    return self.subquotient_form(subobject, perpendicular)

                @cached_method
                def invariant_factor_form(self):
                    return _invariant_factor_form_isomorphism(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def p_adic_jordan_decomposition(self):
                    return _p_adic_jordan_decomposition(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def p_adic_jordan_module_generators(self):
                    return _p_adic_jordan_module_generators(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def p_adic_jordan_form(self):
                    return _p_adic_jordan_form(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                normal_form = p_adic_jordan_form

                def normal_form_isometry(self):
                    return self.normal_form().inverse()

                def twist(self, scalar):
                    quadratic = self._torsion_form_is_quadratic()
                    category = (
                        TorsionQuadraticFormModules(self.base_ring())
                        if quadratic
                        else TorsionBilinearFormModules(self.base_ring())
                    )
                    return TorsionFormTwistFunctor(
                        category,
                        scalar,
                        quadratic=quadratic,
                    )(self)

                def is_isomorphic(self, other) -> bool:
                    quadratic = self._torsion_form_is_quadratic()
                    category = (
                        TorsionQuadraticFormModules(self.base_ring())
                        if quadratic
                        else TorsionBilinearFormModules(self.base_ring())
                    )
                    if other not in category:
                        return False
                    return _forms_are_isomorphic(self, other, quadratic=quadratic)

                is_isometric_to = is_isomorphic

                def is_anti_isometric(self, other) -> bool:
                    quadratic = self._torsion_form_is_quadratic()
                    category = (
                        TorsionQuadraticFormModules(self.base_ring())
                        if quadratic
                        else TorsionBilinearFormModules(self.base_ring())
                    )
                    if other not in category:
                        return False
                    return self.is_isomorphic(other.twist(-1))

                @cached_method
                def automorphism_group(self):
                    return _torsion_form_automorphism_group(
                        self,
                        quadratic=self._torsion_form_is_quadratic(),
                    )

                def orthogonal_group(self):
                    return self.automorphism_group()

                def O(self):
                    return self.automorphism_group()


class NondegenerateGenericFibreFormModules(OwnedCategoryOverBaseRing):
    r"""Finite nondegenerate formed modules over an integral domain.

    Their scalar extensions to the fraction field have invertible Gram forms.
    """

    def super_categories(self):
        if self.base_ring() not in OwnedIntegralDomains():
            raise TypeError("generic-fibre formed modules require an integral domain")
        return [FormModules(self.base_ring()).Nondegenerate().FinitelyGenerated()]

    def an_object(self):
        from sage_extensions.categories.lattices import Lattices

        return self(Lattices(self.base_ring())("U"))

    def _call_(self, formed):
        from sage_extensions.refine import refine

        if formed not in FormModules(self.base_ring()) or not formed.is_nondegenerate():
            raise ValueError("generic-fibre index raising needs a nondegenerate form")
        if formed not in Modules(self.base_ring()).FinitelyGenerated():
            raise ValueError("generic-fibre index raising needs finite rank")
        return refine(formed, self)

    class ParentMethods:
        def raise_index_over_fraction_field(self, tensor, slot=0):
            r"""Raise a covariant index over the fraction field of the base domain."""
            ring_map = self.base_ring().fraction_field_map()
            changed_form = self.base_change(ring_map)
            changed_tensor = tensor.change_ring(changed_form.base_ring())
            return changed_tensor.raise_index(changed_form, slot)


def _primary_form_component_family(form):
    r"""The primary decomposition indexed by primes of the finite form."""
    primes = finite_ordered_set(
        tuple(
            sorted(
                {
                    prime
                    for invariant in form.invariant_factors()
                    for prime in abs(invariant).prime_divisors()
                }
            )
        )
    )
    return indexed_family(
        primes,
        lambda prime: form.primary_part(prime),
        name=f"Primary components of {form}",
    )


def _finite_form_orbit(form, element, group=None):
    acting = form.automorphism_group() if group is None else group
    return acting.orbit(form(element))


def _finite_form_orbits(form, group=None):
    acting = form.automorphism_group() if group is None else group
    action = _torsion_form_element_action(form, acting)
    return finite_ordered_set(tuple(orbit.points() for orbit in action.orbits()))


def _finite_form_subobject_orbits(form, isotropic=False, group=None):
    acting = form.automorphism_group() if group is None else group
    subobjects = form.isotropic_subobjects() if isotropic else form.subobjects()
    return _torsion_form_subobject_orbits(form, subobjects, acting)


def _finite_form_metabolizer(form):
    lagrangians = form.lagrangian_subobjects()
    if lagrangians.cardinality() == 0:
        raise ValueError(f"{form} is not metabolic: it has no Lagrangian submodule")
    return lagrangians[0]


class BilinearFormModules(OwnedCategoryOverBaseRing):
    def an_object(self):
        r"""Return U over a declared commutative base, else the zero formed module."""
        ring = self.base_ring()
        if ring in OwnedRings().Commutative():
            module = ring.free_module(2)
            form = module.bilinear_forms(ring)([[0, 1], [1, 0]])
        else:
            module = ring.free_module(0)
            form = module.bilinear_forms(ring)(lambda left, right: ring.zero())
        return BilinearFormModules(ring).Symmetric().Even()(form)

    def _repr_object_names(self):
        return f"modules with a bilinear form over {self.base_ring()}"

    def super_categories(self):
        return [FormModules(self.base_ring())]

    _MorCategory = FormedModuleMorCategoryConstruction

    class ParentMethods:
        def is_symmetric(self):
            r"""Whether ``b(x,y)=b(y,x)`` for all ``x,y``.

            A selected finite spanning family decides symmetry from its pairwise
            values by bilinearity.  Without such a finite determining family,
            retain the exact proposition instead of forcing an infinite check.
            """
            module = self.unformed_module()
            if (
                not module.has_selected_module_resolution()
                or module.module_generating_set().is_finite() is not True
            ):
                return AtomicProposition("is_symmetric", self)
            generators = tuple(self.module_generators())
            return conjunction(
                self.b(left, right) == self.b(right, left)
                for left in generators
                for right in generators
            )

        def is_even(self):
            r"""Whether ``b(x,x)`` lies in ``2W`` for every ``x``.

            Over a commutative scalar ring, for a selected finite spanning
            family ``g_i`` it is enough to test ``q(g_i)`` and
            ``q(g_i+g_j)`` in ``2W``, where ``q(x)=b(x,x)``: the cross term
            ``b(g_i,g_j)+b(g_j,g_i)`` is their difference from the two
            diagonal values.  Hence these values generate the image of ``q``
            modulo ``2W``.  When the finite spanning/value-module computation
            is unavailable, retain the exact proposition instead of forcing a
            Boolean answer.
            """
            ring = self.base_ring()
            module = self.unformed_module()
            values = _represented_module(self.value_module(), ring)
            if (
                ring not in OwnedRings().Commutative()
                or not module.has_selected_module_resolution()
                or module.module_generating_set().is_finite() is not True
                or not values.has_selected_module_resolution()
                or values.module_generating_set().is_finite() is not True
            ):
                return AtomicProposition("is_even", self)

            generators = tuple(self.module_generators())
            two = ring(2)
            doubling = (
                values.module_category()
                .Mor(values, values)
                ._from_constructed_element_map(
                    lambda element: values.scalar_multiple(two, element)
                )
            )
            probes = tuple(
                self.b(generator, generator) for generator in generators
            ) + tuple(
                self.b(left + right, left + right)
                for left_position, left in enumerate(generators)
                for right in generators[left_position + 1 :]
            )
            return conjunction(
                doubling.is_in_image(
                    _as_module_element(self.value_module(), ring, value)
                )
                for value in probes
            )

    def _call_(
        self,
        form,
        *,
        _extra_categories=(),
        _extra_construction_data=None,
        _subobject_ambient=None,
        _subobject_generator_images=None,
        _subobject_lift=None,
        _subobject_inclusion_factory=None,
    ):
        r"""Equip the module of an actual bilinear form; reject quadratic data at this entry."""
        if not _is_bilinear_form(form):
            raise TypeError(
                f"{self} is constructed from a bilinear form, but {form} is not bilinear"
            )
        return FormModules._call_(
            self,
            form,
            _extra_categories=_extra_categories,
            _extra_construction_data=_extra_construction_data,
            _subobject_ambient=_subobject_ambient,
            _subobject_generator_images=_subobject_generator_images,
            _subobject_lift=_subobject_lift,
            _subobject_inclusion_factory=_subobject_inclusion_factory,
        )

    class SubcategoryMethods:
        def Symmetric(self):
            r"""Return this category with the axiom that the bilinear form is symmetric."""
            return self._with_axiom("Symmetric")

        def Even(self):
            r"""Return this category with the axiom that ``b(x, x)`` lies in ``2W`` for every ``x``."""
            return self._with_axiom("Even")

    class Symmetric(CategoryWithAxiom):
        r"""Modules with a symmetric bilinear form."""

        _certifying_predicate = "is_symmetric"

        def an_object(self):
            r"""Return the generic bilinear-form witness, already symmetric by construction."""
            return BilinearFormModules(self.base_ring()).an_object()

        class ParentMethods:
            def square_fibre_action(self, square, *, orbit_relation=None):
                r"""The orthogonal action on the complete square fibre."""
                from sage_extensions.categories.group.g_objects import GObjects

                points = self.square_fibre(square).object()
                return GObjects(self.Aut(), OwnedSets()).on_set(
                    points,
                    lambda isometry, vector: isometry(vector),
                    orbit_relation=orbit_relation,
                )

            def vector_of_sign(self, sign):
                r"""Return a vector of square sign ``-1`` or ``1``, or ``None``.

                The vector belongs to this formed module. For a represented
                submodule its inclusion supplies the ambient vector. Exact
                diagonalization supplies the computation over ``QQ``, ``ZZ``
                and ``AA``; the integral result is primitive.

                EXAMPLES::

                    sage: U = Lattices(ZZ)("U")
                    sage: S = U.subobject_on((U.basis_vector(0) - U.basis_vector(1),))
                    sage: v = S.vector_of_sign(-1)
                    sage: v.parent() is S and S.inclusion()(v).q() < ZZ(0)
                    True
                    sage: S.vector_of_sign(1) is None
                    True
                    sage: T = U.subobject_on((U.basis_vector(0) + U.basis_vector(1), U.basis_vector(0) - U.basis_vector(1)))
                    sage: p, n = T.positive_vector(), T.negative_vector()
                    sage: p.parent() is T and n.parent() is T
                    True
                    sage: p.q() > 0 and n.q() < 0
                    True
                    sage: T.inclusion()(p).q() == p.q() and T.inclusion()(n).q() == n.q()
                    True
                """
                if sign not in (-1, 1):
                    raise ValueError("a signed-vector request requires sign -1 or 1")
                from sage_extensions.categories.lattice_engines import (
                    _signed_vector_witness,
                )

                return _signed_vector_witness(self, sign)

            def positive_vector(self):
                r"""Return a positive-square vector, or ``None`` if none exists."""
                return self.vector_of_sign(1)

            def negative_vector(self):
                r"""Return a negative-square vector, or ``None`` if none exists."""
                return self.vector_of_sign(-1)

            @cached_method
            def signature_pair(self):
                r"""Return the Sylvester inertia pair of a finite symmetric form.

                Nondegenerate represented-real forms use Arb enclosures and
                an exact rational inverse-norm stopping test. This needs
                convergent enclosures of the closed scalar expressions;
                it does not decide singularity or return a basis.

                EXAMPLES::

                    sage: V = Lattices(RR).Nondegenerate()([[0, RR.pi()], [RR.pi(), 0]])
                    sage: assert V.signature_pair().first() == cardinal(1)
                    sage: assert V.signature_pair().second() == cardinal(1)
                    sage: a = RR.pi()
                    sage: P = Lattices(RR).Nondegenerate()([[1, a], [a, a*a + RR(2)**(-512)]])
                    sage: assert P.signature_pair().first() == cardinal(2)
                    sage: assert P.signature_pair().second() == cardinal(0)
                    sage: from sage_extensions.categories.rings.ring_foundation import _owned_rationals
                    sage: from sage_extensions.categories.sets.set_categories import NN, Sets
                    sage: Q = _owned_rationals()
                    sage: a = Sets().Mor(NN, Q)(lambda n: Q(1) + Q(1)/Q(2)**int(n))
                    sage: x = RR.of_cauchy(a)
                    sage: C = Lattices(RR).Nondegenerate()([[x, 0], [0, -1]])
                    sage: assert C.signature_pair().first() == cardinal(1)
                    sage: assert C.signature_pair().second() == cardinal(1)
                    sage: E = Lattices(RR).Nondegenerate()(0)
                    sage: assert E.signature_pair().first() == cardinal(0)
                    sage: assert E.signature_pair().second() == cardinal(0)
                    sage: S = Lattices(RR)([[1, 0], [0, 0]])
                    sage: assert S.signature_pair().first() == cardinal(1)
                    sage: assert S.signature_pair().second() == cardinal(0)
                """
                assert self.module_rank().is_finite(), (
                    f"the signature of {self} is computed here only at finite rank, "
                    f"but it has rank {self.module_rank()}"
                )
                from sage_extensions.tensors.tensor import Tensor

                numerical = self.gram_tensor()
                assert isinstance(numerical, Tensor), (
                    f"the signature of {self} needs scalar numerical Gram data, "
                    f"but its values lie in {self.value_module()}"
                )
                from sage_extensions.categories._lattice import (
                    _nonsingular_real_signature,
                    _signature_pair_of_gram,
                )
                from sage_extensions.rings.real import RR

                if self.base_ring() is RR and self in FormModules(RR).Nondegenerate():
                    return _nonsingular_real_signature(numerical)
                return _signature_pair_of_gram(numerical)

            def signature(self):
                r"""Return the Sylvester inertia pair of this symmetric form."""
                return self.signature_pair()

            def definiteness(self):
                r"""Return the sign type of this finite-rank symmetric form."""
                rank = int(self.module_rank())
                signature = self.signature_pair()
                positive = int(signature.first())
                negative = int(signature.second())
                zero = rank - positive - negative
                match (positive, negative, zero):
                    case (0, 0, _):
                        return "zero"
                    case (_, 0, 0):
                        return "positive_definite"
                    case (0, _, 0):
                        return "negative_definite"
                    case (_, 0, _):
                        return "positive_semidefinite"
                    case (0, _, _):
                        return "negative_semidefinite"
                    case _:
                        return "indefinite"

            def to_quadratic_module(self):
                r"""Return the canonical quadratic form ``q(v)=b(v,v)/2``.

                The original module and value object ``W`` are retained.
                Doubling on ``W`` must be injective: its unique halves then
                satisfy quadratic homogeneity and have polarization ``b``.
                When ``2`` is invertible, its inverse supplies every half.
                Otherwise a selected finite spanning family tests evenness;
                symmetry already makes the cross terms divisible by ``2``.

                Scalar values use regularity of ``2`` and exact division in
                their actual ring.  Module values use the represented doubling
                map and its existing preimage computation.  Without established
                injectivity, choosing halves would require a quadratic
                refinement, which this canonical operation does not select.
                """
                ring = self.base_ring()
                values = self.value_module()
                unformed = self.unformed_module()
                assert ring in OwnedRings().Commutative(), (
                    f"canonical half-norm conversion of {self} is defined here over a commutative scalar ring, "
                    f"but the base ring is {ring}"
                )
                represented = _represented_value_module(self)
                two = ring(2)
                inverse = two.inverse_of_unit() if two.is_unit() is True else None
                doubling = (
                    represented.module_category()
                    .Mor(represented, represented)
                    ._from_constructed_element_map(
                        lambda element: represented.scalar_multiple(two, element)
                    )
                )
                if inverse is None:
                    assert (
                        represented.has_selected_module_resolution()
                        and represented.module_generating_set().is_finite() is True
                    ), (
                        f"canonical half-norm conversion of {self} has no selected finite doubling computation on {values}"
                    )
                    injective = doubling.is_injective()
                    if injective is False:
                        raise ValueError(
                            f"canonical half-norm conversion of {self} is not defined: doubling on {values} is not injective, "
                            "so an even bilinear form does not select a unique quadratic refinement"
                        )
                    assert injective is True, (
                        f"canonical half-norm conversion of {self} cannot decide whether doubling on {values} is injective"
                    )

                def half(value):
                    element = _value_as_module_element(self, value)
                    halved = (
                        represented.scalar_multiple(inverse, element)
                        if inverse is not None
                        else doubling.preimage(element)
                    )
                    return _value_from_module_element(self, halved)

                def half_norm(element):
                    element = self(element)
                    return half(self.b(element, element))

                if inverse is None:
                    assert (
                        unformed.has_selected_module_resolution()
                        and unformed.module_generating_set().is_finite() is True
                    ), (
                        f"canonical half-norm conversion of {self} has no selected finite spanning family for its evenness computation"
                    )
                    for generator in unformed.module_generators():
                        half_norm(generator)

                return unformed.equip_quadratic_form(values, half_norm)

    class Even(CategoryWithAxiom):
        r"""Modules with a bilinear form satisfying ``b(x, x) in 2W`` for every ``x``."""

        _certifying_predicate = "is_even"

        def an_object(self):
            r"""Return the generic bilinear-form witness, already even by construction."""
            return BilinearFormModules(self.base_ring()).an_object()

    class FinitelyPresented(CategoryWithAxiom):
        r"""Finitely presented modules with a bilinear form."""

        def an_object(self):
            r"""Return the zero finitely presented module with its zero bilinear form."""
            ring = self.base_ring()
            module = ring.free_module(0)
            form = module.bilinear_forms(ring)(lambda left, right: ring.zero())
            return BilinearFormModules(ring)(form, _extra_categories=(self,))

        class Torsion(CategoryWithAxiom):
            r"""Finitely presented torsion modules with a bilinear form."""

            def an_object(self):
                r"""Return the common torsion module equipped through this bilinear constructor."""
                ring = self.base_ring()
                common = FormModules(ring).FinitelyPresented().Torsion().an_object()
                return self.from_module(common.unformed_module(), (), ring)

            def extra_super_categories(self):
                return [FormModules(self.base_ring()).FinitelyPresented().Torsion()]

            _IsoCategory = TorsionBilinearFormIsoCategoryConstruction

            def from_module(
                self,
                module,
                gram,
                value_module,
                *,
                _subobject_ambient=None,
                _subobject_generator_images=None,
                _subobject_lift=None,
                _subobject_inclusion_factory=None,
                _extra_categories=(),
            ):
                r"""Equip ``module`` with the bilinear form represented by ``gram``.

                The value object is explicit.  Descent to the quotient is the
                validator ``validate_descent`` (``OWN-22``).
                """
                if (
                    module
                    not in Modules(self.base_ring()).FinitelyPresented().Torsion()
                ):
                    raise ValueError(
                        f"a torsion bilinear form in {self} is defined on a finitely presented torsion "
                        f"{self.base_ring()}-module, but {module} is in {module.category()}"
                    )

                rank = int(module.module_generating_set().cardinality())
                values = _coerced_gram(value_module, gram, rank)
                formed = FormModules(module.base_ring())(
                    module.bilinear_forms(value_module)(values),
                    _extra_categories=(self, *tuple(_extra_categories)),
                    _subobject_ambient=_subobject_ambient,
                    _subobject_generator_images=_subobject_generator_images,
                    _subobject_lift=_subobject_lift,
                    _subobject_inclusion_factory=_subobject_inclusion_factory,
                )
                formed.validate_descent(check=False)
                return formed

            def from_relations_and_gram(self, relation_rows, gram, value_module):
                r"""Construct a torsion bilinear form on ``coker(r)`` from relation rows and a Gram matrix.

                ``relation_rows`` write the relations in the module generators and
                define ``r: F(relations) -> F(module_generators)``; ``gram`` gives
                ``b`` on the module generators, valued in ``value_module``.
                """

                relations = _relation_morphism(self.base_ring(), relation_rows)
                module = (
                    Modules(self.base_ring()).FinitelyPresented().Torsion()(relations)
                )
                return self.from_module(module, gram, value_module)

            def cokernel(self, morphism):
                r"""Return the quotient-valued bilinear form on the literal finite cokernel of ``morphism``."""
                cover = morphism.codomain()
                if cover.base_ring() is not self.base_ring():
                    raise ValueError(
                        f"the cokernel form of {morphism} in {self} needs its codomain over {self.base_ring()}, "
                        f"but {cover} is over {cover.base_ring()}"
                    )
                module = morphism.cokernel()
                values = FractionFieldQuotients(self.base_ring())(1)
                generators = tuple(cover.module_generators())
                gram = tuple(
                    tuple(values(cover.b(left, right)) for right in generators)
                    for left in generators
                )
                return self.from_module(
                    module,
                    gram,
                    values,
                    _extra_categories=(CokernelTorsionFormModules(self.base_ring()),),
                )

            @cached_method
            def twist_functor(self, scalar):
                r"""Return the endofunctor ``(A,b) |-> (A, scalar*b)`` of this category."""
                return TorsionFormTwistFunctor(self, scalar, quadratic=False)

            class ParentMethods:
                @validator
                def validate_descent(self) -> None:
                    r"""Raise ``ValueError`` unless the form descends to the quotient (``OWN-22``).

                    The Gram values on the chosen generators define a form on
                    the cokernel exactly when every chosen relation pairs to
                    zero with every chosen generator, on both sides.
                    """
                    module = self.unformed_module()
                    value_module = self.value_module()
                    values = _coerced_gram(
                        value_module,
                        _representative_gram(self, quadratic=False),
                        int(module.module_generating_set().cardinality()),
                    )
                    if not _bilinear_descends(
                        _relation_images(module), values, value_module
                    ):
                        raise ValueError(
                            f"the Gram matrix {values} does not define a bilinear form on {module}: some "
                            f"relation of {module} does not pair to zero in {value_module} with every generator"
                        )

                def pontryagin_dual_identification(self):
                    r"""Return ``A -> Hom(A,K/R)``, ``x |-> b(x,-)``, for perfect ``b``."""
                    zero = self.zero()
                    generators = tuple(self.module_generators())
                    if any(
                        element != zero
                        and all(
                            self.b(element, generator) == self.value_module().zero()
                            for generator in generators
                        )
                        for element in self.elements()
                    ):
                        raise ValueError(
                            f"the form on {self} is degenerate: some nonzero element pairs to zero with every "
                            f"generator, so it does not identify {self} with its Pontryagin dual"
                        )
                    characters = self.module_category().Mor(self, self.value_module())

                    def character(element):
                        element = self(element)
                        return characters(
                            {
                                label: self.b(element, self.module_generator(label))
                                for label in self.module_generating_set()
                            }
                        )

                    return OwnedSets().Mor(self, characters)(character)


class QuadraticFormModules(OwnedCategoryOverBaseRing):
    def an_object(self):
        r"""The discriminant group of U, which carries a quadratic form."""
        from sage_extensions.categories.lattices import Lattices

        return Lattices(self.base_ring())("U").discriminant_group()

    def _repr_object_names(self):
        return f"modules with a quadratic form over {self.base_ring()}"

    def super_categories(self):
        return [FormModules(self.base_ring())]

    _MorCategory = FormedModuleMorCategoryConstruction

    class ParentMethods:
        def associated_bilinear_module(self):
            r"""Return the bilinear module polarized from this quadratic form.

            The result is a distinct formed object on the same unformed
            module.  Its form is

            ``b_q(x,y)=q(x+y)-q(x)-q(y)``.

            This generic construction keeps the same scalar value ring.  A
            discriminant quadratic form valued in ``K/2R`` polarizes into a
            different quotient ``K/R`` and is handled by its specialized
            discriminant-form owner instead.
            """
            assert self.value_module() is self.base_ring(), (
                f"the polar bilinear form b(x,y)=q(x+y)-q(x)-q(y) of {self} is computed here only for "
                f"forms valued in {self.base_ring()}, but q takes values in {self.value_module()}"
            )
            unformed = self.unformed_module()
            polar = unformed.bilinear_forms(self.value_module())(
                lambda left, right: (
                    self.norm(self(left) + self(right))
                    - self.norm(self(left))
                    - self.norm(self(right))
                )
            )
            return BilinearFormModules(self.base_ring()).Symmetric()(polar)

    class FinitelyPresented(CategoryWithAxiom):
        r"""Finitely presented modules with a quadratic form."""

        def an_object(self):
            r"""The discriminant group of U."""
            from sage_extensions.categories.lattices import Lattices

            return Lattices(self.base_ring())("U").discriminant_group()

        class Torsion(CategoryWithAxiom):
            r"""Finitely presented torsion modules with a quadratic form."""

            def an_object(self):
                r"""The discriminant group of U."""
                from sage_extensions.categories.lattices import Lattices

                return Lattices(self.base_ring())("U").discriminant_group()

            _IsoCategory = TorsionQuadraticFormIsoCategoryConstruction

            def from_module(
                self,
                module,
                gram,
                value_module,
                *,
                _subobject_ambient=None,
                _subobject_generator_images=None,
                _subobject_lift=None,
                _subobject_inclusion_factory=None,
                _extra_categories=(),
            ):
                r"""Equip ``module`` with ``q(x)=x^T gram x`` valued in ``value_module``.

                Symmetry of ``gram`` is the validator of the quadratic map, and
                descent to the quotient is the validator ``validate_descent``
                (``OWN-22``).
                """
                if (
                    module
                    not in Modules(self.base_ring()).FinitelyPresented().Torsion()
                ):
                    raise ValueError(
                        f"a torsion quadratic form in {self} is defined on a finitely presented torsion "
                        f"{self.base_ring()}-module, but {module} is in {module.category()}"
                    )

                rank = int(module.module_generating_set().cardinality())
                values = _coerced_gram(value_module, gram, rank)
                formed = FormModules(module.base_ring())(
                    module.quadratic_forms(value_module)(values),
                    _extra_categories=(self, *tuple(_extra_categories)),
                    _subobject_ambient=_subobject_ambient,
                    _subobject_generator_images=_subobject_generator_images,
                    _subobject_lift=_subobject_lift,
                    _subobject_inclusion_factory=_subobject_inclusion_factory,
                )
                formed.validate_descent(check=False)
                return formed

            def from_relations_and_gram(self, relation_rows, gram, value_module):
                r"""Construct a torsion quadratic form on ``coker(r)`` from relation rows and a Gram matrix.

                ``relation_rows`` write the relations in the module generators and
                define ``r: F(relations) -> F(module_generators)``; ``gram`` gives
                ``q`` on the diagonal and ``b`` off it on the module generators,
                valued in ``value_module``.
                """

                relations = _relation_morphism(self.base_ring(), relation_rows)
                module = (
                    Modules(self.base_ring()).FinitelyPresented().Torsion()(relations)
                )
                return self.from_module(module, gram, value_module)

            def cokernel(self, morphism):
                r"""Return the quotient-valued quadratic form on the literal finite cokernel of ``morphism``."""
                cover = morphism.codomain()
                if cover.base_ring() is not self.base_ring():
                    raise ValueError(
                        f"the cokernel form of {morphism} in {self} needs its codomain over {self.base_ring()}, "
                        f"but {cover} is over {cover.base_ring()}"
                    )
                module = morphism.cokernel()
                values = FractionFieldQuotients(self.base_ring())(2)
                generators = tuple(cover.module_generators())
                gram = tuple(
                    tuple(values(cover.b(left, right)) for right in generators)
                    for left in generators
                )
                return self.from_module(
                    module,
                    gram,
                    values,
                    _extra_categories=(CokernelTorsionFormModules(self.base_ring()),),
                )

            @cached_method
            def twist_functor(self, scalar):
                r"""Return the endofunctor ``(A,q) |-> (A, scalar*q)`` of this category."""
                return TorsionFormTwistFunctor(self, scalar, quadratic=True)

            class ParentMethods:
                @validator
                def validate_descent(self) -> None:
                    r"""Raise ``ValueError`` unless the quadratic form descends to the quotient (``OWN-22``).

                    For every chosen relation ``r``, ``q(r) = 0`` and the polar
                    value ``q(x+r)-q(x)-q(r)`` vanishes against every chosen
                    generator ``x``.  These are exactly the conditions for the
                    quadratic map on the cover to descend to the quotient.
                    """
                    module = self.unformed_module()
                    value_module = self.value_module()
                    values = _coerced_gram(
                        value_module,
                        _representative_gram(self, quadratic=True),
                        int(module.module_generating_set().cardinality()),
                    )
                    if not _quadratic_descends(
                        _relation_images(module), values, value_module
                    ):
                        raise ValueError(
                            f"the Gram matrix {values} does not define a quadratic form on {module}: for "
                            f"some relation r, q(r) or the polar value of r with a generator is nonzero in "
                            f"{value_module}"
                        )

                @cached_method
                def scale_submodule(self):
                    r"""Return the submodule of the value module generated by quadratic values."""
                    values = tuple(self.q(element) for element in self.elements())
                    return self.value_module().subobject_on(values)

                def subobject_generated_by(self, generators):
                    r"""Return the span as a quadratic-form-bearing subobject."""
                    return _torsion_form_subobject_on(self, generators, quadratic=True)

                def primary_part(self, prime):
                    r"""Return the ``prime``-primary quadratic-form-bearing subobject."""
                    return _torsion_form_primary_part(self, prime, quadratic=True)

                @cached_method
                def isotropic_subobjects(self):
                    r"""Return all subobjects on which the quadratic form vanishes."""
                    return _torsion_form_isotropic_subobjects(self, quadratic=True)

                @cached_method
                def maximal_isotropic_subobjects(self):
                    r"""Return the quadratic-isotropic subobjects maximal by inclusion."""
                    return _torsion_form_maximal_isotropic_subobjects(
                        self, quadratic=True
                    )

                def form_vanishes_on(self, elements) -> bool:
                    return all(
                        self.q(element) == self.value_module().zero()
                        for element in elements
                    )

                def gram_matrix(self):
                    r"""Return canonical rational representatives of the finite-form Gram values."""
                    representative = _representative_gram(self, quadratic=True)
                    rows, columns = map(int, representative.tensor_shape())
                    return (
                        representative.base_ring()
                        .matrix_space(rows, columns)
                        .from_rows(
                            tuple(
                                tuple(
                                    representative[row, column]
                                    for column in range(columns)
                                )
                                for row in range(rows)
                            )
                        )
                    )

                @cached_method(
                    key=lambda self, generators: tuple(
                        id(generator) for generator in generators
                    )
                )
                def reframing_isometry(self, generators):
                    r"""Return the explicit isometry to this form on the selected generating family."""
                    return _regenerate_form_on_generators(
                        self, tuple(generators), quadratic=True
                    )

                def regenerate(self, generators):
                    r"""Return this finite form written on the selected generating family."""
                    return self.reframing_isometry(generators).codomain()

                @cached_method
                def primary_components(self):
                    r"""Return the prime-indexed family of primary form-bearing subobjects."""
                    return _primary_form_component_family(self)

                def primary_decomposition(self, *args, **kwargs):
                    return self.primary_components(*args, **kwargs)

                @cached_method
                def subobjects(self):
                    r"""Return all form-bearing subobjects of this finite form."""
                    return _torsion_form_all_subobjects(self, quadratic=True)

                def orbit(self, element, group=None):
                    r"""Return the orbit of ``element`` under ``group`` or the full orthogonal group."""
                    return _finite_form_orbit(self, element, group)

                @cached_method
                def orbits(self, group=None):
                    r"""Return the orbit partition of the finite underlying module."""
                    return _finite_form_orbits(self, group)

                def orbits_on_subobjects(self, group=None):
                    r"""Return the orthogonal-group orbits on all form-bearing subobjects."""
                    return _finite_form_subobject_orbits(self, group=group)

                def orbits_on_isotropic_subobjects(self, group=None):
                    r"""Return the orthogonal-group orbits on isotropic subobjects."""
                    return _finite_form_subobject_orbits(
                        self, isotropic=True, group=group
                    )

                @cached_method
                def isotropic_elements(self):
                    r"""Return the elements on which the quadratic form vanishes."""
                    zero = self.value_module().zero()
                    return finite_ordered_set(self.elements()).filtered(
                        lambda element: self.q(element) == zero,
                    )

                def is_anisotropic(self) -> bool:
                    r"""Return whether zero is the only element on which ``q`` vanishes."""
                    return self.isotropic_elements().cardinality() == 1

                def orthogonal_subobject(self, subobject):
                    return _torsion_form_orthogonal_subobject(
                        self, subobject, quadratic=True
                    )

                @cached_method
                def lagrangian_subobjects(self):
                    return _torsion_form_lagrangian_subobjects(self, quadratic=True)

                def is_metabolic(self) -> bool:
                    return self.lagrangian_subobjects().cardinality() != 0

                def metabolizer(self):
                    return _finite_form_metabolizer(self)

                def restricted_form(self, subobject):
                    if subobject.inclusion().codomain() is not self:
                        raise ValueError(
                            f"the form of {self} restricts only to a submodule of {self}, but {subobject} "
                            f"is included into {subobject.inclusion().codomain()}"
                        )
                    return subobject

                def subquotient_form(self, subobject, over):
                    return _torsion_form_subquotient(
                        self, subobject, over, quadratic=True
                    )

                def orthogonal_quotient(self, subobject):
                    perpendicular = self.orthogonal_subobject(subobject)
                    return self.subquotient_form(subobject, perpendicular)

                @cached_method
                def invariant_factor_form(self):
                    r"""Return the quadratic-form isomorphism to invariant-factor framing."""
                    return _invariant_factor_form_isomorphism(self, quadratic=True)

                def p_adic_jordan_decomposition(self):
                    r"""Return the chosen quadratic Jordan generators indexed by prime."""
                    return _p_adic_jordan_decomposition(self, quadratic=True)

                def p_adic_jordan_module_generators(self):
                    r"""Return the chosen prime-by-prime quadratic Jordan generators."""
                    return _p_adic_jordan_module_generators(self, quadratic=True)

                def p_adic_jordan_form(self):
                    r"""Return the explicit isometry to this quadratic form in Jordan framing."""
                    return _p_adic_jordan_form(self, quadratic=True)

                normal_form = p_adic_jordan_form

                def normal_form_isometry(self):
                    r"""Return the normal-form-to-original morphism."""
                    return self.normal_form().inverse()

                def twist(self, scalar):
                    r"""Return the same finite module equipped with ``scalar*q``."""
                    return TorsionQuadraticFormModules(self.base_ring()).twist_functor(
                        scalar
                    )(self)

                def is_isomorphic(self, other) -> bool:
                    r"""Decide isometry of represented finite quadratic forms."""
                    if other not in TorsionQuadraticFormModules(self.base_ring()):
                        return False
                    return _forms_are_isomorphic(self, other, quadratic=True)

                is_isometric_to = is_isomorphic

                def is_anti_isometric(self, other) -> bool:
                    r"""Return whether ``(self,q)`` is isometric to ``(other,-q)``."""
                    if other not in TorsionQuadraticFormModules(self.base_ring()):
                        return False
                    return self.is_isomorphic(other.twist(-1))

                def is_discriminant_form_of_even_lattice(self, signature) -> bool:
                    r"""Return whether an even lattice of ``signature`` has discriminant form ``self``.

                    ``signature`` is a signature pair ``(t_+, t_-)``.  Existence
                    is decided by [nikulin1979integral, Thm. 1.10.1]: the
                    signature condition ``t_+ - t_- = sign q mod 8``, the rank
                    bound ``t_+ + t_- >= l(A_q)``, and the discriminant
                    conditions at each prime ``p`` with
                    ``t_+ + t_- = l(A_{q_p})``.
                    """
                    assert _engine_ring(self.base_ring()) is SageZZ, (
                        f"Nikulin's existence theorem concerns finite abelian groups; {self!r} is a finite quadratic module over {self.base_ring()!r}"
                    )
                    return _even_lattice_genus_exists(self, signature)

                @cached_method
                def automorphism_group(self):
                    r"""Return ``O(A,q)`` as a finite owned group of live automorphisms."""
                    return _torsion_form_automorphism_group(self, quadratic=True)

                def orthogonal_group(self):
                    return self.automorphism_group()

                def O(self):
                    return self.automorphism_group()

                @cached_method
                def brown_invariant(self):
                    r"""Return the Brown invariant ``Br(q)`` in ``ZZ/8ZZ`` from the Gauss sum.

                    For a nondegenerate torsion quadratic form ``q: A -> QQ/2ZZ``
                    the normalized Gauss sum is an eighth root of unity, and

                    ``|A|^(-1/2) * sum_x exp(pi*i*q(x)) = exp(pi*i*Br(q)/4)``.

                    By Milgram's formula, ``Br(q_L)`` is the signature of an even
                    lattice ``L`` mod ``8``.  The sum is computed in ``QQbar``, so
                    the comparison with each eighth root of unity is exact
                    algebraic-number equality.
                    """
                    from sage.rings.qqbar import QQbar

                    assert self.is_nondegenerate(), (
                        f"the Brown invariant is defined by the Gauss sum of a nondegenerate torsion "
                        f"quadratic form, but the bilinear form of {self} has a nonzero radical "
                        f"{self.left_radical()}"
                    )
                    values = self.value_module()
                    total = QQbar.zero()
                    for element in self.elements():
                        lifted = values.lift(self.q(element))
                        value = _engine_element(lifted.parent(), lifted)
                        total += (
                            QQbar.zeta(2 * value.denominator()) ** value.numerator()
                        )
                    phase = total / QQbar(int(self.cardinality())).sqrt()
                    zeta8 = QQbar.zeta(8)
                    integers = _owned_integers()
                    residues = integers.quotient_ring(integers.ideal(integers(8)))
                    return residues(
                        next(residue for residue in range(8) if phase == zeta8**residue)
                    )

                def b(self, left, right):
                    r"""The bilinear form ``b: A x A -> K/R`` of ``q: A -> K/2R``.

                    ``q(x + y) - q(x) - q(y) = 2 b(x, y)`` in ``K/2R``, and halving
                    ``K/2R -> K/R``, ``t + 2R |-> t/2 + R``, is an isomorphism, so
                    ``b`` is determined by ``q``: a change of lift by ``2R`` changes
                    its half by ``R``.
                    """
                    values = self.value_module()
                    assert (
                        values in FractionFieldQuotients(self.base_ring())
                        and values.modulus() == 2
                    ), (
                        f"the bilinear form of {self} is the half of its polar value, which is defined here "
                        f"for q valued in K/2R, but q takes values in {values}"
                    )
                    polar = self.q(left + right) - self.q(left) - self.q(right)
                    bilinear_values = FractionFieldQuotients(self.base_ring())(1)
                    return bilinear_values(
                        values.lift(polar) / values.fraction_field()(2)
                    )

                def value_module(self):
                    r"""Return ``K/2R``, the codomain of ``q``."""
                    return self.form().codomain()

                def _pairing_value_module(self):
                    r"""Return ``K/R``, the value module of the pairing :meth:`b`.

                    The correlation ``A -> Mor(A, K/R)``, ``x |-> b(x, -)``, is
                    the map whose kernel is the radical of ``q``.
                    """
                    return FractionFieldQuotients(self.base_ring())(1)

                def associated_bilinear_form(self):
                    r"""Forget ``q:A->K/2R`` to its bilinear form ``b:A^2->K/R``.

                    The result is a distinct object on the same unformed module,
                    whose pairing is :meth:`b`.
                    """
                    module = self.unformed_module()
                    bilinear_values = FractionFieldQuotients(self.base_ring())(1)
                    return FormModules(module.base_ring())(
                        module.bilinear_forms(bilinear_values)(
                            lambda left, right: self.b(
                                self._element_from_unformed_module(left),
                                self._element_from_unformed_module(right),
                            )
                        ),
                        _extra_categories=(
                            TorsionBilinearFormModules(self.base_ring()),
                        ),
                    )


SymmetricBilinearFormModules = BilinearFormModules.Symmetric
TorsionBilinearFormModules = BilinearFormModules.FinitelyPresented.Torsion
TorsionQuadraticFormModules = QuadraticFormModules.FinitelyPresented.Torsion


class FreeFormModules(OwnedCategoryOverBaseRing):
    def an_object(self):
        r"""The hyperbolic plane U, free and carrying a form."""
        from sage_extensions.categories.lattices import Lattices

        return Lattices(self.base_ring())("U")

    def _repr_object_names(self):
        return f"free form modules over {self.base_ring()}"

    def super_categories(self):

        return [FormModules(self.base_ring()), FramedFreeModules(self.base_ring())]

    class ParentMethods:
        def base_change(self, ring_map):
            return FormBaseChanges(ring_map.codomain())(self, ring_map)

        @cached_method
        def correlation_morphism(self):
            r"""Return the algebraic correlation ``M -> Hom_R(M,R)``."""
            injective = self in FormModules(self.base_ring()).Nondegenerate()
            return _algebraic_correlation_morphism(self, injective=injective)

        def is_unimodular(self) -> bool | Predicate:
            r"""Return whether the algebraic correlation is an isomorphism.

            On a finite free module over a commutative ring, its selected
            matrix is the Gram tensor, and the correlation is invertible
            exactly when the Gram determinant is a unit.  No correlation
            morphism or dual-module presentation needs constructing.
            A supplied unimodular placement is used before asking the
            determinant computation, as at the general form owner.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: from sage_extensions.rings.real import RR
                sage: from sage_extensions.categories.sets.set_categories import NN, Sets
                sage: from sage_extensions.categories.rings.ring_foundation import _owned_rationals
                sage: Q = _owned_rationals()
                sage: a = Sets().Mor(NN, Q)(lambda n: Q(1)/Q(2)**8192 + Q(1)/Q(2)**int(n))
                sage: x = RR.of_cauchy(a)
                sage: L = Lattices(RR).Unimodular()([[x]])
                sage: assert L.is_unimodular() is True
            """
            if self.category().is_subcategory(
                FormModules(self.base_ring()).Unimodular()
            ):
                return True
            return self._unimodularity_decision()

        @cached_method
        def _unimodularity_decision(self):
            ring = self.base_ring()
            if (
                self.module_rank().is_finite()
                and self.value_module() is ring
                and ring in OwnedRings().Commutative()
            ):
                return self.determinant().is_unit()
            correlation = _algebraic_correlation_morphism(self, injective=False)
            return conjunction(
                (correlation.is_injective(), correlation.is_surjective())
            )

        def subobject_on(self, module_generating_set):
            r"""Return the span equipped with the pulled-back form."""

            basis = _span_basis_elements(self, module_generating_set)
            return _form_subobject_spanning(self, basis)

    class FinitelyGenerated(CategoryWithAxiom):
        r"""Form modules framed by a finite basis."""

        def an_object(self):
            r"""The hyperbolic plane U."""
            from sage_extensions.categories.lattices import Lattices

            return Lattices(self.base_ring())("U")

        class ParentMethods:
            def base_change(self, ring_map):
                return FormBaseChanges(ring_map.codomain())(self, ring_map)

            def gram_matrix(self, basis=None):
                r"""Return the coordinate matrix of the selected finite free form."""
                if (
                    basis is None
                    and _is_bilinear_form(self.form())
                    and self.value_module() in OwnedRings()
                ):
                    size = int(self.module_rank())
                    gram = self.gram_tensor()
                    return (
                        self.value_module()
                        .matrix_space(size, size)
                        .from_rows(
                            (gram[row, column] for column in range(size))
                            for row in range(size)
                        )
                    )
                selected = (
                    tuple(self.module_generators()) if basis is None else tuple(basis)
                )
                if any(vector.parent() is not self for vector in selected):
                    raise ValueError(
                        f"a Gram matrix of {self} is taken on elements of {self}, but {basis} contains "
                        "an element of another module"
                    )
                size = len(selected)
                return (
                    self.value_module()
                    .matrix_space(size, size)
                    .from_rows(
                        tuple(
                            tuple(self.b(left, right) for right in selected)
                            for left in selected
                        )
                    )
                )

            @cached_method
            def dual_module(self):

                return self.base_ring().free_module(self.module_generating_set())

            @cached_method
            def radical(self):
                r"""Return the left radical ``ker(M -> Hom_R(M,W))``."""
                return self.left_radical()

            @cached_method
            def radical_quotient(self):
                r"""Return ``M/(rad_left(M) ∩ rad_right(M))`` with its descended form.

                For a nonsymmetric bilinear form, the left and right radicals
                can differ. The quotient pairing is defined only after killing
                their intersection, the largest submodule that annihilates in
                both arguments. Over a field, the result is re-presented on a
                basis of that quotient, so the returned module need not be the
                literal cokernel object.
                """
                radical = self.left_radical().intersection(self.right_radical())
                inclusion = radical.inclusion()
                value_module = self.value_module()
                value_identity = (
                    value_module.module_category()
                    .Mor(value_module, value_module)
                    .identity()
                )
                descended = self._formed_form().descend_along(inclusion, value_identity)
                quotient = descended.module()
                ring = quotient.base_ring()
                cokernel_projection = inclusion.cokernel_projection()
                basis_map = None
                # Over a field, a finite presentation is not itself a free
                # presentation: its selected generators can outnumber its
                # vector-space dimension.  Re-present the quotient on an
                # actual basis before returning the formed module, so its
                # underlying module and Gram tensor have the same rank.
                if (
                    ring in OwnedFields()
                    and quotient.module_generating_set().cardinality().is_finite()
                ):
                    basis_labels = quotient.basis_generator_labels()
                    free = ring.free_module(basis_labels)
                    basis_map = free.module_category().Mor(free, quotient)(
                        lambda label: quotient.module_generator(label)
                    )
                    pulled_back = descended.pullback(basis_map)
                    if value_module in OwnedRings():
                        descended = free.bilinear_forms(value_module)(
                            pulled_back.gram_tensor()
                        )
                    else:
                        descended = free.bilinear_forms(value_module)(
                            lambda left, right: pulled_back(left, right)
                        )
                return FormModules(ring)(
                    descended,
                    _extra_construction_data={
                        "radical_quotient_cokernel_projection": cokernel_projection,
                        "radical_quotient_basis_map": basis_map,
                    },
                )

            @cached_method
            def radical_quotient_projection(self):
                r"""Return the canonical formed-module map to ``radical_quotient()``.

                The quotient retains the canonical map from the unformed
                module to its cokernel. When that cokernel is re-presented on
                a field basis, compose this map with the inverse of the basis
                isomorphism. The resulting arrow has the exact returned
                formed module as codomain.
                """
                quotient = self.radical_quotient()
                projection = quotient._preamble_radical_quotient_cokernel_projection
                if projection is not None:
                    basis_map = quotient._preamble_radical_quotient_basis_map
                    if basis_map is not None:
                        projection = basis_map.inverse() * projection
                else:
                    # Lattices retain their specialized isotropic-reduction
                    # construction. Its projection starts at the represented
                    # perpendicular subobject, so lift the ambient generators
                    # through that subobject's retained inclusion first.
                    perpendicular = quotient.orthogonal_complement()
                    inclusion = perpendicular.inclusion()
                    reduction_projection = quotient.projection()
                    source_module = self.unformed_module()
                    target_module = quotient.unformed_module()
                    projection = source_module.module_category().Mor(
                        source_module, target_module
                    )(
                        lambda label: quotient._element_of_unformed_module(
                            reduction_projection(
                                inclusion.lift(
                                    self(source_module.module_generator(label))
                                )
                            )
                        )
                    )
                values = self.value_module()
                value_identity = values.module_category().Mor(values, values).identity()
                return FormModules(self.base_ring()).Mor(self, quotient)(
                    (projection, value_identity)
                )

            def determinant(self):
                r"""Return the Gram determinant of a form with values in a ring containing ``R``."""
                from sage_extensions.tensors.tensor import Tensor

                numerical = self.gram_tensor()
                assert isinstance(numerical, Tensor), (
                    f"the determinant of the form on {self} needs numerical scalar data, "
                    f"but it takes values in {self.value_module()}"
                )
                rank = int(self.module_rank())
                return (
                    numerical.base_ring()
                    .matrix_space(rank)
                    .from_rows(
                        (numerical[i, j] for j in range(rank)) for i in range(rank)
                    )
                    .determinant()
                )


class FormBaseChanges(OwnedCategoryOverBaseRing):
    r"""Formed scalar extensions retaining their source and scalar map."""

    def super_categories(self):
        return [FormModules(self.base_ring())]

    def _call_(self, source, ring_map):
        if ring_map.codomain() is not self.base_ring():
            raise ValueError(
                "the scalar extension must end at this category's base ring"
            )
        return _formed_module_base_change(source, ring_map)

    class ParentMethods:
        def __init__(self, base_change_source, base_change_ring_map, **rest):
            self._base_change_source = base_change_source
            self._base_change_ring_map = base_change_ring_map
            super().__init__(**rest)

        def _pairing_value_module(self):
            return self.base_ring()

        def b(self, left, right):
            return _value_from_module_element(self, super().b(left, right))

        def norm(self, element):
            return _value_from_module_element(self, super().norm(element))

        def gram_tensor(self):
            source = self.base_change_source()
            if source.module_rank().is_finite() and _is_bilinear_form(self.form()):
                return _base_changed_scalar_gram(source, self.base_change_ring_map())
            return super().gram_tensor()

        def base_change_source(self):
            return self._base_change_source

        def base_change_ring_map(self):
            return self._base_change_ring_map

        def base_change_unit(self):
            r"""The source-to-restriction map of this scalar-extension construction."""
            source = self.base_change_source()
            return (
                Modules(source.base_ring())
                .base_change_adjunction(self.base_change_ring_map())
                .unit(source)
            )


class FormValueScalings(OwnedCategoryOverBaseRing):
    r"""Scalar changes of a form's values, normalized under composition.

    Unit simplification and property preservation require explicit true
    scalar decisions. An unknown equality or unit predicate does not
    prevent forming the scaled bilinear or quadratic map.

    EXAMPLES::

        sage: from sage_extensions.categories.lattices import Lattices
        sage: from sage_extensions.categories.sets.set_categories import NN, Sets
        sage: from sage_extensions.rings.real import RR
        sage: from sage_extensions.categories.rings.ring_foundation import _owned_rationals
        sage: QQ = _owned_rationals()
        sage: a = Sets().Mor(NN, QQ)(lambda n: QQ(1)/QQ(2)**int(n))
        sage: z = RR.of_cauchy(a)
        sage: U = Lattices(RR)("U")
        sage: scaled = U.twist(z)
        sage: assert scaled.unscaled_form_module() is U
        sage: assert scaled.form_scale() is z
        sage: assert scaled.base_ring() is RR
        sage: assert U.twist(RR.one()) is U
    """

    def super_categories(self):
        return [FormModules(self.base_ring())]

    def __call__(self, source, scalar):
        return self._call_(source, scalar)

    def _call_(self, source, scalar):
        scalar = self.base_ring()(scalar)
        if source in self:
            scalar *= source.form_scale()
            source = source.unscaled_form_module()
        if (scalar == self.base_ring().one()) is True:
            return source
        return _scaled_form_module(source, scalar)

    class ParentMethods:
        def __init__(self, unscaled_form_module, form_scale, **rest):
            self._unscaled_form_module = unscaled_form_module
            self._form_scale = form_scale
            super().__init__(**rest)

        def unscaled_form_module(self):
            return self._unscaled_form_module

        def form_scale(self):
            return self._form_scale


@cached_function(key=lambda source, scalar: (id(source), scalar))
def _scaled_form_module(source, scalar):
    r"""Realize value scaling on the original underlying module and form.

    Composition multiplies the value scalars before this constructor runs.
    Thus the unit action returns the original object, including a double
    sign twist. No cancellation by a nonunit is used.
    """
    from sage_extensions.categories.lattices import Lattices, OrthogonalSumLattices

    # Scaling changes the selected form on its original module, not the
    # form re-expressed on the already-formed parent.  The latter constructs
    # a second tensor-product Hom object before any scaling takes place.
    form = source.form()
    module = form.module()
    values = source.value_module()
    if _is_bilinear_form(form):
        # This is already the defining Hom object of the form; rebuilding it
        # from the module can allocate a fresh rank^2 tensor-power framing.
        forms = form.parent()
        if form.codomain() in OwnedRings() and _has_finite_framing(module):
            scaled_gram = scalar * form.gram_tensor()
            scaled = forms(scaled_gram)
            # The Hom constructor retains its defining tensor directly.
        elif _has_finite_framing(module):
            scaled = forms(form.coordinate_values().map(lambda value: scalar * value))
        else:
            scaled = forms(lambda left, right: scalar * form(left, right))
    elif form.has_selected_bilinear_lift():
        scaled = module.quadratic_forms(values)(
            form.lift_coordinate_values().map(lambda value: scalar * value)
        )
    else:
        scaled = module.quadratic_map(values, lambda element: scalar * form(element))

    ring = source.base_ring()
    categories = [FormValueScalings(ring)]
    if _is_bilinear_form(form) and source in BilinearFormModules(ring).Symmetric():
        # (sb)(x,y) = s b(x,y) = s b(y,x) = (sb)(y,x): symmetry
        # transports through scalar change, without inspecting any entries.
        categories.append(BilinearFormModules(ring).Symmetric())
    unit = (scalar != ring.zero()) if ring in OwnedFields() else scalar.is_unit()
    known_unit = unit is True
    if known_unit and source in FormModules(ring).Unimodular():
        # Multiplication by a unit is an isomorphism on the value module;
        # the correlation of sb is the correlation of b composed with it.
        categories.append(FormModules(ring).Unimodular())
    if source in FormModules(ring).Nondegenerate() and (
        known_unit
        or (ring in OwnedIntegralDomains() and (scalar != ring.zero()) is True)
    ):
        # Multiplication by a unit is injective on every value module;
        # on an integral domain it is injective on this R-valued form.
        # Hence both radicals remain zero under the scalar change.
        if known_unit or form.codomain() in OwnedRings():
            categories.append(FormModules(ring).Nondegenerate())
    data = dict(unscaled_form_module=source, form_scale=scalar)
    if source in Lattices(ring):
        categories.append(Lattices(ring))
        # The lattice's defining Gram is a tensor or a pairing rule, also at
        # infinite rank.  The scaled form morphism cannot recover a Gram by
        # listing basis pairs when its basis is infinite.  Scale the original
        # selected Gram directly; pairing-rule tensors retain that rule.
        data["gram_tensor"] = (
            scaled_gram
            if _is_bilinear_form(form)
            and form.codomain() in OwnedRings()
            and _has_finite_framing(module)
            else source.gram_tensor() * scalar
        )
        if source in Lattices(ring).FinitelyGenerated():
            categories.append(Lattices(ring).FinitelyGenerated())
        # The lattice parity axiom is determined by the scaled diagonal.
        # The tensor has already been supplied and cached; no new pairing
        # evaluation, tensor-product classifier or determinant is required.
        from sage_extensions.categories._lattice import _gram_is_even

        if _gram_is_even(data["gram_tensor"], ring) is True:
            categories.append(Lattices(ring).Even())
        # The zero free module has an isomorphism 0 -> Hom(0,R) for every
        # scalar, including zero and nonunits.
        if source.module_rank().is_finite() and int(source.module_rank()) == 0:
            categories.extend(
                (Lattices(ring).Nondegenerate(), Lattices(ring).Unimodular())
            )
        if source in OrthogonalSumLattices(ring):
            categories.append(OrthogonalSumLattices(ring))
            data["biproduct_factors"] = source.biproduct_factors().map(
                lambda factor: FormValueScalings(ring)(factor, scalar),
                name=f"Orthogonal summands scaled by {scalar}",
            )
    return _form_module(
        scaled, _extra_categories=categories, _extra_construction_data=data
    )


def _form_module_categories(module, *, bilinear, extra_categories):
    r"""Return the placement of a module equipped with the stated kind of form."""
    base_ring = module.base_ring()
    categories = [FormModules(base_ring)]
    if module in VectorSpaces(base_ring):
        categories.append(VectorSpaces(base_ring))
    is_free = module in FramedFreeModules(base_ring)
    is_presented = module in ModulesWithChosenFinitePresentation(base_ring)
    if is_free:
        categories.append(FreeFormModules(base_ring))
    if is_presented:
        categories.append(FormModules(base_ring).FinitelyPresented())
        if module in Modules(base_ring).FinitelyPresented().Torsion():
            categories.append(FormModules(base_ring).FinitelyPresented().Torsion())
    if module in FramedFreeModules(base_ring).FinitelyGenerated():
        categories.append(FreeFormModules(base_ring).FinitelyGenerated())
    if bilinear:
        categories.append(BilinearFormModules(base_ring))
        symmetric = BilinearFormModules(base_ring).Symmetric()
        # An existing category inclusion already establishes symmetry.  For
        # example Lattices(R) is a subcategory of symmetric bilinear forms,
        # and scalar changes preserve this property.  Rechecking all tensor
        # entries at construction would redo an established fact.
        known_symmetric = any(
            category.is_subcategory(symmetric) for category in extra_categories
        )
        if known_symmetric:
            categories.append(symmetric)
    else:
        categories.append(QuadraticFormModules(base_ring))
    categories.extend(tuple(extra_categories))
    return categories


def _form_module(
    form,
    *,
    _extra_categories=(),
    _extra_construction_data=None,
    _subobject_ambient=None,
    _subobject_generator_images=None,
    _subobject_lift=None,
    _subobject_inclusion_factory=None,
):
    r"""Equip the exact represented module carrying ``form`` with that form.

    The module owner chooses the realization of the stronger object.  The
    formed layer supplies only its selected form and, for a subobject, the
    retained inclusion datum.  A distinct structured parent still represents
    each choice of form, but this owner does not rebuild the module's framing
    or presentation.
    """

    if not (_is_bilinear_form(form) or _is_quadratic_form(form)):
        raise TypeError(
            f"a module with a form is built from a bilinear or quadratic form, but {form} is neither"
        )
    module = form.module()
    categories = _form_module_categories(
        module,
        bilinear=_is_bilinear_form(form),
        extra_categories=_extra_categories,
    )
    construction_data = dict(_extra_construction_data or {})
    construction_data["source_form"] = form
    return _construct_form_module(
        module,
        categories,
        construction_data,
        _subobject_ambient=_subobject_ambient,
        _subobject_generator_images=_subobject_generator_images,
        _subobject_lift=_subobject_lift,
        _subobject_inclusion_factory=_subobject_inclusion_factory,
    )


def _construct_form_module(
    module,
    categories,
    construction_data,
    *,
    _subobject_ambient=None,
    _subobject_generator_images=None,
    _subobject_lift=None,
    _subobject_inclusion_factory=None,
):
    r"""Build the formed module after its placement and defining data are selected."""
    base_ring = module.base_ring()
    match (_subobject_ambient, _subobject_inclusion_factory):
        case (None, None):
            pass
        case _:
            from sage_extensions.categories.abstract_categories.cat import Cat
            from sage_extensions.categories.modules.pure.modules import ModuleSubobjects

            # A formed submodule is a formed module with an inclusion as
            # additional data: its ambient category (ARC-07) is that of the
            # formed modules, without the subobject placements below.
            construction_data["_constructing_category"] = Cat().meet(tuple(categories))
            categories.append(ModuleSubobjects(base_ring))
            match _subobject_ambient:
                case None:
                    pass
                case ambient:
                    categories.append(Modules(base_ring).Subobjects(ambient))
            construction_data.update(
                subobject_ambient=_subobject_ambient,
                subobject_generator_images=_subobject_generator_images,
                subobject_lift=_subobject_lift,
                subobject_inclusion_factory=_subobject_inclusion_factory,
            )
    formed = module._module_with_structure(tuple(categories), construction_data)
    formed.validate_form_placement(check=False)
    return formed


def _form_module_from_bilinear_computation(
    module,
    form_computation,
    *,
    _extra_categories=(),
    _extra_construction_data=None,
    _subobject_ambient=None,
    _subobject_generator_images=None,
    _subobject_lift=None,
    _subobject_inclusion_factory=None,
):
    r"""Equip ``module`` from defining data that computes its bilinear form lazily."""
    categories = _form_module_categories(
        module,
        bilinear=True,
        extra_categories=_extra_categories,
    )
    construction_data = dict(_extra_construction_data or {})
    construction_data["source_form"] = None
    construction_data["source_form_computation"] = form_computation
    return _construct_form_module(
        module,
        categories,
        construction_data,
        _subobject_ambient=_subobject_ambient,
        _subobject_generator_images=_subobject_generator_images,
        _subobject_lift=_subobject_lift,
        _subobject_inclusion_factory=_subobject_inclusion_factory,
    )


@cached_function(key=lambda module, basis: (id(module), basis))
def _form_subobject_spanning(module, basis):
    r"""Return the canonical formed subobject on a finite span basis."""

    subobject = _module_subobject_spanning(module, basis)
    construction = subobject.module_subobject_construction()
    restricted = module.pullback_form(subobject.inclusion())
    embedded = construction.generator_images()

    def inclusion_factory(source):
        return source.Mono(module)(embedded)

    return FormModules(module.base_ring())(
        restricted,
        _subobject_ambient=construction.ambient_module(),
        _subobject_generator_images=embedded,
        _subobject_lift=construction.selected_lift(),
        _subobject_inclusion_factory=inclusion_factory,
    )


def _bilinear_form(module, form):
    r"""Equip ``module`` with its already constructed bilinear Hom element."""
    formed = FormModules(module.base_ring())(form)
    if formed.unformed_module() is not module:
        raise TypeError(
            f"{module} can be equipped only with a form on that exact module, "
            f"but this form is on {formed.unformed_module()}"
        )
    return formed


def _quadratic_form(module, value_module, datum):
    r"""Return ``module`` equipped with the stated quadratic form."""

    coordinate_datum = isinstance(datum, IndexedFamily) or (
        isinstance(datum, Iterable) and not isinstance(datum, (str, bytes))
    )
    form = (
        module.quadratic_forms(value_module)(datum)
        if coordinate_datum
        else module.quadratic_map(value_module, datum)
    )
    return FormModules(module.base_ring())(form)
