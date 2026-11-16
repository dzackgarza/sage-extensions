r"""Torsion of a presented module over $\mathbf{Z}[x]$.

$M = \mathbf{Z}[x]/(x)$ is $\mathbf{Z}$ as an abelian group, and as a
$\mathbf{Z}[x]$-module it is torsion: $x$ kills the class of $1$, and $x$ is a
non-zero-divisor of $\mathbf{Z}[x]$.  So every element of $M$ is killed by a
non-zero-divisor, which is what torsion means (Mathlib's
``Submodule.torsion``), and $\operatorname{Frac}(\mathbf{Z}[x]) \otimes M = 0$
as well, since $x$ is inverted.

The decision is not read off the relation map being injective: the relations
of a presentation may be dependent, and then the relation map has a kernel
after extending scalars.  Over $\mathbf{Z}$ the map $(8, 16) \colon
\mathbf{Z}^2 \to \mathbf{Z}$ has rank one over $\mathbf{Q}$, so its kernel
there has rank one; its cokernel $\mathbf{Z}/8$ is torsion all the same, and
its rank -- $\operatorname{rank} F_0 - \operatorname{rank}(r)$ over the
fraction field -- vanishes.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_class_modulo_x_is_a_torsion_module_over_ZZx() -> None:
    r"""$\mathbf{Z}[x]/(x)$ is torsion, killed by the non-zero-divisor $x$.

    The class of $1$ satisfies $x \cdot 1 = 0$, so it is a torsion element,
    and its multiples are the whole module.  The rank over the fraction field
    vanishes with it: $\operatorname{Frac}(\mathbf{Z}[x]) \otimes
    \mathbf{Z}[x]/(x) = 0$.

    Both readings are asserted, because they are two statements about the same
    module: torsion is the vanishing of $\operatorname{Frac}(R) \otimes_R M$,
    and the rank is the dimension of that fibre.
    """
    ring = ZZ["x"]
    x = ring.algebra_generator("x")
    line = ring ** 1
    (line_label,) = tuple(line.module_generating_set())
    (unit,) = tuple(line.module_generators())
    class_of_one = line.module_category().Mor(line, line)({line_label: x * unit}).cokernel()

    assert class_of_one.module_rank() == 0
    assert class_of_one.is_torsion() is True


def test_a_class_modulo_eight_is_torsion_over_ZZ_even_though_eight_and_sixteen_are_dependent() -> None:
    r"""$\mathbf{Z}/8$ is torsion, and $(8, 16)$ is not injective over $\mathbf{Q}$.

    $\mathbf{Z}/8 = \operatorname{coker}\big((8, 16) \colon \mathbf{Z}^2 \to
    \mathbf{Z}\big)$: the two relations of the class of $1$ are dependent --
    $16 = 2 \cdot 8$ -- so the relation map has rank one over $\mathbf{Q}$ and
    its kernel there has rank one.  It is not injective after extending
    scalars.

    The module is torsion all the same.  Its rank is
    $\operatorname{rank} F_0 - \operatorname{rank}(r) = 1 - 1 = 0$, not
    $\operatorname{rank} F_0 - \operatorname{rank} F_1 = 1 - 2$.
    """
    line = ZZ ** 1
    plane = ZZ ** 2
    (line_label,) = tuple(line.module_generating_set())
    (left_label, right_label) = tuple(plane.module_generating_set())
    (unit,) = tuple(line.module_generators())
    class_of_one = plane.module_category().Mor(plane, line)(
        {left_label: ZZ(8) * unit, right_label: ZZ(16) * unit}
    ).cokernel()

    assert class_of_one.module_rank() == 0
    assert class_of_one.is_torsion() is True
