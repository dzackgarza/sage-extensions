from sage_extensions.all import *

GRAM = [[1, 1], [1, 1]]


def degenerate():
    return Lattices(ZZ)(GRAM)


def test_the_lattice_and_the_form_module_constructions_agree() -> None:
    module = ZZ ^ 2
    assert degenerate() == FormModules(ZZ)(module.bilinear_forms(ZZ)(GRAM))


def test_the_categories_of_the_degenerate_plane() -> None:
    r"""$\det = 0$: a lattice with a form, but not a nondegenerate one."""
    formed = degenerate()
    assert formed in Lattices(ZZ)
    assert formed in FiniteRankLattices(ZZ)
    assert formed not in NondegenerateLattices(ZZ)


def test_the_radical_is_the_line_through_e0_minus_e1() -> None:
    r"""$b(xe_0 + ye_1, -) = (x + y)(e_0^* + e_1^*)$ vanishes exactly on $\mathbb Z(e_0 - e_1)$."""
    formed = degenerate()
    e0, e1 = formed.module_generator(0), formed.module_generator(1)
    radical = formed.radical()
    left_radical = formed.left_radical()
    right_radical = formed.right_radical()
    vector = radical.inclusion()(radical.module_generator(0))
    assert formed.determinant() == 0
    assert not formed.is_nondegenerate()
    assert radical.module_rank() == 1
    assert left_radical.module_rank() == 1
    assert right_radical.module_rank() == 1
    assert formed.b(vector, e0) == 0
    assert formed.b(vector, e1) == 0
    assert vector != formed.zero()
    assert formed.correlation_morphism().kernel().module_rank() == 1
    assert not formed.correlation_morphism().is_injective()


def test_the_form_is_odd() -> None:
    formed = degenerate()
    assert formed.b(formed.module_generator(0), formed.module_generator(0)) == 1
    assert not formed.is_even()


def test_the_quotient_by_the_radical() -> None:
    r"""$L/\operatorname{rad} L = \mathbb Z\bar e_0$ with $b(\bar e_0, \bar e_0) = 1$."""
    quotient = degenerate().radical_quotient()
    assert quotient.module_rank() == 1
    assert quotient.determinant() == 1
    assert quotient.is_nondegenerate()
