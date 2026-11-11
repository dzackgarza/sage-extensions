r"""The discriminant image of a line stabilizer does not depend on the chosen basis (#310).

``stabilizer_discriminant_image()`` computes ``rho(G_L)`` by the action groupoid of
``thm:schreier-discriminant-image`` (dzackgarza/research#750, in
``writing/coble/computations/discriminant-form-descent.md``): over the lattice orbit at
``m = exp(M/L)`` each Schreier factor ``t_(s.p)^-1 s t_p`` contributes the composite of
discriminant isometries between *integral lattice objects*,

    alpha_{t_(s.p)}(L_(s.p))^-1 : A_(L_(s.p)) -> A_L,
    alpha_s(L_p)                : A_(L_p)     -> A_(L_(s.p)),
    alpha_{t_p}(L)              : A_L         -> A_(L_p),

where ``alpha_g(L_0): A_{L_0} -> A_{gL_0}`` is ``[y] |-> [gy]``, the discriminant morphism
of the isometry ``g|_{L_0}: L_0 -> g L_0`` (item 4 of ``thm:discriminant-transport-functor``).

The factors are realized as isometries *between* lattice objects, so the construction reads
the source lattice's own generators and the image module's canonical basis.  The published
specimen, ``U + <-6>`` in its named basis, has an identity image epimorphism at its orbit
points and therefore establishes nothing about that reading.  These tests rebuild the same
lattice in the basis ``w_1 = u_1 + u_2``, ``w_2 = u_2``, ``w_3 = u_3``, which is the same
lattice through an ordinary isometric change of basis and whose orbit points do have a
nonidentity image epimorphism, and they ask for the same three things:

* every orbit point's transporter is an isometry of the two lattice objects, so the
  composite of discriminant isometries the theorem composes is well typed;
* the image equals ``subobject.parabolic_subgroup().image_under(rho)``, the integral
  stabilizer's own discriminant image, in either basis;
* the two images are carried into each other by the change of basis's discriminant
  isometry -- naturality in the lattice variable (``thm:discriminant-transport-functor``),
  which is what a mis-read basis in the middle factor would break.

The discriminant action stays nontrivial in the changed basis: the witness ``id_U + (-id)``
of the named specimen, conjugated by the change of basis, is again an integral isometry
fixing the line and negating every class of ``A_L = Z/6``, where ``Aut(Z/6) = {+-1}``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _named_specimen():
    r"""``U + <-6>`` in its named basis, with its first basis line, which is isotropic."""
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[-6]])
    labels = tuple(lattice.module_generating_set())
    return lattice, labels, lattice.module_generator(labels[0])


def _rebuilt_specimen():
    r"""The same lattice in the basis ``w_1 = u_1 + u_2``, ``w_2 = u_2``, ``w_3 = u_3``."""
    lattice = Lattices(ZZ)([[2, 1, 0], [1, 0, 0], [0, 0, -6]])
    labels = tuple(lattice.module_generating_set())
    line = lattice.linear_combination({labels[0]: ZZ.one(), labels[1]: -ZZ.one()})
    return lattice, labels, line


def _change_of_basis():
    r"""The isometry ``U + <-6> -> `the rebuilt lattice`` the change of basis expresses.

    ``u_1 = w_1 - w_2``, ``u_2 = w_2`` and ``u_3 = w_3``, so this is the identity map of the
    underlying rational space presented in the two bases; it carries the named line onto the
    rebuilt one.
    """
    named, named_labels, _line = _named_specimen()
    rebuilt, rebuilt_labels, _rebuilt_line = _rebuilt_specimen()
    first, second, third = rebuilt_labels
    return named.Isom(rebuilt)(
        {
            named_labels[0]: rebuilt.linear_combination({first: ZZ.one(), second: -ZZ.one()}),
            named_labels[1]: rebuilt.module_generator(second),
            named_labels[2]: rebuilt.module_generator(third),
        }
    )


def _named_graph_character():
    r"""``id_U + (-id)`` on the named lattice: it fixes ``u_1`` and negates ``u_3``."""
    named, named_labels, _line = _named_specimen()

    def image(label):
        if label == named_labels[2]:
            return -named.module_generator(label)
        return named.module_generator(label)

    return named.Aut()({label: image(label) for label in named.module_generating_set()})


def _specimens():
    r"""``(lattice, line, graph character)`` for the named and the rebuilt basis."""
    named, _named_labels, named_line = _named_specimen()
    rebuilt, _rebuilt_labels, rebuilt_line = _rebuilt_specimen()
    basis_change = _change_of_basis()
    witness = _named_graph_character()
    return (
        (named, named_line, witness),
        (rebuilt, rebuilt_line, basis_change * witness * basis_change.inverse()),
    )


def test_the_change_of_basis_is_an_isometry_carrying_one_line_to_the_other() -> None:
    r"""The rebuilt lattice is the same lattice, and the two specimens are one specimen."""
    named, _named_labels, named_line = _named_specimen()
    rebuilt, _rebuilt_labels, rebuilt_line = _rebuilt_specimen()
    basis_change = _change_of_basis()

    assert basis_change in named.Isom(rebuilt)
    assert basis_change(named_line) == rebuilt_line
    assert basis_change.inverse()(rebuilt_line) == named_line
    assert named.q(named_line) == named.base_ring().zero()
    assert rebuilt.q(rebuilt_line) == rebuilt.base_ring().zero()
    # Same form, same discriminant: an ordinary change of basis, not another lattice.
    assert named.is_even() == rebuilt.is_even()
    assert named.discriminant_group().cardinality() == rebuilt.discriminant_group().cardinality()


def test_the_specimens_carry_a_nontrivial_action_and_a_nonidentity_image_epimorphism() -> None:
    r"""Both readings act nontrivially, and one orbit point reads a nonidentity epimorphism.

    The second half is what the published ``U + <-6>`` specimen does not test: with an
    identity image epimorphism at every orbit point, reading the transported source basis as
    the image module's basis gives the same answer as reading the module's own basis.
    """
    for lattice, line, witness in _specimens():
        subobject = lattice.primitive_isotropic_subobject(line)
        image = subobject.stabilizer_discriminant_image()
        rho = lattice.discriminant_representation()
        assert witness(line) == line
        assert rho(witness) in image
        assert any(
            rho(witness)(element) != element for element in lattice.discriminant_group()
        )
        records = subobject.orbit_lattice_records()
        assert any(
            tuple(record["images"]) != tuple(record["module"].module_generators())
            for record in records
        )
        # Every orbit point's transporter joins the two lattice objects it is read on.
        assert all(record["transport"] in lattice.Isom(record["lattice"]) for record in records)


def test_the_image_is_the_integral_parabolic_image_in_either_basis() -> None:
    r"""``rho(G_L)`` equals the integral stabilizer's own discriminant image, in both bases."""
    for lattice, line, _witness in _specimens():
        subobject = lattice.primitive_isotropic_subobject(line)
        image = subobject.stabilizer_discriminant_image()
        reference = subobject.parabolic_subgroup().image_under(
            lattice.discriminant_representation()
        )

        assert image.cardinality() == reference.cardinality()
        assert all(generator in reference for generator in image.group_generators())
        assert all(generator in image for generator in reference.group_generators())


def test_the_image_transports_through_the_change_of_basis() -> None:
    r"""The rebuilt image is the named image conjugated by the change of basis's transport.

    Elementwise: for every generator of the named image there is one of the rebuilt image
    that carries ``transport(x)`` to ``transport(generator(x))`` for every class ``x``, and
    conversely.  A mis-read basis in the middle factor gives a composite that is not a
    conjugate of the integral stabilizer's image, so the two families would not match.
    """
    named, named_line, _named_witness = _specimens()[0]
    rebuilt, rebuilt_line, _rebuilt_witness = _specimens()[1]
    basis_change = _change_of_basis()
    transport = basis_change.discriminant_isometry()
    named_form = named.discriminant_group()
    rebuilt_form = rebuilt.discriminant_group()

    named_image = named.primitive_isotropic_subobject(named_line).stabilizer_discriminant_image()
    rebuilt_image = (
        rebuilt.primitive_isotropic_subobject(rebuilt_line).stabilizer_discriminant_image()
    )
    rebuilt_generators = tuple(rebuilt_image.group_generators())
    named_generators = tuple(named_image.group_generators())

    assert transport.domain() is named_form
    assert transport.codomain() is rebuilt_form
    for generator in named_generators:
        assert any(
            all(
                transport(generator(element)) == candidate(transport(element))
                for element in named_form
            )
            for candidate in rebuilt_generators
        )
    for generator in rebuilt_generators:
        assert any(
            all(
                transport.inverse()(generator(element))
                == candidate(transport.inverse()(element))
                for element in rebuilt_form
            )
            for candidate in named_generators
        )
