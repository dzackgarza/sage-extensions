r"""The group that ``Stab_\Gamma(v)`` induces on ``v^\perp/<v>``, at Sterk's five Enriques cusps.

``T_{\mathrm{En}} = U \oplus U(2) \oplus E_8(-2)`` is the Enriques period lattice
(rank 12, signature ``(2, 10)``, ``|det| = 1024``), and ``\Gamma_{\mathrm{En},2}``
is H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*,
Math. Z. 207 (1991), 1--36, Proposition 2.7, p. 6 -- the group whose five
``0``-cusps are Proposition 4.2.3 with Remark 4.2.4, p. 16.  Its five cusp
representatives are ``Sterk.selected_isotropic_vectors()``, and at each one
``V. Alexeev, P. Engel, D. Z. Garza, L. Schaffler, *Compact moduli of Enriques
surfaces of degree 2*, Nagoya Math. J. 259 (2025), §3.3, p. 590`` counts five
``0``-cusps of ``F_{En,2}``.

For a primitive isotropic ``v`` the group that the stabilizer induces on
``N = v^\perp/\mathbf Z v`` is the image of ``\Gamma_{\mathrm{En},2} \cap P_v``
under the Levi map ``P_v \to O(N)`` (Dutour Sikirić--Hulek, arXiv:2302.01679v2,
theorem `theorem_isotropic_k_planes`, printed p. 22).  An isometry of ``N`` has
many lifts in ``P_v`` and two differ by an element of the kernel ``K_v``, so
membership is decided on the discriminant image: ``\sigma`` is in the image when
``\rho`` of one lift lies in ``\rho(K_v)\rho(\Gamma)``.  ``K_v`` contains the
Eichler transvections ``t(v, a)``, ``a \perp v`` (Gritsenko--Hulek--Sankaran,
arXiv:0810.1614, §3.1, equation (4)); their image ``\rho(K_v)`` is an output of
the call, and at all five cusps here it is trivial.

The wall counts Sterk publishes for the cusp diagrams (4.3.5--4.3.9) are the
sizes of ``Sterk.sterk_roots()``: twelve, ten, twelve, eleven and fourteen roots
for the five cusps.  What is asserted below is the stronger statement at the
three cusps whose printed roots the library holds in ``T_{\mathrm{En}}``
coordinates: *every* one of those roots' reflections lies in the image, decided
by the discriminant criterion and not by one lift each.  The chamber of that
reflection subgroup -- the wall count itself -- is #297's call.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _gamma_en_2():
    r"""``\Gamma_{En,2}`` on ``T_En``, by the construction of #286 item 2.

    The group is the coinvariant extension subgroup of the degree-two
    polarization of the Enriques involution: Alexeev--Engel--Garza--Schaffler,
    Nagoya Math. J. 259 (2025), Definition 2.6, and Sterk, Proposition 2.7,
    p. 6.  It is built here by that construction and never from a description of
    its image in ``O(A_L)``.
    """
    invariant = Involutions.I_En.invariant_lattice()
    labels = tuple(invariant.module_generating_set())
    marks = [
        (left, right)
        for left in labels
        for right in labels
        if left <= right
        and invariant.q(invariant.module_generator(left)) == ZZ.zero()
        and invariant.q(invariant.module_generator(right)) == ZZ.zero()
        and invariant.b(invariant.module_generator(left), invariant.module_generator(right)) == ZZ(2)
    ]
    left, right = marks[0]
    polarization = invariant.module_generator(left) + invariant.module_generator(right)
    return Involutions.I_En.polarized(invariant.inclusion()(polarization)).coinvariant_extension_subgroup()


def _cusp_images():
    r"""One reduction image per cusp of ``\Gamma_{En,2}``, keyed by Sterk's label."""
    subgroup = _gamma_en_2()
    return {
        name: subgroup.isotropic_vector_reduction_image(vector)
        for name, vector in Sterk.selected_isotropic_vectors().items()
    }


