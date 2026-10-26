"""Graded Lie algebras over a commutative ring."""

from sage.structure.parent import Parent

from sage_extensions.categories.algebras.graded_nonassociative_algebras import GradedNonassociativeAlgebras
from sage_extensions.categories.modules.graded_modules import GradedModules
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing
from sage_extensions.lexicon.algebra import MonoidObject
from sage_extensions.logic import AtomicProposition


class GradedLieAlgebras(OwnedCategoryOverBaseRing):
    r"""Lie algebras in graded modules, with the Koszul sign rule.

    Let \(M\) be a commutative monoid with a parity \(\varepsilon: M \to
    \mathbb{Z}/2\).  An \(M\)-graded Lie algebra over \(R\) is an \(M\)-graded
    \(R\)-module \(L = \bigoplus_{m \in M} L_m\) with an \(R\)-bilinear bracket
    sending \(L_m \times L_{m'}\) into \(L_{m+m'}\) such that, for homogeneous
    \(x, y, z\),

    - \([x, y] = -(-1)^{\varepsilon(x)\varepsilon(y)} [y, x]\), and
    - \((-1)^{\varepsilon(x)\varepsilon(z)}[x,[y,z]] + (-1)^{\varepsilon(y)\varepsilon(x)}[y,[z,x]]
      + (-1)^{\varepsilon(z)\varepsilon(y)}[z,[x,y]] = 0\).

    This is a Lie algebra object in the symmetric monoidal category of
    graded modules with the Koszul braiding (Felix, Halperin and Thomas,
    *Rational Homotopy Theory*, GTM 205, §21).  The sign rule is not the
    ungraded one, so these objects are not objects of
    ``Algebras(R).Lie()``.  The default grading is \(\mathbb{Z}\) with
    reduction modulo 2.

    The bracket is an \(R\)-bilinear multiplication on the underlying module,
    so an object is an object of ``Algebras(R)``; the grading is the
    ``GradedModules(R, M, parity)`` datum.  Both forgetful functors end at the
    same underlying \(R\)-module, so the square through ``Modules(R)``
    commutes.  The source of the main example is the rational homotopy Lie
    algebra \(\pi_{*}(\Omega X) \otimes \mathbb{Q}\) of a simply connected
    space under the Samelson bracket (op. cit., §21(d)).
    """

    @staticmethod
    def __classcall__(cls, base_ring, grading_monoid=None, parity=None):
        r"""``GradedLieAlgebras(R, M, parity)``: the grading datum is that of ``GradedModules``."""
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
        return f"graded Lie algebras over {self.base()}"

    def _make_named_class_key(self, name):
        return (super()._make_named_class_key(name), self._graded_modules)

    def super_categories(self):
        r"""Forgetting the antisymmetry and Jacobi identities leaves a graded nonassociative algebra."""
        return [
            GradedNonassociativeAlgebras(
                self.base_ring(), self.grading_monoid(), self.parity_homomorphism()
            ),
        ]

    def _call_(self, graded_module, bracket):
        r"""The pair ``(L, [-,-])`` of a graded module and a degree-zero graded bracket on it.

        Domain: an object ``L`` of ``GradedModules(R, M, parity)`` and an
        ``R``-linear morphism ``[-,-]: L tensor_R L -> L`` of degree zero.
        Construction trusts the caller with the three identities, recorded as
        the propositions ``respects_grading``, ``graded_antisymmetry`` and
        ``graded_jacobi`` of the bracket; it checks none of them.
        """
        from sage_extensions.categories.algebras.algebras import _algebra_on_module

        assert graded_module in self._graded_modules, (
            f"a graded Lie algebra in {self} is built on an object of {self._graded_modules}, "
            f"but {graded_module} is not one"
        )
        return _algebra_on_module(
            graded_module,
            bracket,
            placement=(self,),
            law_decisions={
                "grading": AtomicProposition("respects_grading", bracket),
                "graded_antisymmetry": AtomicProposition("graded_antisymmetry", bracket),
                "graded_jacobi": AtomicProposition("graded_jacobi", bracket),
            },
        )

    def universal_enveloping_algebra_functor(self):
        r"""``U : GrLie_R -> GrAlg_R``, left adjoint to the graded commutator Lie algebra.

        ``U(L)`` is the tensor algebra on ``L`` modulo
        ``x tensor y - (-1)^{eps(x) eps(y)} y tensor x - [x, y]``; it is an
        object of ``GradedAlgebras(R, M, parity)`` (Felix-Halperin-Thomas,
        op. cit., §21(a)).
        """
        assert False, "universal_enveloping_algebra_functor on GradedLieAlgebras: not implemented"


__all__ = ["GradedLieAlgebras"]
