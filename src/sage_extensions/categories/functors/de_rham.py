r"""The algebraic de Rham functor, its degree-zero adjunction, and de Rham cohomology of smooth schemes."""
from sage.misc.cachefunc import cached_function, cached_method

from sage_extensions.categories.algebras.algebras import (
    Algebras,
)
from sage_extensions.categories.algebras.differential_graded_algebras import (
    DifferentialGradedAlgebras,
)
from sage_extensions.categories.algebras.graded_algebras import GradedAlgebras
from sage_extensions.categories.functors.core import Adjunction, Functor
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import LocalizationRings, _owned_ring


from sage_extensions.categories.modules.powers import _exterior_word


def _extend_degree_zero_map(source_dga, target_dga, algebra_morphism):
    r"""Extend ``A -> B^0`` uniquely to ``DR(A) -> B`` on the live algebras."""
    source_algebra = source_dga.de_rham_source_algebra()
    degree_zero = _degree_zero_dga_functor(source_dga.base_ring())
    target_algebra, target_inclusion, _ = degree_zero._degree_zero_data(target_dga)
    if algebra_morphism.domain() is not source_algebra:
        raise ValueError(
            f"the extension DR(A) -> B of {algebra_morphism} needs a map starting at A = {source_algebra}, "
            f"but it starts at {algebra_morphism.domain()}"
        )
    if algebra_morphism.codomain() is not target_algebra:
        raise ValueError(
            f"the extension DR(A) -> B of {algebra_morphism} needs a map ending at B^0 = "
            f"{target_algebra}, but it ends at {algebra_morphism.codomain()}"
        )
    if algebra_morphism not in degree_zero.codomain().Mor(source_algebra, target_algebra):
        raise TypeError(
            f"extending {algebra_morphism} to a DGA map requires an algebra morphism "
            f"over the retained coefficient ring {source_dga.base_ring()}"
        )

    source_exterior = source_dga.extension_algebra()
    # The Kähler differentials of S^{-1}A are S^{-1}A tensor_A Omega_{A/R}, so
    # their labels ("d", a) name algebra generators a of A (Stacks, Tag 00RT).
    generator_algebra = (
        source_algebra.localization_source()
        if source_algebra in LocalizationRings()
        else source_algebra
    )

    def image(element):
        represented = source_dga.realize(element)
        result = target_dga.zero()
        for degree, component in represented.homogeneous_components().items():
            source_piece = source_exterior.graded_piece(degree)
            coordinates = source_piece.framing_morphism().lift(component)
            for label in coordinates.support().domain():
                coefficient = coordinates(label)
                coefficient_image = target_inclusion(
                    algebra_morphism(source_algebra(coefficient))
                )
                term = coefficient_image
                for differential_label in _exterior_word(label, degree):
                    # The Kähler differential module frames ``da`` by the
                    # label ``("d", a)`` (``KahlerDifferentialModules
                    # .differential_generator``); read ``a`` from that datum.
                    match differential_label:
                        case ("d", generator_label):
                            source_generator = source_algebra(
                                generator_algebra.algebra_generator(generator_label)
                            )
                        case _:
                            raise ValueError(
                                f"the basis element {label} of the exterior algebra in {source_dga} is not a product of "
                                f"Kahler differentials da: its factor {differential_label} is not of the form da"
                            )
                    mapped_generator = target_inclusion(
                        algebra_morphism(source_generator)
                    )
                    term *= target_dga.d(mapped_generator)
                result += term
        return result

    # ``image`` is the unique extension on every element, so the arrow is
    # built from that element map: functoriality of the de Rham complex makes
    # it R-linear, multiplicative, degree-preserving and compatible with ``d``
    # (Stacks, Tag 0FKF, Section 10.132, "The de Rham complex").  The algebra generators of DR_R(A) need not be a
    # free family over an engine ring, so generator extension is not used.
    base = source_dga.base_ring()
    linear = source_dga.module_category().Mor(
        source_dga, target_dga
    )._from_constructed_element_map(image)
    graded = GradedAlgebras(base, source_dga.grading_monoid()).Mor(
        source_dga, target_dga
    )._from_degree_preserving_underlying_morphism(linear)
    mor = DifferentialGradedAlgebras(base).Mor(source_dga, target_dga)
    return mor._from_differential_preserving_underlying_morphism(graded, True)


