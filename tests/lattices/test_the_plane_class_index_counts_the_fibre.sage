r"""The plane class index is the fibre of the plane row over the classes `J`.

The issue's index is `[Stab_{O(q)}(J) : rho(Stab_{O(L)}(P))]` -- the *ambient*
stabilizer's image, not the subgroup's -- and it is the number of the row's
plane cusps that lie over one class `J`.  Two things make that checkable at a
size one command reaches:

* a kernel subgroup cuts the plane row down to the classes, one orbit per class
  for every fibre of the index, so the row's count is the classes times the
  index; and
* the index is the same at every class because both of its entries conjugate:
  for `g` in `O(q)`, `Stab(gJ) = g Stab(J) g^-1` and `rho(Pi_{gP}) = g rho(Pi_P)
  g^-1`, so the quotient of their orders does not move.  No normality of the
  subgroup's image is used, and none is true here.

`U + U(2) + <-4>` is the smallest specimen where the fibre is not `1`: its
`O(q)` has order 12, the class stabilizer 4, so three classes `J`, and the
kernel row returns three planes -- one per class.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""`U + U(2) + <-4>`: three plane classes and one plane orbit under `O(L)`."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)([[0, 2], [2, 0]])
        + Lattices(ZZ)([[-4]])
    )


def test_the_kernel_plane_row_counts_the_classes_times_the_index():
    r"""`row cusps = [O(q) : Stab(J)] * [Stab(J) : rho(Stab_O(L)(P))]`, all three computed.

    The index is read from the plane's own parabolic, the class count from the
    finite group's order and the class stabilizer's, and the row from the public
    orbit call; the identity is what makes the index the fibre.
    """
    lattice = _specimen()
    plane = next(iter(lattice.Aut().cusps(2))).representative()
    kernel = lattice.stable_orthogonal_group()

    stabilizer_order, image_order = plane.stabilizer_discriminant_image_orders()
    index = plane.stabilizer_discriminant_image_index()
    classes = int(lattice.discriminant_group().O().cardinality()) // int(stabilizer_order)
    cusps = kernel.cusps(2)

    assert index == int(stabilizer_order) // int(image_order)
    assert classes == int(3)
    assert index == int(1)
    assert cusps.cardinality() == cardinal(classes * index)
    assert stabilizer_order == int(image_order) * index
