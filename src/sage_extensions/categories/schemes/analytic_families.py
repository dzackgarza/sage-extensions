r"""Analytic-disc families and the analytification of affine and projective spaces.

The analytic objects here are genuine complex manifolds with the topology of
open subsets of ``C^n``.  The comparison is deliberately narrow: an affine
space over ``QQ`` is first read through the selected embedding ``QQ -> CC`` and
then sent to its complex analytic affine space; polynomial morphisms are sent
to the same polynomial coordinate formulas.  Restricting the analytified
projection ``A^2 -> A^1`` to the unit disc gives the first analytic family.

No formal power series is used to construct the disc.  Coherent GAGA is also
not asserted for this affine example: transport of coherent sheaf cohomology
requires the usual proper complex-algebraic hypotheses, which this family does
not satisfy.
"""

from sage.all import QQ as SageQQ
from sage.all import QQbar as SageQQbar
from sage.categories.number_fields import NumberFields as SageNumberFields
from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import parent as element_parent
from sage.symbolic.ring import SR as SageSR

from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.manifolds import (
    ComplexManifolds,
    _engine_manifold_expression,
    _raise_manifold_expression,
)
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_complex_field,
    _owned_rationals,
    _owned_ring,
)
from sage_extensions.categories.schemes.schemes import (
    AffineSpaces,
    ProjectiveSpaces,
    Schemes,
    _evaluate_owned_homogeneous_polynomial_on_coordinates,
    _polynomial_exponents,
    _projective_coordinate_morphism,
)
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.rings.real import RR


def _exact_algebraic_embedding(source_ring, scalar_embedding):
    r"""The embedding ``K -> QQbar`` through which ``sigma : K -> CC`` factors.

    A number field ``K`` has finitely many embeddings ``K -> QQbar``, and
    ``sigma`` is one of them followed by ``QQbar -> CC``: the one whose
    generator image agrees exactly with ``sigma`` of that generator.
    Over ``QQ`` it is the unique embedding.  The coefficients of an
    analytified map are their exact images under it.

    Engine adapter (``OWN-06``): read the private Sage field of ``K`` and
    return the private Sage embedding into ``QQbar``.
    """
    engine_source = _engine_ring(source_ring)
    assert engine_source in SageNumberFields(), (
        f"cannot keep the coefficients of an analytification along {scalar_embedding} "
        f"exact: their exact images are computed for number fields, and {source_ring} is "
        f"not a number field"
    )
    if engine_source is SageQQ:
        return SageQQbar.coerce_map_from(SageQQ)
    target = scalar_embedding.codomain()
    generator_image = scalar_embedding(_owned_engine_element(source_ring, engine_source.gen()))
    matching = tuple(
        embedding for embedding in engine_source.embeddings(SageQQbar)
        if (target(embedding(engine_source.gen())) == generator_image) is True
    )
    assert len(matching) == 1, (
        f"the exact generator image {generator_image} of {scalar_embedding} "
        f"must select one algebraic embedding, but it selects {len(matching)}"
    )
    return matching[0]


def _exact_coefficient_expression(algebraic_number):
    r"""Write an algebraic number as an exact symbolic constant.

    Engine adapter: Sage's symbolic ring holds a rational number exactly, and
    an irrational algebraic number exactly as its radical expression.
    ``radical_expression`` returns the algebraic number itself, outside the
    symbolic ring, when it finds none.
    """
    if algebraic_number in SageQQ:
        return SageSR(SageQQ(algebraic_number))
    expression = algebraic_number.radical_expression()
    assert element_parent(expression) is SageSR, (
        f"cannot write the coefficient {algebraic_number} of an analytified map exactly: "
        f"it has no expression by radicals"
    )
    return expression


def _polynomial_chart_expression(algebra, polynomial, chart, scalar_embedding):
    r"""Raise one algebra polynomial to the corresponding complex chart formula.

    Each coefficient ``c`` becomes the exact algebraic number ``sigma(c)``, so
    that analytification preserves identities and composites exactly; it is
    read in ``CC`` only when a point is substituted.

    Engine adapter (``OWN-06``): read the private Sage polynomial of an owned
    algebra element and write the Sage symbolic chart expression.
    """
    backend = _engine_element(algebra, algebra(polynomial))
    source_ring = algebra.base_ring()
    engine_source = _engine_ring(source_ring)
    exact_embedding = _exact_algebraic_embedding(source_ring, scalar_embedding)
    variables = tuple(
        _engine_manifold_expression(variable)
        for variable in chart.coordinates()
    )
    result = 0
    for exponent, coefficient in backend.monomial_coefficients().items():
        powers = _polynomial_exponents(exponent, len(variables))
        term = _exact_coefficient_expression(exact_embedding(engine_source(coefficient)))
        for variable, power in zip(variables, powers, strict=True):
            if power:
                term *= variable**power
        result += term
    return _raise_manifold_expression(result)


