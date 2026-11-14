r"""Hermitian modules over nonmaximal orders, in coordinates of a `Z`-basis.

Let `R` be an order in a quadratic extension `E/K`, `\Lambda` a torsion-free `R`-module
and `B` the Gram matrix of a scaled trace form on a `Z`-basis of `\Lambda`. If the
matrices `F_i` give multiplication by generators of `R`, then

.. MATH::

    U(\Lambda, h) = \{g \in GL_r(Z) : g^t B g = B, g F_i = F_i g\},

because `b(x, a y) = Tr(a h(x, y))` and the trace pairing is nondegenerate.

The saturation `\Lambda' = O_E \Lambda` is preserved by every `E`-linear automorphism
of `\Lambda`. With `m \Lambda' \subseteq \Lambda \subseteq \Lambda'`, an element of
`U(\Lambda', h)` preserves `\Lambda` exactly when it preserves `\Lambda / m \Lambda'`,
so `U(\Lambda, h)` is the stabilizer of that submodule, computed with Schreier's lemma.
"""

from sage.arith.functions import lcm
from sage.matrix.constructor import matrix
from sage.matrix.special import identity_matrix
from sage.quadratic_forms.quadratic_form import QuadraticForm
from sage.rings.finite_rings.integer_mod_ring import Zmod
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ


class OrderHermitianModule:
    r"""An `R`-lattice with the action of `O_E` on its rational span.

    ``coefficient_actions`` are integer matrices of generators of `R`.
    ``maximal_actions`` are rational matrices of a `Z`-basis of `O_E`.
    """

    def __init__(self, gram, coefficient_actions, maximal_actions):
        self.gram = matrix(ZZ, gram)
        self.rank = self.gram.nrows()
        self.coefficient_actions = tuple(
            matrix(ZZ, self.rank, self.rank, a) for a in coefficient_actions
        )
        self.maximal_actions = tuple(
            matrix(QQ, self.rank, self.rank, a) for a in maximal_actions
        )
        self.saturation_basis = self._saturation()
        inclusion = self.saturation_basis.inverse()
        assert inclusion.denominator() == 1
        self._inclusion = inclusion.change_ring(ZZ)
        self.conductor_exponent = self._inclusion.inverse().denominator()

    def _saturation(self):
        columns = [
            column for action in self.maximal_actions for column in action.columns()
        ]
        denominator = lcm([c.denominator() for c in columns])
        scaled = matrix(ZZ, [list(denominator * c) for c in columns]).hermite_form(
            include_zero_rows=False
        )
        return (scaled.change_ring(QQ) / denominator).transpose()

    def saturation_gram(self):
        return self.saturation_basis.transpose() * self.gram * self.saturation_basis

    def to_saturation(self, element):
        r"""Return an automorphism of `\Lambda` in coordinates of `\Lambda'`."""
        return matrix(
            ZZ,
            self.saturation_basis.inverse()
            * matrix(QQ, element)
            * self.saturation_basis,
        )

    def from_saturation(self, element):
        r"""Return an automorphism of `\Lambda'` preserving `\Lambda` in `\Lambda`-coordinates."""
        return matrix(
            ZZ,
            self.saturation_basis
            * matrix(QQ, element)
            * self.saturation_basis.inverse(),
        )

    def is_unitary(self, element):
        r"""Decide the equations defining `U(\Lambda, h)`."""
        element = matrix(QQ, element)
        return (
            element.denominator() == 1
            and element.det() in (1, -1)
            and element.transpose() * self.gram * element == self.gram
            and all(element * a == a * element for a in self.coefficient_actions)
        )

    def _submodule_key(self, element):
        modulus = self.conductor_exponent
        generators = (element * self._inclusion).columns() + [
            modulus * row for row in identity_matrix(ZZ, self.rank).rows()
        ]
        return matrix(ZZ, generators).hermite_form(include_zero_rows=False)

    def stabilizer_of_module(self, saturation_generators):
        r"""Return `(index, generators)` of `U(\Lambda, h)` in the supplied group.

        ``saturation_generators`` generate a subgroup of `U(\Lambda', h)` in the
        coordinates of `\Lambda'`. The result is in the coordinates of `\Lambda`.
        """
        generators = tuple(matrix(ZZ, g) for g in saturation_generators)
        one = identity_matrix(ZZ, self.rank)
        transversal = {self._submodule_key(one).str(): one}
        frontier = [one]
        schreier = {}
        while frontier:
            current = frontier.pop()
            for generator in generators:
                image = generator * current
                key = self._submodule_key(image).str()
                if key not in transversal:
                    transversal[key] = image
                    frontier.append(image)
                    continue
                element = transversal[key].inverse().change_ring(ZZ) * image
                if element != one:
                    schreier[element.str()] = element
        return len(transversal), tuple(
            self.from_saturation(element) for element in schreier.values()
        )

    def definite_unitary_elements(self):
        r"""Return every element of `U(\Lambda, h)` for a definite form."""
        form = self.gram if self.gram[0, 0] > 0 else -self.gram
        automorphisms = QuadraticForm(ZZ, 2 * form).automorphisms()
        return tuple(
            matrix(ZZ, g) for g in automorphisms if self.is_unitary(matrix(ZZ, g))
        )

    def congruence_intersection(self, generators, modulus, allowed):
        r"""Return `(index, generators)` of the elements whose reduction lies in ``allowed``.

        ``generators`` generate a subgroup of `U(\Lambda, h)`. ``allowed`` is a set of
        reductions modulo ``modulus``, forming a subgroup. Right cosets of the preimage are
        compared in the finite image, and Schreier's lemma gives generators.
        """
        ring = Zmod(modulus)
        generators = tuple(matrix(ZZ, g) for g in generators)
        one = identity_matrix(ZZ, self.rank)

        def reduce(element):
            return element.change_ring(ring)

        allowed = tuple(matrix(ring, a) for a in allowed)
        transversal = [one]
        schreier = {}
        position = 0
        while position < len(transversal):
            current = transversal[position]
            position += 1
            for generator in generators:
                image = generator * current
                for known in transversal:
                    quotient = image * known.inverse().change_ring(ZZ)
                    if reduce(quotient) in allowed:
                        if quotient != one:
                            schreier[quotient.str()] = quotient
                        break
                else:
                    transversal.append(image)
        return len(transversal), tuple(schreier.values())

    def definite_transporter(self, other):
        r"""Return `g` with `g^t B' g = B` and `g F_i = F'_i g` for definite forms, or ``None``."""
        assert self.rank == other.rank and len(self.coefficient_actions) == len(other.coefficient_actions)
        form, target = (self.gram, other.gram) if self.gram[0, 0] > 0 else (-self.gram, -other.gram)
        witness = QuadraticForm(ZZ, 2 * target).is_globally_equivalent_to(QuadraticForm(ZZ, 2 * form), return_matrix=True)
        if witness is False:
            return None
        base = matrix(ZZ, witness)
        for automorphism in QuadraticForm(ZZ, 2 * form).automorphisms():
            candidate = base * matrix(ZZ, automorphism)
            if candidate.transpose() * other.gram * candidate == self.gram and all(
                candidate * a == b * candidate
                for a, b in zip(self.coefficient_actions, other.coefficient_actions, strict=True)
            ):
                return candidate
        return None
