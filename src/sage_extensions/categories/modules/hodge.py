r"""Determinant, Poincaré-duality, and Hodge constructions on finite free modules."""

from sage_extensions.categories.modules.pure.modules import (
    FinitelyGeneratedFreeModules,
    Modules,
)
from sage_extensions.categories.modules.framed.framed_free_modules import (
    FramedFreeModules,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedIntegralDomains,
    OwnedRings,
)


def _require_finite_free(module) -> int:
    r"""Select the currently implemented finite framed exterior computations.

    These algorithms use a finite free framing.  The assertion does not deny
    determinant or duality constructions on other finite projective modules.
    """
    ring = module.base_ring()
    assert ring in OwnedRings().Commutative(), (
        f"the current determinant, Poincaré duality and Hodge computations on {module} "
        f"require a declared commutative coefficient ring, but the base is {ring}"
    )
    assert (
        module in FinitelyGeneratedFreeModules(ring)
        and module in FramedFreeModules(ring)
    ), (
        f"the current determinant, Poincaré duality and Hodge computations on {module} "
        "require a selected finite free framing; no computation for this represented module is selected"
    )
    rank = module.module_rank()
    assert rank.is_finite() is True, (
        f"the selected determinant, Poincaré duality and Hodge computation on {module} "
        f"requires a finite represented rank, but its rank is {rank}"
    )
    return int(rank)


from sage_extensions.categories.modules.powers import (
    _degree,
    _exterior_word as _power_word,
)


def _power_label(word: tuple, degree: int):
    if degree == 0:
        return 0
    if degree == 1:
        return word[0]
    return tuple(word)


def _unique_generator(module):
    labels = tuple(module.module_generating_set())
    if len(labels) != 1:
        raise ValueError(
            f"{module} is not free of rank one: its chosen generating set has {len(labels)} elements"
        )
    return module.module_generator(labels[0])


def _determinant_line(module):
    r"""Return ``det(module) = Lambda^rank(module) module``."""

    rank = _require_finite_free(module)
    return module.exterior_power(rank)


def _exterior_forms(module, degree):
    r"""Return ``Lambda^degree(module^vee)``."""

    rank = _require_finite_free(module)
    degree = _degree(degree)
    if degree < 0 or degree > rank:
        raise ValueError(f"no exterior power of degree {degree} of {module}: the degree must lie in [0, {rank}], the rank of {module}")
    return module.dual_module().exterior_power(degree)


def _volume_trivialization(module, forward, inverse):
    r"""Return the stated isomorphism ``det(module) ~= R``.

    No orientation or volume is inferred from a framing.  This constructor
    merely verifies two already represented mutually inverse module maps.
    """

    determinant = module.determinant_line()
    scalars = module.base_ring().regular_module()
    if forward.domain() is not determinant or forward.codomain() is not scalars:
        raise ValueError(
            f"{forward} is not a map det({module}) -> {module.base_ring()}: it is a map "
            f"{forward.domain()} -> {forward.codomain()}"
        )
    if inverse.domain() is not scalars or inverse.codomain() is not determinant:
        raise ValueError(
            f"{inverse} is not a map {module.base_ring()} -> det({module}): it is a map "
            f"{inverse.domain()} -> {inverse.codomain()}"
        )
    modules = Modules(module.base_ring())
    result = modules.Core().Mor(determinant, scalars)(forward, inverse)
    if result not in modules.Iso(determinant, scalars):
        raise ValueError(
            f"{forward} and {inverse} are not mutually inverse, so they do not give an isomorphism "
            f"det({module}) -> {module.base_ring()}"
        )
    return result


