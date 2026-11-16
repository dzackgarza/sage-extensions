r"""The elements of a general module hash the element of its underlying set.

A module presented by an abelian group and a ring action is an element of that
group with scalars acting on it, so two elements of one general module are
equal exactly when the underlying elements are.  The three modules here are the
quotient of the free module on the pure tensors, the Cartier divisor group
``CDiv(X)`` of the projective line (a quotient sheaf ``K^*/O^*``), and ``L^1``
modulo the null functions; each element hashes the element of its group that
names it, and the module is retained beside it.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_zero_class_of_a_tensor_quotient_is_a_point_of_a_finite_ordered_set() -> None:
    r"""``QQ (x)_ZZ QQ`` without a chosen framing: its zero is one element.

    The tensor product is the generators-and-relations quotient of the free
    module on the pure tensors, so its elements are classes of that quotient.
    The zero class and the sum of the zero class with itself are one element,
    and each is a point of a finite ordered set.
    """
    rationals = Modules(ZZ)(QQ)
    product = Modules(ZZ).tensor_product((rationals, rationals))
    zero = product.zero()
    doubled = zero + zero

    assert zero == doubled
    assert hash(zero) == hash(doubled)
    assert FiniteOrderedSets()((zero, doubled)).cardinality() == 1
    assert FiniteOrderedSets()((zero,)).cardinality() == 1


def test_two_cartier_divisors_of_one_class_hash_alike() -> None:
    r"""``-0 = 0`` in ``CDiv(P^1_Q)``, at the module and not only at its classes.

    ``CDiv(X)`` is the group of global sections of ``K^*/O^*``, so the negation
    of the zero divisor is the zero divisor.  The two elements are one element
    of the module, and a finite ordered set of them holds one point.
    """
    line = ProjectiveSpaces(QQ)(1)
    divisors = CartierDivisorGroups().of_scheme(line)
    zero = divisors.zero()
    negated = -zero

    assert negated == zero
    assert hash(negated) == hash(zero)
    assert FiniteOrderedSets()((zero, negated)).cardinality() == 1


def test_the_element_hashes_the_group_element_and_not_the_module() -> None:
    r"""``hash(zero)`` is ``hash(zero's group element)``: one datum, not two.

    A general module is its underlying group with a ring acting on it, so the
    element of that group is what the module's element is and what its equality
    compares.  A hash that mixed the module into the answer would read a
    second datum that equality does not, and would refuse nothing when the
    group element refuses a hash: the tensor quotient's zero class, the Cartier
    zero divisor and the class of the zero function each hash exactly the
    element of their group.
    """
    rationals = Modules(ZZ)(QQ)
    product = Modules(ZZ).tensor_product((rationals, rationals))
    zero = product.zero()
    assert hash(zero) == hash(zero.underlying_element())

    line = ProjectiveSpaces(QQ)(1)
    divisors = CartierDivisorGroups().of_scheme(line)
    divisor_zero = divisors.zero()
    assert hash(divisor_zero) == hash(divisor_zero.underlying_element())

    quotient = Lp(1, RR, RR).quotient_by_null_functions()
    class_zero = quotient.zero()
    assert hash(class_zero) == hash(class_zero.underlying_element())


def test_the_zero_class_of_the_almost_everywhere_quotient_is_a_point() -> None:
    r"""The zero class of ``L^1(RR)`` modulo the null functions is one element.

    Two integrable maps that agree outside a null set are one class, so the sum
    of the zero class with itself is the zero class.  The class of the zero
    function is what the module's element is, and its hash is that class's hash:
    the module is not mixed into the answer, so the assertion reads a value of
    the group rather than one the module alone could supply.
    """
    quotient = Lp(1, RR, RR).quotient_by_null_functions()
    zero = quotient.zero()

    assert zero == quotient.zero()
    assert hash(zero) == hash(zero.underlying_element())
    assert FiniteOrderedSets()((zero, quotient.zero())).cardinality() == 1
