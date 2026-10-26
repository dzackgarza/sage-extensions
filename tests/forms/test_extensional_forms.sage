r"""Bilinear and quadratic forms on \(\mathbf Z^2\) with values in \(\mathbf Q\).

\(\mathbf Q\) is not a \(\mathbf Z\)-module of the session's module category, so these
forms are given by their values.  A bilinear form is determined by its values on pairs
of basis vectors, \(b(\sum x_s e_s, \sum y_t e_t) = \sum x_s y_t\, b(e_s,e_t)\); a quadratic
form by a symmetric bilinear lift \(\beta\) with \(q(x) = \beta(x,x)\), and its polar form is
\(b_q(x,y) = q(x+y)-q(x)-q(y) = 2\beta(x,y)\).  Pulling back along
\(\varphi\colon\mathbf Z\to\mathbf Z^2\) is precomposition.

With \(b(e_0,e_0)=\tfrac12\), \(b(e_0,e_1)=1\), \(b(e_1,e_0)=0\), \(b(e_1,e_1)=3\):
\(b(e_0+e_1,e_0+e_1) = \tfrac92\).  With the lift
\(\beta = \begin{pmatrix}1&\tfrac12\\\tfrac12&2\end{pmatrix}\): \(q(e_0)=1\), \(q(e_1)=2\),
\(q(e_0+e_1)=4\), \(q(2e_0)=4\), \(b_q(e_0,e_1)=1\).
"""

import pytest

from sage_extensions.all import *


def test_a_bilinear_form_is_determined_by_its_values_on_basis_pairs() -> None:
    module = ZZ.free_module(2)
    first, second = module.module_generators()
    form = module.bilinear_forms(QQ)([[QQ(1) / 2, 1], [0, 3]])

    assert form(first, second) == 1
    assert form(second, first) == 0
    assert form.b(first, second) == 1
    assert form(first + second, first + second) == QQ(9) / 2
    assert form.norm(first + second) == QQ(9) / 2

    indefinite = module.equip_bilinear_form(QQ, [[QQ(1) / 2, 0], [0, -2]])
    positive = module.equip_bilinear_form(QQ, [[QQ(1) / 2, 0], [0, 3]])
    assert indefinite.signature_pair() == (1, 1)
    assert indefinite.determinant() == -1
    assert positive.signature_pair() == (2, 0)
    assert positive.scale_submodule() == ZZ.fractional_ideal(QQ(1) / 2)


def test_extensional_equality_of_bilinear_forms() -> None:
    module = ZZ.free_module(2)
    forms = module.bilinear_forms(QQ)
    form = forms([[QQ(1) / 2, 1], [0, 3]])

    assert form == forms(lambda left, right: form(left, right))
    assert not (form == forms([[QQ(1) / 2, 0], [1, 3]]))


def test_a_quadratic_form_from_a_symmetric_lift_and_its_polar_form() -> None:
    module = ZZ.free_module(2)
    first, second = module.module_generators()
    form = module.quadratic_forms(QQ)([[1, QQ(1) / 2], [QQ(1) / 2, 2]])

    assert form(first) == 1
    assert form(second) == 2
    assert form(first + second) == 4
    assert form(2 * first) == 4 * form(first)
    assert form.polar_form()(first, second) == 1
    assert form.lift_form()(first, second) == QQ(1) / 2
    assert form.lift_pairing(first, second) == QQ(1) / 2


def test_a_quadratic_form_needs_a_symmetric_lift() -> None:
    module = ZZ.free_module(2)

    with pytest.raises(ValueError):
        module.quadratic_forms(QQ)([[1, 1], [0, 2]])


def test_a_quadratic_map_given_by_a_function() -> None:
    module = ZZ.free_module(2)
    first, second = module.module_generators()
    lifted = module.quadratic_forms(QQ)([[1, QQ(1) / 2], [QQ(1) / 2, 2]])

    assert module.quadratic_map(QQ, lambda vector: lifted(vector))(first + second) == 4
    assert module.quadratic_forms(QQ).from_quadratic_map(lambda vector: lifted(vector))(second) == 2


def test_pulling_back_a_form_along_the_diagonal_line() -> None:
    module = ZZ.free_module(2)
    first, second = module.module_generators()
    line = ZZ.free_module(1)
    (generator,) = line.module_generators()
    diagonal = line.Mor(module)((first + second,))
    bilinear = module.bilinear_forms(QQ)([[QQ(1) / 2, 1], [0, 3]])
    quadratic = module.quadratic_forms(QQ)([[1, QQ(1) / 2], [QQ(1) / 2, 2]])

    assert bilinear.pullback(diagonal)(generator, generator) == QQ(9) / 2
    assert quadratic.pullback(diagonal)(generator) == 4
