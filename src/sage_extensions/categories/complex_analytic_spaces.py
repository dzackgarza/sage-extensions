r"""Complex analytic spaces (Grauert--Remmert, *Coherent Analytic Sheaves*, Ch. 1).

A complex analytic space is a locally ``C``-ringed Hausdorff space
``(X, O_X)`` locally isomorphic to a local model: for a domain ``U`` in
``C^n`` and holomorphic ``f_1, ..., f_k`` on ``U``, the zero set
``N = V(f_1, ..., f_k)`` with the sheaf ``(O_U/(f_1, ..., f_k))|_N``.  A
complex manifold is a complex analytic space whose local models are domains
in ``C^n``; such a space is reduced and normal.
"""

from sage.categories.category_with_axiom import all_axioms

from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.schemes.ringed_spaces import LocallyRingedSpaces
from sage_extensions.owned_category_bases import CategoryWithAxiom

if "Normal" not in all_axioms:
    all_axioms.add("Normal")


class ComplexAnalyticSpaces(OwnedCategory):
    r"""Complex analytic spaces ``(X, O_X)`` with holomorphic maps (Grauert--Remmert, Ch. 1).

    The structure sheaf ``O_X`` is a sheaf of local ``C``-algebras: its stalk
    at ``x`` is a quotient of the ring of convergent power series
    ``C{z_1, ..., z_n}``, a local ring.  So a complex analytic space is a
    locally ringed space whose stalks are ``C``-algebras, and forgetting that
    it is locally a model space is the functor to ``LocallyRingedSpaces()``.
    A morphism is a morphism of locally ``C``-ringed spaces.
    """

    def super_categories(self):
        return [LocallyRingedSpaces()]

    @classmethod
    def _repr_object_names(cls):
        return "complex analytic spaces"

    class SubcategoryMethods:
        def Normal(self):
            r"""The axiom: every local ring ``O_{X,x}`` is an integrally closed domain.

            A normal complex space is reduced, and its singular locus has
            codimension at least two (Grauert--Remmert, Ch. 8).  The quotient
            of a complex manifold by a properly discontinuous group of
            biholomorphisms is normal (H. Cartan, "Quotient d'un espace
            analytique par un groupe d'automorphismes", 1957).
            """
            return self._with_axiom("Normal")

    class Normal(CategoryWithAxiom):
        r"""Complex analytic spaces whose local rings are integrally closed domains."""

        class ParentMethods:
            def is_normal(self):
                return True


__all__ = ["ComplexAnalyticSpaces"]