def _framing_volume_trivialization(module, unit=None):
    r"""Explicitly trivialize ``det(M)`` using the selected framing.

    This is deliberately opt-in: a chosen module framing is not silently
    treated as orientation data.  ``unit`` rescales the selected top wedge and
    must be a unit of the coefficient ring.
    """
    determinant = module.determinant_line()
    ring = module.base_ring()
    scalars = ring.regular_module()
    top = _unique_generator(determinant)
    one = _unique_generator(scalars)
    unit = ring.one() if unit is None else ring(unit)
    match unit.is_unit():
        case True:
            pass
        case False:
            raise ValueError(
                f"cannot trivialize det({module}) by sending its generator to {unit}: {unit} is not a unit of {ring}"
            )
        case _:
            assert False, (
                f"the selected framing-volume computation on {module} cannot decide whether {unit} is a unit of {ring}"
            )
    inverse_unit = unit.inverse_of_unit()
    forward = determinant.module_category().Mor(determinant, scalars)(
        {next(iter(determinant.module_generating_set())): scalars.scalar_multiple(unit, one)}
    )
    inverse = scalars.module_category().Mor(scalars, determinant)(
        {next(iter(scalars.module_generating_set())): determinant.scalar_multiple(inverse_unit, top)}
    )
    return module.volume_trivialization(forward, inverse)


def _volume_scalars(module, volume):

    determinant = module.determinant_line()
    scalars = module.base_ring().regular_module()
    if volume not in Modules(module.base_ring()).Iso(determinant, scalars):
        raise TypeError(
            f"{volume} is not an isomorphism det({module}) -> {module.base_ring()}, so it is not a volume form on {module}"
        )
    top = _unique_generator(determinant)
    one = _unique_generator(scalars)
    forward_coordinates = scalars(volume(top)).to_vector()
    inverse_coordinates = determinant.framing_morphism().lift(volume.inverse()(one))
    scalar_label = next(iter(scalars.module_generating_set()))
    determinant_label = next(iter(determinant.module_generating_set()))
    return (
        forward_coordinates(scalar_label),
        inverse_coordinates(determinant_label),
    )


def _poincare_duality(module, volume, degree):
    r"""Return ``Lambda^k M ~= Lambda^(n-k) M^vee`` from ``volume``."""

    rank = _require_finite_free(module)
    degree = _degree(degree)
    if degree < 0 or degree > rank:
        raise ValueError(f"no Poincaré duality in degree {degree} on {module}: the degree must lie in [0, {rank}], the rank of {module}")
    volume_scalar, inverse_volume_scalar = _volume_scalars(module, volume)
    dual = module.dual_module()
    source = module.exterior_power(degree)
    target = dual.exterior_power(rank - degree)
    module_labels = tuple(module.module_generating_set())
    positions = {label: index for index, label in enumerate(module_labels)}

    forward_images = {}
    for source_label in source.module_generating_set():
        word = _power_word(source_label, degree)
        occupied = {positions[label] for label in word}
        complement = tuple(
            label
            for index, label in enumerate(module_labels)
            if index not in occupied
        )
        complement_positions = tuple(positions[label] for label in complement)
        inversions = sum(
            left > right
            for left in tuple(positions[label] for label in word)
            for right in complement_positions
        )
        coefficient = -volume_scalar if inversions % 2 else volume_scalar
        target_label = _power_label(complement, rank - degree)
        forward_images[source_label] = target.scalar_multiple(
            coefficient,
            target.module_generator(target_label),
        )

    inverse_images = {}
    for target_label in target.module_generating_set():
        complement = _power_word(target_label, rank - degree)
        complement_positions = {positions[label] for label in complement}
        word = tuple(
            label
            for index, label in enumerate(module_labels)
            if index not in complement_positions
        )
        inversions = sum(
            left > right
            for left in tuple(positions[label] for label in word)
            for right in tuple(positions[label] for label in complement)
        )
        coefficient = (
            -inverse_volume_scalar if inversions % 2 else inverse_volume_scalar
        )
        source_label = _power_label(word, degree)
        inverse_images[target_label] = source.scalar_multiple(
            coefficient,
            source.module_generator(source_label),
        )

    forward = source.module_category().Mor(source, target)(forward_images)
    inverse = target.module_category().Mor(target, source)(inverse_images)
    modules = Modules(module.base_ring())
    # Complementary wedges have inverse signs, and the two volume scalars
    # come from the retained volume isomorphism and its actual inverse.
    return modules.Core().Mor(source, target)._from_known_inverse_pair(
        forward, inverse
    )


