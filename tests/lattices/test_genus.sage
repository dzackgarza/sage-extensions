from sage_extensions.all import *


def test_level_uses_the_quadratic_discriminant_form_for_even_lattices() -> None:
    lattice = Lattices(ZZ)([[2]])

    assert lattice.discriminant_module().exponent() == 2
    assert lattice.level() == 4


def test_level_of_an_odd_lattice_is_the_bilinear_level() -> None:
    lattice = Lattices(ZZ)([[3]])

    assert not lattice.is_even()
    assert lattice.discriminant_module().exponent() == 3
    assert lattice.level() == 3


def test_unimodular_even_lattice_has_level_one() -> None:
    lattice = Lattices(ZZ)("E8")

    assert lattice.is_even() and lattice.is_unimodular()
    assert lattice.level() == 1


def test_genus_of_a2_is_determined_by_signature_and_discriminant_form() -> None:
    r"""An even lattice's genus is fixed by its signature and discriminant
    quadratic form (Nikulin 1979, Cor. 1.9.4); ``A2`` is negative definite of
    determinant ``3``.
    """
    lattice = Lattices(ZZ)("A2")
    genus = Lattices(ZZ).genus(signature_pair(0, 2), lattice.discriminant_quadratic_form())

    assert genus == lattice.genus()
    assert genus.determinant() == 3
    assert genus != Lattices(ZZ)([[-2, 0], [0, -2]]).genus()


def test_local_genus_symbol_and_excess_detect_nonisometry() -> None:
    a2 = Lattices(ZZ)("A2")
    diagonal = Lattices(ZZ)([[-2, 0], [0, -2]])
    genus = a2.genus()

    assert genus.level(3) == 3
    assert genus.excess(3) == 2
    assert a2.is_locally_isometric(a2, 3)
    assert not a2.is_locally_isometric(diagonal, 3)


def test_definite_genus_mass_and_class_number_are_exact() -> None:
    genus = Lattices(ZZ)("A2").genus()

    assert genus.class_number() == 1
    assert genus.representatives().cardinality() == 1
    assert genus.mass() == ZZ(1) / 12


