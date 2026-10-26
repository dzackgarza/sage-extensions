r"""Cartan calculus on represented affine algebraic de Rham algebras.

No new object is introduced here.  Vector fields are exactly derivations
``Der_R(A) = Der_R(A, A^1)``; each composes as the ``R``-linear endomorphism
of ``A`` obtained through ``Res_f(A^1) -> A``, ``a e_0 |-> a``, while
contractions and Lie derivatives are actual graded derivations of the existing
de Rham DGA.
"""

from sage.structure.element import parent


def _lie_bracket(left, right):
    r"""Return the commutator ``[left,right]`` of two vector fields."""
    if parent(left) is not parent(right):
        raise ValueError(
            f"the Lie bracket [X, Y] needs vector fields on one algebra, but {left} lies in {left.parent()} "
            f"and {right} lies in {right.parent()}"
        )
    algebra = left.domain()
    vector_fields = algebra.vector_fields()
    if left.parent() is not vector_fields:
        raise TypeError(
            f"the Lie bracket [X, Y] needs derivations A -> A, but {left} is not a vector field on {algebra}"
        )
    left_endomorphism = left.linear_endomorphism()
    right_endomorphism = right.linear_endomorphism()
    return vector_fields(
        {
            label: left(right_endomorphism(algebra.algebra_generator(label)))
            - right(left_endomorphism(algebra.algebra_generator(label)))
            for label in vector_fields.generator_labels()
        }
    )


def _graded_commutator(left, right):
    r"""Return the graded commutator of endo-derivations.

    For homogeneous derivations of shifts ``p`` and ``q`` this is
    ``D E - (-1)^(pq) E D`` and has shift ``p+q``.
    """
    if left.algebra() is not right.algebra():
        raise ValueError(
            f"the graded commutator needs derivations of one graded algebra, but {left} is on "
            f"{left.algebra()} and {right} is on {right.algebra()}"
        )
    algebra = left.algebra()
    if left.target() is not algebra or right.target() is not algebra:
        raise TypeError(
            f"the graded commutator needs derivations A -> A of {algebra}, but {left} or {right} takes "
            "values elsewhere"
        )
    parity = (left.degree_shift() * right.degree_shift()) % 2

    def commutator(element):
        result = left(right(element))
        second = right(left(element))
        return result + second if parity else result - second

    return algebra.graded_derivations(
        algebra,
        shift=left.degree_shift() + right.degree_shift(),
    )._from_derived_elementwise(commutator, left, right)


from sage_extensions.categories.modules.powers import _exterior_word


def _exterior_label(word):
    if len(word) == 0:
        return 0
    if len(word) == 1:
        return word[0]
    return tuple(word)


def _interior_product(vector_field):
    r"""Return contraction ``i_X`` as a degree ``-1`` derivation of ``DR(A)``."""
    algebra = vector_field.domain()
    if vector_field.parent() is not algebra.vector_fields():
        raise TypeError(
            f"the contraction i_X needs a derivation X: A -> A with A = {algebra}, but {vector_field} "
            "takes values elsewhere"
        )
    endomorphism = vector_field.linear_endomorphism()
    de_rham = algebra.de_rham_algebra()
    exterior = de_rham.extension_algebra()

    def contract_extension(element):
        element = exterior(element)
        result = exterior.zero()
        for degree, component in element.homogeneous_components().items():
            if degree == 0:
                continue
            source_piece = exterior.graded_piece(degree)
            target_piece = exterior.graded_piece(degree - 1)
            target_component = target_piece.zero()
            coordinates = source_piece.framing_morphism().lift(component)
            for label in coordinates.support().domain():
                coefficient = coordinates(label)
                word =_exterior_word(label, degree)
                for position, differential_label in enumerate(word):
                    differential_kind, algebra_label = differential_label
                    assert differential_kind == "d", (
                        f"the Kahler generator {differential_label} in {label} must be a differential"
                    )
                    scalar = endomorphism(algebra.algebra_generator(algebra_label))
                    if not scalar:
                        continue
                    remaining = word[:position] + word[position + 1 :]
                    basis = target_piece.module_generator(_exterior_label(remaining))
                    signed = -scalar if position % 2 else scalar
                    target_component += target_piece.scalar_multiple(
                        coefficient * signed,
                        basis,
                    )
            if target_component != target_piece.zero():
                result += exterior.from_component(degree - 1, target_component)
        return result

    def contraction(element):
        return de_rham.from_realization(contract_extension(de_rham.realize(element)))

    return de_rham.graded_derivations(
        de_rham, shift=-1
    )._from_constructed_elementwise(contraction)


def _lie_derivative(vector_field):
    r"""Return ``L_X = [d,i_X]`` as a degree-zero derivation of ``DR(A)``."""
    contraction = vector_field.interior_product()
    return contraction.algebra().differential().graded_commutator(contraction)
