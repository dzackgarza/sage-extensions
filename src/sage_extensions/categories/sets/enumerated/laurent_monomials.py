r"""The enumerated set of Laurent monomials \(\{z^n : n\in\mathbb Z\}\).

Elements are formal symbols in \(\mathrm{SR}\), not evaluated powers:
\(z^0\) is the symbol, not the scalar \(1\).
"""

from sage.misc.cachefunc import cached_function
from sage_extensions.categories.sets.enumerated.function_sets import (
    EnumeratedByIntegers,
    FunctionEnumeratedSets,
)
from sage_extensions.lexicon.set_theory import SetObject


@cached_function
def LaurentMonomials() -> SetObject:
    r"""The enumerated set \(\{z^n : n\in\mathbb Z\}\subset\mathrm{SR}\)."""
    return FunctionEnumeratedSets()(
        "z",
        "z",
        "{z^n : n in ZZ}",
        indexing=EnumeratedByIntegers(),
    )