def _algebraic_correlation_morphism(metric, *, injective=False):
    r"""Return ``g^flat : M -> M^vee`` for a scalar-valued bilinear metric."""

    if metric.value_module() is not metric.base_ring():
        raise TypeError(
            f"the form on {metric} takes values in {metric.value_module()}, not in its base ring "
            f"{metric.base_ring()}, so it has no correlation {metric} -> dual module"
        )
    ring = metric.base_ring()
    if metric not in FramedFreeModules(ring):
        raise TypeError(
            f"cannot compute the correlation of {metric}: this needs a free {ring}-module with a chosen basis, "
            f"but {metric} is only known to be in {metric.category()}"
        )
    dual = metric.dual_module()
    source_labels = metric.module_generating_set()

    def correlation_from_generator_images(images):
        if injective:
            # The linear extension of images of a basis is linear, and a
            # nondegenerate form is one whose correlation has zero kernel.
            return Modules(ring).Mono(metric, dual)._from_constructed_embedding(
                images,
                elementwise=False,
            )
        return metric.module_category().Mor(metric, dual)(images)

    match source_labels.cardinality().is_finite():
        case True:
            dual_labels = tuple(dual.module_generating_set())

            def finite_generator_image(source_label):
                source_generator = metric.module_generator(source_label)
                coefficients = {}
                for dual_label in dual_labels:
                    coefficient = metric.b(
                        source_generator,
                        metric.module_generator(dual_label),
                    )
                    if (coefficient == ring.zero()) is not True:
                        coefficients[dual_label] = coefficient
                return dual.linear_combination(coefficients)

            return correlation_from_generator_images(finite_generator_image)
        case False:
            from sage_extensions.categories.modules.framed.formed.form_modules import (
                _as_module_element,
            )

            def infinite_generator_image(source_label):
                source_generator = metric.module_generator(source_label)
                return dual(
                    lambda target_label: _as_module_element(
                        ring,
                        ring,
                        metric.b(
                            source_generator,
                            metric.module_generator(source_labels(target_label)),
                        )
                    )
                )

            return correlation_from_generator_images(infinite_generator_image)


def _correlation_isomorphism(metric):
    r"""Return the perfect correlation ``M ~= M^vee`` for a unimodular form."""

    _require_finite_free(metric)
    assert metric.value_module() is metric.base_ring(), (
        f"the selected scalar correlation-inverse computation on {metric} requires values in {metric.base_ring()}; "
        f"no identification of its value module {metric.value_module()} with that scalar module is selected"
    )
    match metric.is_unimodular():
        case True:
            pass
        case False:
            raise ValueError(
                f"the form on {metric} is not unimodular, so its correlation {metric} -> dual module is not an "
                f"isomorphism and there is no Hodge star over {metric.base_ring()}; use the Hodge star over the fraction field"
            )
        case _:
            assert False, (
                f"the selected correlation-inverse computation cannot decide whether the scalar pairing on {metric} is perfect"
            )
    forward = metric.algebraic_correlation_morphism()
    dual = forward.codomain()
    inverse = dual.module_category().Mor(dual, metric)(
        {
            label: forward.lift(dual.module_generator(label))
            for label in dual.module_generating_set()
        }
    )
    modules = Modules(metric.base_ring())
    # Lift supplies actual preimages of the target basis.  Their linear
    # extension is a right inverse, and bijectivity makes it a left inverse.
    return modules.Core().Mor(metric, dual)._from_known_inverse_pair(
        forward, inverse
    )


