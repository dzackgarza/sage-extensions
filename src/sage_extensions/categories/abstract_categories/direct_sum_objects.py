r"""Objects of a category with a chosen finite direct-sum decomposition.

For a category ``C`` with finite biproducts, an object of ``DirectSumObjects(C)``
is an object ``X`` of ``C`` together with a chosen indexed family of summands
whose biproduct in ``C`` is ``X``.  The injections and projections of that
decomposition are morphisms of ``C``, so the notion is relative to ``C``.
An orthogonal sum of lattices retains such a decomposition of its underlying
module in ``Modules(R)``; the module projections need not preserve the form.
Forgetting the choice lands in ``C`` itself, which is the one
declaration this construction makes.
"""

from collections.abc import Iterable
from typing import TypeVar

from sage.categories.category import Category
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.sets.cardinals import Cardinal, cardinal
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import IndexedFamily, indexed_family
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.lexicon.category_theory import ObjectOfCategory

LabelT = TypeVar("LabelT")


class DirectSumObjects(OwnedCategory):
    r"""Objects of ``C`` carrying a selected ordered family of direct summands.

    The direct-sum object retains its ordinary module placement and the
    source and target of every selected biproduct structure arrow::

        sage: from dzack_research.preamble.all import ZZ, Modules
        sage: C = Modules(ZZ)
        sage: D = DirectSumObjects(C)
        sage: X = D.an_object()
        sage: X in D and X in C and X.number_of_summands() == 2
        True
        sage: all(X.injection(i).codomain() is X and X.projection(i).domain() is X for i in X.summand_index_set())
        True
    """

    @staticmethod
    def __classcall__(cls, base_category: Category):
        return Category.__classcall__(cls, base_category)

    def __init__(self, base_category: Category) -> None:
        self._base_category = base_category
        OwnedCategory.__init__(self)

    def base_category(self) -> Category:
        r"""The category ``C`` in which the biproducts are taken."""
        return self._base_category

    def _repr_object_names(self):
        return f"objects of {self.base_category()._repr_object_names()} with a chosen direct-sum decomposition"

    def an_object(self) -> ObjectOfCategory:
        r"""``X (+) X`` for an object ``X`` of ``C``, decomposed into its two summands."""
        witness = self.base_category().an_object()
        return self.base_category().biproduct((witness, witness))

    def super_categories(self):
        return [self.base_category()]

    def verify_decomposition(
        self,
        underlying_object: Parent,
        summands: IndexedFamily | Iterable[Parent],
        summand_index_set: Parent | None = None,
    ) -> ObjectOfCategory:
        r"""Verify the constructor-owned decomposition ``underlying_object = ⊕ M_i``."""
        match summands:
            case IndexedFamily():
                if summand_index_set is not None and summands.index_set() is not summand_index_set:
                    raise ValueError(
                        f"the summands {summands} are indexed by {summands.index_set()}, so they cannot also be "
                        f"indexed by {summand_index_set}"
                    )
                family = summands
                labels = family.index_set()
            case _:
                values = tuple(summands)
                labels = (
                    Sets.Δ[len(values) - 1]
                    if summand_index_set is None
                    else finite_ordered_set(summand_index_set)
                )
                if labels.cardinality() != cardinal(len(values)):
                    raise ValueError(
                        f"a direct sum of {len(values)} summands needs an index set of {len(values)} labels, but "
                        f"{labels} has cardinality {labels.cardinality()}"
                    )
                family = indexed_family(
                    labels,
                    lambda label: values[int(labels.ranking_map()(label))],
                    name=f"Direct summands of {underlying_object}",
                )

        if underlying_object not in self:
            raise ValueError(
                f"{underlying_object} is not in {self}: it was not constructed as a direct sum"
            )
        # An object placed here answers its decomposition by this category's
        # own accessors; the decomposition is its constructor datum.
        selected = underlying_object.summands()
        selected_labels = underlying_object.summand_index_set()
        if labels != selected_labels:
            raise ValueError(
                f"{underlying_object} is a direct sum indexed by {selected_labels}, not by {labels}"
            )
        if any(selected[label] is not family[label] for label in labels):
            raise ValueError(
                f"the summands {family} differ from the summands {selected} of the direct sum {underlying_object}"
            )
        return underlying_object

    class ParentMethods:
        def __init__(self, summands: IndexedFamily, **rest) -> None:
            match summands:
                case IndexedFamily():
                    pass
                case _:
                    raise TypeError(
                        f"the summands of a direct sum are an indexed family, but {summands!r} is not one"
                    )
            if summands.index_set().cardinality().is_finite() is not True:
                raise ValueError(
                    f"{self} is a selected finite direct sum, but its summands are indexed by the "
                    f"non-finite set {summands.index_set()}"
                )
            self._summands = summands
            super().__init__(**rest)

        def summands(self) -> IndexedFamily:
            return self._summands

        def summand_index_set(self) -> Sets().ObjectType:
            return self.summands().index_set()

        def summand(self, label: LabelT) -> ObjectOfCategory:
            labels = self.summand_index_set()
            if label not in labels:
                raise ValueError(
                    f"{label!r} is not a label of a summand of {self}; the labels are {labels}"
                )
            return self.summands()[label]

        def number_of_summands(self) -> Cardinal:
            return self.summand_index_set().cardinality()

__all__ = ["DirectSumObjects"]
