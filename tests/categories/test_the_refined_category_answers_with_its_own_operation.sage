r"""Which category level answers the operations a refinement rebuilds a class for.

Refining an object into another category rebuilds its class with the categories
it now reaches, and when two of those levels declare the same operation the
rebuild keeps the one the final category order names.

``QQ(i)`` is the object each of these acts on: an algebra over ``QQ`` that is
also a finitely generated framed free module, a module with a chosen finite
presentation, and an infinite ring.

* ``order_ideal`` is ``FramedFreeModules.ElementMethods.order_ideal`` -- the
  coordinate reading of the chosen basis -- not the module level's image of the
  linear functionals.  The framed level is a subcategory of
  ``Modules(QQ).Free()``, so it is the more specific provider and the rebuild
  rule keeps it; the general ``Modules`` level answers only where no more
  specific level reaches the name, which is why ``ZZ/8`` keeps it.  On ``QQ(i)``
  the two readings agree, so that example states the level only in its
  docstring; the case where they cannot be confused is
  ``tests/modules/test_the_order_ideal_of_a_ring_element_over_its_base_ring.sage``,
  where the dual ``prod_N ZZ`` has no selected generating family in this
  library and the module level therefore cannot answer at all.
* ``__iter__`` on ``QQ(i)`` is
  ``FramedFreeModules.FinitelyGenerated.ParentMethods.__iter__``: the field is a
  finitely generated framed free module over ``QQ``, and its framing's
  coordinates enumerate its points.  ``OwnedRings.Finite.ParentMethods.__iter__``
  enumerates a *finite* ring's points through its selected engine, and the
  general ring states no enumeration at all -- which is the answer for
  ``ZZ['x']``, whose framing has no finite basis, as
  ``tests/rings/test_a_ring_states_no_enumeration_of_its_points.sage`` states.
* ``adic_completion`` is ``OwnedRings.ParentMethods.adic_completion``, the
  ring's inverse limit, not the module's base change to the completed scalar
  ring of ``ModulesWithChosenFinitePresentation.ParentMethods``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_module_level_states_the_order_ideal_of_an_algebra_element() -> None:
    r"""$O_{\mathbf{Q}(i)}(1 + i) = \mathbf{Q}$: the image of evaluation at $1 + i$.

    ``FramedFreeModules.ElementMethods.order_ideal`` answers for an element of
    $\mathbf{Q}(i)$: it is the ideal the coordinates of the chosen basis
    generate, and $1 + i \neq 0$ makes it the unit ideal of $\mathbf{Q}$.  The
    level is stated because the module level's image of the linear functionals
    states an ideal of the same ring as well, and here both readings give the
    same ideal -- so this value alone does not say which of the two answered.
    """
    field = QuadraticField(-1)
    element = field(1 + field.primitive_element())

    assert element.order_ideal() == QQ.ideal(1)


def test_a_finite_ring_enumerates_its_points_through_its_engine() -> None:
    r"""$\mathbf{Z}/8$ is finite, so it states its eight residue classes.

    ``OwnedRings.Finite.ParentMethods.__iter__`` answers -- not the general ring
    level, which states no enumeration of its points, and not the framed free
    module's coordinate iteration, which would list the coefficients of a chosen
    basis.  The ring has eight points, each an element of it and each different
    from the others, and the classes of $0, \ldots, 7$ are exactly those eight
    points: the enumeration is of the ring's whole underlying set, not of a
    generating family of it.
    """
    ring = Zmod(8)
    points = tuple(ring)

    assert int(sum(1 for _ in points)) == int(ring.cardinality())
    assert all(point in ring for point in points)
    assert all(
        point != other
        for position, point in enumerate(points)
        for other in points[:position]
    )
    assert all(ring(residue) in points for residue in range(8))


def test_the_ring_states_the_completion_of_the_field_at_the_zero_ideal() -> None:
    r"""$\lim_n \mathbf{Q}(i)/(0)^n = \mathbf{Q}(i)$: the ring's own completion.

    ``OwnedRings.ParentMethods.adic_completion`` answers.  The module level's
    base change $M \otimes_R \hat{R}$ would need the ideal to be an ideal of the
    module's base ring, and the zero ideal of $\mathbf{Q}(i)$ is not an ideal of
    $\mathbf{Q}$; the ring's inverse limit is defined, and at $(0)$ in a field
    every quotient $\mathbf{Q}(i)/(0)^n$ is the field itself, so the completion
    map is injective and its codomain is the field again.

    The map is stated by what it is decided to be.  ``is_injective`` reads the
    kernel, which is the zero ideal; ``is_surjective`` is undecided for these
    two endpoints, because the decision between infinite sets is not
    implemented, so the test does not claim the map is a bijection.
    """
    field = QuadraticField(-1)
    completion = field.adic_completion(field.ideal(0))
    completion_map = completion.completion_map()

    assert completion.completion_map_kernel() == field.ideal(0)
    assert completion_map.is_injective() is True
    assert completion.is_isomorphic_to(field)


def test_z_x_mod_x_squared_is_free_of_rank_two_hence_torsion_free() -> None:
    r"""$\mathbf{Z}[x]/(x^2)$ is free on $\{1, x\}$ over $\mathbf{Z}$, so it is torsion-free.

    The algebra is free on the two classes of $1$ and $x$: $r(a + bx) = 0$ over
    the integers forces $a = b = 0$, so no nonzero scalar kills a nonzero
    element.  It is also a framed free module over $\mathbf{Z}$ on those two
    classes, and that category and the category of algebras with a chosen
    finite presentation over $\mathbf{Z}$ are neither below the other, so which
    of the two answers is the category order's to say.
    """
    x = ZZ["x"].algebra_generator("x")
    algebra = ZZ["x"].quotient_by_relations([x**2])

    assert algebra.module_rank() == 2
    assert algebra.is_torsion_free() is True


def test_the_framed_level_answers_the_question_the_general_level_left_undecided() -> None:
    r"""On $\mathbf{Z}[x]$ the module questions are answered, not merely asked.

    $\mathbf{Z}[x]$ is free on the monomials, so it is torsion-free: a basis
    element is killed only by a scalar killing its coefficient, and $\mathbf{Z}$
    is a domain.  A nonzero scalar of $\mathbf{Z}$ annihilates no element of
    $\mathbf{Z}[x]$, so $\operatorname{Ann}_{\mathbf{Z}}(\mathbf{Z}[x]) = (0)$,
    and that is the zero ideal of the base ring $\mathbf{Z}$ -- an element of the
    ideals of $\mathbf{Z}$, not a submodule of $\mathbf{Z}[x]$.

    Both answers come from ``FramedFreeModules.ParentMethods``, the level that
    reads the frame, because the module level has no basis to read here.
    """
    line = ZZ["x"]
    ideal = line.annihilator()

    assert line.is_torsion_free() is True
    assert ideal in CommutativeIdeals(ZZ)
    assert ideal == ZZ.ideal(0)


def test_the_free_modules_over_a_domain_and_over_a_field_are_torsion_free() -> None:
    r"""$\mathbf{Q}[x]$, $\mathbf{Z}[x, y]$ and $\mathbf{Q}(i)$ are torsion-free with zero annihilator.

    Each is free on a chosen family, over a field for two of them and over
    $\mathbf{Z}$ for the third, so $r m = 0$ with $r \neq 0$ reads $r a_s = 0$
    in every coefficient and forces $m = 0$: no nonzero scalar kills an
    element.  The scalars annihilating every element are therefore none, and
    their ideal is the zero ideal of the base ring -- an element of that ring's
    ideals, not a submodule of the module.
    """
    for module in (QQ["x"], ZZ["x", "y"], QuadraticField(-1)):
        ring = module.base_ring()
        ideal = module.annihilator()

        assert module.is_torsion_free() is True
        assert ideal in CommutativeIdeals(ring)
        assert ideal == ring.ideal(0)


def test_a_free_module_over_a_ring_with_zero_divisors_is_torsion_free() -> None:
    r"""$\mathbf{Z}/4[x]$ is torsion-free although $2 \cdot (2x) = 0$ there.

    An element is torsion when a non-zero-divisor kills it, and the
    non-zero-divisors of $\mathbf{Z}/4$ are its units, which kill nothing: the
    scalar $2$ is a zero-divisor, so $2 \cdot (2x) = 0$ is not a torsion
    element's annihilation.  Free on the monomials, the ring is therefore
    torsion-free, and the level answering is the framed free module's -- the
    one that reads the monomials.  $\mathbf{Z}/4[x]/(x^2)$, free on
    $\{1, x\}$ over the same ring, is torsion-free for the same reason, and
    there the algebra level answers: the two categories are incomparable, and
    neither level asks for a domain, which is not a hypothesis of this reading.
    """
    line = Zmod(4)["x"]
    x = line.algebra_generator("x")
    element = 2 * x
    truncated = line.quotient_by_relations([x**2])

    assert 2 * element == line.zero()
    assert element != line.zero()
    assert line.is_torsion_free() is True
    assert truncated.is_torsion_free() is True
