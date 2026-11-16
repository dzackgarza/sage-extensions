r"""Transporting a primitive isotropic plane builds the span of its image once.

An isometry carries a plane \(P\) to the plane spanned by the images of its
basis, and the transported plane is admitted by `primitive_isotropic_subobject`:
that constructor builds the span, verifies isotropy and primitivity, and places
the result in the lattice category the parabolic and reduction methods live on.

A morphism image on the way to it would build the same span -- its Hermite form
and its restricted Gram, in a category of its own -- a second time, and the
transported plane reads nothing from it but the images of the basis.  The span
computed there answers a question nobody asks, and the plane rows pay it once
per plane.  The count below is the number of spans one transport builds.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_transporting_a_plane_builds_its_span_once() -> None:
    r"""One span per transport, and the plane it returns is the image of the basis.

    \(U\oplus U\) has basis \(e_1,f_1,e_2,f_2\) with \(b(e_i,f_i)=1\) and
    \(q(e_i)=q(f_i)=0\).  Both \(\langle e_1,f_2\rangle\) and its image under
    the summand swap \(\langle e_2,f_1\rangle\) are primitive totally isotropic
    planes, and \(e_1\) lies in the first and not in the second.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    e1, f1, e2, f2 = lattice.module_generators()
    plane = lattice.primitive_isotropic_subobject(e1, f2)
    images = {0: e2, 1: f2, 2: e1, 3: f1}
    isometry = lattice.Isom(lattice)(lambda label: images[int(label)])

    constructing = Lattices(ZZ).ParentMethods
    original = constructing.subobject_on
    built = []

    def counted(self, generating_set):
        built.append(1)
        return original(self, generating_set)

    constructing.subobject_on = counted
    moved = isometry.transport_isotropic_object(plane)
    constructing.subobject_on = original

    assert tuple(built) == (1,)
    assert moved.is_primitive()
    assert isometry(e1) in moved and isometry(f2) in moved
    assert e1 not in moved