class _AffineSpaceAnalytificationFunctor(Functor):
    r"""Supported analytification of affine spaces and polynomial maps."""

    def __init__(self, scalar_embedding) -> None:
        self._scalar_embedding = scalar_embedding
        source = _owned_ring(scalar_embedding.domain())
        target = _owned_ring(scalar_embedding.codomain())
        assert target is _owned_complex_field(), (
            f"analytification along {scalar_embedding} needs an embedding into the complex "
            f"numbers CC, but its codomain is {target}"
        )
        super().__init__(AffineSpaces(source), ComplexManifolds())

    def scalar_embedding(self):
        return self._scalar_embedding

    @cached_method
    def _apply_object(self, affine_space):
        labels = tuple(affine_space.coordinate_algebra().algebra_generating_set())
        return ComplexManifolds().affine_space(
            int(affine_space.relative_dimension()),
            name=f"{affine_space}^an",
            coordinate_names=tuple(str(label) for label in labels),
        )

    @cached_method
    def _apply_morphism(self, morphism):
        assert morphism.domain() in self.domain() and morphism.codomain() in self.domain(), (
            f"analytification over {self.domain().base_ring()} cannot be applied to {morphism}: "
            f"its domain {morphism.domain()} and codomain {morphism.codomain()} must both be "
            f"affine spaces in {self.domain()}"
        )
        analytic_source = self.object_image(morphism.domain())
        analytic_target = self.object_image(morphism.codomain())
        source_chart = analytic_source.atlas()["standard"]
        pullback = morphism.coordinate_algebra_morphism()
        target_algebra = morphism.codomain().coordinate_algebra()
        expressions = tuple(
            _polynomial_chart_expression(
                morphism.domain().coordinate_algebra(),
                pullback(target_algebra.algebra_generator(label)),
                source_chart,
                self.scalar_embedding(),
            )
            for label in target_algebra.algebra_generating_set()
        )
        return analytic_source.holomorphic_polynomial_map(
            analytic_target,
            expressions,
        )

    def _repr_(self):
        return f"Affine analytification along {self.scalar_embedding()}"


@cached_function
def _affine_space_analytification_functor(scalar_embedding):
    return _AffineSpaceAnalytificationFunctor(scalar_embedding)


