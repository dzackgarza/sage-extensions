r"""Research issue 614, cells 61 and 84: the two free-algebra notebook specimens.

Cell 61 asks which free algebras a torsion module has: for
``M = coker(2: ZZ -> ZZ)`` it builds ``T(M)`` and ``Γ(M)`` and states the
tensor identities, the degree-two invariant factor and one divided-power
identity.  Cell 84 asks whether an infinite generator map still induces
substitution: it builds ``Sym(ZZ[NN])`` and pushes one finite expression along
the doubling map, without enumerating the generating set.

Both cells are reproduced exactly as ``preamble-lattices.ipynb`` writes them,
and then checked for the data behind the identities: the retained generating
family of each construction, the endpoints of the substitution morphism, and
the module morphism it is built from.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _cell_61_module():
    r"""``M = coker(2: ZZ -> ZZ)``, exactly as cell 61 constructs it."""
    free = ZZ.free_module(Sets.Δ[0])
    generator = free.module_generator(0)
    return free.module_category().Mor(free, free)({0: 2 * generator}).cokernel()


def test_cell_61_tensor_and_divided_power_algebras_of_a_torsion_module() -> None:
    r"""Cell 61: ``2t = 0``, ``t*t != 0``, ``2(t*t) = 0``, ``Γ^2(M) = ZZ/4``.

    ``M`` is ``ZZ/2`` on one generator, so ``T(M)`` kills ``2t`` while ``t*t``
    survives, and ``Γ^2(M)`` is the divided square of ``ZZ/2``, which is
    ``ZZ/4``: its invariant factors are ``[4]``, and ``4 γ_2(γ) = 0``.
    """
    module = _cell_61_module()
    tensor = module.tensor_algebra()
    divided = module.divided_power_algebra()
    t = tensor.algebra_generator(0)
    gamma = divided.algebra_generator(0)

    assert 2 * t == tensor.zero()
    assert t * t != tensor.zero()
    assert 2 * (t * t) == tensor.zero()

    degree_two_invariants = divided.graded_piece(2).invariant_factors()
    assert degree_two_invariants.cardinality() == 1
    assert degree_two_invariants[0] == 4
    assert 4 * divided.divided_power(gamma, 2) == divided.zero()


def test_cell_61_keeps_the_module_it_quotients_and_its_own_generators() -> None:
    r"""The two algebras retain ``M`` as their generating module and its frame.

    ``T(M)`` is graded by tensor powers of the exact input module and ``Γ(M)``
    by its divided powers; degree one is ``M`` itself in both, so the tensor
    algebra's selected generating family is ``M``'s frame rather than a fresh
    basis.  ``Γ(M)``'s divided power ``γ_2`` of a degree-one generator is not a
    polynomial in it over ``ZZ``, so its selected family carries the
    positive-degree frames as well, and the label of ``M``'s frame still names
    the degree-one generator it is the image of.
    """
    module = _cell_61_module()
    tensor = module.tensor_algebra()
    divided = module.divided_power_algebra()

    assert tensor.generating_module() is module
    assert divided.generating_module() is module
    assert tensor.graded_piece(1).module_generating_set() is module.module_generating_set()
    assert divided.graded_piece(1) is module
    assert divided.degree_one_generator(0) == divided.algebra_generator(0)
    assert divided.graded_piece(0).module_generating_set().cardinality() == 1


def test_cell_61_module_generating_set_of_the_finitely_presented_module() -> None:
    r"""``M`` itself keeps the frame its own presentation states.

    The chosen-resolution contract is what cells 61 depends on: the cokernel
    retains the endpoint's generators and relations, so ``M`` answers its
    generating set, its framing morphism and its invariant factors without
    inventing a basis or substituting a free module.
    """
    module = _cell_61_module()

    assert tuple(module.module_generating_set()) == (0,)
    assert module.has_selected_module_resolution()
    assert module.framing_morphism().codomain() is module
    assert module.invariant_factors()[0] == 2


def test_cell_84_an_infinite_generator_map_induces_substitution() -> None:
    r"""Cell 84: ``psi(2 c_3 + c_8 c_3) = 2 c_6 + c_16 c_6`` on ``Sym(ZZ[NN])``.

    The expression is finite and the substitution is read off the generator
    images, so nothing enumerates the infinite generating set: the doubling
    map is a set morphism on ``NN``, and ``psi`` is the algebra morphism it
    induces.
    """
    natural = NN
    symmetric = ZZ.free_module(natural).symmetric_algebra()
    doubling = Sets().Mor(natural, natural)(lambda n: natural(2 * int(n)))
    psi = symmetric.Mor(symmetric)(lambda n: symmetric.algebra_generator(doubling(n)))
    c3, c8 = symmetric.algebra_generator(3), symmetric.algebra_generator(8)
    expression = 2 * c3 + c8 * c3
    expected = (
        2 * symmetric.algebra_generator(6)
        + symmetric.algebra_generator(16) * symmetric.algebra_generator(6)
    )

    assert psi(expression) == expected


def test_cell_84_keeps_the_infinite_basis_and_the_morphism_endpoints() -> None:
    r"""``Sym(ZZ[NN])`` states every finite monomial, on ``NN`` itself.

    The generating set is all of ``NN``, not a finite truncation, and the
    substitution is a morphism of that exact algebra: its domain and codomain
    are the one ``symmetric`` object, and it agrees with the doubling map on
    the generators it is stated on.
    """
    natural = NN
    symmetric = ZZ.free_module(natural).symmetric_algebra()
    doubling = Sets().Mor(natural, natural)(lambda n: natural(2 * int(n)))
    psi = symmetric.Mor(symmetric)(lambda n: symmetric.algebra_generator(doubling(n)))

    assert symmetric.algebra_generating_set() is natural
    assert symmetric.algebra_generating_set().cardinality().is_finite() is False
    assert psi.domain() is symmetric and psi.codomain() is symmetric
    for label in (0, 1, 3, 8, 41):
        assert psi(symmetric.algebra_generator(label)) == symmetric.algebra_generator(
            doubling(label)
        )
    assert psi(symmetric.one()) == symmetric.one()
