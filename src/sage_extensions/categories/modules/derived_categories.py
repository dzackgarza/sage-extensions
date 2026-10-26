r"""Derived categories of modules and the localization functor from cochain complexes."""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.abstract_categories.objects import Objects
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.modules.cochain_complexes import (
    CochainComplexes,
)
from sage_extensions.categories.modules.linear_categories import (
    TriangulatedCategories,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    _owned_ring,
)
from sage_extensions.owned_category import _object_of


class DerivedCategory(OwnedCategoryOverBaseRing):
    r"""The derived category \(D(R)\) of the abelian category of \(R\)-modules.

    \(D(R) = \mathrm{Ch}(R)[W^{-1}]\) is the localization of the category
    \(\mathrm{Ch}(R)\) of \(\mathbb{Z}\)-graded cochain complexes of
    \(R\)-modules at the class \(W\) of quasi-isomorphisms, the cochain maps
    \(f\) for which every \(H^n(f)\) is an isomorphism (Stacks Project, Tag
    05RU, Definition 13.11.3).  It comes with the localization functor
    \(Q : \mathrm{Ch}(R) \to D(R)\), which is the identity on objects, sends
    every quasi-isomorphism to an isomorphism, and is initial among functors
    out of \(\mathrm{Ch}(R)\) with that property.  Mathlib states this as
    ``DerivedCategory C`` with
    ``DerivedCategory.Q : CochainComplex C ℤ ⥤ DerivedCategory C`` and the
    instance ``Q.IsLocalization`` for the quasi-isomorphisms
    (``Mathlib/Algebra/Homology/DerivedCategory/Basic.lean``).

    The cohomology functors \(H^n : \mathrm{Ch}(R) \to \mathrm{Mod}_R\)
    invert quasi-isomorphisms, so each factors uniquely as
    \(H^n = H^n_D \circ Q\).

    \(D(R)\) is an object of ``DerivedCategories(R)``, which is
    ``category()``.  ``super_categories`` states what every *object* of
    \(D(R)\) is.  An object of \(D(R)\) is a cochain complex, but a morphism
    of \(D(R)\) is a roof \(X \xleftarrow{s} X' \to Y\) with \(s\) a
    quasi-isomorphism, not a cochain map, so \(D(R)\) is not a subcategory of
    ``CochainComplexes(R)``, and no structure of an object of \(D(R)\) can
    be forgotten in place to reach another category: the declaration is the
    root.
    """

    def _repr_object_names(self):
        return f"objects of the derived category over {self.base_ring()}"

    def category(self):
        r"""``D(R)`` as an object of ``Cat``: a derived category over ``R``."""
        return DerivedCategories(self.base_ring())

    def super_categories(self):
        return [Objects()]

    def an_object(self):
        r"""``Q(C)`` of the sample cochain complex ``C``."""
        return CochainComplexes(self.base_ring()).localization_at_quasi_isomorphisms()(
            CochainComplexes(self.base_ring()).an_object()
        )

    def cohomology(self, degree):
        r"""``H^degree : D(R) -> Mod_R``, the factorization of cochain cohomology through ``Q``."""
        assert False, "cohomology on DerivedCategory: not implemented"

    class ParentMethods:
        def __init__(self, representing_complex, **rest) -> None:
            self._preamble_representing_complex = representing_complex
            super().__init__(**rest)

        def representing_complex(self):
            r"""The cochain complex \(C\) with \(Q(C)\) this object."""
            return self._preamble_representing_complex

        def cohomology(self, degree):
            r"""``H^degree(K)`` of an object \(K\) of \(D(R)\), an object of ``Modules(R)``.

            It is \(H^{\mathrm{degree}}\) of any cochain complex representing
            \(K\); quasi-isomorphic representatives give isomorphic modules.
            """
            return self.representing_complex().cohomology(degree)

        def graded_cohomology(self):
            r"""\(\bigoplus_n H^n(K)\), an object of ``GradedModules(R)`` with \(H^n(K)\) in degree \(n\)."""
            assert False, "graded_cohomology on DerivedCategory: not implemented"

        def _repr_(self):
            complex_ = self.representing_complex()
            return f"Image in the derived category over {complex_.base_ring()} of {complex_}"


class DerivedCategories(OwnedCategoryOverBaseRing):
    r"""The category of derived categories over \(R\) and exact functors.

    Its objects are the derived categories \(D(\mathcal{A})\) of
    \(R\)-linear abelian categories \(\mathcal{A}\), each the localization of
    \(\mathrm{Ch}(\mathcal{A})\) at the quasi-isomorphisms (Stacks Project,
    Tag 05RU, Definition 13.11.3); the derived category \(D(R)\) of
    \(R\)-modules is ``DerivedCategory(R)``.  A derived category is a
    category (owner ruling, 2026-10-16), and more structured, an \(R\)-linear
    triangulated category (Stacks Project, Tag 0145, Definition 13.3.2;
    Mathlib ``DerivedCategory.instPretriangulated`` and ``IsTriangulated``):
    the declaration is ``TriangulatedCategories(R)``, which declares the
    linear categories and so ``Cat``.
    """

    def _repr_object_names(self):
        return f"derived categories over {self.base_ring()}"

    def super_categories(self):
        return [TriangulatedCategories(self.base_ring())]

    def an_object(self):
        r"""The derived category \(D(R)\) of \(R\)-modules."""
        return DerivedCategory(self.base_ring())


class _DerivedLocalizationFunctor(Functor):
    r"""``Q : Ch(R) -> D(R)``, the localization of cochain complexes at quasi-isomorphisms."""

    def __init__(self, base_ring) -> None:
        self._base_ring = _owned_ring(base_ring)
        super().__init__(
            CochainComplexes(self._base_ring),
            DerivedCategory(self._base_ring),
        )

    def base_ring(self):
        return self._base_ring

    def _apply_object(self, complex_):
        r"""A cochain complex \(C\) as the object \(Q(C)\) of \(D(R)\); ``Q`` is the identity on objects."""
        return _object_of(self.codomain(), representing_complex=complex_)

    def _apply_morphism(self, morphism):
        r"""A cochain map \(f\) as the roof \(Q(f)\) with identity left leg."""
        assert False, "localization on CochainComplexes: not implemented"

    def _repr_(self):
        return f"Localization of cochain complexes over {self.base_ring()} at quasi-isomorphisms"


@cached_function
def _derived_localization_functor(base_ring) -> _DerivedLocalizationFunctor:
    return _DerivedLocalizationFunctor(base_ring)


__all__ = ["DerivedCategories", "DerivedCategory"]
