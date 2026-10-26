r"""Graded cohomology algebras of represented differential graded algebras.

The cohomology computation is deliberately the common owned cochain-complex
construction: each homogeneous piece is literally ``dga.cohomology(p)``, so
its cycle inclusion, boundary-in-cycles map, quotient projection and selected
representatives remain available to multiplication and induced maps.  Sage's
``CommutativeDifferentialGradedAlgebra`` backend is not a replacement for this
boundary: in its supported field regime ``cocycles`` and ``coboundaries`` are
coordinate vector subspaces and ``cohomology`` is an abstract free module,
which does not retain those comparison maps.  The maintained module backends
used by the cochain-complex owner therefore remain the private computation authority for
both commutative and noncommutative source DGAs.
"""

from sage.misc.cachefunc import cached_function
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.algebras.differential_graded_algebras import (
    DGAMorphism,
    DifferentialGradedAlgebras,
)
from sage_extensions.categories.algebras.algebras import (
    Algebras,
    MultiplicativeAlgebraMorphism,
    _algebra_on_module,
    _root_algebra_law_decisions,
)
from sage_extensions.categories.algebras.graded_algebras import (
    GradedAlgebras,
    _graded_multiplication_from_components,
)
from sage_extensions.categories.modules.graded_modules import GradedModules
from sage_extensions.categories.sets.indexed_families import indexed_family
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


class CohomologyAlgebraMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return CohomologyAlgebraMor


class _CohomologyAlgebra:
    r"""The source DGA and scalar ingress of its cohomology algebra.

    The graded module and multiplication are supplied to their owners before
    this level is constructed.  Cycle quotients remain the actual summands.
    """

    def __init__(self, source_dga, **rest) -> None:
        self._source_dga = source_dga
        super().__init__(**rest)

    def source_dga(self):
        return self._source_dga

    def _element_constructor_(self, value):
        match value:
            case _ if element_parent(value) is self:
                return value
            case dict():
                return super()._element_constructor_(value)
            case _ if value in self.base_ring():
                return self.scalar_multiple(self.base_ring()(value), self.one())
            case _:
                return super()._element_constructor_(value)

    def _repr_(self):
        return f"H^*({self.source_dga()})"


class CohomologyAlgebras(OwnedCategoryOverBaseRing):
    r"""Graded algebras ``H^*(B)`` represented from a DGA ``B``."""

    def an_object(self):
        r"""The cohomology of the de Rham algebra of the polynomial algebra."""
        from sage_extensions.categories.algebras.de_rham_algebras import DeRhamAlgebras

        return self(DeRhamAlgebras(self.base_ring()).an_object())

    def _call_(self, dga):
        r"""Construct ``H^*(dga)`` with its descended graded multiplication.

        The source DGA is the defining datum.  This category constructor owns
        both identity caching and the private graded-direct-sum realization;
        DGA objects and the cohomology-algebra functor both land here through
        this one category-owned construction path.
        """
        dgas = DifferentialGradedAlgebras(self.base_ring())
        if dga not in dgas:
            raise TypeError(
                f"the cohomology algebra over {self.base_ring()} is built from a differential graded algebra "
                f"over {self.base_ring()}, but {dga} is not one"
            )
        return _cohomology_algebra_from_dga(dga)

    def _repr_object_names(self):
        return f"cohomology algebras over {self.base_ring()}"

    def super_categories(self):
        return [GradedAlgebras(self.base_ring())]

    _MorCategory = CohomologyAlgebraMorCategoryConstruction

    ParentMethods = _CohomologyAlgebra


def CohomologyAlgebraElement(parent, components):
    r"""Read homogeneous cohomology classes in their constructed algebra."""
    return parent.from_components(components)



