r"""Finite words and finite multisets over a two-letter alphabet.

Derivation: the words of length `n` over a `k`-letter alphabet are the functions
`\{1, \dots, n\} \to A`, `k^n` of them; the multisets of size `n` number
`\binom{n + k - 1}{n}`, which is `n + 1` for `k = 2`.  Both collections, graded by
`n \in \mathbb{N}`, are countably infinite.
"""

from sage_extensions.all import *


def test_words_and_multisets_over_two_letters_number_two_to_the_n_and_n_plus_one() -> None:
    alphabet = Sets()(("a", "b"))
    words = alphabet.finite_words()
    multisets = alphabet.finite_multisets()

    assert words.cardinality().is_countably_infinite()
    assert multisets.cardinality().is_countably_infinite()
    assert words.cofactor(NN(2)).cardinality() == 4
    assert words.cofactor(NN(3)).cardinality() == 8
    assert multisets.cofactor(NN(2)).cardinality() == 3
    assert multisets.cofactor(NN(3)).cardinality() == 4
    assert words.cofactor(NN(0)).cardinality() == 1
