r"""Affine algebraic de Rham algebras of represented commutative algebras."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.algebras.algebras import Algebras
from sage_extensions.categories.algebras.differential_graded_algebras import (
    DifferentialGradedAlgebras,
    _fix_selected_differential,
)
from sage_extensions.categories.algebras.restricted_graded_algebras import (
    _restricted_graded_algebra,
)
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing


class _DeRhamAlgebra:
    r"""The differential on the constructed restricted exterior algebra."""

    def __init__(
        self,
        de_rham_source_algebra,
        kahler_differentials,
        coefficient_algebra=None,
        **rest,
    ) -> None:
        self._de_rham_source_algebra = de_rham_source_algebra
        self._kahler_differentials = kahler_differentials
        self._coefficient_algebra = (
            de_rham_source_algebra
            if coefficient_algebra is None
            else coefficient_algebra
        )
        super().__init__(**rest)
        exterior = self.extension_algebra()
        omega = self.kahler_differentials()
        universal = omega.universal_derivation()

        def differential(element):
            image = _de_rham_differential_on_extension(exterior, omega, universal, self.realize(element))
            return self.from_realization(image)

        _fix_selected_differential(
            self,
            differential,
            graded_leibniz=True,
            square_zero=True,
        )


class DeRhamAlgebras(OwnedCategoryOverBaseRing):
    r"""De Rham algebras ``DR_R(A) = Ω^•_{A/R}`` of commutative ``R``-algebras ``A``.

    ``Ω^•_{A/R}`` is the exterior algebra of the Kähler differentials with
    the differential extending ``d : A -> Ω^1_{A/R}``; it is a
    supercommutative differential graded ``R``-algebra.  On a smooth scheme
    ``X`` over ``R`` these are the sections over affine opens
    ``Spec A ⊆ X`` of the sheaf ``Ω^•_{X/R}``
    (``Schemes(R).Smooth()`` objects' ``de_rham_complex()``).
    """

    def an_object(self):
        r"""The de Rham algebra of a finite dual-number presentation.

        The witness must inhabit the same represented cohomology route used by
        downstream DGA constructions.  A polynomial algebra over ``R`` is
        infinite as an ``R``-module, while the current cohomology owner retains
        finite presentations of cycles and boundaries.  The selected quotient
        ``R[x]/(x^2)`` is still nontrivial Kähler calculus and is finite free
        over ``R``.
        """
        ring = self.base_ring()
        polynomial = Algebras(ring).Associative().Unital().Commutative().an_object()
        label = next(iter(polynomial.algebra_generating_set()))
        generator = polynomial.algebra_generator(label)
        return self((polynomial).quotient_by_relations((generator**2,)))

    def _call_(self, algebra):
        r"""Construct ``Omega^*_{A/R}`` from the represented ``R``-algebra ``A``.

        The source algebra is the defining datum.  This category constructor
        owns the Kähler-differential/exterior-algebra realization and identity
        cache; ``A.de_rham_algebra()`` is the algebra's spelling of it.  An
        algebra presented as a polynomial quotient ``R[x]/I`` states the cover
        as its base ring, so the coefficient ring is read from the presentation:
        the calculus is ``Omega^*_{A/R}``, not ``Omega^*_{A/R[x]}``.
        """
        from sage_extensions.categories.algebras.derivations import (
            _algebra_coefficient_ring,
        )

        base = self.base_ring()
        coefficient_ring = _algebra_coefficient_ring(algebra)
        if coefficient_ring is not base or algebra not in Algebras(
            algebra.base_ring()
        ).Associative().Unital().Commutative():
            raise TypeError(
                f"the de Rham algebra over {base} is built from a commutative algebra over "
                f"{base}, but {algebra} is an algebra over {coefficient_ring}"
            )
        return _de_rham_algebra_from_source(algebra)

    def _repr_object_names(self):
        return f"algebraic de Rham algebras over {self.base_ring()}"

    def super_categories(self):
        return [DifferentialGradedAlgebras(self.base_ring()).Supercommutative().Alternating()]

    class ParentMethods(_DeRhamAlgebra):
        def de_rham_source_algebra(self):
            return self._de_rham_source_algebra

        def coefficient_algebra(self):
            r"""Return the algebra this complex is built on, over the base ring.

            For an algebra that states its own coefficient ring this is the
            source algebra.  For a polynomial quotient ``R[x]/I`` the calculus
            is taken over ``R`` on the quotient's ``R``-algebra view — the same
            ring through the coefficient structure, retaining the ring and with
            it the presentation — and that view is what the graded pieces, the
            differential and the base change are built on.
            """
            return self._coefficient_algebra

        def kahler_differentials(self):
            return self._kahler_differentials

        def cohomology(self, degree):
            r"""``H^degree_dR(A/R)``, the cohomology of ``Omega^*_{A/R}``.

            Let ``R`` be a ``QQ``-algebra and ``A = Sym_R(F)`` with ``F``
            finite free, a polynomial algebra ``R[x_1, ..., x_n]``.  The
            augmentation ``A -> Sym_R(0) = R`` sending every generator of
            ``F`` to zero and the unit ``R -> A`` induce cochain maps of de Rham
            complexes that are inverse up to homotopy (Stacks Project,
            Lemma 50.10.5, Tag 0FUI, whose proof states that
            ``Omega^*_{B/R} -> Omega^*_{B[t]/R}`` is a quasi-isomorphism for
            every ``R``-algebra ``B``; induct on the generators).  So
            ``H^0 = R`` and ``H^k = 0`` for ``k != 0``, computed on the de
            Rham complex of ``Sym_R(0)``.  The homotopy integrates in ``t``,
            which needs ``QQ ⊆ R``; over ``F_p`` the statement fails
            (Stacks Project, Example 50.10.6, Tag 0FUJ).  Every other
            algebra has the cycle quotient of its own de Rham complex.
            """
            from sage_extensions.categories.algebras.free_algebras import (
                SymmetricAlgebras,
            )
            from sage_extensions.categories.modules.cochain_complexes import (
                _cohomology,
            )
            from sage_extensions.categories.modules.pure.modules import Modules
            from sage_extensions.categories.rings.ring_foundation import (
                _owned_rationals,
            )

            source = self.de_rham_source_algebra()
            base = self.base_ring()
            match source:
                case _ if (
                    source in SymmetricAlgebras(base)
                    and base in Algebras(_owned_rationals())
                    and source.generating_module() in Modules(base).FinitelyGenerated().Free()
                ):
                    return _polynomial_de_rham_cohomology(self, degree)
                case _:
                    return _cohomology(self, degree)


@cached_function(key=lambda de_rham_algebra, degree: (id(de_rham_algebra), int(degree)))
def _polynomial_de_rham_cohomology(de_rham_algebra, degree):
    r"""``H^degree_dR(Sym_R(F)/R)`` through the de Rham complex of ``Sym_R(0)``.

    Stacks Project, Lemma 50.10.5, Tag 0FUI: for a ``QQ``-algebra ``R`` the
    augmentation and the unit of ``Sym_R(F)`` over ``Sym_R(0)`` induce de Rham
    cochain maps inverse to each other up to homotopy.
    """
    from sage_extensions.categories.modules.cochain_complexes import (
        _cohomology_along,
    )

    polynomial = de_rham_algebra.de_rham_source_algebra()
    base = de_rham_algebra.base_ring()
    constants = base.free_module(0).symmetric_algebra()
    augmentation = polynomial.Mor(constants)(
        {label: constants.zero() for label in polynomial.algebra_generating_set()}
    )
    unit = constants.Mor(polynomial)({})
    de_rham = Algebras(base).Associative().Unital().Commutative().de_rham()
    return _cohomology_along(de_rham_algebra, degree, de_rham(augmentation), de_rham(unit))


def _de_rham_differential_on_extension(exterior_algebra, omega, universal_derivation, element):
    element = exterior_algebra(element)
    result = exterior_algebra.zero()
    for degree, component in element.homogeneous_components().items():
        source_piece = exterior_algebra.graded_piece(degree)
        target_degree = degree + 1
        if target_degree not in exterior_algebra.degree_index_set():
            continue
        target_piece = exterior_algebra.graded_piece(target_degree)
        target_component = target_piece.zero()
        coordinates = source_piece.framing_morphism().lift(component)
        for label in coordinates.support().domain():
            coefficient = coordinates(label)
            d_coefficient = universal_derivation(coefficient)
            if (d_coefficient == omega.zero()) is True:
                continue
            if degree == 0:
                contribution = d_coefficient
            else:
                basis_element = source_piece.module_generator(label)
                contribution = omega.exterior_power_product(
                    1,
                    d_coefficient,
                    degree,
                    basis_element,
                )
            target_component += contribution
        if (target_component == target_piece.zero()) is not True:
            result += exterior_algebra.from_component(target_degree, target_component)
    return result




def _coefficient_algebra(algebra, base):
    r"""``algebra`` read as an algebra over its coefficient ring ``base``.

    An algebra that already states ``base`` is that algebra.  A polynomial
    quotient ``R[x]/I`` states the cover instead; its ``R``-algebra view —
    ``A.as_algebra_over(R)``, the same ring through the coefficient structure,
    retaining the ring itself — is what the graded construction and the de Rham
    functor need.  Nothing is rebuilt: the view is the documented reading of the
    same ring, and the differential calculus reads the presentation through it.
    """
    if algebra.base_ring() is base:
        return algebra
    return algebra.as_algebra_over(base)


@cached_function(key=lambda algebra: id(algebra))
def _de_rham_algebra_from_source(algebra):
    from sage_extensions.categories.algebras.derivations import (
        _algebra_coefficient_ring,
    )

    base = _algebra_coefficient_ring(algebra)
    source = _coefficient_algebra(algebra, base)
    omega = source.kahler_differentials()
    exterior = omega.exterior_algebra()
    ring_map = source.algebra_structure_morphism()
    assert ring_map.domain() is base and ring_map.codomain() is source, (
        f"the structure map of {source} must be {base} -> {source}, but it is "
        f"{ring_map.domain()} -> {ring_map.codomain()}"
    )
    return _restricted_graded_algebra(
        exterior, ring_map, extra_categories=(DeRhamAlgebras(base),),
        construction_data={
            "de_rham_source_algebra": source,
            "coefficient_algebra": source,
            "kahler_differentials": omega,
        },
    )


__all__ = ["DeRhamAlgebras"]
