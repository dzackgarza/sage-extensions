r"""The orbit lattice basis identification in the action-groupoid image (#286).

``image_factorization`` presents the image of ``t_p: L -> V`` in the *span's*
canonical basis (``_restricted_fraction_field_subobject_on`` uses
``engine_span.basis()``), which is not the image of ``L``'s own generator basis.
Measured on this specimen, the epimorphism is the identity at orbit point 0 and
nonidentity at every other point, for example

    [[12,-1,-2],[1,0,0],[12,-1,-1]]  at point 1 of six.

So the two structures on the same underlying module must be told apart, and each
map is asserted through the square it has to satisfy:

    inclusion_p * transport_p == wrap * t_p * inclusion        (domain L)
    inclusion_(s.p) * middle_(p,s) == wrap * s * inclusion_p   (domain L_p)

with the second read on ``L_p``'s *own* generators.  Reading it on the
transported source basis instead applies the epimorphism a second time; on this
specimen that gives a different map for 6 of the 18 (orbit point, letter) pairs,
so the two squares below separate the two readings.

The two maps agree as subgroups on these small lattices even where they differ as
maps, which is why the squares, and not the group order, are the assertion here.
``A_L`` is ``Z/6``, whose quadratic orthogonal group is
``{u : u^2 = 1 mod 12} = {1,5,7,11}``; the constructed image is its order-two
subgroup ``{1,5}``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[-6]])
    labels = tuple(lattice.module_generating_set())
    line = lattice.module_generator(labels[0])
    subobject = lattice.primitive_isotropic_subobject(line)
    return lattice, labels, subobject


def _module_image_of(record, element):
    r"""Read an element of the orbit lattice as the same element of the module image.

    The two structures share the framing, so the coefficients transfer label for
    label; the inclusion of the record is stated on the module image.
    """
    read = element.to_vector()
    return record["module"].linear_combination(
        {
            module_label: read(lattice_label)
            for module_label, lattice_label in zip(
                record["module_labels"], record["lattice_labels"], strict=True
            )
            if read(lattice_label)
        }
    )


def test_a_transport_commutes_with_the_transported_generators() -> None:
    r"""``inclusion_p * transport_p == wrap * t_p * inclusion`` on ``L``'s generators."""

    lattice, labels, subobject = _specimen()
    _letters, transversals = subobject.stabilizer_schreier_factors()
    ambient = subobject.ambient_lattice()
    records = subobject.orbit_lattice_records()

    # ``strict=True`` is the assertion that the records are one per orbit point.
    for record, transporter in zip(records, tuple(transversals), strict=True):
        # Both sides are read as elements their own owners produced: the transport
        # of a source generator *is* the lattice element with that generator's
        # module coordinates, and the transporter acts on the recorded space image.
        for index, _label in enumerate(record["source_labels"]):
            through_transport = record["inclusion"](
                record["images"][index]
            ).underlying_element()
            direct = transporter(record["space_images"][index])
            assert through_transport == direct


def test_a_middle_transport_commutes_on_the_image_module_own_basis() -> None:
    r"""``inclusion_(s.p) * middle == wrap * s * inclusion_p`` on ``L_p``'s generators.

    The middle map's domain is the orbit lattice ``L_p``, whose generators are the
    image module's canonical basis; reading the transported source basis here
    instead is a different map whenever the epimorphism is not the identity.
    """

    lattice, labels, subobject = _specimen()
    letters, _transversals = subobject.stabilizer_schreier_factors()
    ambient = subobject.ambient_lattice()
    records = subobject.orbit_lattice_records()

    for position, record in enumerate(records):
        for letter in tuple(letters):
            middle = subobject.middle_transport(position, letter)
            target = next(
                record
                for record in records
                if record["lattice"] is middle.codomain()
            )
            assert middle.domain() is record["lattice"]
            assert middle.codomain() is target["lattice"]
            for index, label in enumerate(record["lattice_labels"]):
                basis_element = record["module"].module_generator(
                    record["module_labels"][index]
                )
                through_middle = target["inclusion"](
                    _module_image_of(
                        target, middle(record["lattice"].module_generator(label))
                    )
                ).underlying_element()
                direct = letter(record["inclusion"](basis_element).underlying_element())
                assert through_middle == direct


def test_the_constructed_image_is_the_parabolic_image() -> None:
    r"""The exact image equals the image of the integral parabolic ``Stab_{O(L)}(<e_1>)``."""

    lattice, labels, subobject = _specimen()
    assert lattice.discriminant_group().cardinality() == cardinal(6)

    image = subobject.stabilizer_discriminant_image()
    reference = subobject.parabolic_subgroup().image_under(
        lattice.discriminant_representation()
    )
    assert image.cardinality() == cardinal(2)
    assert image.cardinality() == reference.cardinality()
    assert all(generator in reference for generator in image.group_generators())
    assert all(generator in image for generator in reference.group_generators())
