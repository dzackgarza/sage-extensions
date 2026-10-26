r"""Graded integrable maps, their a.e. quotients, and the two distinct products.

Pointwise multiplication is total on the nonnegative Holder grading. Young
convolution is a family of bilinear maps on s+t>=1, not a multiplication on
all pairs in the direct sum. Its L1 component is a total nonunital algebra.
"""

from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.infinity import Infinity
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.algebras.algebras import (
    Algebras,
    _algebra_on_module,
)
from sage_extensions.categories.algebras.graded_algebras import GradedAlgebras
from sage_extensions.categories.functions.real_functions import (
    Lp,
    _constant_map,
    _pointwise_product,
    _integrability,
    _is_lebesgue_space,
)
from sage_extensions.categories.modules.graded_direct_sums import (
    GradedDirectSumElement,
    _DirectSumOfModules,
    _direct_sum_of_modules,
)
from sage_extensions.categories.modules.graded_modules import GradedModules
from sage_extensions.categories.modules.pure.modules import Modules, TensorProductModules
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    _owned_ring,
)
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.rings.nonnegative_reals import NonNegativeReals
from sage_extensions.rings.real import RR
from sage_extensions.rings.unit_interval import UnitInterval
from sage_extensions.categories.functions.lebesgue_quotients import _is_lebesgue_quotient
from sage_extensions.categories.functions.convolution import _convolution_algebra, _convolution_pairing_family


def _real_ring():
    return _owned_ring(RR)


def _holder_degree(space):
    exponent = space.integrability_exponent()
    if exponent is Infinity:
        return NonNegativeReals.zero()
    return ~NonNegativeReals(exponent)


def _lebesgue_exponent(degree):
    value = degree.as_extended_real()
    if value is Infinity:
        raise TypeError(f"degree {degree} is ∞, so the graded piece would be L^0")
    if value == RR.zero():
        return Infinity
    return _integrability(RR.one() / RR(value))


def _pointwise_piece_product(left, right, degree):
    r"""The pointwise product, in the Lebesgue space of the sum of the Hölder degrees."""
    return Lp(_lebesgue_exponent(degree), RR, RR)(_pointwise_product(left, right))


def _compose_morphisms(left, right):
    r"""Compose the represented linear maps in their common module Mor."""
    assert right.codomain() is left.domain(), (
        f"cannot compose {left} after {right}: {right} ends at {right.codomain()}, but {left} starts at "
        f"{left.domain()}"
    )
    modules = Modules(left.domain().base_ring())
    return modules.Mor(left.domain(), left.codomain())(left) * modules.Mor(
        right.domain(), right.codomain()
    )(right)


class LebesgueGradedModules(OwnedCategoryOverBaseRing):
    r"""Graded modules whose homogeneous pieces are Lebesgue spaces \(L^{1/s}\)."""

    def an_object(self):
        r"""The Lebesgue spaces graded by the non-negative reals."""
        return GradedLebesgueModule(NonNegativeReals)

    @classmethod
    def _repr_object_names(cls):
        return "Lebesgue graded modules"

    def super_categories(self):
        return [Modules(self.base_ring())]

    class ParentMethods:
        def quotient_by_null_functions(self):
            return _graded_lebesgue_quotient(self)

        def degree_projection(self, degree):
            r"""The projection \(\pi_s\colon N\to L^{1/s}\) onto a homogeneous piece."""
            return self.projection(degree)

        def integration_of_degree_one(self):
            r"""Integration \(\iota\colon L^1\to\mathbb R\) of the degree-\(1\) piece."""
            return self.graded_piece(self.grading_index_set()(1)).integration_morphism()

        def integral_form(self):
            r"""The linear form \(\varepsilon=\iota\circ\pi_1\colon N\to\mathbb R\).

            This is not an algebra morphism. It integrates the degree-\(1\)
            piece and vanishes on the complementary summands.
            """
            degree_one = self.grading_index_set()(1)
            return _compose_morphisms(
                self.integration_of_degree_one(),
                self.degree_projection(degree_one),
            )

        def unit_piece_projection(self):
            r"""The graded augmentation \(A\to A_u\), for a unital graded algebra.

            Convolution \(L^1(\mathbb R)\) is not unital, so it does not
            supply this morphism.
            """
            ring = self.base_ring()
            match self:
                case _ if self in Algebras(ring).Unital():
                    return self.degree_projection(
                        self.grading_monoid().monoidal_unit()
                    )
                case _:
                    raise TypeError(
                        f"{self} is not a unital algebra; "
                        "the unit-piece projection is the graded augmentation "
                        "of a unital graded algebra"
                    )

        def integral_pairing_morphism(self):
            r"""The pairing \(B=\varepsilon\circ m\colon A\otimes_{\mathbb R}A\to\mathbb R\)."""
            ring = self.base_ring()
            match self:
                case _ if self in Algebras(ring).Associative():
                    multiplication = self.multiplication_morphism()
                    return _compose_morphisms(self.integral_form(), multiplication)
                case _:
                    raise TypeError(
                        f"{self} has no chosen multiplication morphism"
                    )

        def integral_pairing(self):
            r"""The pairing \(B\) as an element of \(\operatorname{Hom}(A\otimes A,\mathbb R)\)."""
            composite = self.integral_pairing_morphism()
            multiplication = self.multiplication_morphism()
            tensor = multiplication.domain()
            return self.pairings_with(self, RR)(
                lambda left, right, composite=composite, tensor=tensor: composite(
                    tensor.pure_tensor(left, right)
                )
            )