class CohomologyAlgebraMorphism:
    r"""The graded algebra morphism induced on cohomology by a DGA morphism."""

    def __init__(self, parent, dga_morphism) -> None:
        domain = parent.domain()
        codomain = parent.codomain()
        if not isinstance(dga_morphism, DGAMorphism):
            raise TypeError(
                f"a morphism {domain} -> {codomain} of cohomology algebras is induced by a "
                f"morphism of differential graded algebras, but {dga_morphism!r} is not one"
            )
        if dga_morphism.domain() is not domain.source_dga():
            raise ValueError(
                f"a morphism of cohomology algebras {domain} -> {codomain} is induced by a map "
                f"starting at {domain.source_dga()}, but {dga_morphism} starts at {dga_morphism.domain()}"
            )
        if dga_morphism.codomain() is not codomain.source_dga():
            raise ValueError(
                f"a morphism of cohomology algebras {domain} -> {codomain} is induced by a map "
                f"ending at {codomain.source_dga()}, but {dga_morphism} ends at {dga_morphism.codomain()}"
            )
        self._dga_morphism = dga_morphism
        linear = domain.module_category().Mor(
            domain, codomain
        )._from_constructed_element_map(
            lambda element: self._call_(element)
        )
        super().__init__(
            parent,
            linear,
            degree_preservation=True,
        )

    def _multiplicativity_derivation(self):
        return True

    def _unit_preservation_derivation(self):
        return True

    def underlying_dga_morphism(self):
        return self._dga_morphism

    def _call_(self, element):
        source = self.domain()
        target = self.codomain()
        element = source(element)
        result = target.zero()
        for degree, cohomology_class in element.homogeneous_components().items():
            source_piece = source.graded_piece(degree)
            target_piece = target.graded_piece(degree)
            cycle = source_piece.cycle_representative(cohomology_class)
            image_cycle = self.underlying_dga_morphism().component(degree)(cycle)
            image_class = target_piece.class_of_cycle(image_cycle)
            if (image_class == target_piece.zero()) is not True:
                result += target.from_component(degree, image_class)
        return result

    def __call__(self, element):
        return self._call_(element)

    def __mul__(self, other):
        if not isinstance(other, CohomologyAlgebraMorphism):
            return MultiplicativeAlgebraMorphism.__mul__(self, other)
        if other.codomain() is not self.domain():
            return NotImplemented
        source = other.domain()
        return CohomologyAlgebras(source.base_ring()).Mor(source, self.codomain())(
            self.underlying_dga_morphism() * other.underlying_dga_morphism()
        )


class CohomologyAlgebraMor(CategoricalMor):
    ElementMethods = CohomologyAlgebraMorphism

    def __init__(self, mor_family, domain, codomain) -> None:
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    def _element_constructor_(self, dga_morphism):
        return self.element_class(self, dga_morphism)

    @object_level
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"the identity morphism exists only on Mor(A, A), but this is Mor({self.domain()}, {self.codomain()})"
            )

        source_dga = self.domain().source_dga()
        return self(
            DifferentialGradedAlgebras(source_dga.base_ring())
            .Mor(source_dga, source_dga)
            .identity()
        )


@cached_function(key=lambda dga: id(dga))
def _cohomology_algebra_from_dga(dga):
    r"""Construct the graded cycle quotient, then its descended product.

    For cycles x,y, Leibniz gives d(xy)=0.  Replacing x by x+d(a)
    changes xy by d(ay); replacing y by y+d(b) changes xy by
    (-1)^deg(x) d(xb).  Thus the product is independent of representatives,
    bilinear, associative and unital.  See Stacks, Tag 061U, Definition 22.3.1.
    """
    ring = dga.base_ring()
    graded = GradedModules(ring)
    pieces = indexed_family(graded.grading_monoid(), dga.cohomology)
    module = graded(pieces)

    def component_product(s, x, t, y):
        left_cycle = module.graded_piece(s).cycle_representative(x)
        right_cycle = module.graded_piece(t).cycle_representative(y)
        product = dga.from_component(s, left_cycle) * dga.from_component(t, right_cycle)
        degree = module.combine_degrees(s, t)
        return module.graded_piece(degree).class_of_cycle(product.homogeneous_component(degree))

    multiplication = _graded_multiplication_from_components(module, component_product)
    law_decisions = _root_algebra_law_decisions(dga)
    law_decisions["grading"] = dga.grading_compatibility_decision()
    placements = (CohomologyAlgebras(ring), *(
        target
        for source, target in (
            (DifferentialGradedAlgebras(ring).Supercommutative(), GradedAlgebras(ring).Supercommutative()),
            (DifferentialGradedAlgebras(ring).Supercommutative().Alternating(), GradedAlgebras(ring).Supercommutative().Alternating()),
        )
        if dga in source
    ))
    match dga.is_commutative():
        case True:
            placements = (*placements, Algebras(ring).Commutative())
            law_decisions["commutativity"] = True
        case _:
            pass
    zero_degree = graded.grading_monoid().zero()
    unit = module.from_component(zero_degree, module.graded_piece(zero_degree).class_of_cycle(
        dga.one().homogeneous_component(zero_degree),
    ))
    return _algebra_on_module(
        module, multiplication, placement=placements, unit=unit,
        construction_data={"source_dga": dga},
        law_decisions=law_decisions,
    )


__all__ = [
    "CohomologyAlgebraElement",
    "CohomologyAlgebraMor",
    "CohomologyAlgebraMorphism",
    "CohomologyAlgebras",
]
