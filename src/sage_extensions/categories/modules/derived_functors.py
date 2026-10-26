r"""Tor and Ext of finitely presented modules, computed from a free resolution.

For a module ``M`` with free resolution ``F_• -> M`` and a second module
``N``, the derived functors of ``- ⊗ N`` and ``Hom(-, N)`` are

``Tor_n(M, N) = H_n(F_• ⊗ N)``  and  ``Ext^n(M, N) = H^n(Hom(F_•, N))``.

Both are read off cohomology modules of represented cochain complexes, so a
result remembers the complex it was computed in and its cycle
representatives.  ``F_• ⊗ N`` is a chain complex; it is stored as a cochain
complex with ``F_i ⊗ N`` in degree ``shift - i``, and ``Tor_n`` is its
cohomology in degree ``shift - n``.

Both read the resolution one term past the degree asked for, because homology
in degree ``n`` needs the map into ``F_n`` as well as the map out of it.  Over
a principal ideal domain the resolution stops in degree one however far it is
asked to go; over a polynomial ring it continues by syzygies.
"""

from sage.misc.cachefunc import cached_function

from sage_extensions.categories.modules.cochain_complexes import CochainComplexes

from sage_extensions.categories.modules.pure.modules import Modules

from sage_extensions.categories.rings.ring_foundation import _owned_ring


def _common_base_ring(module, other):
    ring = _owned_ring(module.base_ring())
    assert _owned_ring(other.base_ring()) == ring, (
        f"Tor and Ext of {module} and {other} are not defined: both modules must be over one ring, "
        f"but they are over {ring} and {other.base_ring()}"
    )
    return ring


@cached_function(key=lambda module, other, shift, steps: (id(module), id(other), shift, steps))
def _tensored_resolution(module, other, shift, steps):
    r"""``F_• ⊗ other`` as a cochain complex with ``F_i ⊗ other`` in degree ``shift - i``."""
    ring = _common_base_ring(module, other)
    resolution = module.free_resolution(steps)
    length = resolution.length()
    tensor = other.tensor_mor_adjunction().left_adjoint()
    return CochainComplexes(ring)(
        {shift - term: tensor(resolution.term(term)) for term in range(length + 1)},
        {
            shift - term: tensor(resolution.differential(term))
            for term in range(1, length + 1)
        },
        name=f"Free resolution of {module} tensored with {other}",
    )


def _tor(module, other, degree=0):
    r"""Return ``Tor_degree(module, other)``, the homology of ``F_• ⊗ other``."""
    degree = int(degree)
    assert degree >= 0, (
        f"Tor_{degree}({module}, {other}) is not defined: Tor is indexed by degrees n >= 0"
    )
    # Homology in degree n reads the map out of F_n and the map into it, so
    # the resolution must reach one term past the degree asked for.
    steps = degree + 1
    length = module.free_resolution(steps).length()
    shift = max(length, degree)
    return _tensored_resolution(module, other, shift, steps).cohomology(shift - degree)


def _ext(module, other, degree=0):
    r"""Return ``Ext^degree(module, other)``, the cohomology of ``Hom(F_•, other)``."""
    degree = int(degree)
    assert degree >= 0, (
        f"Ext^{degree}({module}, {other}) is not defined: Ext is indexed by degrees n >= 0"
    )
    ring = _common_base_ring(module, other)
    resolution = module.free_resolution(degree + 1)
    length = resolution.length()
    identity = other.module_category().Mor(other, other).identity()
    dualized = CochainComplexes(ring)(
        {term: resolution.term(term).module_category().Mor(resolution.term(term), other) for term in range(length + 1)},
        {
            term - 1: resolution.differential(term).internal_mor_map(
                identity,
                source_internal_mor=resolution.term(term - 1).module_category().Mor(
                    resolution.term(term - 1), other
                ),
                target_internal_mor=resolution.term(term).module_category().Mor(
                    resolution.term(term), other
                ),
            )
            for term in range(1, length + 1)
        },
        name=f"Free resolution of {module} dualized into {other}",
    )
    return dualized.cohomology(degree)


