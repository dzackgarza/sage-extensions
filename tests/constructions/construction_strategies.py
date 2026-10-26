"""Hypothesis strategies for the two parameterization modes of the survey.

Natural parameters: integers, primes, squarefree radicands, rationals, Gram
matrices, ranks, Cartan types.  Category objects: members of the named
families in ``tests/conftest.py``, drawn by name and built by the session.
"""

from fractions import Fraction

from hypothesis import strategies as st

from natural_parameters import determinant_2x2, is_prime, is_squarefree

small_integers = st.integers(min_value=2, max_value=60)
positive_integers = st.integers(min_value=1, max_value=40)
nonzero_integers = st.integers(min_value=-30, max_value=30).filter(lambda n: n != 0)
primes = st.integers(min_value=2, max_value=60).filter(is_prime)
odd_primes = primes.filter(lambda p: p != 2)
ranks = st.integers(min_value=0, max_value=4)
positive_ranks = st.integers(min_value=1, max_value=4)
degrees = st.integers(min_value=0, max_value=4)
radicands = st.integers(min_value=-40, max_value=40).filter(lambda d: d not in (0, 1) and is_squarefree(d))
rationals = st.fractions(min_value=Fraction(-20), max_value=Fraction(20), max_denominator=12)
nonzero_rationals = rationals.filter(lambda q: q != 0)
cartan_types = st.sampled_from([["A", 1], ["A", 2], ["A", 3], ["D", 4], ["E", 6], ["E", 7], ["E", 8]])
symmetric_groups = st.integers(min_value=1, max_value=5)
cyclic_orders = st.integers(min_value=2, max_value=30)


@st.composite
def symmetric_gram_matrices(draw, rank=2, bound=6):
    entries = draw(st.lists(st.integers(min_value=-bound, max_value=bound), min_size=rank * rank, max_size=rank * rank))
    gram = [[0] * rank for _ in range(rank)]
    for i in range(rank):
        for j in range(i, rank):
            gram[i][j] = gram[j][i] = entries[i * rank + j]
    return gram


nondegenerate_gram_2x2 = symmetric_gram_matrices(2).filter(lambda gram: determinant_2x2(gram) != 0)
even_gram_2x2 = nondegenerate_gram_2x2.filter(lambda gram: gram[0][0] % 2 == 0 and gram[1][1] % 2 == 0)


@st.composite
def cyclic_module_orders(draw):
    return draw(st.lists(st.integers(min_value=1, max_value=24), min_size=1, max_size=3))


def family(names):
    """A member of a catalogue family, by name; the test builds it through the session."""
    return st.sampled_from(sorted(names))
