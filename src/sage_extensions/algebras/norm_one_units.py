r"""Norm-one units of an order in a central simple algebra, from generators of its unit group.

Let ``Lambda`` be an order of degree ``d`` over ``K`` with ``C = (Lambda meet K)^x``.
``H = nrd^{-1}(C^d)`` is computed by a Schreier transversal over the actual image of
``nrd`` in the finite group ``O_K^x / C^d``. Each generator ``h`` of ``H`` is written
``k c`` with ``c`` in ``C``, ``c^d = nrd(h)`` and ``nrd(k) = 1``. The ``k`` together
with the ``c`` in ``C`` satisfying ``c^d = 1`` generate ``Lambda^1``. The method and its
proof are in sage-indefinite-port issue #57, section B; the unit group input comes from
Braun, Coulangeon, Nebe and Schoennenbeck, J. Algebra 435 (2015).
"""

from sage.matrix.constructor import matrix
from sage.modules.free_module import FreeModule
from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ


def _unit_logarithms(field):
    r"""Return ``(log, n, torsion_relation, roots)`` for the unit group of ``field``."""
    if field is QQ:
        return (lambda u: [0 if u == 1 else 1] if abs(u) == 1 else _not_a_unit(u)), 1, [2], [QQ.one(), -QQ.one()]
    group = field.unit_group()
    rank = group.ngens()
    order = group.torsion_generator().order()
    return (
        lambda u: [int(e) for e in group(u).exponents()],
        rank,
        [int(order)] + [0] * (rank - 1),
        list(field.roots_of_unity()),
    )


def _not_a_unit(value):
    raise ValueError(f"{value} is not a unit")


def norm_one_generators(units, central_generators, degree, reduced_norm, base_field):
    r"""Return generators of the reduced-norm-one units of the order.

    ``units`` generates ``Lambda^x``, ``central_generators`` generates ``C``.
    """
    log, rank, torsion_relation, roots = _unit_logarithms(base_field)
    central_logs = [log(c) for c in central_generators]
    ambient = FreeModule(ZZ, rank)
    relation = ambient(torsion_relation)
    powers = [ambient([degree * entry for entry in row]) for row in central_logs]
    quotient = ambient / ambient.span([relation, *powers])
    key = lambda element: tuple(quotient(ambient(log(reduced_norm(element)))).vector())

    one = units[0].parent().one()
    representatives = {key(one): one}
    frontier = [one]
    while frontier:
        following = []
        for element in frontier:
            for unit in units:
                image = element * unit
                label = key(image)
                if label not in representatives:
                    representatives[label] = image
                    following.append(image)
        frontier = following

    generators = []
    system = matrix(ZZ, [relation, *powers])
    for element in representatives.values():
        for unit in units:
            image = element * unit
            schreier = image * ~representatives[key(image)]
            if schreier == one:
                continue
            target = reduced_norm(schreier)
            coefficients = system.solve_left(ambient(log(target)))
            root = base_field.one()
            for exponent, generator in zip(list(coefficients)[1:], central_generators, strict=True):
                root *= generator ** int(exponent)
            if root**degree != target:
                raise ValueError(f"the root {root} does not have power {target}")
            generators.append(schreier * ~root)

    span = ambient.span([relation, *(ambient(row) for row in central_logs)])
    central_kernel = [root for root in roots if root**degree == 1 and root != 1 and ambient(log(root)) in span]
    return tuple(generators), tuple(central_kernel)

