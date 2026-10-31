r"""Public isometries are complete formed-module arrows with usable keys.

Regression for ``sage-extensions#5``.  A lattice isometry is a lattice
morphism, so it carries the formed-module datum :class:`FormedModuleMorphism`
defines: the retained module component, the value-object component and the
element evaluator.  The isometry constructor enters through the isomorphism
contract, whose own initializer stores only the forward/inverse pair, so the
formed-module half must be initialized from the retained module map.  The
third case covers what an unhashable arrow does to a ``cached_method`` keyed
on it.
"""

from sage_extensions.all import Lattices, ZZ


def _hyperbolic_plane():
    return Lattices(ZZ)([[0, 1], [1, 0]])


def _two_hyperbolic_planes():
    return Lattices(ZZ)([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])


def test_every_public_isometry_constructor_exposes_the_retained_module_component() -> None:
    r"""``module_morphism()`` answers for each route the public homsets offer."""
    lattice = _hyperbolic_plane()
    images = tuple(lattice.module_generators())
    labels = tuple(lattice.module_generating_set())
    module_mor = lattice.module_category().Mor(lattice, lattice)

    for name, build in {
        "Isom(images)": lambda: lattice.Isom(lattice)(images),
        "Aut(images)": lambda: lattice.Aut()(images),
        "Isom(dict)": lambda: lattice.Isom(lattice)(
            {label: images[index] for index, label in enumerate(labels)}
        ),
        "Isom.identity()": lambda: lattice.Isom(lattice).identity(),
    }.items():
        isometry = build()
        module_morphism = isometry.module_morphism()
        assert module_morphism.parent() is module_mor, name
        assert isometry._form_module_morphism is module_morphism, name
        assert isometry._element_function is not None, name
        assert all(
            isometry(generator) == images[index]
            for index, generator in enumerate(lattice.module_generators())
        ), name


def test_a_module_morphism_composes_with_an_isometry() -> None:
    r"""Composition asks the isometry for its evaluator, not a missing attribute.

    ``ModuleMorphism.__mul__`` asks whether the other factor is the identity
    before building the composite, and that question reads
    ``_element_function``.  The same composition is what a Witt extension of
    a partial isometry prescribes.
    """
    lattice = _two_hyperbolic_planes()
    z, a, m, b = tuple(lattice.module_generators())
    labels = tuple(lattice.module_generating_set())

    def isometry(images):
        return lattice.Isom(lattice)(dict(zip(labels, images, strict=True)))

    exchange = isometry((m, b, z, a))
    transvection = isometry((z + m, a, m, b - a))
    identity_map = lattice.module_category().Mor(lattice, lattice)(
        {label: lattice.module_generator(label) for label in labels}
    )

    assert (identity_map * exchange)(z) == exchange(z)
    assert (identity_map * transvection)(z) == transvection(z)
    assert (exchange * identity_map)(z) == exchange(z)
    assert exchange(z) != transvection(z)


def test_a_resolution_augmentation_maps_each_free_generator_to_its_own_basis_element() -> None:
    r"""Distinct isometries are distinct cache keys.

    A hash that raises makes Sage's ``cached_method`` key on the ``repr``,
    and every isometry between fixed lattice endpoints has the same
    ``repr``, so the first computed value would be returned for every
    argument.  The augmentation of a selected resolution is computed through
    exactly such a cache: its word-to-group evaluation reads
    ``_signed_generator_image``, which is a cached method in the basis
    element.
    """
    lattice = _two_hyperbolic_planes()
    vector_space = lattice.vector_space()
    z, a, m, b = tuple(vector_space.module_generators())
    labels = tuple(vector_space.module_generating_set())

    def isometry(images):
        return vector_space.Isom(vector_space)(dict(zip(labels, images, strict=True)))

    exchange = isometry((m, b, z, a))
    transvection = isometry((z + m, a, m, b - a))
    reflection = isometry((-z, -a, m, b))

    assert len({exchange, transvection, reflection}) == 3
    assert hash(exchange) != hash(transvection)
    assert hash(exchange) != hash(reflection)

    group = vector_space.O().subgroup((exchange, transvection, reflection))
    resolution = group.selected_group_resolution()
    augmentation = resolution.augmentation()
    basis = resolution.generating_set()
    free_generators = tuple(augmentation.domain().group_generators())

    assert len(free_generators) == len(basis)
    assert tuple(augmentation(generator) for generator in free_generators) == tuple(basis)
