r"""Public centralizers of infinite-order isometries.

U + U, F the Eichler transvection f1 -> f1 + e2, f2 -> f2 - e1: C(Z) is <F> x SL_2(Z), whose
image modulo three has order 72. Norm form of Z[sqrt 2], F = (1 + sqrt 2)^2: C(Z) = +-F^Z.
"""

from sage_extensions.all import *


def _closure_mod(lattice, generators, modulus):
    frame = tuple(lattice.module_generators())
    reduce = lambda g: tuple(tuple(int(c) % int(modulus) for c in g(v)) for v in frame)
    compose = lambda a, b: tuple(
        tuple(sum(a[j][i] * b[k][j] for j in range(len(frame))) % int(modulus) for i in range(len(frame)))
        for k in range(len(frame))
    )
    letters = [reduce(g) for g in generators]
    one = reduce(lattice.O().one())
    known = set([one])
    frontier = [one]
    while frontier:
        current = frontier.pop()
        for letter in letters:
            image = compose(letter, current)
            if image not in known:
                known.add(image)
                frontier.append(image)
    return len(known)


def test_eichler_centralizer_through_the_public_group():
    L = Lattices(ZZ)("U") + Lattices(ZZ)("U")
    labels = L.module_generating_set()
    e1, f1, e2, f2 = tuple(L.module_generators())
    F = L.O()({labels[0]: e1, labels[1]: f1 + e2, labels[2]: e2, labels[3]: f2 - e1})
    generators = tuple(L.O().centralizer(F).group_generators())
    assert all(g * F == F * g for g in generators)
    assert F in generators or ~F in generators
    assert _closure_mod(L, generators, 3) == int(72)


def test_norm_form_centralizer_through_the_public_group():
    L = Lattices(ZZ)([[2, 0], [0, -4]])
    labels = L.module_generating_set()
    one, root = tuple(L.module_generators())
    F = L.O()({labels[0]: L.scalar_multiple(3, one) + L.scalar_multiple(2, root), labels[1]: L.scalar_multiple(4, one) + L.scalar_multiple(3, root)})
    generators = tuple(L.O().centralizer(F).group_generators())
    assert all(g * F == F * g for g in generators)
    assert _closure_mod(L, generators, 7) == _closure_mod(L, (F, L.O()(lambda label: -L.module_generator(label))), 7)
