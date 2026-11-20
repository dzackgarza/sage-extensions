from sage_extensions.all import *


def hash_of_a_name():
    return hash("the line-cusp key")


def rank_of_u_plus_a_negative_two_line():
    return int((Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])).rank())


def test_a_string_hash_depends_on_the_seed_of_the_process_that_computes_it():
    first, again, other = in_fresh_processes(hash_of_a_name, [1, 1, 2])
    assert first == again
    assert first != other


def test_a_session_computation_returns_its_value_from_the_fresh_process():
    assert in_fresh_processes(rank_of_u_plus_a_negative_two_line, [1]) == (3,)
