r"""Module morphisms retain generator images and induce tensor and biproduct maps."""

from sage_extensions.all import *  # noqa: F401,F403


def test_projection_retains_its_selected_generator_images() -> None:
    plane = ZZ.free_module(2)
    line = ZZ.free_module(1)
    projection = plane.Mor(line)(
        {0: line.module_generator(0), 1: line.zero()}
    )
    images = projection.module_generator_images()

    assert images[0] == line.module_generator(0)
    assert images[1] == line.zero()


def test_identity_induces_identity_on_tensor_product_and_biproduct() -> None:
    line = ZZ.free_module(1)
    identity = line.Mor(line).identity()
    tensor_map = identity.tensor_product_map(identity)
    biproduct_map = identity.biproduct_map(identity)

    assert tensor_map == tensor_map.domain().Mor(tensor_map.codomain()).identity()
    assert biproduct_map == biproduct_map.domain().Mor(biproduct_map.codomain()).identity()
