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
red.  The first request, run inside the same instrument, must raise a count:
otherwise the instrument never fired and the construction's zero answers
nothing.

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
    span of $e_1$ and $f_2$ is saturated, so its quotient is free of rank two:
    every invariant factor is $0$.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e1, f1, e2, f2 = lattice.module_generators()
    inclusion = lattice.subobject_on((e1, f2)).inclusion()

    quotient, constructed, requested = construction_work_of(
        inclusion.cokernel,
        lambda module: module.invariant_factors(),
    )

    assert constructed == 0
    assert requested > 0
    assert quotient.is_torsion_free() is True
    assert tuple(quotient.invariant_factors()) == (ZZ(0), ZZ(0))
