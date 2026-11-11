r"""`T_En`'s orthogonal group reaches its discriminant image, and `O()` and `Aut()` are one group.

`T_En = U + U(2) + E8(-2)` (`NamedLattices.TEn`, rank 12, signature (2, 10)), whose
discriminant form has 1024 classes.  On an indefinite lattice `O(T_En)` is infinite and is
not enumerated: its generators come from the indefinite-lattice computation
(`sage_indefinite_port`), through `LatticeIsometryMor._computed_group_generators`, and the
discriminant image is the image of *those* generators,
`rho(subgroup(generators))`.

**What #333 reported, and where the two calls differ.**  A chat reported that
`TEn.O().discriminant_image()` stops in `group_generators`, while another measured
`TEn.Aut().discriminant_image()` returning order `46 998 591 897 600` in 0.2 s.  There is
one parent and one generator source behind both spellings:

* `O` is an alias of `orthogonal_group`, which returns `self.Aut()`; `Aut()` is
  `self.Isom(self)`, and `_lattice_isometry_mor` is cached on `(id(L), id(L))`, so the two
  calls return the *same* object;
* the cached method is `group_generators`, cached per isometry Mor object: the first read
  in a process runs the indefinite-lattice computation (198 generators here, measured at
  76 s) and every later read is free, which is the whole of the difference between a 0.2 s
  answer and a call that appears to stop;
* nothing else is cached: the Mor's `discriminant_image` carries no cache decorator, so a
  second call rebuilds a fresh subgroup object of the same order, while the lattice's
  `discriminant_image` is the cached one.

So the stop is the cold generator computation, not a second code path.  (The other way the
same call fails in this environment is not a computation at all: with the port imported
from the runtime image's own copy instead of the port project at `/work`, the generator
call raises `TypeError: int() argument must be ... not 'OwnedJoinCategory.element_class'`
at `recursive.py:154`.  That is a setup error, and this file's run has the port at
`/work`.)

**What is asserted.**  That the two spellings return one image -- the same subgroup of
`O(A_{T_En})`, with equal computed orders and equal generating families -- that it is
non-trivial, and that it is *all* of `O(A_{T_En})`, which the owner decides by computation
(`discriminant_representation_is_surjective`) and which the two computed orders state
independently.  Every generator of the image is checked to be the discriminant morphism of
a generator of `O(T_En)`, so the subgroup returned is the image of that generating family
and not some subgroup of it.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_orthogonal_group_of_ten_has_a_discriminant_image() -> None:
    r"""`O().discriminant_image()` returns the image `Aut().discriminant_image()` returns.

    The parent is asserted to be one object and the two families one family, and the two
    images one subgroup: equal computed orders and equal generating families.  The image
    is contained in `O(A_{T_En})`, is non-trivial, and equals the whole of it -- the
    computed statement of `rho` being onto here -- and each of its generators is the
    discriminant morphism of a generator of `O(T_En)`.
    """
    lattice = NamedLattices.TEn
    orthogonal = lattice.O()
    automorphisms = lattice.Aut()

    # One parent: `O` is `orthogonal_group`, and that is `Aut()`, which is cached on id(L).
    assert orthogonal is automorphisms
    assert frozenset(orthogonal.group_generators()) == frozenset(
        automorphisms.group_generators()
    )

    target = lattice.discriminant_group().orthogonal_group()
    image = orthogonal.discriminant_image()
    same = automorphisms.discriminant_image()

    assert image.supergroup() is target
    assert int(image.cardinality()) > 1
    assert int(image.cardinality()) == int(same.cardinality())
    assert frozenset(image.group_generators()) == frozenset(same.group_generators())

    # rho is onto this discriminant form: the image is O(A_{T_En}) itself, by the owner's
    # computed decision and independently by the two computed orders.
    assert int(image.cardinality()) == int(target.cardinality())
    assert lattice.discriminant_representation_is_surjective() is True

    # The image is the image of the selected generating family, not a subgroup of it.
    letters = frozenset(
        generator.discriminant_morphism() for generator in orthogonal.group_generators()
    )
    assert frozenset(image.group_generators()) <= letters
