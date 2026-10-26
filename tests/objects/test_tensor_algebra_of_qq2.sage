from sage_extensions.all import *


def plane():
    return QQ.free_module(("a", "b"))


def tensor():
    return plane().tensor_algebra()


def test_the_functor_and_the_object_constructions_agree() -> None:
    assert Modules(QQ).tensor_algebra()(plane()) is tensor()


def test_the_categories_of_the_tensor_algebra() -> None:
    algebra = tensor()
    assert algebra in Algebras(QQ)
    assert algebra in TensorAlgebras(QQ)
    assert algebra in GradedAlgebras(QQ)
    assert algebra not in Algebras(QQ).Associative().Unital().Commutative()


def test_the_graded_pieces_of_the_tensor_algebra() -> None:
    r"""$\dim (\mathbb Q^2)^{\otimes n} = 2^n$."""
    algebra = tensor()
    assert algebra.graded_piece(0).module_rank() == 1
    assert algebra.graded_piece(1).module_rank() == 2
    assert algebra.graded_piece(2).module_rank() == 4
    assert algebra.graded_piece(2) in Modules(QQ)
    assert algebra.graded_piece(3).module_rank() == 8


def test_the_tensor_algebra_is_noncommutative() -> None:
    algebra = tensor()
    a, b = algebra.algebra_generator("a"), algebra.algebra_generator("b")
    assert a * b != b * a
    assert (a + b) ^ 2 == a ^ 2 + a * b + b * a + b ^ 2


def test_the_centre_of_the_tensor_algebra() -> None:
    r"""The centre of the free associative algebra on at least two letters is the scalars."""
    assert tensor().center().module_rank() == 1


def test_the_tensor_algebra_has_one_endomorphism_category() -> None:
    algebra = tensor()
    endomorphisms = algebra.Mor(algebra)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert algebra.Mor(algebra) is endomorphisms
    assert identity * identity == identity