class _LebesgueDirectSum(_DirectSumOfModules):
    r"""The module direct-sum engine with literal ingress for an integrable map.

    Arithmetic, homogeneous components, scalar action, injections, projections
    and reconstruction under extra structure belong to the direct-sum owner.
    Only reading a map in its summand is specific to the Lebesgue presentation.
    """

    def _direct_sum_realization(self):
        return _LebesgueDirectSum, GradedDirectSumElement

    def _element_constructor_(self, value):
        source = element_parent(value)
        if source is self:
            return value
        if _is_lebesgue_space(source):
            degree = self.grading_index_set()(_holder_degree(source).as_extended_real())
            return self.from_component(degree, value)
        if self in Algebras(self.base_ring()).Unital() and value in self.base_ring():
            return self.from_component(self.grading_monoid().monoidal_unit(), Lp(Infinity, RR, RR)(_constant_map(value)))
        return super()._element_constructor_(value)

    def _repr_(self):
        return f"Lebesgue direct sum over {self.grading_index_set()}"

    def _latex_(self):
        return r"\bigoplus_s \mathcal{L}^{1/s}(\mathbb{R})"


@cached_function
def GradedLebesgueModule(grading_monoid):
    r"""The finite-support direct sum of the integrable-map spaces in Hölder degree.

    Hölder degrees are finite.  Extending this grading to the extended
    nonnegative monoid puts the zero module in degree infinity; it does not
    introduce a nonexistent integrability exponent zero.
    """
    ring = _real_ring()

    def piece(degree):
        match degree.as_extended_real():
            case value if value is Infinity:
                return ring.free_module(0)
            case _:
                return Lp(_lebesgue_exponent(degree), RR, RR)

    return _direct_sum_of_modules(
        ring, grading_monoid, indexed_family(grading_monoid, piece),
        extra_categories=(LebesgueGradedModules(ring),),
        _realization=(_LebesgueDirectSum, GradedDirectSumElement),
    )


def _pointwise_graded_product(module, left, right):
    r"""Multiply finite homogeneous sums, with Hölder degree added in each term."""
    return sum((
        module.from_component(
            module.combine_degrees(s, t),
            _pointwise_piece_product(f, g, module.combine_degrees(s, t)),
        )
        for s, f in module(left).homogeneous_components().items()
        for t, g in module(right).homogeneous_components().items()
    ), module.zero())


