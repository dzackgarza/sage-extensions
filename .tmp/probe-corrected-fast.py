r"""#603: a matrix-level correction search, checked against the current one.

The current search builds a rational Eichler transvection and restricts it to
the lattice for every representative of the box.  The corrected map is a rank
two update of the rational lift's own matrix, so the same integrality decision
is a matrix sum.  For every representative of every specimen this prints
whether the two decisions agree and how long each search takes.
"""

import time

from sage.matrix.constructor import matrix as engine_matrix
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ

import sage_extensions.categories.lattices as lattices_module
from sage_extensions.all import Lattices, ZZ
from sage_extensions.categories.lattice_morphisms import _module_matrix
from sage_extensions.categories.modules.pure.modules import ModulesOverIntegralDomains

START = time.perf_counter()


def stamp(label):
    print(f"[{time.perf_counter() - START:8.3f}s] {label}")


SPECIMENS = (
    ("U(2)+<2>", [[0, 2, 0], [2, 0, 0], [0, 0, 2]]),
    ("U(2)+<3>", [[0, 2, 0], [2, 0, 0], [0, 0, 3]]),
    ("U(3)+<3>", [[0, 3, 0], [3, 0, 0], [0, 0, 3]]),
    (
        "rank five",
        [
            [0, 2, 0, 0, 0],
            [2, 0, 1, 0, 0],
            [0, 1, 0, 2, 0],
            [0, 0, 2, 0, 0],
            [0, 0, 0, 0, -2],
        ],
    ),
)


def to_rational(entry):
    r"""A rational number from a coefficient of the owned rings."""
    numerator = getattr(entry, "numerator", entry)
    numerator = numerator() if callable(numerator) else numerator
    denominator = getattr(entry, "denominator", 1)
    denominator = denominator() if callable(denominator) else denominator
    return SageQQ(int(numerator)) / SageQQ(int(denominator))


def setup(reduction, isometry):
    r"""The current method's own setup, returned as one bundle."""
    lattice = reduction.isotropic_embedding().codomain()
    ring = lattice.base_ring()
    line = reduction.isotropic_sublattice()
    marked = line.embedded_module_generators()[line.module_generating_set()[0]]
    divisibility = int(marked.div())
    fraction_map = ring.fraction_field_map()
    rational = lattice.base_change(fraction_map)
    rational_ring = rational.base_ring()
    rationalize = ModulesOverIntegralDomains(ring)(lattice).generic_fibre_map()
    extension, denominator = reduction._rational_pointwise_levi_lift(isometry)
    scale = divisibility * int(denominator)
    labels = tuple(lattice.module_generating_set())
    perpendicular = reduction.orthogonal_complement()
    jbasis = tuple(
        perpendicular.inclusion()(perpendicular.module_generator(label))
        for label in perpendicular.module_generating_set()
    )
    width = len(labels)

    def coordinates_of(element):
        values = element.to_vector()
        return [int(values(label)) for label in labels]

    jrows = engine_matrix(SageQQ, [coordinates_of(vector) for vector in jbasis])
    gram = jrows * jrows.transpose()
    inverse = gram.inverse()

    def on_the_perpendicular(element):
        row = engine_matrix(SageQQ, 1, width, coordinates_of(element))
        return row * jrows.transpose() * inverse

    parameters = engine_matrix(
        SageZZ,
        [
            [int(value) * scale for value in on_the_perpendicular(parameter)[0]]
            for parameter in reduction._pointwise_kernel_parameter_vectors()
        ],
    )
    diagonal = parameters.hermite_form()
    counts = [int(diagonal[index, index]) for index in range(diagonal.nrows())]

    rational_labels = tuple(rational.module_generating_set())
    assert len(rational_labels) == width, (rational_labels, labels)

    def rational_image(element):
        start = time.perf_counter()
        value = extension(rationalize(element).underlying_element())
        elapsed[0] += time.perf_counter() - start
        coordinates = value.to_vector()
        return [to_rational(coordinates(label)) for label in rational_labels]

    elapsed = [0.0]
    extension_of_generators = [rational_image(lattice.module_generator(label)) for label in labels]
    extension_of_marked = rational_image(marked)
    extension_of_basis = [rational_image(vector) for vector in jbasis]
    print(f"      nine evaluations of the lift: {elapsed[0]:8.3f}s")
    return {
        "extension_of_generators": extension_of_generators,
        "extension_of_marked": extension_of_marked,
        "extension_of_basis": extension_of_basis,
        "lattice": lattice,
        "ring": ring,
        "marked": marked,
        "divisibility": divisibility,
        "rational": rational,
        "rational_ring": rational_ring,
        "rationalize": rationalize,
        "extension": extension,
        "denominator": denominator,
        "scale": scale,
        "labels": labels,
        "jbasis": jbasis,
        "coordinates_of": coordinates_of,
        "gram": gram,
        "lattice_gram": engine_matrix(
            SageQQ,
            [[SageQQ(int(lattice.b(lattice.module_generator(left), lattice.module_generator(right)))) for right in labels] for left in labels],
        ),
        "jbasis_coordinates": [coordinates_of(vector) for vector in jbasis],
        "counts": counts,
    }