def test_indefinite_isotropic_genus_has_complete_spinor_seed_enumeration() -> None:
    r"""For an isotropic indefinite lattice of rank at least three, each spinor
    genus contains one class (Conway--Sloane, *Sphere Packings, Lattices and Groups*,
    3rd ed., Ch. 15, §9.1, Thm. 14).  This isotropic ternary specimen has trivial
    improper spinor quotient, so the complete seed list is empty and the genus
    enumeration must return its single class.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 4, 0], [0, 0, -5]])
    genus = lattice.genus()

    assert lattice.signature_pair() == signature_pair(2, 1)
    assert lattice([1, 1, 1]).norm() == 0
    assert genus.spinor_genus_count() == 1
    assert genus.class_number() == 1
    assert genus.representatives().cardinality() == 1
    assert tuple(lattice.spinor_genus_class_numbers()) == (ZZ(1),)


def test_published_four_spinor_genus_is_counted_from_all_generators() -> None:
    r"""Benham--Hsia, *On spinor exceptional representations*, Nagoya Math. J.
    87 (1982), §2.3, p. 252, identify ``diag(1, 20, 400)`` as a genus with four
    spinor genera and twelve classes.  This checks the public consumer of Sage's
    spinor-generator list against the independent four-way partition.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 20, 0], [0, 0, 400]])
    genus = lattice.genus()

    # The improper spinor quotient is C2 x C2, not cyclic.  Its generating
    # list must therefore contain two independent prime classes; merely
    # counting the spinor genera below can otherwise obscure a regression in
    # how the quotient's generated subgroup is accumulated.
    # Exercise Sage's maintained public Genus constructor directly, using the
    # same owned-tensor-to-Sage-matrix boundary as the production adapter.
    from sage.rings.integer_ring import ZZ as SageZZ
    from sage.quadratic_forms.genera.genus import Genus as SageGenus
    from sage_extensions.tensors.tensor import _engine_component_matrix

    sage_genus = SageGenus(
        _engine_component_matrix(lattice.gram_tensor()).change_ring(SageZZ)
    )
    spinor_primes = sage_genus.spinor_generators(proper=False)
    # The independent kernel computation gives an improper quotient of order
    # four. Check that the returned prime classes span it, without requiring
    # a particular valid choice of prime representatives.
    spinor_operators, kernel = sage_genus._improper_spinor_kernel()
    quotient = spinor_operators.quotient(kernel)
    assert quotient.order() == 4
    # Independently checked prime classes [3, 11] generate this C2 x C2
    # quotient; this fixes the expected quotient rather than only its order.
    independent_classes = tuple(
        quotient(spinor_operators.delta(prime)) for prime in (ZZ(3), ZZ(11))
    )
    assert tuple(g.order() for g in independent_classes) == (2, 2)
    assert independent_classes[0] != independent_classes[1]
    assert quotient.subgroup(independent_classes).order() == 4
    assert Set(spinor_primes).cardinality() == 2
    assert all(not prime.divides(sage_genus.determinant()) for prime in spinor_primes)
    accumulated = quotient.subgroup([])
    expected_orders = (1, 2, 4)
    assert accumulated.order() == expected_orders[0]
    for step, prime in enumerate(spinor_primes, start=1):
        prime_class = quotient(spinor_operators.delta(prime))
        assert prime_class.order() == 2
        # Each update must retain the previously accumulated subgroup and add
        # a genuinely independent coset, not merely reproduce an earlier one.
        accumulated = quotient.subgroup((prime_class,) + accumulated.gens())
        assert accumulated.order() == expected_orders[step]
    assert accumulated.order() == quotient.order()
    prime_classes = {
        quotient(spinor_operators.delta(prime)) for prime in spinor_primes
    }
    assert len(prime_classes) == 2

    # The proper and improper quotients have the same order here, but their
    # operator groups and kernels are distinct. Check the proper public
    # generator list against its own independently computed quotient too.
    proper_primes = sage_genus.spinor_generators(proper=True)
    proper_operators, proper_kernel = sage_genus._proper_spinor_kernel()
    proper_quotient = proper_operators.quotient(proper_kernel)
    assert proper_quotient.order() == 4
    assert Set(proper_primes).cardinality() == 2
    assert all(not prime.divides(sage_genus.determinant()) for prime in proper_primes)
    proper_generated = proper_quotient.subgroup([])
    assert proper_generated.order() == 1
    for step, prime in enumerate(proper_primes, start=1):
        prime_class = proper_quotient(proper_operators.delta(prime))
        assert prime_class.order() == 2
        proper_generated = proper_quotient.subgroup(
            (prime_class,) + proper_generated.gens()
        )
        assert proper_generated.order() == (2, 4)[step - 1]
    assert proper_generated.order() == proper_quotient.order()
    assert lattice.spinor_genus_count() == 4
    assert genus.class_number() == 12
    representatives = genus.representatives()
    assert representatives.cardinality() == 12
    assert all(
        Lattices(ZZ)(representative) in genus for representative in representatives
    )
    # The public contract puts the input lattice's improper spinor genus first;
    # class count alone would not detect a wrong initial seed.
    assert Lattices(ZZ)(representatives[0]).is_isometric(lattice)
    # Check the claimed class count against the public isometry decision, not
    # just the representative container's length.
    for i, representative in enumerate(representatives):
        for other in representatives[i + 1 :]:
            assert not Lattices(ZZ)(representative).is_isometric(
                Lattices(ZZ)(other)
            )
    assert genus.mass() == QQ(3) / 2
    # Independently sum reciprocal automorphism-group orders over the public
    # representative list, rather than relying only on Sage's genus mass.
    from sage.quadratic_forms.quadratic_form import QuadraticForm
    from sage.rings.integer_ring import ZZ as SageZZ
    from sage_extensions.tensors.tensor import _engine_component_matrix

    assert sum(
        QQ.one()
        / QuadraticForm(
            SageZZ,
            2
            * _engine_component_matrix(representative.gram_tensor()).change_ring(
                SageZZ
            ),
        ).automorphism_group().order()
        for representative in representatives
    ) == QQ(3) / 2
    numbers = lattice.spinor_genus_class_numbers()
    assert numbers.cardinality() == 4
    assert tuple(sorted(numbers)) == (ZZ(3), ZZ(3), ZZ(3), ZZ(3))
    assert sum(numbers) == 12


