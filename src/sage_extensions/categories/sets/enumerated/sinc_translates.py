r"""The enumerated set of Shannon sinc translates \(\{\operatorname{sinc}(\,\cdot\,-n):n\in\mathbb Z\}\).

Elements are formal symbols in \(\mathrm{SR}\), not evaluated sinc
functions. This set does not compute integrals or \(L^2\) Gram matrices.
"""

from sage.misc.cachefunc import cached_function
from sage_extensions.categories.sets.enumerated.function_sets import (
    EnumeratedByIntegers,
    FunctionEnumeratedSets,
)
from sage_extensions.lexicon.set_theory import SetObject


@cached_function
def SincTranslates() -> SetObject:
    r"""The enumerated set \(\{\operatorname{sinc}(\,\cdot\,-n):n\in\mathbb Z\}\subset\mathrm{SR}\).

    Each translate is the formal symbol \(\mathrm{sinc}_n\), not Sage's
    evaluated \(\operatorname{sinc}\).
    """
    return FunctionEnumeratedSets()(
        "sinc",
        r"\mathrm{sinc}",
        "{sinc(· - n) : n in ZZ}",
        indexing=EnumeratedByIntegers(),
    )