class _DeRhamFunctor(Functor):
    r"""``DR_R : CAlg_R -> SCDGA_R^{>=0}`` on represented affine algebras."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            Algebras(self._base_ring).Associative().Unital().Commutative(),
            DifferentialGradedAlgebras(self._base_ring).Supercommutative().Alternating(),
        )

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, algebra):
        return algebra.de_rham_algebra()

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        return _extend_degree_zero_map(source, target, morphism)

    def _repr_(self):
        return f"Algebraic de Rham functor over {self.base_ring()}"


class _DegreeZeroDGAFunctor(Functor):
    r"""Degree zero ``(-)^0 : SCDGA_R^{>=0} -> CAlg_R``."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            DifferentialGradedAlgebras(self._base_ring).Supercommutative().Alternating(),
            Algebras(self._base_ring).Associative().Unital().Commutative(),
        )

    def base_ring(self):
        return self._base_ring

    @cached_method(key=lambda self, dga: id(dga))
    def _degree_zero_data(self, dga):
        r"""The exact algebra ``B^0``, its module inclusion, and its degree-zero lift.

        De Rham data retain their literal source algebra. A standard power
        algebra restricted along its coefficient algebra's own structure map
        also retains that algebra. Other represented graded pieces carry the
        product induced from B, not a guessed identification with its scalars.

        The last component is used only on elements known to have degree zero;
        a subobject supplies its existing lift, not a projection on arbitrary
        elements. Unrepresented pieces or lifts retain their named computation
        frontier. The identity-keyed cache retains all three data together.
        """
        from sage_extensions.categories.abstract_categories.arrow_categories import SubobjectCategory
        from sage_extensions.categories.abstract_categories.direct_sum_objects import DirectSumObjects
        from sage_extensions.categories.algebras.de_rham_algebras import DeRhamAlgebras
        from sage_extensions.categories.algebras.free_algebras import (
            AlternatingAlgebras, DividedPowerAlgebras, SymmetricAlgebras, TensorAlgebras,
        )
        from sage_extensions.categories.algebras.restricted_graded_algebras import _RestrictedGradedAlgebra
        from sage_extensions.categories.modules.graded_direct_sums import _DirectSumOfModules

        ring = self.base_ring()
        assert dga in self.domain() and dga.base_ring() is ring, (
            f"degree zero requires a strictly commutative DGA over the exact ring {ring}"
        )
        modules = Modules(ring)
        algebra = None
        if dga in DeRhamAlgebras(ring):
            algebra = dga.de_rham_source_algebra()
        elif isinstance(dga, _RestrictedGradedAlgebra):
            extension = dga.extension_algebra()
            coefficient = extension.base_ring()
            if (
                coefficient in self.codomain()
                and dga.ring_map() is coefficient.algebra_structure_morphism()
                and any(extension in category(coefficient) for category in (
                    AlternatingAlgebras, DividedPowerAlgebras,
                    SymmetricAlgebras, TensorAlgebras,
                ))
            ):
                # These selected standard gradings have B^0 = coefficient.
                algebra = coefficient
        if algebra is not None:
            inclusion = modules.Mor(algebra, dga)._from_constructed_element_map(
                lambda element: dga.from_degree_zero(algebra(element))
            )
            return algebra, inclusion, lambda element: algebra(dga.degree_zero_element(element))

        zero = dga.grading_monoid()(0)
        if (
            dga in DirectSumObjects(modules)
            and dga.summand_index_set() is dga.grading_index_set()
        ):
            piece = dga.graded_piece(zero)
            assert dga.summand(zero) is piece, (
                "the selected direct-sum summand must be the exact degree-zero piece"
            )
            inclusion, extract = dga.injection(zero), dga.projection(zero)
        elif isinstance(dga, _DirectSumOfModules):
            # This existing graded-sum engine has no DirectSumObjects placement.
            piece = dga.graded_piece(zero)
            inclusion, extract = dga.injection(zero), dga.projection(zero)
        else:
            assert (
                dga.has_selected_module_resolution()
                and dga.module_generating_set().cardinality().is_finite() is True
            ), (
                f"degree zero of {dga} needs represented homogeneous inclusion/lift data; "
                "the available generic subobject construction uses a known finite module framing"
            )
            piece = dga.graded_piece(zero)
            assert piece in SubobjectCategory(modules, dga), (
                f"degree zero of {dga} needs the selected inclusion of its homogeneous module piece"
            )
            inclusion = piece.inclusion()
            extract = inclusion.lift
        assert inclusion.domain() is piece and inclusion.codomain() is dga, (
            "the degree-zero inclusion must retain its actual homogeneous piece and DGA endpoints"
        )
        multiplication = modules.tensor_product((piece, piece)).from_bilinear_map(
            piece,
            lambda left, right: extract(inclusion(left) * inclusion(right)),
        )
        algebra = self.codomain()(piece, multiplication, extract(dga.one()))
        algebra_inclusion = modules.Mor(algebra, dga)._from_constructed_element_map(
            lambda element: inclusion(algebra._element_of_unformed_module(element))
        )
        return (
            algebra,
            algebra_inclusion,
            lambda element: algebra._element_from_unformed_module(extract(element)),
        )

    def _apply_object(self, dga):
        r"""Return the algebra on the actual represented degree-zero piece."""
        return self._degree_zero_data(dga)[0]

    def inclusion(self, dga):
        r"""The linear inclusion ``B^0 -> B`` of the degree-zero algebra as the degree-zero piece."""
        return self._degree_zero_data(dga)[1]

    def _apply_morphism(self, morphism):
        source_dga = morphism.domain()
        target_dga = morphism.codomain()
        source, inclusion, _ = self._degree_zero_data(source_dga)
        target, _, extract = self._degree_zero_data(target_dga)

        def image(element):
            return extract(morphism(inclusion(element)))

        mor = self.codomain().Mor(source, target)
        if source.is_framed_algebra():
            assert source.algebra_generating_set().cardinality().is_finite() is True, (
                "the selected degree-zero generator-extension computation needs a known finite algebra framing"
            )
            return mor(lambda label: image(source.algebra_generator(label)))
        linear = Modules(self.base_ring()).Mor(source, target)._from_constructed_element_map(
            image, premises=(morphism,)
        )
        return mor(linear)

    def _repr_(self):
        return f"Degree-zero DGA functor over {self.base_ring()}"


