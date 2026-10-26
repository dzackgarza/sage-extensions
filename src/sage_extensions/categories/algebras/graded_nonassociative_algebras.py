"""Graded nonassociative algebras over a commutative ring."""

from sage.structure.parent import Parent

from sage_extensions.categories.algebras.algebras import Algebras
from sage_extensions.categories.modules.graded_modules import GradedModules
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing
from sage_extensions.lexicon.algebra import MonoidObject
from sage_extensions.logic import AtomicProposition


class GradedNonassociativeAlgebras(OwnedCategoryOverBaseRing):
    r"""Graded modules with a degree-additive bilinear multiplication.

    Let \(M\) be a commutative monoid with a parity \(\varepsilon: M \to
    \mathbb{Z}/2\).  An \(M\)-graded nonassociative algebra over \(R\) is an
    \(M\)-graded \(R\)-module \(A = \bigoplus_{m \in M} A_m\) with an
    \(R\)-bilinear multiplication of degree zero, sending \(A_m \times A_{m'}\)
    into \(A_{m+m'}\).  No associativity, unit or commutativity identity is
    imposed; graded Lie algebras are the objects whose multiplication is
    graded antisymmetric and satisfies the graded Jacobi identity (nLab,
    *graded Lie algebra*: a graded vector space with a bilinear map of degree
    zero; Felix, Halperin and Thomas, *Rational Homotopy Theory*, GTM 205,
    §21).

    The multiplication is an \(R\)-bilinear multiplication on the underlying
    module, so an object is an object of ``Algebras(R)``; the grading is the
    ``GradedModules(R, M, parity)`` datum.  Both forgetful functors end at the
    same underlying \(R\)-module.

    The rational homotopy Lie algebra of a pointed space \((X, x)\) is an
    object of ``GradedNonassociativeAlgebras(QQ)`` through
    ``GradedLieAlgebras(QQ)``: it is \(\pi_{*}(\Omega X) \otimes
    \mathbb{Q}\) under the Samelson product, with the shift convention
    \(\pi_n(\Omega X, c_x) \cong \pi_{n+1}(X, x)\), under which the Samelson
    product corresponds to the Whitehead product up to sign (op. cit.,
    §21(d)).  In degree \(0\) this reads \(\pi_0(\Omega X) = \pi_1(X, x)\),
    a group under loop concatenation; the graded Lie algebra structure is
    stated for simply connected \(X\), where that degree vanishes.
    """

    @staticmethod
    def __classcall__(cls, base_ring, grading_monoid=None, parity=None):
        r"""``GradedNonassociativeAlgebras(R, M, parity)``: the grading datum is that of ``GradedModules``."""
        graded_modules = GradedModules(base_ring, grading_monoid, parity)
        return OwnedCategoryOverBaseRing.__classcall__(
            cls, graded_modules.base_ring(), graded_modules
        )

    def __init__(self, base_ring, graded_modules: Parent) -> None:
        self._graded_modules = graded_modules
        graded_modules.parity_homomorphism()
        super().__init__(base_ring)

    def grading_monoid(self) -> MonoidObject:
        return self._graded_modules.grading_monoid()

    def parity_homomorphism(self):
        r"""Return the parity ``M -> ZZ/2`` the Koszul sign is read through."""
        return self._graded_modules.parity_homomorphism()

    def _repr_object_names(self) -> str:
        return f"graded nonassociative algebras over {self.base()}"

    def _make_named_class_key(self, name):
        return (super()._make_named_class_key(name), self._graded_modules)

    def super_categories(self):
        r"""The multiplication is an algebra multiplication; the grading is a graded-module datum."""
        return [
            Algebras(self.base_ring()),
            self._graded_modules,
        ]

    def _call_(self, graded_module, multiplication):
        r"""The pair ``(A, m)`` of a graded module and a degree-zero bilinear multiplication on it.

        Domain: an object ``A`` of ``GradedModules(R, M, parity)`` and an
        ``R``-linear morphism ``m: A tensor_R A -> A`` of degree zero.
        Codomain: this category.  That ``m`` sends ``A_p (x) A_q`` into
        ``A_{p+q}`` is the hypothesis this entry takes with ``m``, recorded as
        the proposition ``respects_grading(m)``.
        """
        from sage_extensions.categories.algebras.algebras import _algebra_on_module

        assert graded_module in self._graded_modules, (
            f"a graded nonassociative algebra in {self} is built on an object of {self._graded_modules}, "
            f"but {graded_module} is not one"
        )
        return _algebra_on_module(
            graded_module,
            multiplication,
            placement=(self,),
            law_decisions={"grading": AtomicProposition("respects_grading", multiplication)},
        )


__all__ = ["GradedNonassociativeAlgebras"]