def _tor_map(morphism, other, degree=0, *, argument=1, lift=None):
    r"""Return the map on ``Tor_degree`` induced by ``morphism`` in one argument.

    With ``argument=1`` this is the existing covariance in the resolved
    variable: a selected free-resolution lift gives a chain map
    ``F(M) -> F(M')``.  With ``argument=2`` the resolution of the fixed first
    variable is unchanged and the component is
    ``id_{F_n} tensor morphism``.  In both cases a represented homology class
    is sent through its selected cycle representative, so the map is induced
    on the same owned quotient that defines ``module.tor``.  The component
    is a chain map, so it sends boundaries to boundaries: the class of the
    image does not depend on the selected representative, and the induced
    map is linear by construction.
    """
    degree = int(degree)
    if degree < 0:
        raise ValueError(
            f"the map induced by {morphism} on Tor_{degree} is not defined: Tor is indexed by degrees n >= 0"
        )
    match int(argument):
        case 1:
            steps = degree + 1
            source_resolution = morphism.domain().free_resolution(steps)
            target_resolution = morphism.codomain().free_resolution(steps)
            lifted = (
                source_resolution.lift_morphism(morphism, target_resolution)
                if lift is None
                else lift
            )
            if lifted.domain() is not source_resolution or lifted.codomain() is not target_resolution:
                raise ValueError(
                    f"{lifted} cannot compute the map on Tor induced by {morphism}: it must be a chain map "
                    f"between the free resolutions {source_resolution} -> {target_resolution}, but it is "
                    f"{lifted.domain()} -> {lifted.codomain()}"
                )
            if lifted.module_morphism() is not morphism:
                raise ValueError(
                    f"{lifted} cannot compute the map on Tor induced by {morphism}: it must lift {morphism}, "
                    f"but it lifts {lifted.module_morphism()}"
                )
            tensor = other.tensor_mor_adjunction().left_adjoint()
            component = tensor(lifted.component(degree))
            source = morphism.domain().tor(other, degree=degree)
            target = morphism.codomain().tor(other, degree=degree)
        case 2:
            if lift is not None:
                raise ValueError(
                    f"the map induced by {morphism} in the second argument of Tor is computed from a free "
                    f"resolution of {other}; a lift {lift} of a map between resolutions applies only in the "
                    f"first argument"
                )
            steps = degree + 1
            resolution = other.free_resolution(steps)
            term = resolution.term(degree)
            identity = term.module_category().Mor(term, term).identity()
            modules = Modules(term.base_ring())
            source_tensor = modules.tensor_product((term, morphism.domain()))
            target_tensor = modules.tensor_product((term, morphism.codomain()))
            component = identity.tensor_product_map(morphism, source=source_tensor, target=target_tensor)
            source = other.tor(morphism.domain(), degree=degree)
            target = other.tor(morphism.codomain(), degree=degree)
        case _:
            raise ValueError(
                f"Tor has two arguments, numbered 1 and 2, so {morphism} cannot act in argument {argument}"
            )
    return source.module_category().Mor(source, target)._from_constructed_element_map(
        lambda class_: target.class_of_cycle(
            component(source.cycle_representative(class_))
        )
    )


def _ext_map(morphism, other, degree=0, *, argument=1, lift=None):
    r"""Return the map on ``Ext^degree`` induced by ``morphism`` in one argument.

    The first variable is contravariant and the second is covariant.  Both
    maps are induced on the owned cohomology quotient by the corresponding
    internal-Mor component, rather than by recomputing an abstract Ext group.
    That component is a cochain map, so it sends coboundaries to
    coboundaries and the induced map is linear by construction.
    """
    degree = int(degree)
    if degree < 0:
        raise ValueError(
            f"the map induced by {morphism} on Ext^{degree} is not defined: Ext is indexed by degrees n >= 0"
        )
    match int(argument):
        case 1:
            steps = degree + 1
            source_resolution = morphism.domain().free_resolution(steps)
            target_resolution = morphism.codomain().free_resolution(steps)
            lifted = (
                source_resolution.lift_morphism(morphism, target_resolution)
                if lift is None
                else lift
            )
            if lifted.domain() is not source_resolution or lifted.codomain() is not target_resolution:
                raise ValueError(
                    f"{lifted} cannot compute the map on Ext induced by {morphism}: it must be a chain map "
                    f"between the free resolutions {source_resolution} -> {target_resolution}, but it is "
                    f"{lifted.domain()} -> {lifted.codomain()}"
                )
            if lifted.module_morphism() is not morphism:
                raise ValueError(
                    f"{lifted} cannot compute the map on Ext induced by {morphism}: it must lift {morphism}, "
                    f"but it lifts {lifted.module_morphism()}"
                )
            identity = other.module_category().Mor(other, other).identity()
            source_internal = target_resolution.term(degree).module_category().Mor(target_resolution.term(degree), other)
            target_internal = source_resolution.term(degree).module_category().Mor(source_resolution.term(degree), other)
            component = lifted.component(degree).internal_mor_map(
                identity,
                source_internal_mor=source_internal,
                target_internal_mor=target_internal,
            )
            source = morphism.codomain().ext(other, degree=degree)
            target = morphism.domain().ext(other, degree=degree)
        case 2:
            if lift is not None:
                raise ValueError(
                    f"the map induced by {morphism} in the second argument of Ext is computed from a free "
                    f"resolution of {other}; a lift {lift} of a map between resolutions applies only in the "
                    f"first argument"
                )
            steps = degree + 1
            resolution = other.free_resolution(steps)
            term = resolution.term(degree)
            identity = term.module_category().Mor(term, term).identity()
            source_internal = term.module_category().Mor(term, morphism.domain())
            target_internal = term.module_category().Mor(term, morphism.codomain())
            component = identity.internal_mor_map(
                morphism,
                source_internal_mor=source_internal,
                target_internal_mor=target_internal,
            )
            source = other.ext(morphism.domain(), degree=degree)
            target = other.ext(morphism.codomain(), degree=degree)
        case _:
            raise ValueError(
                f"Ext has two arguments, numbered 1 and 2, so {morphism} cannot act in argument {argument}"
            )
    return source.module_category().Mor(source, target)._from_constructed_element_map(
        lambda class_: target.class_of_cycle(
            component(source.cycle_representative(class_))
        )
    )


__all__ = []
