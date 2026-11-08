r"""The upper unipotent subgroup of GL(F5^2) has all five shear parameters.

Its matrices fix the first basis vector and send the second to f+a*e.
The lower shear and simultaneous negation do not belong to this group.
"""

from sage_extensions.all import *


def test_finite_native_module_subgroup_has_exact_shear_membership():
    field = PrimeFields()(5)
    module = field.free_module(2)
    e, f = tuple(module.module_generators())
    left, right = tuple(module.module_generating_set())
    group = module.general_linear_group()
    assert group.is_finite() is True

    def shear(coefficient):
        return group({left: e, right: f+module.scalar_multiple(coefficient, e)})

    upper = group.subgroup((shear(field.one()),))
    assert upper.cardinality() == cardinal(5)
    assert all(shear(coefficient) in upper for coefficient in field)
    assert group({left: e+f, right: f}) not in upper
    assert group({left: -e, right: -f}) not in upper