class _ProjectiveSpaceAnalytificationFunctor(Functor):
    r"""Analytification ``P^n_K -> CP^n`` along an embedding ``sigma: K -> CC``.

    ``(P^n_K)^an`` is the complex manifold of ``C``-points of the base change
    ``P^n_K x_{K,sigma} C``, which is ``CP^n`` with the standard atlas
    (Serre, GAGA, Sec. 2; SGA 1, Exp. XII, 1.1).  The chart ``D_+(x_i)`` of
    ``P^n_K`` goes to the chart ``U_i = {x_i != 0}`` with the same coordinates
    ``x_k/x_i``.  ``P^n_K`` is proper, so its analytification is compact.
    """

    def __init__(self, scalar_embedding) -> None:
        self._scalar_embedding = scalar_embedding
        source = _owned_ring(scalar_embedding.domain())
        target = _owned_ring(scalar_embedding.codomain())
        assert target is _owned_complex_field(), (
            f"analytification along {scalar_embedding} needs an embedding into the complex "
            f"numbers CC, but its codomain is {target}"
        )
        super().__init__(ProjectiveSpaces(source), ComplexManifolds().Compact())

    def scalar_embedding(self):
        return self._scalar_embedding

    @cached_method
    def _apply_object(self, projective_space):
        return ComplexManifolds().projective_space(
            int(projective_space.relative_dimension()), name=f"({projective_space})^an",
        )

    @cached_method
    def _apply_morphism(self, morphism):
        r"""A morphism ``P^n_K -> P^m_K`` goes to the holomorphic map given chartwise by its homogeneous polynomials.

        A morphism ``f = [F_0 : ... : F_m]`` is given by homogeneous
        polynomials of one degree with no common zero (Hartshorne II.7.1;
        Stacks, Tag 01ND).  On ``U_i = {x_i != 0}`` its analytification has,
        into ``V_j = {y_j != 0}``, the coordinate representation
        ``y_k/y_j = F_k/F_j`` with ``x_i = 1``, defined where ``F_j`` does not
        vanish.  These open sets cover ``U_i`` because the ``F_j`` have no
        common zero.  A chart pair on which ``F_j`` restricts to zero has
        empty domain and is not listed.
        """
        assert morphism.domain() in self.domain() and morphism.codomain() in self.domain(), (
            f"analytification over {self.domain().base_ring()} cannot be applied to {morphism}: "
            f"its domain {morphism.domain()} and codomain {morphism.codomain()} must both be "
            f"projective spaces in {self.domain()}"
        )
        source = morphism.domain()
        analytic_source = self.object_image(source)
        analytic_target = self.object_image(morphism.codomain())
        sections = tuple(_projective_coordinate_morphism(morphism).homogeneous_coordinates())
        representations = {}
        for i in range(int(source.relative_dimension()) + 1):
            chart_coordinates = tuple(
                _projective_coordinate_morphism(
                    source.standard_affine_chart_embedding(i)
                ).homogeneous_coordinates()
            )
            algebra = chart_coordinates[0].parent()
            local_sections = tuple(
                _evaluate_owned_homogeneous_polynomial_on_coordinates(
                    section, section.parent(), chart_coordinates
                )
                for section in sections
            )
            analytic_chart = analytic_source.atlas()[f"U{i}"]
            expressions = tuple(
                _polynomial_chart_expression(
                    algebra, local_section, analytic_chart, self.scalar_embedding()
                )
                for local_section in local_sections
            )
            for j, denominator in enumerate(expressions):
                if local_sections[j] == algebra.zero():
                    continue
                representations[f"U{i}", f"U{j}"] = (
                    tuple(
                        numerator / denominator
                        for k, numerator in enumerate(expressions)
                        if k != j
                    ),
                    (denominator,),
                )
        return analytic_source.Mor(analytic_target).rational(representations)

    def _repr_(self):
        return f"Projective analytification along {self.scalar_embedding()}"


@cached_function
def _projective_space_analytification_functor(scalar_embedding):
    return _ProjectiveSpaceAnalytificationFunctor(scalar_embedding)


class _AnalyticDiscFamilyEngine:
    r"""Private realization of one selected object of ``ComplexManifolds()/Delta``.

    The slice object itself retains the analytic family morphism.  This engine
    adds only the chosen algebraic family, analytification, and comparison
    morphism used to exhibit the analytic family as a restriction.
    """

    def __init__(
        self,
        *,
        scalar_embedding,
        algebraic_family,
        analytification,
        analytified_family,
        **rest,
    ) -> None:
        self._scalar_embedding = scalar_embedding
        self._algebraic_family = algebraic_family
        self._analytification = analytification
        self._analytified_family = analytified_family
        super().__init__(**rest)

    def scalar_embedding(self):
        return self._scalar_embedding

    def algebraic_family_morphism(self):
        return self._algebraic_family

    def analytification_functor(self):
        return self._analytification

    def analytified_family_morphism(self):
        return self._analytified_family

    def analytic_base(self):
        return self.arrow().codomain()

    def analytic_total_space(self):
        return self.arrow().domain()

    def analytic_family_morphism(self):
        return self.arrow()

    def analytic_family_object(self):
        return self

    @cached_method
    def fibre_inclusion(self, point):
        r"""The inclusion ``X_t -> X_Delta``, ``x |-> (x, t)``, of the fibre over a point ``t`` of ``Delta``.

        The family is the restriction of the projection ``C^2 -> C``,
        ``(x, t) |-> t``, to the preimage of ``Delta``, so its fibre over
        ``t`` is the line ``{(x, t)}``.  Domain: the fibre, a complex line
        with coordinate ``x``.  The composite with the family is constant at
        ``t``.  A complex number ``t`` with ``|t| < r`` is read as the point
        of ``Delta`` it names, through the disc's element constructor; the
        fibre is named by ``t`` as an element of the complex field ``CC``.
        """
        point = self.analytic_base()(point)
        (coordinate,) = tuple(point.coordinates())
        complex_field = _owned_complex_field()
        parameter = _owned_engine_element(
            complex_field, _engine_ring(complex_field)(_engine_manifold_expression(coordinate)),
        )
        fibre = ComplexManifolds().affine_space(
            1, name=f"X_{parameter}", coordinate_names=("x",),
        )
        x = fibre.atlas()["standard"].coordinate(0)
        return fibre.holomorphic_polynomial_map(self.analytic_total_space(), (x, coordinate))

    def fibre(self, point):
        r"""The fibre ``X_t`` of the family over a point ``t`` of ``Delta``; its inclusion is :meth:`fibre_inclusion`."""
        return self.fibre_inclusion(point).domain()

    def comparison_maps(self):
        r"""The open inclusions ``X_Delta -> X^an`` and ``Delta -> B^an``, the horizontal legs of the comparison square."""
        total_inclusion = self.analytic_total_space().open_inclusion()
        base_inclusion = self.analytic_base().open_inclusion()
        product = Sets().product((total_inclusion.parent(), base_inclusion.parent()))
        return product((total_inclusion, base_inclusion))

    def comparison_square_commutes(self) -> bool:
        total_inclusion, base_inclusion = self.comparison_maps()
        return (
            base_inclusion * self.analytic_family_morphism()
            == self.analytified_family_morphism() * total_inclusion
        )

    def coherent_gaga_applies(self) -> bool:
        r"""Whether the selected algebraic family satisfies the proper GAGA hypothesis."""
        algebraic_total = self.algebraic_family_morphism().domain()
        return algebraic_total in Schemes(
            algebraic_total.scheme_base_ring()
        ).Projective()

    def _repr_(self) -> str:
        return f"Analytic family {self.analytic_total_space()} -> {self.analytic_base()}"


