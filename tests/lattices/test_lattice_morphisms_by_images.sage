r"""Lattice morphisms given by the images of a basis.

A lattice morphism \(\varphi\colon L\to M\) is a linear map with
\(\varphi(x)\cdot\varphi(y) = x\cdot y\).  In \(U\) with isotropic basis \(e,f\),
\(ef=1\):

- \(a\mapsto e-f\) is a morphism \(A_1\to U\), since \((e-f)^2 = -2 = a^2\);
  \(a\mapsto e+f\) is not, since \((e+f)^2 = 2\).
- The swap \(e\leftrightarrow f\) preserves the form, is an involution, and composing it
  after \(a\mapsto e-f\) gives \(a\mapsto f-e\).
- The swap and \(-1\) are isometries of \(U\), so they are elements of \(O(U)\).
"""

import pytest

from sage_extensions.all import *


def test_a_root_of_a1_maps_to_a_vector_of_square_minus_two_in_u() -> None:
    root_lattice = Lattices(ZZ)("A1")
    plane = Lattices(ZZ)("U")
    (root,) = root_lattice.module_generators()
    e, f = plane.module_generators()
    morphism = root_lattice.Mor(plane)((e - f,))

    assert morphism.domain() is root_lattice
    assert morphism.codomain() is plane
    assert morphism(root) == e - f
    assert morphism(root) * morphism(root) == root * root


def test_a_map_that_does_not_preserve_the_square_is_not_a_lattice_morphism() -> None:
    root_lattice = Lattices(ZZ)("A1")
    plane = Lattices(ZZ)("U")
    e, f = plane.module_generators()

    with pytest.raises(ValueError):
        root_lattice.Mor(plane)((e + f,))


def test_the_swap_of_u_is_a_form_preserving_involution() -> None:
    plane = Lattices(ZZ)("U")
    e, f = plane.module_generators()
    swap = plane.Mor(plane)((f, e))

    assert swap(e) == f
    assert swap(f) == e
    assert swap(e) * swap(f) == 1
    assert (swap * swap)(e) == e
    assert (swap * swap)(f) == f


def test_composition_of_lattice_morphisms_is_composition_of_maps() -> None:
    root_lattice = Lattices(ZZ)("A1")
    plane = Lattices(ZZ)("U")
    (root,) = root_lattice.module_generators()
    e, f = plane.module_generators()
    embedding = root_lattice.Mor(plane)((e - f,))
    swap = plane.Mor(plane)((f, e))

    assert (swap * embedding)(root) == f - e
    assert (swap * embedding).domain() is root_lattice


def test_the_swap_and_minus_one_are_elements_of_o_u() -> None:
    plane = Lattices(ZZ)("U")
    e, f = plane.module_generators()
    group = plane.O()
    swap = group((f, e))
    minus_one = group((-e, -f))

    assert swap * swap == group.one()
    assert minus_one * minus_one == group.one()
    assert swap * minus_one == minus_one * swap
    assert swap != minus_one
