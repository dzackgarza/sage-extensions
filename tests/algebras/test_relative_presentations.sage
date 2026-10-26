r"""Families, fibres, pushouts and tensor products of presented commutative algebras."""

from sage_extensions.all import *  # noqa: F401,F403


def test_special_fiber_of_xy_equals_t_is_the_node() -> None:
    r"""In ``A = QQ[t][x,y]/(xy - t)`` the scalar ``t`` acts as ``xy``, and the
    fibre over ``t = 0``, ``A ⊗_{QQ[t]} QQ[t]/(t)``, is the node ``QQ[x,y]/(xy)``:
    ``xy = 0`` there while ``x ≠ 0`` and ``y ≠ 0``."""
    parameter = QQ["t"]
    t = parameter.gen()
    presentation = parameter["x,y"]
    x, y = presentation.algebra_generator("x"), presentation.algebra_generator("y")
    family = presentation.quotient(presentation.ideal([x * y - t]))

    assert family(t) == family(x) * family(y)
    assert family(t) != family.zero()

    special_fiber = family.base_change(parameter.Mor(QQ)({t: QQ.zero()}))
    xs, ys = special_fiber.algebra_generator("x"), special_fiber.algebra_generator("y")
    assert xs * ys == special_fiber.zero()
    assert xs != special_fiber.zero()
    assert ys != special_fiber.zero()
    assert xs + ys != special_fiber.zero()


def test_gaussian_field_tensor_itself_over_qq_splits_by_an_idempotent() -> None:
    r"""``QQ(i) ⊗_QQ QQ(i) ≅ QQ(i) × QQ(i)``: ``e = (1 + i ⊗ i)/2`` satisfies
    ``e^2 = e`` (as ``(i ⊗ i)^2 = i^2 ⊗ i^2 = 1``) and ``e ≠ 0, 1``, so the
    tensor product is not an integral domain."""
    gaussian = QuadraticField(-1, "i")
    tensor = Algebras(QQ).Associative().Unital().Commutative().coproduct((gaussian, gaussian))
    i_left = tensor.left_coproduct_map()(gaussian.gen())
    i_right = tensor.right_coproduct_map()(gaussian.gen())
    idempotent = (tensor.one() + i_left * i_right) / 2

    assert idempotent * idempotent == idempotent
    assert idempotent != tensor.zero()
    assert idempotent != tensor.one()
    assert idempotent * (tensor.one() - idempotent) == tensor.zero()
    assert i_left != i_right
    assert i_left != -i_right


def test_pushout_of_t_to_x_squared_and_t_to_y_squared_is_qq_xy_mod_x2_minus_y2() -> None:
    r"""The pushout of ``QQ[x] <- QQ[t] -> QQ[y]``, ``t ↦ x^2``, ``t ↦ y^2``, is
    ``QQ[x] ⊗_{QQ[t]} QQ[y] = QQ[x, y]/(x^2 - y^2)``: there ``x^2 = y^2`` but
    ``x ≠ ±y``."""
    source, left, right = QQ["t"], QQ["x"], QQ["y"]
    t = source.gen()
    to_left = source.Mor(left)({t: left.gen() ** 2})
    to_right = source.Mor(right)({t: right.gen() ** 2})
    pushout = Algebras(QQ).Commutative().pushout(to_left, to_right)
    into_pushout_left, into_pushout_right = pushout.pushout_maps()
    x, y = into_pushout_left(left.gen()), into_pushout_right(right.gen())

    assert x * x == y * y
    assert x != y
    assert x != -y
    assert into_pushout_left(to_left(t**3)) == into_pushout_right(to_right(t**3))