@cached_function
def graded_lebesgue_algebra():
    r"""The pointwise algebra, constructed on the module by its tensor classifier.

    Hölder gives the product of the summands.  Pointwise associativity and
    commutativity extend to finite sums, and the constant one in degree zero
    is a two-sided unit.  These are the construction's axioms, not conclusions
    drawn from sampling functions or the grading monoid.
    """
    ring = _real_ring()
    module = GradedLebesgueModule(NonNegativeReals)
    tensor = Modules(ring).tensor_product((module, module))
    multiplication = tensor.from_bilinear_map(
        module, lambda left, right: _pointwise_graded_product(module, left, right),
    )
    category = Cat().meet((
        GradedAlgebras(ring, NonNegativeReals),
        Algebras(ring).Associative().Unital().Commutative(),
        LebesgueGradedModules(ring),
    ))
    return _algebra_on_module(
        module, multiplication, placement=(category,),
        unit=module.from_component(NonNegativeReals.zero(), Lp(Infinity, RR, RR).one()),
        law_decisions={
            "associativity": True,
            "unit": True,
            "commutativity": True,
            "grading": True,
        },
    )




class _LebesgueQuotientSum(_DirectSumOfModules):
    def __init__(self, map_sum, **rest):
        self._map_sum = map_sum
        super().__init__(**rest)

    def map_sum(self):
        return self._map_sum

    def _direct_sum_realization(self):
        return _LebesgueQuotientSum, GradedDirectSumElement

    def _module_with_structure(self, categories, construction_data):
        return super()._module_with_structure(categories, {**construction_data, "map_sum": self.map_sum()})

    def _element_constructor_(self, value):
        source = element_parent(value)
        if _is_lebesgue_quotient(source) or _is_lebesgue_space(source):
            exponent = source.integrability_exponent()
            degree = self.grading_index_set()(RR.zero() if exponent is Infinity else RR.one() / RR(exponent))
            return self.from_component(degree, self.graded_piece(degree)(value))
        return super()._element_constructor_(value)

    @cached_method
    def quotient_projection(self):
        def component_map(degree):
            source, target = self.map_sum().graded_piece(degree), self.graded_piece(degree)
            projection = Modules(RR).Mor(source, source).identity() if source is target else target.quotient_projection()
            return self.injection(degree) * projection

        return self.map_sum().from_maps(self, indexed_family(self.grading_index_set(), component_map))

    def convolution(self, left, right):
        r"""Sum the Young pairings of the finitely many represented components.

        A pair outside Young's domain is refused, not replaced by zero. With
        undecided null components this may require a better representative;
        no rejection is interpreted as proof that an individual convolution
        integral cannot exist outside Young's sufficient exponent hypotheses.
        """
        def product(s, f, t, g):
            pair = UnitInterval.degree_pairs()(lambda i: UnitInterval(s.as_extended_real()) if int(i) == 0 else UnitInterval(t.as_extended_real()))
            degree = UnitInterval.young_degree_map()(pair)
            value = f.parent().convolution_pairing(g.parent())(f, g)
            return self.from_component(self.grading_index_set()(degree.as_extended_real()), value)

        return sum((product(s, f, t, g)
            for s, f in self(left).homogeneous_components().items()
            for t, g in self(right).homogeneous_components().items()), self.zero())


@cached_function(key=id)
def _graded_lebesgue_quotient(map_sum):
    def piece(degree):
        source = map_sum.graded_piece(degree)
        return source.quotient_by_null_functions() if _is_lebesgue_space(source) else source

    indices = map_sum.grading_index_set()
    return _direct_sum_of_modules(RR, indices, indexed_family(indices, piece),
        extra_categories=(LebesgueGradedModules(RR),),
        _realization=(_LebesgueQuotientSum, GradedDirectSumElement),
        construction_data={"map_sum": map_sum})


def GradedTensorProductModules(ring):
    return TensorProductModules(ring)


def GradedTensorSquare(module):
    return Modules(module.base_ring()).tensor_product((module, module))


def lebesgue_convolution_algebra():
    return _convolution_algebra()


GradedLebesgueAlgebra = graded_lebesgue_algebra()
LebesgueConvolution = _convolution_pairing_family()
LebesgueConvolutionModule = GradedLebesgueModule(UnitInterval).quotient_by_null_functions()
LebesgueConvolutionAlgebra = lebesgue_convolution_algebra()
