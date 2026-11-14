r"""``FreeModules`` is a public session name, and free-module maps stay inside it.

``FreeModules = Modules.Free`` is declared in the module owner and the category
was not re-exported, so a consumer could not even write ``M in FreeModules(R)``.
The placement itself was never broken: a free module, the image of a free-module
endomorphism and its kernel all lie in ``FreeModules(ZZ)`` once the name is
reachable.
"""

from sage_extensions.all import FreeModules, Modules, ZZ


def test_free_modules_are_nameable_and_placed() -> None:
    module = Modules(ZZ).free_module(3)

    assert module in FreeModules(ZZ)


def test_images_and_kernels_of_free_module_maps_stay_free() -> None:
    module = Modules(ZZ).free_module(3)
    labels = tuple(module.module_generating_set())
    two = ZZ.one() + ZZ.one()
    images = tuple(
        module.scalar_multiple(two, module.module_generator(label)) for label in labels
    )
    endomorphism = Modules(ZZ).Mor(module, module)(images)

    assert endomorphism.image() in FreeModules(ZZ)
    assert endomorphism.kernel() in FreeModules(ZZ)
