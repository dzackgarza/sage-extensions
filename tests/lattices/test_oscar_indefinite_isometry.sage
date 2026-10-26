r"""An isometry between two presentations of an indefinite lattice."""

from sage_extensions.all import *


def test_u_plus_minus_two_is_isometric_to_its_skewed_presentation() -> None:
    r"""\(\begin{psmallmatrix}0&1\\1&2\end{psmallmatrix}\cong U\): with basis \(e,f\)
    of the former, \(e\) and \(f-e\) satisfy \(e^2=0\), \((f-e)^2=2-2=0\),
    \(e\cdot(f-e)=1\).  Adding \(\langle-2\rangle\) to both sides preserves this.
    """
    source = Lattices(ZZ)([[0, 1, 0], [1, 0, 0], [0, 0, -2]])
    target = Lattices(ZZ)([[0, 1, 0], [1, 2, 0], [0, 0, -2]])

    assert not source.is_definite()
    assert source.is_isometric_to(target)
    isometry = source.isometry_to(target)
    assert all(
        target.b(isometry(left), isometry(right)) == source.b(left, right)
        for left in source.module_generators()
        for right in source.module_generators()
    )
    assert (~isometry) * isometry == source.identity_morphism()
