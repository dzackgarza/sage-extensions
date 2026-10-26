r"""Tensor algebras retain their generating module and tensor-degree decomposition."""

from sage_extensions.all import *  # noqa: F401,F403


def test_tensor_algebra_exposes_its_generators_and_homogeneous_components() -> None:
    module = QQ.free_module(("x", "y"))
    tensor = module.tensor_algebra()
    x = tensor.algebra_generator("x")
    y = tensor.algebra_generator("y")
    element = tensor.one() + x + x * y

    assert tensor in TensorAlgebras(QQ)
    assert tensor.generating_module() is module
    assert tensor.from_component(1, module.module_generator("x")) == x
    assert tensor.homogeneous_degree(x * y) == 2
    assert tensor.homogeneous_component(element, 1) == x
    assert element.homogeneous_component(2) == x * y
    assert element.homogeneous_components() == tensor.homogeneous_components(element)


def test_two_generator_tensor_algebra_has_scalar_center() -> None:
    tensor = QQ.free_module(2).tensor_algebra()
    center = tensor.ring_center()
    inclusion = tensor.center_inclusion()

    assert inclusion.domain() is center
    assert inclusion.codomain() is tensor
    assert inclusion(center.one()) == tensor.one()