def test_indefinite_genus_enumerates_each_nontrivial_spinor_seed() -> None:
    r"""The isotropic ternary lattice ``diag(1, 20, -400)`` has improper
    spinor quotient of order two.  Conway--Sloane, *Sphere Packings, Lattices
    and Groups*, 3rd ed., Ch. 15, §9.1, Thm. 14, says each spinor genus of an
    isotropic indefinite lattice of rank at least three is one class; hence
    this genus has exactly two.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 20, 0], [0, 0, -400]])
    genus = lattice.genus()

    assert lattice.signature_pair() == signature_pair(2, 1)
    assert lattice([20, 0, 1]).norm() == 0
    assert genus.spinor_genus_count() == 2
    from sage.rings.integer_ring import ZZ as SageZZ
    from sage.quadratic_forms.genera.genus import Genus as SageGenus
    from sage_extensions.tensors.tensor import _engine_component_matrix

    sage_genus = SageGenus(
        _engine_component_matrix(lattice.gram_tensor()).change_ring(SageZZ)
    )
    spinor_primes = sage_genus.spinor_generators(proper=False)
    spinor_operators, kernel = sage_genus._improper_spinor_kernel()
    quotient = spinor_operators.quotient(kernel)
    assert quotient.order() == 2
    assert Set(spinor_primes).cardinality() == 1
    accumulated = quotient.subgroup([])
    assert accumulated.order() == 1
    for prime in spinor_primes:
        prime_class = quotient(spinor_operators.delta(prime))
        assert prime_class.order() == 2
        accumulated = quotient.subgroup((prime_class,) + accumulated.gens())
        assert accumulated.order() == 2
    assert accumulated.order() == quotient.order()
    assert genus.class_number() == 2
    representatives = genus.representatives()
    assert representatives.cardinality() == 2
    assert all(
        Lattices(ZZ)(representative) in genus for representative in representatives
    )
    first, second = representatives
    assert Lattices(ZZ)(first).is_isometric(lattice)
    assert not Lattices(ZZ)(first).is_isometric(Lattices(ZZ)(second))
    assert tuple(lattice.spinor_genus_class_numbers()) == (ZZ(1), ZZ(1))


def test_indefinite_signature_does_not_imply_rational_isotropy() -> None:
    r"""Real indefiniteness does not imply rational isotropy.

    For ``x^2 + y^2 = 3 z^2``, reduction modulo 3 forces ``x`` and ``y``
    to be divisible by 3; substitution then forces ``z`` to be divisible by
    3.  Thus ``diag(1, 1, -3)`` has no nonzero rational isotropic vector,
    despite having real signature ``(2, 1)``.
    """
    lattice = Lattices(ZZ)([[1, 0, 0], [0, 1, 0], [0, 0, -3]])

    assert lattice.signature_pair() == signature_pair(2, 1)
    assert lattice.is_isotropic() is False
    genus = lattice.genus()
    from sage.rings.integer_ring import ZZ as SageZZ
    from sage.quadratic_forms.genera.genus import Genus as SageGenus
    from sage_extensions.tensors.tensor import _engine_component_matrix

    sage_genus = SageGenus(
        _engine_component_matrix(lattice.gram_tensor()).change_ring(SageZZ)
    )
    spinor_primes = sage_genus.spinor_generators(proper=False)
    spinor_operators, kernel = sage_genus._improper_spinor_kernel()
    quotient = spinor_operators.quotient(kernel)
    quotient_order = quotient.order()
    accumulated = quotient.subgroup([])
    for prime in spinor_primes:
        prime_class = quotient(spinor_operators.delta(prime))
        assert not prime.divides(sage_genus.determinant())
        previous_order = accumulated.order()
        accumulated = quotient.subgroup((prime_class,) + accumulated.gens())
        assert accumulated.order() > previous_order
    assert accumulated.order() == quotient_order
    # Hanke, Theorem 3.5.1, applies to indefinite integral forms in rank >= 3
    # without a rational-isotropy hypothesis: one class lies in each spinor genus.
    assert genus.spinor_genus_count() == quotient_order
    assert genus.class_number() == genus.spinor_genus_count()
    representatives = genus.representatives()
    assert representatives.cardinality() == genus.spinor_genus_count()
    assert all(
        Lattices(ZZ)(representative) in genus for representative in representatives
    )
    assert Lattices(ZZ)(representatives[0]).is_isometric(lattice)
    assert genus.class_number() == quotient_order
    for i, representative in enumerate(representatives):
        for other in representatives[i + 1 :]:
            assert not Lattices(ZZ)(representative).is_isometric(
                Lattices(ZZ)(other)
            )
    assert tuple(lattice.spinor_genus_class_numbers()) == tuple(
        ZZ.one() for _ in range(int(genus.spinor_genus_count()))
    )