class _DeRhamAdjunction(Adjunction):
    r"""The adjunction ``DR_R ⊣ (-)^0``.

    On the represented algebras the Mor object bijection is the universal
    extension of an algebra map ``A -> B^0`` by ``da |-> d_B(a)``.
    """

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(_de_rham_functor(self._base_ring), _degree_zero_dga_functor(self._base_ring))

    def base_ring(self):
        return self._base_ring

    def _unit_component(self, algebra):
        degree_zero = self.right_adjoint()(self.left_adjoint()(algebra))
        assert degree_zero is algebra, (
            "degree zero of the selected de Rham algebra must retain its literal source"
        )
        return self.left_adjoint().domain().Mor(algebra, algebra).identity()

    def _counit_component(self, dga):
        r"""Extend id_(B^0); DR retains its existing presentation frontier.

        The generic degree-zero algebra need not have a selected algebra
        presentation, even when it is isomorphic to R. No presentation solver
        is inferred from that isomorphism.
        """
        degree_zero = self.right_adjoint()(dga)
        source = self.left_adjoint()(degree_zero)
        identity = Algebras(degree_zero.base_ring()).Associative().Unital().Mor(degree_zero, degree_zero).identity()
        return _extend_degree_zero_map(source, dga, identity)


    def _repr_(self):
        return f"Algebraic de Rham/degree-zero adjunction over {self.base_ring()}"