def _hodge_discriminant(metric, volume):
    r"""Return ``Delta_(g,eps) = det(g) / eps(e_1 wedge ... wedge e_n)^2``."""
    _require_finite_free(metric)
    _volume_scalar, inverse_volume_scalar = _volume_scalars(metric, volume)
    return metric.determinant() * inverse_volume_scalar**2


def _hodge_star(metric, volume, degree):
    r"""Return the Hodge isomorphism on covariant ``degree``-forms.

    For a perfect metric this is the categorical composite

    ``Lambda^k M^vee --Lambda^k(g^sharp)--> Lambda^k M --PD--> Lambda^(n-k) M^vee``.
    """

    rank = _require_finite_free(metric)
    degree = _degree(degree)
    if degree < 0 or degree > rank:
        raise ValueError(f"no Hodge star on {degree}-forms of {metric}: the degree must lie in [0, {rank}], the rank of {metric}")
    correlation = metric.correlation_isomorphism()
    poincare = metric.poincare_duality(volume, degree)
    raise_metric = correlation.inverse().forward().exterior_power(degree)
    lower_metric = correlation.forward().exterior_power(degree)
    forward = poincare.forward() * raise_metric
    inverse = lower_metric * poincare.inverse().forward()
    source = metric.exterior_forms(degree)
    target = metric.exterior_forms(rank - degree)
    modules = Modules(metric.base_ring())
    return modules.Core().Mor(source, target)._from_known_inverse_pair(
        forward, inverse
    )


def _multivector_hodge_star(metric, volume, degree):
    r"""Return the integral multivector Hodge map ``Lambda^k M -> Lambda^(n-k) M``.

    Unlike the covariant-form Hodge star, this direction uses ``g^flat`` and
    therefore does not require the metric to be perfect over the coefficient
    ring.  It need not be an isomorphism for a non-unimodular metric.
    """

    rank = _require_finite_free(metric)
    degree = _degree(degree)
    if degree < 0 or degree > rank:
        raise ValueError(f"no Hodge star on {degree}-vectors of {metric}: the degree must lie in [0, {rank}], the rank of {metric}")
    correlation = metric.algebraic_correlation_morphism()
    poincare_complement = metric.poincare_duality(volume, rank - degree)
    lower_metric = correlation.exterior_power(degree)
    forward = poincare_complement.inverse() * lower_metric
    source = metric.exterior_power(degree)
    target = metric.exterior_power(rank - degree)
    if forward.domain() is not source or forward.codomain() is not target:
        raise ArithmeticError(
            f"the Hodge star on {degree}-vectors of {metric} should be a map {source} -> {target}, "
            f"but it is a map {forward.domain()} -> {forward.codomain()}"
        )
    return forward


def _hodge_star_over_fraction_field(metric, volume, degree):
    r"""Return the covariant-form Hodge isomorphism after ``R -> Frac(R)``.

    This is the explicit scalar-extension path for a nondegenerate but
    non-unimodular metric.  The returned isomorphism lives over the fraction
    field; it is never reported as an integral Hodge star on ``metric``.
    """

    _require_finite_free(metric)
    degree = _degree(degree)
    ring = metric.base_ring()
    assert ring in OwnedIntegralDomains(), (
        f"the selected fraction-field Hodge computation on {metric} requires a declared integral domain, "
        f"but its base ring is {ring}"
    )
    ring_map = ring.fraction_field_map()
    fraction_field = ring_map.codomain()
    if fraction_field is ring:
        return metric.hodge_star(volume, degree)
    changed_metric = metric.base_change(ring_map)
    volume_scalar, _inverse_volume_scalar = _volume_scalars(metric, volume)
    changed_volume = changed_metric.framing_volume_trivialization(
        unit=ring_map(volume_scalar),
    )
    # Perfection is decided by the actual extended correlation.  Over the
    # fraction field this is exactly the generic-fibre nondegeneracy needed.
    return changed_metric.hodge_star(changed_volume, degree)
