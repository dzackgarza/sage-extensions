r"""Extension and restriction of scalars along \(\mathbb Q \to \mathbb Q(i)\) form an adjunction.

For \(\iota: \mathbb Q \to K = \mathbb Q[x]/(x^2+1)\), extension \(K\otimes_{\mathbb Q} -\)
is left adjoint to restriction; the counit \(K \otimes_{\mathbb Q} N \to N\) multiplies
scalars back in, and both triangle identities hold (Mac Lane, CWM, IV.1).
"""

from sage_extensions.all import *


def _gaussian_extension():
    polynomials = QQ["x"]
    x = polynomials.gen()
    scalars = polynomials.quotient(x**2 + 1)
    i = scalars(x)
    structure_map = scalars.algebra_structure_morphism()
    return scalars, i, structure_map


def test_base_change_counit_multiplies_the_restricted_scalar_basis_back_into_the_module() -> None:
    r"""The restriction of \(K g\) has \(\mathbb Q\)-basis \(\{g, ig\}\)."""
    scalars, i, structure_map = _gaussian_extension()
    module = Modules(scalars)(scalars**1)
    (generator,) = module.module_generators()
    adjunction = Modules(QQ).base_change_adjunction(structure_map)

    restricted = adjunction.right_adjoint()(module)
    extended = adjunction.left_adjoint()(restricted)
    counit = adjunction.counit(module)

    assert counit.domain() is extended
    assert counit.codomain() is module
    labels = restricted.module_generating_set()
    assert labels.cardinality() == 2
    restricted_values = {
        restricted.module_generator(label).underlying_element()
        for label in labels
    }
    assert restricted_values == {generator, i * generator}
    for label in extended.module_generating_set():
        assert counit(extended.module_generator(label)) == restricted.module_generator(label).underlying_element()


def test_extension_restriction_triangle_is_the_identity_on_a_free_module() -> None:
    r"""\(\varepsilon_{FM} \circ F(\eta_M) = \mathrm{id}_{FM}\) for \(M = \mathbb Q\)."""
    _scalars, _i, structure_map = _gaussian_extension()
    source = Modules(QQ)(QQ**1)
    adjunction = Modules(QQ).base_change_adjunction(structure_map)
    extension = adjunction.left_adjoint()

    unit = adjunction.unit(source)
    extended_source = extension(source)
    extended_unit = extension(unit)
    counit = adjunction.counit(extended_source)
    triangle = counit * extended_unit

    assert triangle.domain() is extended_source
    assert triangle.codomain() is extended_source
    for label in extended_source.module_generating_set():
        generator = extended_source.module_generator(label)
        assert triangle(generator) == generator


def test_restriction_extension_triangle_is_the_identity_on_a_free_extension_module() -> None:
    r"""\(G(\varepsilon_N) \circ \eta_{GN} = \mathrm{id}_{GN}\) for \(N = K\)."""
    scalars, _i, structure_map = _gaussian_extension()
    target = Modules(scalars)(scalars**1)
    adjunction = Modules(QQ).base_change_adjunction(structure_map)
    restriction = adjunction.right_adjoint()

    restricted_target = restriction(target)
    unit = adjunction.unit(restricted_target)
    counit = adjunction.counit(target)
    restricted_counit = restriction(counit)
    triangle = restricted_counit * unit

    assert triangle.domain() is restricted_target
    assert triangle.codomain() is restricted_target
    for label in restricted_target.module_generating_set():
        generator = restricted_target.module_generator(label)
        assert triangle(generator) == generator
