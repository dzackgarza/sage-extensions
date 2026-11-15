r"""One datum, one object: the embedded framing a subobject records.

A subobject of a module records its chosen inclusion, and the embedded framing
is the family of the images of its generators in the ambient module.  Both are
data of the subobject alone -- ``inclusion`` already answers with one stored
monomorphism ("Return the chosen monomorphism represented by constructor
data") -- so a reader asking twice is asking about one family, not building a
second one:

    plane.embedded_module_generators() is plane.embedded_module_generators()
    False                                (before the repair: a new family, and a
                                          new image of every generator, per call)

The transport of a plane asks for it once per construction, and the census that
found this priced the plane's transport at 10.59 ms with 20 indexed families
built inside it, so the framing was being rebuilt while the inclusion it is built
from was not.

The tests pin the identity and pin the datum: the family is the images of the
generators under the stored inclusion, not a second construction that happens to
print the same.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _plane_of_two_hyperbolic_planes():
    r"""The plane spanned by one isotropic generator of each ``U`` summand."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    labels = tuple(lattice.module_generating_set())
    plane = lattice.primitive_isotropic_subobject(
        lattice.module_generator(labels[1]), lattice.module_generator(labels[2])
    )
    return lattice, plane


def test_the_embedded_framing_of_a_subobject_is_one_family() -> None:
    r"""Asked twice, a subobject's embedded framing is the family it built once."""
    lattice, plane = _plane_of_two_hyperbolic_planes()

    assert plane.embedded_module_generators() is plane.embedded_module_generators()


def test_the_embedded_framing_is_the_images_under_the_stored_inclusion() -> None:
    r"""The framing's points are the generator images, so the two routes agree."""
    lattice, plane = _plane_of_two_hyperbolic_planes()
    inclusion = plane.inclusion()

    assert tuple(plane.embedded_module_generators().values()) == tuple(
        inclusion(plane.module_generator(label))
        for label in plane.module_generating_set()
    )
    assert all(
        vector.parent() is lattice
        for vector in plane.embedded_module_generators().values()
    )