def slow(bundle):
    lattice = bundle["lattice"]
    ring = bundle["ring"]
    rational = bundle["rational"]
    rational_ring = bundle["rational_ring"]
    rationalize = bundle["rationalize"]
    extension = bundle["extension"]
    scale = bundle["scale"]
    jbasis = bundle["jbasis"]
    rational_marked = rationalize(bundle["marked"]).underlying_element()
    answers = []
    for representative in lattices_module._representatives_of_the_box(bundle["counts"]):
        combination = sum(
            (
                lattice.scalar_multiple(ring(int(value)), vector)
                for value, vector in zip(representative, jbasis, strict=True)
                if value
            ),
            lattice.zero(),
        )
        rational_parameter = rational.scalar_multiple(
            rational_ring.one() / rational_ring(scale),
            rationalize(combination).underlying_element(),
        )
        corrected = extension * rational.eichler_transvection(rational_marked, rational_parameter)
        answers.append(corrected.integral_restriction(lattice, lattice) is not None)
    return answers


def fast(bundle, describe=False):
    r"""The same decision, from the rank-two update of the lift's own matrix."""
    width = len(bundle["labels"])
    gram = bundle["lattice_gram"]
    scale = bundle["scale"]
    marked_column = engine_matrix(SageQQ, width, 1, bundle["extension_of_marked"])
    basis_images = [
        engine_matrix(SageQQ, width, 1, coordinates)
        for coordinates in bundle["extension_of_basis"]
    ]
    generator_images = [
        engine_matrix(SageQQ, width, 1, coordinates)
        for coordinates in bundle["extension_of_generators"]
    ]
    pairing_with_marked = gram * marked_column
    if describe:
        print("   the lift fixes the marked vector:", bundle["extension_of_marked"] == bundle["coordinates_of"](bundle["marked"]))
        print("   the indecomposable box of the lift:", bundle["counts"])
    answers = []
    for representative in lattices_module._representatives_of_the_box(bundle["counts"]):
        image_of_parameter = sum(
            (
                SageQQ(int(value)) * column
                for value, column in zip(representative, basis_images, strict=True)
            ),
            engine_matrix(SageQQ, width, 1, [SageQQ(0)] * width),
        ) / SageQQ(scale)
        parameter = sum(
            (
                SageQQ(int(value)) * column
                for value, column in zip(representative, [engine_matrix(SageQQ, width, 1, [SageQQ(entry) for entry in bundle["jbasis_coordinates"][position]]) for position in range(len(bundle["jbasis_coordinates"]))], strict=True)
            ),
            engine_matrix(SageQQ, width, 1, [SageQQ(0)] * width),
        ) / SageQQ(scale)
        half_norm = (parameter.transpose() * gram * parameter)[0, 0] / SageQQ(2)
        integral = True
        for column in generator_images:
            image = column - (parameter.transpose() * gram * column)[0, 0] * marked_column + (marked_column.transpose() * gram * column)[0, 0] * (image_of_parameter - half_norm * marked_column)
            if not all(entry.is_integer() for entry in image.list()):
                integral = False
                break
        answers.append(integral)
    return answers


for name, gram in SPECIMENS:
    print(f"===== {name} =====")
    lattice = Lattices(ZZ)(gram)
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[0])
    reduction = lattice.primitive_isotropic_subobject(vector).isotropic_reduction()
    quotient = reduction.quotient_lattice()
    generators = tuple(quotient.O().group_generators())
    print("   rank:", lattice.module_rank(), "div:", vector.div(), "K_I rank:", quotient.module_rank(), "generators:", len(generators))
    for index, generator in enumerate(generators):
        bundle = setup(reduction, generator)
        print(f"   generator {index}: scale {bundle['scale']} box {bundle['counts']}")
        start = time.perf_counter()
        slow_answers = slow(bundle)
        slow_time = time.perf_counter() - start
        start = time.perf_counter()
        fast_answers = fast(bundle, describe=(index == 0))
        fast_time = time.perf_counter() - start
        agreement = slow_answers == fast_answers
        print(f"      slow {slow_time:8.3f}s -> {sum(slow_answers)} of {len(slow_answers)} integral")
        print(f"      fast {fast_time:8.3f}s -> {sum(fast_answers)} of {len(fast_answers)} integral")
        print(f"      agree: {agreement}")
        if not agreement:
            for position, (left, right) in enumerate(zip(slow_answers, fast_answers, strict=True)):
                if left != right:
                    print(f"      first disagreement at {position}: slow {left} fast {right}")
                    break

stamp("done")
