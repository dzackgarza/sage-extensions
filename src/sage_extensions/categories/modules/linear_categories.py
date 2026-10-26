r"""Categories of \(R\)-linear categories: the additive ones and the triangulated ones."""

from sage.categories.category_with_axiom import all_axioms

from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
)
from sage_extensions.owned_category_bases import CategoryWithAxiom

# Additivity of a linear category (finite biproducts) is a property relative
# to its linear structure (lean-categories FOUNDATIONS Definition 14.1).
if "Additive" not in all_axioms:
    all_axioms.add("Additive")


class LinearCategories(OwnedCategoryOverBaseRing):
    r"""The category of \(R\)-linear categories and \(R\)-linear functors.

    An \(R\)-linear category is a category \(\mathcal{C}\) with an
    \(R\)-module structure on every \(\operatorname{Mor}_{\mathcal{C}}(X, Y)\)
    for which composition is \(R\)-bilinear.  Mathlib states it as
    ``CategoryTheory.Linear R C`` over ``Preadditive C``
    (``Mathlib/CategoryTheory/Linear/Basic.lean``).  Over \(\mathbb{Z}\) the
    linear structure is the enrichment in abelian groups, so
    ``LinearCategories(ZZ)`` is the category of preadditive categories of
    ``lean-categories`` FOUNDATIONS Definition 14.1.

    Forgetting the linear structure in place leaves a category, which is the
    declaration.  The preadditive category underlying an \(R\)-linear category
    is its restriction of scalars along \(\mathbb{Z} \to R\), a change of base
    and so a functor, never a supercategory (``CAT-16``).
    """

    def _repr_object_names(self):
        return f"linear categories over {self.base_ring()}"

    def super_categories(self):
        from sage_extensions.categories.abstract_categories.cat import Cat

        return [Cat()]

    class SubcategoryMethods:
        def Additive(self):
            r"""The additive ones: those with finite biproducts (FOUNDATIONS Definition 14.1)."""
            return self._with_axiom("Additive")

    class Additive(CategoryWithAxiom):
        r"""The additive \(R\)-linear categories: those with finite biproducts.

        ``lean-categories`` FOUNDATIONS Definition 14.1 states additivity as a
        property relative to the chosen preadditive structure; Mathlib states
        it as ``HasFiniteBiproducts C`` over ``Preadditive C``.
        """


class TriangulatedCategories(OwnedCategoryOverBaseRing):
    r"""The category of \(R\)-linear triangulated categories and exact functors.

    A triangulated category is a triple \((\mathcal{D}, [1], T)\) with
    \(\mathcal{D}\) an additive category, \([1] : \mathcal{D} \to \mathcal{D}\)
    an additive auto-equivalence, and \(T\) a class of triangles
    \(X \to Y \to Z \to X[1]\), the distinguished triangles, subject to
    TR1--TR4 (Stacks Project, Tag 0145, Definition 13.3.2).  It is
    \(R\)-linear when \(\mathcal{D}\) is \(R\)-linear and \([1]\) is
    \(R\)-linear.  Mathlib states the structure as ``Pretriangulated C`` with
    ``IsTriangulated C`` (``Mathlib/CategoryTheory/Triangulated/``), together
    with ``Linear R C``.  The derived category \(D(R)\) of
    \(R\)-modules is one (Stacks Project, Tag 05RU, Definition 13.11.3).

    The shift and the distinguished triangles are chosen structure on an
    additive \(R\)-linear category; forgetting them in place leaves the
    additive \(R\)-linear category, which is the declaration.  The
    1-morphisms are the exact functors: \(R\)-linear functors commuting with
    the shift and carrying distinguished triangles to distinguished
    triangles (Mathlib ``Functor.IsTriangulated``).  ``lean-categories``
    FOUNDATIONS Remark 65.2 states that for categories of triangulated categories this
    class of 1-morphisms is part of the definition.
    """

    def _repr_object_names(self):
        return f"triangulated linear categories over {self.base_ring()}"

    def super_categories(self):
        return [LinearCategories(self.base_ring()).Additive()]

    def an_object(self):
        r"""The derived category \(D(R)\) of \(R\)-modules."""
        from sage_extensions.categories.modules.derived_categories import (
            DerivedCategory,
        )

        return DerivedCategory(self.base_ring())


__all__ = ["LinearCategories", "TriangulatedCategories"]
