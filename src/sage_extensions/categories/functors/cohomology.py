r"""Cohomology functors for represented cochain complexes and de Rham DGAs."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.algebras.algebras import Algebras
from sage_extensions.categories.algebras.cohomology_algebras import (
    CohomologyAlgebras,
)
from sage_extensions.categories.algebras.differential_graded_algebras import (
    DifferentialGradedAlgebras,
)
from sage_extensions.categories.functors.core import (
    _CompositeFunctor,
    Functor,
)
from sage_extensions.categories.modules.cochain_complexes import (
    CochainComplexes,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import _owned_ring


class _CohomologyFunctor(Functor):
    r"""The degree-``p`` cohomology functor ``H^p : Coch_R -> Mod_R``."""

    def __init__(self, base_ring, degree) -> None:
        self._base_ring = _owned_ring(base_ring)
        self._degree = int(degree)
        super().__init__(
            CochainComplexes(self._base_ring),
            Modules(self._base_ring),
        )

    def base_ring(self):
        return self._base_ring

    def degree(self):
        return self._degree

    def _apply_object(self, complex_):
        return complex_.cohomology(self.degree())

    def _apply_morphism(self, morphism):
        source = self(morphism.domain())
        target = self(morphism.codomain())
        # A cochain map is its family of degreewise components; the arrow was
        # admitted by the Mor of cochain complexes, which owns that family.
        component = morphism.component(self.degree())
        return source.module_category().Mor(source, target)(
            {
                label: target.class_of_cycle(
                    component(
                        source.cycle_representative(source.module_generator(label))
                    )
                )
                for label in source.module_generating_set()
            }
        )

    def _repr_(self):
        return f"H^{self.degree()} on cochain complexes over {self.base_ring()}"


class _DeRhamCohomologyFunctor(_CompositeFunctor):
    r"""The literal composite ``H^p ∘ U_Coch ∘ DR_R``."""

    def __init__(self, base_ring, degree) -> None:

        self._base_ring = _owned_ring(base_ring)
        self._degree = int(degree)
        de_rham = Algebras(self._base_ring).Associative().Unital().Commutative().de_rham()
        forget_to_complex = (
            DifferentialGradedAlgebras(self._base_ring)
            .Supercommutative()
            .Alternating()
            .inclusion_into(CochainComplexes(self._base_ring))
        )
        de_rham_complex = _CompositeFunctor(de_rham, forget_to_complex)
        super().__init__(
            de_rham_complex,
            CochainComplexes(self._base_ring).cohomology(self._degree),
        )

    def base_ring(self):
        return self._base_ring

    def degree(self):
        return self._degree

    def _repr_(self):
        return f"H^{{{self.degree()}}}_dR(-/{self.base_ring()})"


class _CohomologyAlgebraFunctor(Functor):
    r"""The graded cohomology-algebra functor ``H^*`` on represented DGAs."""

    def __init__(self, base_ring) -> None:

        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            DifferentialGradedAlgebras(self._base_ring),
            CohomologyAlgebras(self._base_ring),
        )

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, dga):

        return dga.cohomology_algebra()

    def _apply_morphism(self, morphism):

        source = self(morphism.domain())
        target = self(morphism.codomain())
        return self.codomain().Mor(source, target)(morphism)

    def _repr_(self):
        return f"graded cohomology algebra over {self.base_ring()}"


class _DeRhamCohomologyAlgebraFunctor(_CompositeFunctor):
    r"""The composite ``H^* ∘ DR_R``."""

    def __init__(self, base_ring) -> None:

        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            Algebras(self._base_ring).Associative().Unital().Commutative().de_rham(),
            DifferentialGradedAlgebras(self._base_ring).cohomology_algebra(),
        )

    def base_ring(self):
        return self._base_ring

    def _repr_(self):
        return f"H^*_dR(-/{self.base_ring()})"


class _SingularCohomologyFunctor(Functor):
    r"""``H^*(-; R): Top^op -> GradedAlgebras(R, ZZ).Supercommutative()``.

    An object of ``Top^op`` is a space ``X``; its image is
    ``X.singular_cohomology(R)``.  An arrow of ``Top^op`` is a continuous map
    ``f: X -> Y``; its image is the pullback ``f^*: H^*(Y; R) -> H^*(X; R)``
    (Hatcher, *Algebraic Topology*, §3.2).
    """

    def __init__(self, base_ring) -> None:
        from sage_extensions.categories.algebras.graded_algebras import (
            GradedAlgebras,
        )
        from sage_extensions.categories.rings.ring_foundation import (
            _owned_integers,
        )
        from sage_extensions.categories.topological_spaces import (
            TopologicalSpaces,
        )

        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            TopologicalSpaces().opposite(),
            GradedAlgebras(self._base_ring, _owned_integers()).Supercommutative(),
        )

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, space):
        return space.underlying_object().singular_cohomology(self.base_ring())

    def _apply_morphism(self, morphism):
        assert False, (
            f"the pullback {morphism.underlying_arrow()}^* on H^*(-; {self.base_ring()}): not implemented"
        )

    def _repr_(self):
        return f"H^*(-; {self.base_ring()}) on topological spaces"


@cached_function
def _cohomology_functor(base_ring, degree) -> _CohomologyFunctor:
    return _CohomologyFunctor(base_ring, degree)


@cached_function
def _de_rham_cohomology_functor(base_ring, degree) -> _DeRhamCohomologyFunctor:
    return _DeRhamCohomologyFunctor(base_ring, degree)


@cached_function
def _cohomology_algebra_functor(base_ring) -> _CohomologyAlgebraFunctor:
    return _CohomologyAlgebraFunctor(base_ring)


@cached_function
def _de_rham_cohomology_algebra_functor(base_ring) -> _DeRhamCohomologyAlgebraFunctor:
    return _DeRhamCohomologyAlgebraFunctor(base_ring)


@cached_function
def _singular_cohomology_functor(base_ring) -> _SingularCohomologyFunctor:
    return _SingularCohomologyFunctor(base_ring)


__all__ = []
