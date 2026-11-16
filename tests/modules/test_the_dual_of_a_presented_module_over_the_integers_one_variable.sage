r"""The dual of a finitely presented module over $\mathbf{Z}[x]$ is presented.

For $M = \operatorname{coker}(A \colon R^m \to R^n)$ the dual is the kernel of
the transpose, $\operatorname{Hom}_R(M, R) = \ker(A^t \colon R^n \to R^m)$: a
functional assigns a value to each generator and kills every relation.  The
kernel is a syzygy computation over $R = \mathbf{Z}[x]$, which is not a
principal ideal domain, so it is not a Smith form: Singular's standard basis
over its integer coefficient ring computes it, and the dual is presented on
that kernel the same way any finitely presented module is.

The values here are read off by hand.  $R$ is a domain, so a functional that
kills every generator is zero: $\operatorname{Hom}_R(R/(x), R) = 0$ and
$\operatorname{Hom}_R(R/(2, x), R) = 0$.  The syzygy module of the row
$(x, 2)$ is free on $(2, -x)$ or $(-2, x)$ -- $x p + 2 q = 0$ forces $2 \mid p$,
say $p = 2c$, and then $q = -xc$ -- so the dual of the module presented by the
column $(x, 2)^t$ is $R$ itself.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_dual_of_a_class_modulo_x_over_ZZx_is_zero() -> None:
    r"""$\operatorname{Hom}_{\mathbf{Z}[x]}(\mathbf{Z}[x]/(x), \mathbf{Z}[x]) = 0$.

    $R/(x)$ is presented on the class of $1$ with the relation $x \cdot 1 = 0$,
    so its dual is $\ker(x \colon R \to R)$, and $x$ is a non-zero-divisor of
    the domain $R$: every functional kills the class of $1$, hence everything.

    The order ideal of the class of $1$ is therefore the zero ideal of $R$ --
    an ideal of $R$ and not of $R/(x)$, because the linear functionals take
    their values in $R$.  It is an answer only because the dual is presented:
    the values of a generating family are what the evaluation image is computed
    from.
    """
    ring = ZZ["x"]
    x = ring.algebra_generator("x")
    line = ring ** 1
    (line_label,) = tuple(line.module_generating_set())
    (unit,) = tuple(line.module_generators())
    class_of_one = line.module_category().Mor(line, line)({line_label: x * unit}).cokernel()

    functionals = class_of_one.dual_module()

    assert functionals.is_zero()
    assert class_of_one.module_generator(line_label).order_ideal() in CommutativeIdeals(ring)
    assert class_of_one.module_generator(line_label).order_ideal() == ring.ideal(0)


def test_the_dual_of_a_class_modulo_two_and_x_over_ZZx_is_zero() -> None:
    r"""$\operatorname{Hom}_{\mathbf{Z}[x]}(\mathbf{Z}[x]/(2, x), \mathbf{Z}[x]) = 0$.

    The class of $1$ is presented with the two relations $2 \cdot 1 = 0$ and
    $x \cdot 1 = 0$, so the dual is $\ker(2 \colon R \to R) \cap
    \ker(x \colon R \to R)$, which is zero in a domain.  The values of the
    functionals at the class of $1$ are therefore $0$ alone.
    """
    ring = ZZ["x"]
    x = ring.algebra_generator("x")
    line = ring ** 1
    plane = ring ** 2
    (line_label,) = tuple(line.module_generating_set())
    (left_label, right_label) = tuple(plane.module_generating_set())
    (unit,) = tuple(line.module_generators())
    presentation = plane.module_category().Mor(plane, line)(
        {left_label: ring(2) * unit, right_label: x * unit}
    )
    class_of_one = presentation.cokernel()

    functionals = class_of_one.dual_module()

    assert functionals.is_zero()
    assert class_of_one.module_generator(line_label).order_ideal() == ring.ideal(0)


def test_the_kernel_of_x_and_two_over_ZZx_is_the_koszul_syzygy() -> None:
    r"""$\ker(x, 2) = \mathbf{Z}[x]\,(2, -x)$ over $\mathbf{Z}[x]$, free of rank one.

    $x p + 2 q = 0$ forces $2 \mid p$, because $2$ does not divide $x$ in the
    unique factorization domain $\mathbf{Z}[x]$ and $2$ is irreducible there:
    write $p = 2c$ and then $q = -xc$.  So the kernel is free on $(2, -x)$,
    and $(-2, x)$ generates the same submodule.

    This is the kernel that presents the dual of the module of the previous
    section's shape, and it is not a Smith form: over $\mathbf{Z}[x]$ the
    kernel of a matrix is a syzygy module, computed in a standard basis over
    the integer coefficient ring.
    """
    ring = ZZ["x"]
    x = ring.algebra_generator("x")
    line = ring ** 1
    plane = ring ** 2
    (line_label,) = tuple(line.module_generating_set())
    (left_label, right_label) = tuple(plane.module_generating_set())
    (unit,) = tuple(line.module_generators())
    (left, right) = tuple(plane.module_generators())
    syzygy = 2 * left - x * right
    row = plane.module_category().Mor(plane, line)(
        {left_label: x * unit, right_label: ring(2) * unit}
    )

    kernel = row.kernel()

    assert kernel.module_rank() == 1
    assert kernel.module_generating_set().cardinality() == 1
    (kernel_label,) = tuple(kernel.module_generating_set())
    image = kernel.inclusion()(kernel.module_generator(kernel_label))
    assert row(image) == line.zero()
    assert image in (syzygy, -syzygy)
