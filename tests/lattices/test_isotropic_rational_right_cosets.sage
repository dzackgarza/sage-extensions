r"""Right cosets of the rational stabilizer of a null line and of a flag.

On U+<-2> let e,f span U and q(x)=-2. The extension of x -> x+k*e fixing e
sends f to f+(k/2)x+(k^2/4)e, which is integral exactly for even k. The
pointwise kernel of a null line in this rank is trivial, so |G/H| = 2.

On U+U+<-2> with the flag <e1> < <e1,e2>, the shear extension has
coefficient k^2/4, so the source's common denominator is d=4 and the
rational group contains f1 -> f1+c*e2, f2 -> f2-c*e1 for c in (1/4)Z.
G maps onto (k1,k2) mod 2 and the kernel of that map contains H with
index |(1/4)Z / Z| = 4, so |G/H| = 16.
"""

from sage_extensions.all import *


def _lattice(hyperbolic_summands):
    lattices = Lattices(ZZ)
    ambient = lattices("A1")
    for _ in range(hyperbolic_summands):
        ambient = lattices("U") + ambient
    return ambient


def _generators(ambient):
    return tuple(ambient.module_generators())


def test_null_line_rational_stabilizer_has_two_cosets():
    ambient = _lattice(1)
    e, f, x = _generators(ambient)
    assert ambient.q(e) == 0 and ambient.b(e, f) == 1 and ambient.q(x) == -2
    subobject = ambient.primitive_isotropic_subobject(e)
    assert subobject.rational_stabilizer_right_cosets().cardinality() == cardinal(2)


def test_null_flag_rational_stabilizer_has_sixteen_cosets():
    from sage_extensions.categories.isotropic_orbits import IsotropicFlag

    ambient = _lattice(2)
    e1, _f1, e2, _f2, _x = _generators(ambient)
    flag = IsotropicFlag(ambient, (e1, e2))
    assert flag.rational_stabilizer_right_cosets().cardinality() == cardinal(16)
