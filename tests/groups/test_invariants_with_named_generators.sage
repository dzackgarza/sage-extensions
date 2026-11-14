r"""A named free-group action with a swap has the constant line as invariants."""

from sage_extensions.all import *


def test_a_swap_and_a_trivial_generator_have_one_invariant_and_coinvariant_dimension() -> None:
    group = Groups.Free(index_set=Sets()(("swap", "fix")))
    two = Groups.C(2)
    involution = next(iter(two.group_generators()))
    character = group.Mor(two)({"swap": involution, "fix": two.one()})
    plane = QQ.free_module(["x", "y"])
    x, y = plane.module_generators()

    def action(element, vector):
        if character(element) == two.one():
            return vector
        coefficients = vector.to_vector()
        return coefficients("x") * y + coefficients("y") * x

    representation = Modules(QQ[group])(plane, action)
    invariants = representation.module_invariants()
    coinvariants = representation.module_coinvariants()

    assert invariants.module_rank() == cardinal(1)
    assert coinvariants.module_rank() == cardinal(1)
    assert invariants.inclusion().is_in_image(x + y)
    assert invariants.inclusion().is_in_image(x) is False
