r"""#528: the owned-ring crossings of one Eichler transvection, on two ranks.

The laziness contract of the transvection's construction is that its matrix --
`rank^2` entries -- costs a number of crossings into the owned ring that is
linear in the rank: the entries' arithmetic is the engine's, and the owned ring
keeps one decision per generator, integrality of `(1/2)q(a)b(e,x)`, which is the
statement that the transvection preserves the lattice.

This probe measures, for the counter a test can use, the crossings one
`eichler_transvection` makes on two ranks of the same form over `QQ`, and prints
the images the formula gives on the control:

    t(e,a): v |-> v - (a,v) e + (e,v) a - (1/2)(a,a)(e,v) e

equation (4) of Gritsenko--Hulek--Sankaran, arXiv:0810.1614, section 3.1,
printed p. 8.  With `q(a) = 6` and `b(e,a) = 0`, `t(a) = a - 6e` fixes the sign
of the `-(a,v)e` term and `t(f) = f + a - 3e` reads the half coefficient, which
a construction writing `q(a)` for `(1/2)q(a)` would send to `f + a - 6e`.
"""

import sys
import traceback

from sage_extensions.all import *  # noqa: F401,F403

from sage_extensions.categories.rings import ring_foundation as ring_foundation_module

COUNTS = {}


def shadow(module, name, label):
    """Count calls to ``module.name`` in place; return the restore callable."""
    original = getattr(module, name)

    def counted(*args, **kwargs):
        COUNTS[label] = COUNTS.get(label, 0) + 1
        return original(*args, **kwargs)

    setattr(module, name, counted)
    return lambda: setattr(module, name, original)


def say(*parts):
    print(*parts, flush=True)


def block():
    """`U + <6>` over `QQ`, which carries an isotropic vector and a square-six partner."""
    return Lattices(QQ)([[0, 1, 0], [1, 0, 0], [0, 0, 6]])


def specimen(rank):
    """The two-rank specimen: `U + <6>` and its direct sum with itself."""
    lattice = block()
    for _ in range(rank // 3 - 1):
        lattice = lattice + block()
    labels = tuple(lattice.module_generating_set())
    isotropic = lattice.module_generator(labels[0])
    orthogonal = lattice.module_generator(labels[2])
    ring = lattice.base_ring()
    assert isotropic.q() == ring.zero(), f"q(e) = {isotropic.q()}"
    assert isotropic.b(orthogonal) == ring.zero(), f"b(e, a) = {isotropic.b(orthogonal)}"
    return lattice, labels, isotropic, orthogonal


def ring_class(ring):
    """The class that defines the owned ring's element constructor."""
    for klass in type(ring).__mro__:
        if "_element_constructor_" in vars(klass):
            return klass
    return None


def main(argv):
    for rank in (3, 6, 9, 12):
        lattice, labels, isotropic, orthogonal = specimen(rank)
        ring = lattice.base_ring()
        COUNTS.clear()
        restores = [
            shadow(ring_foundation_module, name, name)
            for name in ("_owned_engine_element", "_engine_element")
        ]
        owned_ring_class = ring_class(ring)
        if owned_ring_class is not None:
            restores.append(shadow(owned_ring_class, "_element_constructor_", "ring._element_constructor_"))
        try:
            transvection = lattice.eichler_transvection(isotropic, orthogonal)
        finally:
            for restore in restores:
                restore()
        rank_ = int(lattice.module_rank())
        say(f"rank {rank_}: " + ", ".join(f"{key}={value}" for key, value in sorted(COUNTS.items())))
        partner = lattice.module_generator(labels[1])
        half = orthogonal.q() / ring(2)
        say(f"  q(a) = {orthogonal.q()} (half {half}); b(e, f) = {isotropic.b(partner)}; rank^2 = {rank_ ** 2}")
        say(f"  t(e) == e: {transvection(isotropic) == isotropic}")
        say(
            f"  t(a) == a - q(a) e: "
            f"{transvection(orthogonal) == orthogonal - lattice.scalar_multiple(orthogonal.q(), isotropic)}"
        )
        say(
            f"  t(f) == f + a - (1/2)q(a) e: "
            f"{transvection(partner) == partner + orthogonal - lattice.scalar_multiple(half, isotropic)}"
        )
        say(
            f"  t(f) with q(a) instead of (1/2)q(a) differs: "
            f"{transvection(partner) != partner + orthogonal - lattice.scalar_multiple(orthogonal.q(), isotropic)}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001
        traceback.print_exc()
        raise
