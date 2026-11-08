r"""The exact discriminant image of an integral isotropic-line stabilizer (#310).

``stabilizer_discriminant_image()`` computes ``rho(G_L)`` by the action-groupoid
construction of ``thm:schreier-discriminant-image``: over the lattice orbit at
``m = exp(M/L)``, each Schreier factor ``t_(s.p)^-1 s t_p`` contributes the
composite of discriminant transports between integral lattice objects,

    Disc(t_(s.p)^-1) : A_(L_(s.p)) -> A_L,   Disc(s) : A_(L_p) -> A_(L_(s.p)),
    Disc(t_p) : A_L -> A_(L_p),

so no individual letter is applied to ``A_L`` and no rational transporter is
assumed to preserve ``L``.

Specimen: ``L = U + <-6>``, discriminant ``Z/6``, with the isotropic line spanned
by the first ``U`` basis vector.  The isometry ``id_U + (-id)`` on ``<-6>`` fixes
that line and acts by ``x |-> -x`` on ``A_L``, which is nontrivial because
``Aut(Z/6) = {+-1}``.  This lattice therefore distinguishes a correct image from a
trivial one, unlike a discriminant group of order two, where ``Aut(Z/2)`` is
trivial and every image is trivial.

The real sign character is carried separately, as the theorem requires.  The
isometry above is *not* a kernel-sign witness: it has nontrivial determinant and
nontrivial discriminant image at once, so it is a graph character and must never
certify the sign flip that ``splitting_isometries_from_line_class`` consumes.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[-6]])
    labels = tuple(lattice.module_generating_set())
    line = lattice.module_generator(labels[0])
    subobject = lattice.primitive_isotropic_subobject(line)
    return lattice, labels, line, subobject


def _minus_on_the_negative_plane(lattice, labels):
    r"""``id_U + (-id)`` on ``U + <-6>``: fixes the first ``U`` basis vector."""

    def image(label):
        if label == labels[2]:
            return -lattice.module_generator(label)
        return lattice.module_generator(label)

    return lattice.Aut()(
        {label: image(label) for label in lattice.module_generating_set()}
    )


def test_the_graph_character_acts_nontrivially_on_the_discriminant() -> None:
    r"""The specimen's witness fixes the line and negates one class of order six."""

    lattice, labels, line, subobject = _specimen()
    assert lattice.discriminant_group().cardinality() == cardinal(6)
    witness = _minus_on_the_negative_plane(lattice, labels)
    assert witness(line) == line
    rho = lattice.discriminant_representation()
    for candidate in lattice.discriminant_group():
        assert rho(witness)(candidate) == -candidate
    assert rho(witness) != lattice.discriminant_group().orthogonal_group().one()


def test_the_groupoid_image_is_the_integral_stabilizer_image() -> None:
    r"""The constructed exact image equals the image of the stabilizer's own generators."""

    lattice, labels, line, subobject = _specimen()
    witness = _minus_on_the_negative_plane(lattice, labels)
    rho = lattice.discriminant_representation()

    image = subobject.stabilizer_discriminant_image()
    assert image.cardinality() == cardinal(2)
    assert rho(witness) in image

    reference = subobject.parabolic_subgroup().image_under(rho)
    assert image.cardinality() == reference.cardinality()
    assert all(generator in reference for generator in image.group_generators())
    assert all(generator in image for generator in reference.group_generators())


def test_the_graph_character_is_not_a_kernel_sign_witness() -> None:
    r"""Nontrivial determinant *and* nontrivial discriminant image: not a kernel element."""

    lattice, labels, line, subobject = _specimen()
    witness = _minus_on_the_negative_plane(lattice, labels)
    assert witness.determinant() == lattice.base_ring()(-1)
    rho = lattice.discriminant_representation()
    assert rho(witness) != lattice.discriminant_group().orthogonal_group().one()
