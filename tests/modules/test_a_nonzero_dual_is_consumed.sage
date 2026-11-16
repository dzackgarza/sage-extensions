r"""A nonzero dual of a finitely presented module is consumed, not only presented.

For $M = \operatorname{coker}(A \colon R^m \to R^n)$ the dual is
$\ker(A^t \colon R^n \to R^m)$ (see
`test_the_dual_of_a_presented_module_over_the_integers_one_variable`), and a
functional is a vector $(p_1, \dots, p_n)$ with $\sum_i A_{ij} p_i = 0$ for every
relation $j$: it assigns the value $p_i$ to the class of the $i$-th generator.
The order ideal $O_M(v)$ of a class is therefore the ideal of the coordinates
the functionals take at it.

Where the dual is zero, as for $\mathbf{Z}/8$, the order ideal is zero and
nothing about the dual has to be read.  These two modules have a dual of rank
one, so the evaluation map's generator images are what the ideal is read from:
one nonzero functional, whose values at the two generators are two scalars.

$\mathbf{Z}^2/(2 e_1 + 3 e_2)$: the dual is $\mathbf{Z}(3, -2)$, so the values
at the classes of $e_1$ and $e_2$ range over $(3)$ and $(2)$.

$\mathbf{Z}[x]^2/(x e_1 + 2 e_2)$: the dual is $\mathbf{Z}[x](2, -x)$, by the
same argument in the unique factorization domain $\mathbf{Z}[x]$ -- $x p =
-2 q$ forces $p = 2c$ and $q = -xc$ -- so the values at the classes of $e_1$
and $e_2$ range over $(2)$ and $(x)$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_order_ideals_of_the_classes_of_a_module_over_the_integers() -> None:
    r"""$O(2 e_1 + 3 e_2)^{-}(e_1) = (3)$ and $O(e_2) = (2)$ in $\mathbf{Z}^2$.

    $\operatorname{Hom}_{\mathbf{Z}}(\mathbf{Z}^2/(2, 3), \mathbf{Z})$ is
    $\{(p, q) : 2p + 3q = 0\} = \mathbf{Z}(3, -2)$.  The functional $(3, -2)$
    takes the value $3$ at the class of $e_1$ and $-2$ at the class of $e_2$,
    and every other functional is an integer multiple of it: the order ideals
    are $(3)$ and $(2)$.
    """
    ring = ZZ
    line = ring ** 1
    plane = ring ** 2
    (line_label,) = tuple(line.module_generating_set())
    (first_label, second_label) = tuple(plane.module_generating_set())
    (unit,) = tuple(line.module_generators())
    (first, second) = tuple(plane.module_generators())
    covering = plane.module_category().Mor(line, plane)(
        {line_label: ring(2) * first + ring(3) * second}
    )
    module = covering.cokernel()

    functionals = module.dual_module()

    assert functionals.module_rank() == 1
    assert module.module_generator(first_label).order_ideal() == ring.ideal(3)
    assert module.module_generator(second_label).order_ideal() == ring.ideal(2)


def test_the_order_ideals_of_the_classes_of_a_module_over_one_variable() -> None:
    r"""$O(x e_1 + 2 e_2)^{-}(e_1) = (2)$ and $O(e_2) = (x)$ in $\mathbf{Z}[x]^2$.

    $\operatorname{Hom}_{\mathbf{Z}[x]}(\mathbf{Z}[x]^2/(x, 2),
    \mathbf{Z}[x]) = \{(p, q) : x p + 2 q = 0\} = \mathbf{Z}[x](2, -x)$: $x$
    does not divide $2$ in the unique factorization domain $\mathbf{Z}[x]$, so
    $p = 2c$ and $q = -xc$.  The functional $(2, -x)$ takes the value $2$ at
    the class of $e_1$ and $-x$ at the class of $e_2$, and every functional is
    a multiple of it: the order ideals are $(2)$ and $(x)$.
    """
    ring = ZZ["x"]
    x = ring.algebra_generator("x")
    line = ring ** 1
    plane = ring ** 2
    (line_label,) = tuple(line.module_generating_set())
    (first_label, second_label) = tuple(plane.module_generating_set())
    (unit,) = tuple(line.module_generators())
    (first, second) = tuple(plane.module_generators())
    covering = plane.module_category().Mor(line, plane)(
        {line_label: x * first + ring(2) * second}
    )
    module = covering.cokernel()

    functionals = module.dual_module()

    assert functionals.module_rank() == 1
    assert module.module_generator(first_label).order_ideal() == ring.ideal(2)
    assert module.module_generator(second_label).order_ideal() == ring.ideal(x)
