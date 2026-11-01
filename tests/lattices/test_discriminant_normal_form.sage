r"""The discriminant group's normal form is an isomorphism with both round trips.

Cell 57 of ``preamble-lattices.ipynb``::

    L.discriminant_group().normal_form()

``TEn`` has discriminant group ``(Z/2)^10`` presented on 12 module generators
(``L`` has rank 12 and the discriminant is computed on its cover), and the
normal form is the invariant-factor module on 10 generators.  The specimen is
checked here with what the arrow retains: its endpoints, that the inverse's
endpoints are those two objects swapped, and that both round trips are the
identity on the generators of their own side.
"""

from sage_extensions.all import NamedLattices


def test_the_normal_form_of_the_discriminant_group_is_an_isomorphism() -> None:
    discriminant = NamedLattices.TEn.discriminant_group()
    assert discriminant.cardinality() == 1024

    normal_form = discriminant.normal_form()
    assert type(normal_form).__name__ == "CategoricalIsomorphism"

    forward, inverse = normal_form.forward(), normal_form.inverse()
    assert normal_form.domain() is discriminant
    assert inverse.domain() is normal_form.codomain()
    assert inverse.codomain() is normal_form.domain()
    assert normal_form.codomain().cardinality() == discriminant.cardinality()

    domain_generators = tuple(normal_form.domain().module_generators())
    codomain_generators = tuple(normal_form.codomain().module_generators())
    assert len(domain_generators) == 12
    assert len(codomain_generators) == 10
    assert all(inverse(forward(generator)) == generator for generator in domain_generators)
    assert all(forward(inverse(generator)) == generator for generator in codomain_generators)
    # The normal form is not the identity arrow: it changes the framing.
    assert normal_form.domain() is not normal_form.codomain()