def AnalyticDiscFamily(radius=1):
    r"""Return the selected holomorphic family as an object of ``ComplexManifolds()/Delta``.

    The algebraic source is ``A^2_QQ -> A^1_QQ``, ``(x,t) |-> t``.  Under the
    selected embedding ``QQ -> CC`` its analytification is ``C^2 -> C``.
    Restricting the base to ``Delta={|t|<r}`` and the total space to its inverse
    image gives the represented slice object.
    """
    qq = _owned_rationals()
    cc = _owned_complex_field()
    embedding = qq.Mor(cc)(lambda scalar: cc(scalar))
    algebraic_total = AffineSpaces(qq)(2, names=("x", "t"))
    algebraic_base = AffineSpaces(qq)(1, names=("t",))
    total_algebra = algebraic_total.coordinate_algebra()
    base_algebra = algebraic_base.coordinate_algebra()
    projection_pullback = base_algebra.Mor(total_algebra)(
        {"t": total_algebra.algebra_generator("t")}
    )
    algebraic_family = algebraic_total.Mor(algebraic_base)(projection_pullback)

    analytification = AffineSpaces(qq).analytification(embedding)
    analytic_total_ambient = analytification(algebraic_total)
    analytic_base_ambient = analytification(algebraic_base)
    analytified_family = analytification(algebraic_family)

    analytic_base = ComplexManifolds().disc(
        radius, "Delta", containing_manifold=analytic_base_ambient,
    )
    total_chart = analytic_total_ambient.atlas()["standard"]
    total_parameter = total_chart.coordinate(1)
    engine_total_parameter = _engine_manifold_expression(total_parameter)
    analytic_total = ComplexManifolds().open_submanifold(
        analytic_total_ambient,
        "X_Delta",
        abs(engine_total_parameter) < RR(radius).expression(),
    )
    restricted_parameter = analytic_total.atlas()["standard"].coordinate(1)
    analytic_family = analytic_total.holomorphic_polynomial_map(
        analytic_base,
        (restricted_parameter,),
    )

    assert analytic_base.open_inclusion() * analytic_family == analytified_family * analytic_total.open_inclusion(), (
        f"the analytic family {analytic_family} over the disc of radius {radius} is not the "
        f"restriction of the analytification {analytified_family}: the square with the open "
        "inclusions of the disc and of its preimage does not commute"
    )

    return ComplexManifolds().SliceOver(analytic_base).object(
        analytic_family,
        _engine=_AnalyticDiscFamilyEngine,
        construction_data={
            "scalar_embedding": embedding,
            "algebraic_family": algebraic_family,
            "analytification": analytification,
            "analytified_family": analytified_family,
        },
    )



__all__ = [
    "AnalyticDiscFamily",
]
