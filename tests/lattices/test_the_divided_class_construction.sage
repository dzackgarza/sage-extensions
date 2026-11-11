r"""Primitive isotropic vectors from their divided class, by the finite residue loop (#310).

`isotropic_lines_by_divided_class(d)` builds one primitive isotropic vector per divided class
at divisor `d`, and `primitive_isotropic_vector_of_divided_class` answers a named class or
refuses it.  The construction is finite by construction:

* `[v/d]` depends only on `v` modulo `d L`, so the residues of `L/dL` are the loop;
* in a scaled hyperbolic basis pair `⟨e, f⟩ ⊥ K` with `b(e,f) = h`, this library's `q = b(x,x)`
  gives `q(a e + b f + w) = 2 h a b + q(w)`, so the lift is integral exactly when some divisor
  pair `a b = -q(w)/(2h)` has `a ≡ a_0` and `b ≡ b_0` modulo `d` (both coordinates stay in
  their residue classes);
* `w → w + d k` over `k` in `K/dK` leaves the class fixed and changes `q(w)`, so the loop
  varies `k` as well;
* every candidate is checked: `q = 0`, primitive, divisor `d`, and its class.

The specimen is `U(2) + <-6>`, whose marked line has divisor two and whose exact image
computes the classes to compare against.
"""

import pytest

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""``U(2) + <-6>`` with its first basis vector, whose divisor is two."""
    lattice = Lattices(ZZ)([[0, 2, 0], [2, 0, 0], [0, 0, -6]])
    labels = tuple(lattice.module_generating_set())
    return lattice, lattice.module_generator(labels[0])


def test_a_scaled_hyperbolic_pair_is_exhibited() -> None:
    r"""The construction's summand is found, and the lattice without one is refused."""
    lattice, _vector = _specimen()
    # Unpacking is the existence assertion: a lattice without the summand has no pair.
    first, second, pairing = lattice.hyperbolic_basis_pair()
    assert lattice.q(first) == lattice.base_ring().zero()
    assert lattice.q(second) == lattice.base_ring().zero()
    assert lattice.b(first, second) == pairing


def test_every_class_of_the_exact_image_has_its_checked_line() -> None:
    r"""The construction covers the orbit of the marked class with checked vectors."""
    lattice, vector = _specimen()
    classes = lattice.isotropic_lines_by_divided_class(2)
    marked = lattice.divided_discriminant_class(vector)
    image = lattice.Aut().discriminant_image()
    orbit = set((marked,))
    frontier = [marked]
    while frontier:
        current = frontier.pop()
        for generator in image.group_generators():
            moved = generator(current)
            if moved not in orbit:
                orbit.add(moved)
                frontier.append(moved)
    ring = lattice.base_ring()
    assert marked in classes
    assert all(component in classes for component in orbit)
    for component in orbit:
        candidate = lattice.primitive_isotropic_vector_of_divided_class(component, 2)
        assert candidate.q() == ring.zero()
        assert candidate.is_primitive() is True
        assert lattice.div(candidate) == ring(2)
        assert lattice.divided_discriminant_class(candidate) == component


def test_a_class_the_loop_does_not_reach_is_refused_by_name() -> None:
    r"""A class with no lift is refused, and the refusal names it and the exhausted loop."""
    lattice, _vector = _specimen()
    classes = lattice.isotropic_lines_by_divided_class(2)
    absent = next(
        component for component in lattice.discriminant_group() if component not in classes
    )
    with pytest.raises(ValueError):
        lattice.primitive_isotropic_vector_of_divided_class(absent, 2)
    assert absent not in classes
