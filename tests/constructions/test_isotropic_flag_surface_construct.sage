r"""A primitive isotropic flag retains its lattice, basis, and nested terms."""

from sage_extensions.all import *  # noqa: F401,F403


def _isotropic_line_flag():
    lattice = NamedLattices.U
    isotropic_vector = lattice.module_generators()[0]
    flag = IsotropicFlag(lattice, (isotropic_vector,))
    return lattice, isotropic_vector, flag


def test_isotropic_line_flag_retains_its_lattice_and_basis() -> None:
    lattice, isotropic_vector, flag = _isotropic_line_flag()

    assert flag.lattice() is lattice
    assert tuple(flag.isotropic_basis()) == (isotropic_vector,)
    assert tuple(flag.basis()) == (isotropic_vector,)
    assert flag.rank() == cardinal(1)


def test_isotropic_line_flag_has_one_nested_term() -> None:
    _lattice, _isotropic_vector, flag = _isotropic_line_flag()
    terms = tuple(flag.terms())

    assert flag.flag_length() == 1
    assert len(terms) == 1
    assert flag.top() is terms[0]
