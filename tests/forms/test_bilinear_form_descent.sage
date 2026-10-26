r"""Descent of a bilinear form to a quotient by vectors in its radical.

A bilinear form \(b\) on \(M\) descends along \(\rho\colon N\to M\) to
\(\operatorname{coker}\rho\) exactly when both \(b(\rho(n), m) = 0\) and
\(b(m, \rho(n)) = 0\) for all \(n, m\); the descended form is \(\bar b(\bar x,\bar y) = b(x,y)\). The Gram
\(\begin{pmatrix}1&1\\1&1\end{pmatrix}\) on \(\mathbf Z^2\) has radical
\(\mathbf Z(e_0-e_1)\), so it descends along \(1\mapsto e_0-e_1\) to
\(\mathbf Z^2/\mathbf Z(e_0-e_1)\cong\mathbf Z\), where the classes of \(e_0\) and \(e_1\) coincide and have square
\(b(e_0,e_0)=1\).  It does not descend along \(1\mapsto e_0\), since \(b(e_0,e_0)=1\ne0\).
Its pullback along \(1\mapsto e_0+e_1\) has value \(b(e_0+e_1,e_0+e_1)=4\).
"""

from sage_extensions.all import *


def test_a_rational_valued_form_descends_to_the_quotient_by_its_radical() -> None:
    module = ZZ.free_module(2)
    first, second = module.module_generators()
    line = ZZ.free_module(1)
    radical = line.Mor(module)((first - second,))
    form = module.bilinear_forms(QQ)([[1, 1], [1, 1]])
    identity = QQ.Mor(QQ).identity()
    descended = form.descend_along(radical, identity)
    first_class, second_class = descended.module().module_generators()

    assert form.descends_along(radical, identity)
    assert not form.descends_along(line.Mor(module)((first,)), identity)
    assert descended(first_class, first_class) == 1
    assert descended(first_class, second_class) == 1


def test_nonsymmetric_form_descends_when_relations_vanish_in_both_slots() -> None:
    module = QQ ^ 3
    relation_module = QQ ^ 1
    labels = tuple(module.module_generating_set())
    inclusion = relation_module.module_category().Mor(relation_module, module)(
        lambda label: module.module_generator(labels[0])
    )
    form = module.bilinear_forms(QQ)(
        [[0, 0, 0], [0, 1, 2], [0, 3, 4]]
    )
    identity = QQ.module_category().Mor(QQ, QQ).identity()

    assert form.descends_along(inclusion, identity)
    descended = form.descend_along(inclusion, identity)
    first, second = descended.module().module_generators()
    assert descended(first, first) == 1
    assert descended(first, second) == 2
    assert descended(second, first) == 3
    assert descended(second, second) == 4


def test_descent_does_not_identify_quotient_generator_labels_with_source_labels() -> None:
    module = QQ.free_module(("discarded", "retained"))
    relation_module = QQ.free_module(("relation",))
    discarded = module.module_generator("discarded")
    inclusion = relation_module.module_category().Mor(relation_module, module)(
        lambda label: discarded
    )
    form = module.bilinear_forms(QQ)([[0, 0], [0, 7]])
    identity = QQ.module_category().Mor(QQ, QQ).identity()

    descended = form.descend_along(inclusion, identity)
    assert descended.module().module_rank() == 1
    (generator,) = descended.module().module_generators()
    assert descended(generator, generator) == 7


def test_descent_checks_relations_after_projecting_form_values() -> None:
    module = ZZ.free_module(2)
    labels = tuple(module.module_generating_set())
    relation_module = ZZ.free_module(1)
    relation = module.module_generator(labels[0])
    inclusion = relation_module.module_category().Mor(relation_module, module)(
        lambda label: relation
    )
    form = module.bilinear_forms(ZZ)([[2, 2], [2, 1]])
    values = ZZ.ideal(ZZ(2)).quotient_ring()
    projection = ZZ.Mor(values)(lambda value: values(value))

    assert form(relation, relation) == 2
    retained = module.module_generator(labels[1])
    assert form(relation, retained) == form(retained, relation) == 2
    assert projection(form(relation, retained)) == values.zero()
    assert not form.descends_along(inclusion, ZZ.Mor(ZZ).identity())
    assert form.descends_along(inclusion, projection)
    descended = form.descend_along(inclusion, projection)
    (generator,) = descended.module().module_generators()
    assert descended(generator, generator) == values(1)
    shifted = retained + relation
    assert form(shifted, retained) == 3
    assert form(retained, shifted) == 3
    assert form(shifted, shifted) == 7
    assert projection(form(shifted, retained)) == descended(generator, generator)
    assert projection(form(retained, shifted)) == descended(generator, generator)
    assert projection(form(shifted, shifted)) == descended(generator, generator)


def test_descent_pairing_is_defined_on_a_torsion_cokernel() -> None:
    module = ZZ.free_module(2)
    first, second = module.module_generators()
    relation_module = ZZ.free_module(1)
    inclusion = relation_module.module_category().Mor(relation_module, module)(
        lambda label: 2 * first
    )
    form = module.bilinear_forms(ZZ)([[1, 0], [0, 3]])
    values = ZZ.ideal(ZZ(2)).quotient_ring()
    projection = ZZ.Mor(values)(lambda value: values(value))

    assert form.descends_along(inclusion, projection)
    descended = form.descend_along(inclusion, projection)
    torsion_class = next(
        generator
        for generator in descended.module().module_generators()
        if 2 * generator == descended.module().zero()
        and generator != descended.module().zero()
    )
    assert 2 * torsion_class == descended.module().zero()
    assert torsion_class != descended.module().zero()
    assert descended(torsion_class, torsion_class) == values(1)


def test_the_form_of_a_degenerate_lattice_descends_only_along_its_radical() -> None:
    lattice = Lattices(ZZ)([[1, 1], [1, 1]])
    form = lattice.form()
    module = form.module()
    first, second = module.module_generators()
    line = ZZ.free_module(1)
    identity = ZZ.Mor(ZZ).identity()

    assert form.descends_along(line.Mor(module)((first - second,)), identity)
    assert not form.descends_along(line.Mor(module)((first,)), identity)


def test_the_descended_form_of_a_degenerate_lattice() -> None:
    lattice = Lattices(ZZ)([[1, 1], [1, 1]])
    form = lattice.form()
    module = form.module()
    first, second = module.module_generators()
    line = ZZ.free_module(1)
    descended = form.descend_along(line.Mor(module)((first - second,)), ZZ.Mor(ZZ).identity())
    first_class, second_class = descended.module().module_generators()

    assert descended(first_class, first_class) == 1
    assert descended(first_class, second_class) == 1


def test_the_pullback_of_a_lattice_form_along_the_diagonal() -> None:
    lattice = Lattices(ZZ)([[1, 1], [1, 1]])
    form = lattice.form()
    module = form.module()
    first, second = module.module_generators()
    line = ZZ.free_module(1)
    (generator,) = line.module_generators()
    pulled_back = form.pullback(line.Mor(module)((first + second,)))

    assert pulled_back(generator, generator) == 4