def test_each_cusp_reduces_to_a_hyperbolic_rank_ten_lattice() -> None:
    r"""``v^\perp/\mathbf Z v`` has rank ``10`` and signature ``(1, 9)``, and is even.

    The determinants separate the first cusp from the other four: ``1024`` for
    ``Sterk_1``, whose vector is the generator ``e`` of the unimodular plane of
    ``T_{\mathrm{En}}``, and ``256`` for the four whose vectors carry a
    divisibility two factor.  Both are read off the lattice, not from a table.
    """
    images = _cusp_images()
    determinants = {
        "Sterk_1": ZZ(-1024),
        "Sterk_2": ZZ(-256),
        "Sterk_3": ZZ(-256),
        "Sterk_4": ZZ(-256),
        "Sterk_5": ZZ(-256),
    }

    assert sorted(images) == ["Sterk_1", "Sterk_2", "Sterk_3", "Sterk_4", "Sterk_5"]
    for name, image in images.items():
        reduction = image.reduction()
        signature = reduction.signature_pair()
        assert reduction.module_rank() == cardinal(10)
        assert (int(signature.first()), int(signature.second())) == (1, 9)
        assert reduction.is_even() is True
        assert reduction.determinant() == determinants[name]
        assert image.lattice().q(image.vector()) == ZZ.zero()
        assert image.vector().is_primitive() is True


def test_the_kernel_of_the_levi_map_acts_trivially_on_the_discriminant_group() -> None:
    r"""``\rho(K_v)`` is trivial at every cusp, so one lift does decide membership there.

    ``K_v`` contains one Eichler transvection per basis vector of ``v^\perp``,
    eleven of them at each cusp (``v^\perp`` has rank eleven), and each is
    returned only after being checked to fix ``v`` and to act trivially on
    ``N``.  Their discriminant images generate ``\rho(K_v)``
    (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §3.1, equation (4)--(5)), and
    here that image is the trivial group, which is the output the membership
    criterion needs and is not assumed.
    """
    for name, image in _cusp_images().items():
        transvections = image.kernel_transvections()
        assert cardinal(sum(1 for _ in transvections)) == cardinal(11)
        for transvection in transvections:
            assert transvection(image.vector()) == image.vector()
        assert image.kernel_discriminant_image_is_trivial() is True
        assert image.kernel_discriminant_image().cardinality() == cardinal(1)


def test_sterks_published_cusp_roots_are_reflections_of_the_stabilizer_image() -> None:
    r"""Every printed root of the cusps ``1``--``3`` is a reflection in the image.

    Sterk's diagrams 4.3.5--4.3.9 for the five cusps have twelve, ten, twelve,
    eleven and fourteen walls; the library's transcription
    ``Sterk.sterk_roots()`` holds those families, and for the first three cusps
    also in ``T_{\mathrm{En}}`` coordinates (``Sterk.sterks_in_TEn()``).  For
    each of those the reflection of ``T_{\mathrm{En}}`` in the root fixes ``v``,
    so it induces a reflection of ``N``, and the discriminant criterion decides
    that reflection's membership -- exactly, not by exhibiting one lift.
    """
    images = _cusp_images()
    transcribed = Sterk.sterks_in_TEn()
    diagrams = Sterk.sterk_roots()

    assert sorted(transcribed) == ["Sterk_1", "Sterk_2", "Sterk_3"]
    assert cardinal(sum(1 for _ in diagrams["Sterk_1"])) == cardinal(12)
    assert cardinal(sum(1 for _ in diagrams["Sterk_2"])) == cardinal(10)
    assert cardinal(sum(1 for _ in diagrams["Sterk_3"])) == cardinal(12)
    for name, family in transcribed.items():
        roots = tuple(family)
        image = images[name]
        reflections = image.reflection_generators(roots)
        assert cardinal(sum(1 for _ in roots)) == cardinal(sum(1 for _ in diagrams[name]))
        assert tuple(root for root, _ in reflections) == roots
        assert image.generators_are_certified_complete() is False
