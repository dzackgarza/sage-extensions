r"""A module with a chosen finite presentation is built before it computes.

The cokernel of a morphism of modules is a module with a chosen finite
presentation.  The construction stores the datum -- the morphism, its codomain's
chosen frame and the labels of that frame -- and its relation morphism, engine
cover, relation submodule and Smith engine are built by the first request that
needs one of them (``AGENTS.md``, "Construction is instant").

Two counts say so, and both are needed.  The construction realizes no chosen
resolution -- that realization is where the arrow's Mor re-wrap, the relation
images, the lifts of the added images and the fraction-field rank run -- and
materializes no engine matrix.  A construction that computes through either is
red.

Each specimen also runs its first request inside the same instrument and
requires a count: without that, a zero would answer nothing, and a cokernel read
from another test's cache would pass the construction's count without having
constructed anything.  Each specimen therefore names its own datum, so the
morphism it cokernels is one no other test holds.

Over $Z$, $\rho = 2 \cdot 1 \colon Z^2 \to Z^2$ has cokernel
$Z/2 \oplus Z/2$: two invariant factors $2$, cardinality four, not torsion-free.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_constructing_a_cokernel_asks_the_engine_for_no_matrix() -> None:
    r"""$\operatorname{coker}(2 \cdot 1_{Z^2})$, built before anything is asked of it."""
    free = ZZ.free_module(2)
    first, second = free.module_generators()
    dilation = free.Mor(free)({0: ZZ(2) * first, 1: ZZ(2) * second})

    quotient, constructed, requested = construction_work_of(
        dilation.cokernel,
        lambda module: module.invariant_factors(),
    )

    assert constructed == 0
    assert requested > 0
    assert quotient.cokernel_morphism() is dilation
    assert int(quotient.cardinality()) == 4
    assert quotient.is_torsion_free() is False
    assert quotient.is_zero() is False
    assert tuple(quotient.invariant_factors()) == (ZZ(2), ZZ(2))


def test_a_plane_inclusions_quotient_is_built_before_it_is_asked() -> None:
    r"""The cokernel of a primitive plane's inclusion, built before it is read.

    $U \oplus U$ has basis $e_1, f_1, e_2, f_2$ with $b(e_i, f_i) = 1$, and the
    span of $f_2$ and $e_1$ is saturated, so its quotient is free of rank two:
    every invariant factor is $0$.  Naming the two generators in that order
    states the plane this specimen owns.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e1, f1, e2, f2 = lattice.module_generators()
    inclusion = lattice.subobject_on((f2, e1)).inclusion()

    quotient, constructed, requested = construction_work_of(
        inclusion.cokernel,
        lambda module: module.invariant_factors(),
    )

    assert constructed == 0
    assert requested > 0
    assert quotient.is_torsion_free() is True
    assert tuple(quotient.invariant_factors()) == (ZZ(0), ZZ(0))


def test_a_localized_cokernels_construction_asks_the_engine_for_no_matrix() -> None:
    r"""$S/3$ for $S = Z[1/2]$, built before anything is asked of it.

    A presentation over a localization is a finite presentation over the source
    ring once each relation row's denominators are cleared, and the quotient it
    presents is the source quotient localized.  Those are the module's defining
    data; building them at construction computes the presentation inside it.
    """
    ring = ZZ.localization(2)
    free = ring.free_module(1)
    generator = free.module_generator(0)
    dilation = free.Mor(free)({0: ring(3) * generator})

    quotient, constructed, requested = construction_work_of(
        dilation.cokernel,
        lambda module: module.cardinality(),
    )

    assert constructed == 0
    assert requested > 0
    assert int(quotient.cardinality()) == 3


def test_a_restricted_scalars_module_is_built_before_it_is_asked() -> None:
    r"""$A^1$ restricted along $F_2 \to A = F_2[x]/(x^2)$, before it is read.

    The extension is free of rank two over the coefficient field, so the
    restricted module's presentation is the extension's transported relation
    morphism.  Construction selects it and computes nothing.
    """
    base = GF(2)
    polynomial = base["x"]
    x = polynomial.algebra_generator("x")
    extension = polynomial.quotient_ring(polynomial.ideal(x**2))
    restriction = Modules(extension).restriction_of_scalars(
        base.Mor(extension)(lambda scalar: extension(scalar))
    )
    line = extension**1

    module, constructed, requested = construction_work_of(
        lambda: restriction(line),
        lambda restricted: restricted.cardinality(),
    )

    assert constructed == 0
    assert requested > 0
    assert module.module_rank() == 2
    assert module.cardinality() == 4
