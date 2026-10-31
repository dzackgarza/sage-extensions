r"""A form with infinite rows has the constant family as a row.

The correlation sends ``e_s`` to ``b(e_s, -)``.  For a diagonal Gram that row is
supported on ``s``, so finite combinations never reach the constant family and
surjectivity is refuted from the form's own construction.  For the symmetric
form ``b(e_i, e_j) = 1`` on ``QQ^(NN)`` the row of ``e_0`` *is* the constant
family, so the constant family is an image; no such refutation may be retained
for it.
"""

from sage_extensions.all import *

from sage_extensions.categories._lattice import _DiagonalGram
from sage_extensions.categories.modules.framed.formed.form_modules import FormModules
from sage_extensions.categories.modules.hodge import (
    _attach_diagonal_correlation_witness,
)
from sage_extensions.categories.modules.pure.modules import Modules


def _all_ones_form():
    r"""The symmetric form ``b(x, y) = (sum x_i)(sum y_j)`` on ``QQ^(NN)``."""
    module = QQ**NN
    ring = QQ
    value_module = ring.regular_module()

    def pairing(left, right):
        left_coordinates = left.to_vector()
        right_coordinates = right.to_vector()
        total_left = sum(
            (
                ring(left_coordinates(label))
                for label in left_coordinates.support().domain()
            ),
            ring.zero(),
        )
        total_right = sum(
            (
                ring(right_coordinates(label))
                for label in right_coordinates.support().domain()
            ),
            ring.zero(),
        )
        return value_module(total_left * total_right)

    return module, module.bilinear_forms(value_module)(pairing), value_module


def _basis_vector(module, position):
    return module.module_generator(NN(position))


def test_the_all_ones_form_row_is_the_constant_family() -> None:
    module, form, value_module = _all_ones_form()
    unit = value_module(QQ.one())
    assert form(_basis_vector(module, 0), _basis_vector(module, 0)) == unit
    assert form(_basis_vector(module, 0), _basis_vector(module, 1)) == unit
    assert form(_basis_vector(module, 1), _basis_vector(module, 7)) == unit


def test_the_witness_is_attached_only_to_a_diagonal_gram() -> None:
    standard = Lattices(QQ)(QQ**NN)
    assert isinstance(standard.gram_tensor(), _DiagonalGram)

    class _Candidate:
        pass

    candidate = _Candidate()
    _attach_diagonal_correlation_witness(
        standard, candidate, standard._dual_product_construction()
    )
    assert "_preamble_non_surjectivity_witness" in vars(candidate)

    module, form, _value_module = _all_ones_form()
    all_ones = FormModules(QQ)(form)
    withheld = _Candidate()
    _attach_diagonal_correlation_witness(
        all_ones, withheld, standard._dual_product_construction()
    )
    assert "_preamble_non_surjectivity_witness" not in vars(withheld)
