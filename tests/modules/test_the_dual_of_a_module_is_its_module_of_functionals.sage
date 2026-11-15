r"""The linear dual of a module is its module of functionals, and nothing else.

The dual of a free module on an infinite basis has no basis: its points are the
families $\varphi(e_s)$ of values on the chosen basis, one scalar per basis
vector, and those are exactly the $R$-linear maps $M \to {}_R R$.  So the dual is
the internal module of morphisms into the free module of rank one, whatever
presentation of it the endpoints happen to give, and the pairing is the
functional applied to the vector.

$\mathbf{Q}^{(\mathbf{N})}$ states this where it is visible: the module of
morphisms $\mathbf{Q}^{(\mathbf{N})} \to \mathbf{Q}$ carries no chosen
presentation, and this library holds no presentation of it -- it is
$\prod_{\mathbf{N}} \mathbf{Q}$, of dimension $2^{\aleph_0}$ over $\mathbf{Q}$,
so no countable family of its points generates it -- and it is still the dual,
and a functional is still written down by its values on the basis.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_dual_of_an_infinite_free_module_is_the_module_of_functionals() -> None:
    r"""$(\mathbf{Q}^{(\mathbf{N})})^*$ is $\operatorname{Mor}(\mathbf{Q}^{(\mathbf{N})}, \mathbf{Q})$.

    The two are the same module: the algebraic dual of a direct sum is the
    product of one copy of $\mathbf{Q}$ per basis vector, and a point of that
    product is a function on the basis, which is what an $R$-linear map out of
    the direct sum is.  The dual is therefore not rebuilt as a product object
    beside the module of morphisms; there is one construction.
    """
    module = QQ**NN
    regular = QQ.regular_module()
    dual = module.dual_module()

    assert dual is module.module_category().Mor(module, regular)
    assert dual.base_ring() is QQ


def test_a_functional_pairs_with_a_vector_by_its_values_on_the_basis() -> None:
    r"""$\varphi(e_0 + e_1) = \varphi(e_0) + \varphi(e_1) = 2$ for the constant functional.

    The functional that is $1$ at every basis vector is a point of the dual: it
    is a function on the basis, and linearity extends it to the whole direct sum,
    where every vector is a finite combination of basis vectors.  Pairing it
    with $e_0 + e_1$ gives $2$, read in the base ring through the regular
    module's identification with $\mathbf{Q}$.
    """
    module = QQ**NN
    regular = QQ.regular_module()
    constant = module.dual_module()(lambda label: regular(QQ.one()))
    sum_of_two = module.module_generator(NN(0)) + module.module_generator(NN(1))

    assert module.dual_evaluation(constant, sum_of_two) == QQ(2)
    assert module.dual_evaluation(constant, module.zero()) == QQ(0)
