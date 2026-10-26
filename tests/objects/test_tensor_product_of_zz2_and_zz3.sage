from sage_extensions.all import *


def factors():
    return ZZ ^ 2, ZZ ^ 3


def product():
    left, right = factors()
    return Modules(ZZ).tensor_product((left, right))


def test_the_category_and_the_object_constructions_agree() -> None:
    left, right = factors()
    assert product() == left.tensor_product(right)


def test_the_categories_of_the_tensor_product() -> None:
    assert product() in Modules(ZZ)
    assert product() in TensorProductModules(ZZ)
    assert product() in FreeModules(ZZ)


def test_the_rank_is_the_product_of_the_ranks() -> None:
    assert product().module_rank() == 6
    assert product().module_generators().cardinality() == 6
    assert product().tensor_factors().cardinality() == 2


def test_pure_tensors_are_bilinear() -> None:
    left, right = factors()
    tensor = product()
    a, a2 = left.module_generator(0), left.module_generator(1)
    b = right.module_generator(1)
    assert tensor.pure_tensor(2 * a, b) == 2 * tensor.pure_tensor(a, b)
    assert tensor.pure_tensor(a, 3 * b) == 3 * tensor.pure_tensor(a, b)
    assert tensor.pure_tensor(a + a2, b) == tensor.pure_tensor(a, b) + tensor.pure_tensor(a2, b)
    assert tensor.pure_tensor(left.zero(), b) == tensor.zero()
    assert tensor.pure_tensor(a, b) != tensor.pure_tensor(a2, b)


def test_the_tensor_product_has_one_endomorphism_category() -> None:
    tensor = product()
    endomorphisms = tensor.Mor(tensor)
    identity = endomorphisms.identity()
    assert endomorphisms in Cat()
    assert tensor.Mor(tensor) is endomorphisms
    assert identity * identity == identity
