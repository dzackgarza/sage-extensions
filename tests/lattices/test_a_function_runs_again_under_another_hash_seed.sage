from sage_extensions.all import *


def hash_of_a_name():
    return hash("the line-cusp key")


def gram_determinant():
    return int(IntegralLattice(matrix(ZZ, [[2, 1], [1, 2]])).determinant())


def test_a_string_hash_depends_on_the_seed_of_the_process_that_computes_it():
    assert in_fresh_process(hash_of_a_name, 1) == in_fresh_process(hash_of_a_name, 1)
    assert in_fresh_process(hash_of_a_name, 1) != in_fresh_process(hash_of_a_name, 2)


def test_a_session_computation_returns_its_value_from_the_fresh_process():
    assert in_fresh_process(gram_determinant, 1) == 3
