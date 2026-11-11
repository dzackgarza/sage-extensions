r"""The unipotent radical of the parabolic at a plane, checked on its own generators (#337).

The radical is $U_I = \ker(P_I \to \mathrm{GL}(I) \times O(I^\perp/I))$, so an element is
in it exactly when it fixes every vector of the plane and acts as the identity on
$I^\perp/I$.  `unipotent_radical_generators` returned the parabola's Eichler
transvections $E_{p,x}$, and an Eichler transvection with $x \perp p$ fixes `p`, acts
trivially on $I^\perp/I$, and *moves the plane*:

$$E_{p,x}(p') = p' + b(p',x)\,p,$$

which is $p'$ only when $b(p',x) = 0$ for every $p'$ in the plane's basis.  So the family
is a subgroup of the parabolic and not of its radical, and the issue is that the method
carries the radical's name.  At Sterk's $P_2$ of $T_{\mathrm{En}}$ this is red: 21
transvections are returned and 7 of them move the plane.

Both properties are asked of the returned elements, in the order the two definitions are
stated, and neither is read off the construction that produced them.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _second_representative(lattice):
    r"""Sterk's $P_2 = \mathbb{Z}(2e_1 + 2e_2 + w) + \mathbb{Z}e_3$, $w$ of norm $-8$ (Math. Z. 207 (1991), Prop. 4.6, p. 29)."""
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    assert lattice.q(w) == ZZ(-8)
    return lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third)


def test_every_unipotent_radical_generator_fixes_the_plane_pointwise() -> None:
    r"""$g(p) = p$ for both generators $p$ of the plane, for every returned element."""
    lattice = NamedLattices.TEn
    plane = _second_representative(lattice)
    returned = plane.unipotent_radical_generators()

    assert returned != ()
    for element in returned:
        for vector in plane.plane_basis():
            assert element(vector) == vector


def test_every_unipotent_radical_generator_acts_trivially_on_the_quotient() -> None:
    r"""$(g - 1)(P^\perp) \subseteq P$, for every returned element."""
    lattice = NamedLattices.TEn
    plane = _second_representative(lattice)
    returned = plane.unipotent_radical_generators()

    assert returned != ()
    for element in returned:
        assert plane.acts_trivially_on_isotropic_reduction(element) is True
