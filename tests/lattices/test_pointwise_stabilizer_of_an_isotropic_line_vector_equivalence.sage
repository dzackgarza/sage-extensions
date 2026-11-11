r"""Vector equivalence under the pointwise stabilizer of an isotropic line that is not maximal (#328).

The consumer: `L.Aut().stabilizer(I, action="pointwise").vector_equivalence_witness(u, v)`
decides whether two vectors of an indefinite lattice $L$ lie in one orbit of
$\{g \in O(L) : g|_I = \mathrm{id}\}$ for a primitive isotropic sublattice
$I \subsetneq I^\perp$, and returns a witness in that stabilizer when they do.

The specimen: $L = U \oplus K$ with $K = A_2(-1) \oplus \langle -2\rangle$,
negative definite of rank three, in the basis $(e, f)$ of $U$ with
$b(e, f) = 1$ and $(r, t, s)$ of $K$ with $q(r) = q(t) = q(s) = -2$,
$b(r, t) = 1$ and $b(r, s) = b(t, s) = 0$; $I = \langle e\rangle$, a primitive
isotropic line.  Then $I^\perp = \langle e \rangle \oplus K$ is properly larger
than $I$ and $K_I = I^\perp/I$ is isometric to $K$, so the pointwise stabilizer
acts on $K_I$ through a finite orthogonal group and
$1 \to U_I \to C_I \to M_I^0 \to 1$ holds, with $U_I$ the radical and $M_I^0$ the
part of the Levi factor that is trivial on $I$.

What is asserted, and what is not:

* $r$ is carried to $-r$ by the element that acts as $-1$ on $K$ and as the
  identity on $U$: it fixes $I$ pointwise and acts nontrivially on $K_I$, so the
  witness lies in the part of the pointwise stabilizer that the pointwise kernel
  on $I^\perp$ does not see;
* $e + r$ is carried to $-e + r$: the two have one reduction modulo $I$, and the
  displacement $-2e$ is realized by the Eichler transvection $t(e, r)$ of the
  radical, so the witness is a unipotent element composed with nothing;
* $r$ and $s$ have the same square and are not equivalent: they are roots of two
  different orthogonal summands of $K_I$, so no isometry of $K_I$ — and hence no
  element of the pointwise stabilizer, which descends to one — carries one onto
  the other;
* $e$ and $-e$ are not equivalent: the stabilizer fixes $e$ pointwise.

No number is asserted: the only claims are the relations above, and every count
in this module's calls is that call's own output, not a lattice-database card
value.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""$L = U \oplus (A_2(-1) \oplus \langle -2\rangle)$, its isotropic line $\langle e\rangle$, and the basis."""

    lattices = Lattices(ZZ)
    negative = lattices([[-2, 1], [1, -2]]) + lattices([[-2]])
    ambient = lattices("U") + negative
    e, f, r, _second_root, s = tuple(ambient.module_generators())
    line = ambient.primitive_isotropic_subobject(e)
    return ambient, line, (e, f, r, s)


def test_the_pointwise_stabilizer_transports_a_vector_by_its_action_on_the_reduction() -> None:
    r"""$r$ is carried to $-r$ by an element fixing $I$ pointwise and acting as $-1$ on $K_I$."""

    ambient, line, (e, f, r, s) = _specimen()
    stabilizer = ambient.Aut().stabilizer(line, action="pointwise")
    witness = stabilizer.vector_equivalence_witness(r, -r)
    assert witness in stabilizer
    assert witness(r) == -r
    assert witness(e) == e


def test_the_pointwise_stabilizer_transports_a_vector_by_a_transvection_of_the_radical() -> None:
    r"""$e + r$ is carried to $-e + r$ by the transvection $t(e, r)$, which fixes $e$."""

    ambient, line, (e, f, r, s) = _specimen()
    stabilizer = ambient.Aut().stabilizer(line, action="pointwise")
    witness = stabilizer.vector_equivalence_witness(e + r, -e + r)
    assert witness in stabilizer
    assert witness(e + r) == -e + r
    assert witness(e) == e


def test_the_pointwise_stabilizer_separates_vectors_in_different_reduction_orbits() -> None:
    r"""$r$ and $s$ have one square and lie in different orbits of the image of $C_I$ in $O(K_I)$."""

    ambient, line, (e, f, r, s) = _specimen()
    stabilizer = ambient.Aut().stabilizer(line, action="pointwise")
    assert stabilizer.vector_equivalence_witness(r, s) is None


def test_the_pointwise_stabilizer_leaves_the_isotropic_line_pointwise_fixed() -> None:
    r"""$-e$ is a vector of $I$ that no element of the stabilizer of $I$ reaches from $e$."""

    ambient, line, (e, f, r, s) = _specimen()
    stabilizer = ambient.O().pointwise_stabilizer(line.inclusion())
    assert stabilizer.vector_equivalence_witness(e, -e) is None
