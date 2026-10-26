r"""Enumerated sets of functions, indexed by \(\mathbb N\) or by \(\mathbb Z\)."""

from typing import SupportsIndex

from sage.categories.category import Category
from sage.misc.cachefunc import cached_method
from sage.rings.integer import Integer
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent
from sage.symbolic.expression import Expression
from sage.symbolic.ring import SR

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalIsomorphism,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _own_ring,
    _owned_engine_element,
    _owned_integers,
)
from sage_extensions.categories.sets.set_categories import NN, EnumeratedSets, Sets
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.owned_category import _object_of, owned_category_join


def _integers():
    return _owned_integers()


def _symbolic_ring():
    return _own_ring(SR)


def _natural_position(value, *, error_type: type[LookupError] | type[ValueError]) -> int:
    r"""The natural number ``value`` names as a position, as ``NN`` or a Sage integer names it.

    The ingress of an enumeration position or a natural index: it is called by
    ``__getitem__`` and ``function`` on these sets and by
    :func:`integer_from_natural`, and it raises ``error_type`` for a value
    that names no natural number.
    """
    match value:
        case _ if value in NN:
            return int(NN(value))
        case _ if value in _integers() and _integers()(value) >= _integers().zero():
            return int(_integers()(value))
        case _ if value in SageZZ and SageZZ(value) >= 0:
            return int(SageZZ(value))
        case _:
            raise error_type(f"{value!r} is not a natural number, so it is not a position")


def integer_from_natural(n: SupportsIndex):
    r"""The bijection \(\mathbb N\to\mathbb Z\) sending \(0,1,2,3,4,\ldots\) to \(0,1,-1,2,-2,\ldots\)."""
    n = SageZZ(_natural_position(n, error_type=IndexError))
    if n == 0:
        result = SageZZ.zero()
    elif n % 2 == 1:
        result = (n + 1) // 2
    else:
        result = -n // 2
    return _owned_engine_element(_integers(), result)


def natural_from_integer(k: SupportsIndex):
    r"""The inverse of :func:`integer_from_natural`."""
    k = SageZZ(int(_integers()(k))) if k in _integers() else SageZZ(k)
    if k == 0:
        return NN(0)
    if k > 0:
        return NN(int(2 * k - 1))
    return NN(int(-2 * k))


def indexed_symbol(
    prefix: str,
    index: SupportsIndex,
    latex_prefix: str,
) :
    r"""The symbol in \(\mathrm{SR}\) for this prefix and integer index."""
    index = SageZZ(int(_integers()(index))) if index in _integers() else SageZZ(index)
    if index >= 0:
        name = f"{prefix}_{index}"
    else:
        name = f"{prefix}_m{-index}"
    return _owned_engine_element(
        _symbolic_ring(),
        SR.var(name, latex_name=rf"{latex_prefix}_{{{index}}}"),
    )


def _symbol_index(
    elt,
    prefix: str,
    latex_prefix: str | None,
) -> int | None:
    r"""The integer \(n\) when ``elt`` is the indexed symbol of this prefix, and ``None`` otherwise."""
    parent = element_parent(elt)
    if parent is _symbolic_ring():
        symbol = SR(_engine_element(_symbolic_ring(), elt))
    elif elt in SR:
        symbol = SR(elt)
    else:
        return None
    if not symbol.is_symbol():
        return None
    text = str(symbol)
    head = f"{prefix}_"
    if not text.startswith(head):
        return None
    rest = text[len(head) :]
    match rest:
        case _ if rest.startswith("m") and rest[1:].isdigit():
            index = -int(rest[1:])
        case _ if rest.isdigit():
            index = int(rest)
        case _:
            return None
    latex = prefix if latex_prefix is None else latex_prefix
    expected = _engine_element(_symbolic_ring(), indexed_symbol(prefix, index, latex))
    if symbol != expected:
        return None
    return index


def index_of_symbol(
    elt: Expression,
    prefix: str,
    latex_prefix: str | None = None,
):
    r"""Return \(n\) when ``elt`` is the indexed symbol of this prefix."""
    index = _symbol_index(elt, prefix, latex_prefix)
    if index is None:
        raise ValueError(f"{elt!r} is not an indexed symbol {prefix}_n")
    return _integers()(index)


