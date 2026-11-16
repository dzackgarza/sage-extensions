r"""The order ideal of a ring element is an ideal of the ring's base ring.

A ring is a left module over its base ring, so an element of $\mathbf{Z}[x]$
carries two readings that both go by the name ``order_ideal``: the ring's
element class reaches ``Modules.ElementMethods.order_ideal`` through the module
structure $U(\mathbf{Z}[x])$ and
``FramedFreeModules.ElementMethods.order_ideal`` from the chosen basis of the
monomials.  The framed level is the one the rebuild rule keeps, and it states
the value: the ideal the coordinates of the chosen basis generate.  The module
level states it only where the dual carries a generating family, and on an
infinite basis it does not: $\operatorname{Hom}_{\mathbf{Z}}
(\mathbf{Z}[x], \mathbf{Z})$ is $\prod_{\mathbf{N}} \mathbf{Z}$, which is
uncountable, so no countable family of its points generates it, and by
Baer--Specker it is not free.  The two readings agree wherever both answer.
The order ideal itself is not a matter of which level answers: it is
$O_M(v) = \{\varphi(v) : \varphi \in \operatorname{Hom}_R(M,R)\}$, an ideal of
the scalar ring $R$.  Reading $\mathbf{Z}[x]$ as a $\mathbf{Z}$-module, that is
an ideal of $\mathbf{Z}$ and not of $\mathbf{Z}[x]$ -- the linear functionals
take values in $\mathbf{Z}$.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_order_ideal_of_an_integer_polynomial_is_the_ideal_of_its_coefficients() -> None:
    r"""$O_{\mathbf{Z}[x]}(2x+2) = (2)$: the values of the functionals at $2x+2$.

    $\mathbf{Z}[x]$ is free on the monomials over $\mathbf{Z}$, so a linear
    functional $\varphi$ is its family of values on them, and
    $\varphi(2x+2) = 2\varphi(1) + 2\varphi(x)$: every value is divisible by
    $2$.  The functional that is $1$ on $1$ and $0$ on every other monomial
    attains $2$, so the values generate exactly $(2)$.

    The algebraic dual of a free module on countably many generators is the
    product of countably many copies of the ring, and this library holds no
    generating family of it: at $R = \mathbf{Z}$ it is uncountable, so no
    countable family generates it, and by Baer--Specker it is not free.  The
    ideal is therefore read off the coordinate functionals of the monomial
    basis, whose values are the coefficients.

    The result is an ideal of the base ring $\mathbf{Z}$, which is what the
    operation states: the linear functionals take values in $\mathbf{Z}$ and not
    in $\mathbf{Z}[x]$.  It is asserted as membership in the ideals of
    $\mathbf{Z}$ and not only by equality with $(2)$, because a module equal to
    $(2)$ is not an ideal.
    """
    line = ZZ["x"]
    x = line.algebra_generator("x")
    ideal = (2 * x + 2).order_ideal()

    assert ideal in CommutativeIdeals(ZZ)
    assert ideal == ZZ.ideal(2)


def test_the_order_ideal_of_a_polynomial_is_read_off_its_coefficients() -> None:
    r"""$O_{\mathbf{Z}[x]}(2x+2)$ is the coordinate ideal $(2)$, and the dual cannot state it.

    The values of the linear functionals on $\mathbf{Z}[x]$ at $2x+2$ generate
    $(2)$: every value is $2\varphi(1) + 2\varphi(x)$, and the functional that
    is $1$ on $1$ attains $2$.  The ideal is an ideal of the base ring
    $\mathbf{Z}$ -- an element of the ideals of $\mathbf{Z}$ and not a
    submodule of anything -- because the linear functionals take their values
    there.

    What states it is not the dual: $\operatorname{Hom}_{\mathbf{Z}}
    (\mathbf{Z}[x], \mathbf{Z})$ is $\prod_{\mathbf{N}} \mathbf{Z}$, which is
    uncountable, so no countable family of its points generates it, and by
    Baer--Specker it is not free; this library holds no generating family of
    it, so the image of evaluation cannot be spanned by their values.  The
    level that answers is the framed free module's, which reads the ideal off
    the coordinate functionals of the monomial basis: each coordinate of
    $2x+2$ is $2$, and each is attained.  That level is a subcategory of
    $\mathrm{Modules}(\mathbf{Z})\mathrm{Free}()$ and so is the more specific
    one, which is the provider the rebuild rule must keep
    (``refine._final_category_operations``).
    """
    line = ZZ["x"]
    x = line.algebra_generator("x")
    element = 2 * x + 2
    dual = element.parent().dual_module()
    ideal = element.order_ideal()

    assert dual.has_selected_module_resolution() is False
    assert ideal in CommutativeIdeals(ZZ)
    assert ideal == ZZ.ideal(2)


def test_the_order_ideal_of_a_rational_polynomial_is_the_unit_ideal() -> None:
    r"""$O_{\mathbf{Q}[x]}(x+1) = \mathbf{Q}$: the coefficients generate the field.

    Over $\mathbf{Q}$ the same functional that is $1$ on $1$ attains the
    coefficient $1$ of $x+1$, so the values generate the unit ideal of
    $\mathbf{Q}$ -- which is $\mathbf{Q}$ itself -- and it is an ideal of
    $\mathbf{Q}$, not of $\mathbf{Q}[x]$.
    """
    line = QQ["x"]
    x = line.algebra_generator("x")
    ideal = (x + 1).order_ideal()

    assert ideal in CommutativeIdeals(QQ)
    assert ideal == QQ.ideal(1)


def test_the_order_ideal_of_a_class_modulo_eight_is_the_zero_ideal() -> None:
    r"""$O_{\mathbf{Z}/8}(3) = (0)$, because $\operatorname{Hom}_{\mathbf{Z}}(\mathbf{Z}/8,\mathbf{Z}) = 0$.

    $\mathbf{Z}/8$ is presented as a $\mathbf{Z}$-module by the class of $1$
    and the single relation $8 \cdot 1 = 0$, so its dual is the kernel of the
    transpose of that presentation, $\ker(8 \colon \mathbf{Z} \to
    \mathbf{Z}) = 0$: a functional $\varphi$ with $\varphi(1) = m$ satisfies $8m
    = \varphi(8 \cdot 1) = 0$, hence $m = 0$, hence $\varphi = 0$.  The values
    of the functionals at $3$ are therefore $0$ alone, and the order ideal is
    the zero ideal of the base ring $\mathbf{Z}$ -- an ideal of $\mathbf{Z}$,
    not of $\mathbf{Z}/8$, because the linear functionals take their values
    there.
    """
    ring = Zmod(8)
    element = ring(3)

    assert ring.dual_module().is_zero()
    assert element.order_ideal() in CommutativeIdeals(ZZ)
    assert element.order_ideal() == ZZ.ideal(0)
