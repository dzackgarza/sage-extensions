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

    # A hash that is not equality-consistent would make a set or a cache miss
    # an equal arrow built from the same images.
    rebuilt = isometry((m, b, z, a))
    assert rebuilt is not exchange
    assert rebuilt == exchange
    assert hash(rebuilt) == hash(exchange)
    assert len({rebuilt, exchange}) == 1

    group = vector_space.O().subgroup((exchange, transvection, reflection))
    resolution = group.selected_group_resolution()
    augmentation = resolution.augmentation()
    basis = resolution.generating_set()
    free_generators = tuple(augmentation.domain().group_generators())

    assert len(free_generators) == len(basis)
    assert tuple(augmentation(generator) for generator in free_generators) == tuple(basis)

    # The subgroup construction keeps the supplied generators distinct, and a
    # subgroup of it keeps them too: generator selection must not collapse
    # equal-but-distinct or distinct elements.
    assert tuple(group.group_generators()) == (exchange, transvection, reflection)
    assert all(generator in group for generator in (exchange, transvection, reflection))
    assert tuple(group.subgroup((transvection,)).group_generators()) == (transvection,)


def _exchange_and_neighbours(space):
    r"""One isometry of ``space`` built by a chosen route, plus distinct ones."""
    labels = tuple(space.module_generating_set())
    z, a, m, b = tuple(space.module_generators())

    def build(images):
        return space.Isom(space)(dict(zip(labels, images, strict=True)))

    exchange = build((m, b, z, a))
    shear = build((z + m, a, m, b - a))
    reflection = build((-z, -a, m, b))
    return exchange, shear, reflection


def _check_equal_routes(space, ring_name) -> None:
    r"""Equal isometries from different routes are one hash key and one dict key.

    ``Tensor._cache_key`` documents a key for presentations with unhashable
    scalars, not a mathematical hash, so the compatibility is measured here on
    arrows built from separately constructed coordinates rather than assumed
    from that comment.
    """
    labels = tuple(space.module_generating_set())
    z, a, m, b = tuple(space.module_generators())
    exchange, shear, reflection = _exchange_and_neighbours(space)
    images = (m, b, z, a)

    routes = {
        "dict": space.Isom(space)(dict(zip(labels, images, strict=True))),
        "generator images": space.Isom(space)(images),
        "rebuilt dict": space.Isom(space)(
            {label: image for label, image in zip(labels, images, strict=True)}
        ),
        "composite": (exchange * shear) * shear.inverse(),
        "involution triple": (exchange * exchange) * exchange,
        "inverse inverse": exchange.inverse().inverse(),
    }
    table = {exchange: "exchange", shear: "shear", reflection: "reflection"}
    for route, candidate in routes.items():
        assert candidate is not exchange, (ring_name, route)
        assert candidate == exchange, (ring_name, route)
        assert hash(candidate) == hash(exchange), (ring_name, route)
        assert table.get(candidate) == "exchange", (ring_name, route)
        assert len({exchange, candidate}) == 1, (ring_name, route)
        assert len({exchange, shear, reflection}) == 3, (ring_name, route)
        assert hash(shear) != hash(exchange), (ring_name, route)


def test_equal_isometries_from_different_routes_share_a_hash_and_a_dictionary_key_over_zz() -> None:
    _check_equal_routes(_two_hyperbolic_planes(), "ZZ")


def test_equal_isometries_from_different_routes_share_a_hash_and_a_dictionary_key_over_qq() -> None:
    _check_equal_routes(_two_hyperbolic_planes().vector_space(), "QQ")


def test_distinct_isometries_remain_distinct_subgroup_generators() -> None:
    r"""A subgroup keeps its supplied generators distinct, over both rings."""
    for ring_name, space in (
        ("ZZ", _two_hyperbolic_planes()),
        ("QQ", _two_hyperbolic_planes().vector_space()),
    ):
        exchange, shear, reflection = _exchange_and_neighbours(space)
        group = space.O().subgroup((exchange, shear, reflection))

        assert tuple(group.group_generators()) == (exchange, shear, reflection), ring_name
        assert len(set(group.group_generators())) == 3, ring_name
        assert all(generator in group for generator in (exchange, shear, reflection)), ring_name

        # An equal arrow from another route is the same element of the group,
        # not a fourth generator.
        rebuilt = space.Isom(space)(
            dict(zip(tuple(space.module_generating_set()), (exchange(g) for g in space.module_generators()), strict=True))
        )
        assert rebuilt == exchange, ring_name
        assert rebuilt in group, ring_name
        assert tuple(group.subgroup((shear,)).group_generators()) == (shear,), ring_name