class FunctionEnumeratedSets(OwnedCategory):
    r"""Enumerated sets whose elements stand for functions.

    The formal-symbol presentation is a private engine of this existing
    category.  Prefixes and print names do not define a new category of sets.
    """

    def an_object(self) -> ObjectOfCategory:
        from sage_extensions.categories.sets.enumerated.hermite_polynomials import (
            HermitePolynomials,
        )

        return HermitePolynomials()

    def super_categories(self):
        return [EnumeratedSets()]

    def _call_(
        self,
        symbol_prefix: str,
        latex_symbol_prefix: str,
        description: str,
        *,
        indexing: Category,
    ) -> Sets().ObjectType:
        r"""Construct the set of symbols with this prefix, indexed as ``indexing`` states."""
        return _object_of(
            owned_category_join([self, indexing]),
            _engine=(self, IndexedSymbolicFunctionSet, None),
            symbol_prefix=symbol_prefix,
            latex_symbol_prefix=latex_symbol_prefix,
            description=description,
        )


class IndexedSymbolicFunctionSet:
    r"""Private formal-symbol realization of the function-set enumeration.

    This engine retains the symbol syntax.  Cardinality, order comparison
    and the ranking-isomorphism construction remain the set owners'.
    """

    def __init__(
        self,
        symbol_prefix: str,
        latex_symbol_prefix: str,
        description: str,
        **rest,
    ) -> None:
        self._symbol_prefix = symbol_prefix
        self._latex_symbol_prefix = latex_symbol_prefix
        self._description = description
        super().__init__(facade=_symbolic_ring(), **rest)

    def _an_element_(self):
        r"""Return the rank-zero function symbol."""
        return self[0]

    def __getitem__(self, position):
        r"""Return the function at a nonnegative enumeration position."""
        rank = _natural_position(position, error_type=IndexError)
        return self.ranking_map().inverse()(rank)

    def _symbol_at_index(self, index):
        return indexed_symbol(self._symbol_prefix, index, self._latex_symbol_prefix)

    def _index_of_element(self, element) -> int | None:
        return _symbol_index(element, self._symbol_prefix, self._latex_symbol_prefix)

    @cached_method
    def ranking_map(self) -> CategoricalIsomorphism:
        r"""The enumeration by index, read through this set's own indexing."""

        def position_of(element):
            if element not in self:
                raise ValueError(f"{element!r} is not an element of {self}")
            return self._rank_from_index(self._index_of_element(element))

        return self._ranking_isomorphism(
            position_of,
            lambda position: self._symbol_at_index(self._index_from_rank(position)),
        )

    def __contains__(self, element) -> bool:
        r"""Whether ``element`` is the symbol of this prefix at an index of this set."""
        index = self._index_of_element(element)
        return index is not None and index in self.index_set()

    def _element_constructor_(self, element):
        if element not in self:
            raise ValueError(f"{element!r} is not in {self}")
        return _symbolic_ring()(element)

    def __iter__(self):
        symbol_at = self.ranking_map().inverse()
        position = 0
        while True:
            yield symbol_at(position)
            position += 1

    def _repr_(self) -> str:
        return self._description


class EnumeratedByNaturals(OwnedCategory):
    r"""Infinite enumerated sets ranked by \(\mathbb N\)."""

    def an_object(self):
        from sage_extensions.categories.sets.enumerated.hermite_polynomials import (
            HermitePolynomials,
        )

        return HermitePolynomials()

    def super_categories(self):
        return [EnumeratedSets(), Sets().Infinite()]

    class ParentMethods:
        def index_set(self) -> Sets().ObjectType:
            return NN

        def _index_from_rank(self, position):
            return _integers()(_natural_position(position, error_type=IndexError))

        def _rank_from_index(self, index):
            return _natural_position(index, error_type=ValueError)

        def function(self, index: SupportsIndex):
            return self[self._rank_from_index(index)]


class EnumeratedByIntegers(OwnedCategory):
    r"""Infinite enumerated sets whose functions are indexed by \(\mathbb Z\).

    The ranking map still runs through \(\mathbb N\); :meth:`function` takes the
    integer index, and indexing takes the corresponding natural number.
    """

    def an_object(self):
        from sage_extensions.categories.sets.enumerated.laurent_monomials import (
            LaurentMonomials,
        )

        return LaurentMonomials()

    def super_categories(self):
        return [EnumeratedSets(), Sets().Infinite()]

    class ParentMethods:
        def index_set(self) -> Sets().ObjectType:
            return _integers()

        def _index_from_rank(self, position):
            return integer_from_natural(position)

        def _rank_from_index(self, index):
            return natural_from_integer(index)

        def function(self, index: SupportsIndex):
            return self[self._rank_from_index(index)]