class _SmoothSchemeDeRhamCohomologyFunctor(Functor):
    r"""``H^k_dR(-/R) : Sm_R^op -> Mod_R``, degree ``k`` of de Rham hypercohomology.

    On a smooth scheme ``X`` over ``R`` the value is
    ``H^k(RΓ(X, Ω^•_{X/R}))``, the ``k``-th hypercohomology of the de Rham
    complex.  A morphism ``f : X -> Y`` of smooth ``R``-schemes acts by the
    pullback ``f^* : H^k_dR(Y/R) -> H^k_dR(X/R)`` induced by
    ``f^{-1} Ω^•_{Y/R} -> Ω^•_{X/R}``.
    """

    def __init__(self, base_ring, degree) -> None:
        from sage_extensions.categories.schemes.schemes import Schemes

        self._base_ring = _owned_ring(base_ring)
        self._degree = int(degree)
        super().__init__(
            Schemes(self._base_ring).Smooth().opposite(),
            Modules(self._base_ring),
        )

    def base_ring(self):
        return self._base_ring

    def degree(self):
        return self._degree

    def _apply_object(self, scheme):
        return scheme.de_rham_cohomology(self.degree())

    def _apply_morphism(self, morphism):
        r"""The pullback ``f^* : H^k_dR(Y/R) -> H^k_dR(X/R)`` of ``f : X -> Y``."""
        assert False, "de_rham_cohomology on Schemes.Smooth morphisms: not implemented"

    def _repr_(self):
        return f"H^{{{self.degree()}}}_dR(-/{self.base_ring()}) on smooth schemes"


class _SmoothSchemeDeRhamCohomologyAlgebraFunctor(Functor):
    r"""``H^*_dR(-/R) : Sm_R^op -> SCGA_R``, de Rham hypercohomology with its cup product.

    On a smooth scheme ``X`` over ``R`` the value is
    ``⊕_k H^k(RΓ(X, Ω^•_{X/R}))``, a supercommutative ``ZZ``-graded
    ``R``-algebra whose product is induced by the wedge product of
    ``Ω^•_{X/R}``.  Morphisms act by pullback.  On ``X = Spec A`` it is the
    cohomology algebra of ``DR_R(A)``, because quasi-coherent sheaves on an
    affine scheme have no higher cohomology.
    """

    def __init__(self, base_ring) -> None:
        from sage_extensions.categories.algebras.graded_algebras import (
            GradedAlgebras,
        )
        from sage_extensions.categories.schemes.schemes import Schemes

        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            Schemes(self._base_ring).Smooth().opposite(),
            GradedAlgebras(self._base_ring).Supercommutative(),
        )

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, scheme):
        return scheme.de_rham_cohomology_algebra()

    def _apply_morphism(self, morphism):
        r"""The graded algebra pullback ``f^* : H^*_dR(Y/R) -> H^*_dR(X/R)`` of ``f : X -> Y``."""
        assert False, "de_rham_cohomology_algebra on Schemes.Smooth morphisms: not implemented"

    def _repr_(self):
        return f"H^*_dR(-/{self.base_ring()}) on smooth schemes"


@cached_function
def _de_rham_functor(base_ring) -> _DeRhamFunctor:
    return _DeRhamFunctor(base_ring)


@cached_function
def _degree_zero_dga_functor(base_ring) -> _DegreeZeroDGAFunctor:
    return _DegreeZeroDGAFunctor(base_ring)


@cached_function
def _de_rham_adjunction(base_ring) -> _DeRhamAdjunction:
    return _DeRhamAdjunction(base_ring)


@cached_function
def _smooth_scheme_de_rham_cohomology_functor(
    base_ring, degree
) -> _SmoothSchemeDeRhamCohomologyFunctor:
    return _SmoothSchemeDeRhamCohomologyFunctor(base_ring, degree)


@cached_function
def _smooth_scheme_de_rham_cohomology_algebra_functor(
    base_ring,
) -> _SmoothSchemeDeRhamCohomologyAlgebraFunctor:
    return _SmoothSchemeDeRhamCohomologyAlgebraFunctor(base_ring)


__all__ = []
