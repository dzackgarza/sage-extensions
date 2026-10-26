r"""Dependency-light access to an algebra category's canonical Mor family.

The retained name returns the family already attached to the supplied
category. Associativity constrains the objects, while multiplication
preservation is the ordinary algebra-map law. A category with a chosen unit
also requires its maps to preserve that unit; its actual family selects
the corresponding representation and any selected presentation algorithm.
"""

from sage.categories.category import Category


def AssociativeAlgebraMorCategoryConstruction(base_category: Category) -> Category:
    r"""Return the exact Mor family of the supplied owned algebra category.

    For associative ``R``-algebras its fixed objects classify ``R``-linear
    maps ``f`` satisfying ``f m_A = m_B (f tensor f)``. Their unit law and
    selected realization are those of ``base_category``. The exported
    spelling introduces no second family or morphism implementation.
    """
    return base_category.MorCategory()


__all__ = ["AssociativeAlgebraMorCategoryConstruction"]
