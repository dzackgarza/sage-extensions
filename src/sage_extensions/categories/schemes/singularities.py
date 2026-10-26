r"""Local algebra invariants of supported hypersurface singularities."""
from sage.libs.singular.function import lib as singular_lib
from sage.libs.singular.function import singular_function
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.categories.algebras.algebras import Algebras
from sage_extensions.categories.abstract_categories.mor_categories import CategoricalIsomorphism
from sage_extensions.categories.algebras.free_algebras import (
    SymmetricAlgebras,
)
from sage_extensions.categories.rings.commutative_ideals import _from_engine_ideal
from sage_extensions.categories.rings.ring_foundation import _owned_engine_element
from sage_extensions.categories.rings.ring_foundation import (
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.indexed_families import finite_indexed_family


def _parse_ade_type(ade_type):
    r"""Return ``(letter, index)`` for a supported ADE label.

    Python-syntax ingress: a pair is read by its sequence pattern, and a label
    such as ``"E6"`` by its letter and index.
    """
    match ade_type:
        case (letter, index):
            return str(letter).upper(), int(index)
        case _:
            label = str(ade_type).strip().upper()
            assert label[1:].isdigit(), (
                f"an ADE type is written as a letter A, D or E followed by an index, such as E6, "
                f"but {ade_type!r} is not"
            )
            return label[0], int(label[1:])


def _ade_normal_form_equation(polynomial_ring, ade_type):
    r"""Return the selected plane-curve ADE normal form in ``k[x,y]``."""
    x, y = tuple(polynomial_ring.algebra_generators())
    letter, index = _parse_ade_type(ade_type)
    match letter:
        case "A":
            assert index >= 1, f"the singularity A_n needs n >= 1, but n = {index}"
            return x**2 + y ** (index + 1)
        case "D":
            assert index >= 4, f"the singularity D_n needs n >= 4, but n = {index}"
            return x**2 * y + y ** (index - 1)
        case "E":
            match index:
                case 6:
                    return x**3 + y**4
                case 7:
                    return x**3 + x * y**3
                case 8:
                    return x**3 + y**5
                case _:
                    raise ValueError(
                        f"the simple plane curve singularities of type E are E6, E7 and E8, not E{index}"
                    )
        case _:
            raise ValueError(
                f"a simple plane curve singularity has type A, D or E, not {letter}{index}"
            )


class _PlaneLinearRightEquivalence(CategoricalIsomorphism):
    r"""A polynomial-ring automorphism carrying one selected germ equation to another."""

    def __init__(self, parent, forward, inverse, *, source, target) -> None:
        self._source_germ = source
        self._target_germ = target
        super().__init__(parent, forward, lambda: inverse, verify=False)

    def source(self):
        return self._source_germ

    def target(self):
        return self._target_germ

    def coordinate_change(self):
        return self.forward()

    def ade_type(self):
        r"""Return the target ADE normal-form label, when the target is one."""
        return self.target().ade_normal_form_type()

    def _repr_(self):
        return f"Linear right-equivalence {self.source()} -> {self.target()}"


def PlaneLinearRightEquivalence(source, target, forward, inverse):
    r"""Return the selected linear right-equivalence as an algebra automorphism."""
    ring = source.polynomial_ring()
    assert target.polynomial_ring() is ring, (
        f"a right equivalence from {source} to {target} is a coordinate change of one plane, "
        f"but their equations lie in {ring} and {target.polynomial_ring()}"
    )
    assert forward.domain() is ring and forward.codomain() is ring, (
        f"the coordinate change {forward} must be an endomorphism of {ring}, but it is a map "
        f"{forward.domain()} -> {forward.codomain()}"
    )
    assert inverse.domain() is ring and inverse.codomain() is ring, (
        f"the inverse coordinate change {inverse} must be an endomorphism of {ring}, but it is a "
        f"map {inverse.domain()} -> {inverse.codomain()}"
    )
    assert all(
        inverse(forward(generator)) == generator
        and forward(inverse(generator)) == generator
        for generator in ring.algebra_generators()
    ), (
        f"the coordinate changes {forward} and {inverse} of {ring} are not mutually inverse on "
        "the variables"
    )
    assert forward(source.equation()) == target.equation(), (
        f"the coordinate change {forward} sends the equation {source.equation()} to "
        f"{forward(source.equation())}, not to {target.equation()}, so it is not a right "
        f"equivalence from {source} to {target}"
    )
    algebras = Algebras(ring.base_ring()).Associative().Unital()
    core_mor = algebras.Core().Mor(ring, ring)
    core_mor._require_base_morphisms(forward, inverse)
    return _PlaneLinearRightEquivalence(
        core_mor,
        forward,
        inverse,
        source=source,
        target=target,
    )


class IsolatedHypersurfaceSingularity:
    r"""A hypersurface germ at the origin with finite Jacobian algebra."""

    def __init__(self, polynomial_ring, equation) -> None:
        base = polynomial_ring.base_ring()
        assert polynomial_ring in SymmetricAlgebras(base), (
            f"a hypersurface singularity is given by an equation in a polynomial ring over {base}, "
            f"but {polynomial_ring} is in {polynomial_ring.category()}"
        )
        self._polynomial_ring = polynomial_ring
        self._equation = polynomial_ring(equation)
        engine = _engine_ring(polynomial_ring)
        f = _engine_element(polynomial_ring, self._equation)
        variables = tuple(engine.gens())
        derivatives = tuple(f.derivative(variable) for variable in variables)
        jacobian = engine.ideal(derivatives)
        dimension = jacobian.vector_space_dimension()
        assert dimension in SageZZ, (
            f"V({equation}) is not an isolated singularity: the Jacobian algebra "
            f"{polynomial_ring}/(partial derivatives) is infinite-dimensional, so the Milnor number is infinite"
        )
        self._engine_derivatives = derivatives
        self._milnor_number = int(dimension)

    @classmethod
    def from_ade_type(cls, base_ring, ade_type, *, names=("x", "y")):
        r"""Construct the selected-coordinate ADE plane-curve normal form.

        The supported classification table is the characteristic-zero simple
        plane-curve list ``A_n``, ``D_n``, ``E_6``, ``E_7``, ``E_8``.  This
        constructor selects a normal form; it does not assert that an arbitrary
        analytically equivalent equation has already been transformed to it.
        """
        assert int(_engine_ring(base_ring).characteristic()) == 0, (
            f"the ADE normal forms of plane curve singularities are the classification in "
            f"characteristic zero, but {base_ring} has characteristic "
            f"{_engine_ring(base_ring).characteristic()}"
        )
        ring = base_ring.polynomial_ring(tuple(names))
        return cls(ring, _ade_normal_form_equation(ring, ade_type))

    def polynomial_ring(self):
        return self._polynomial_ring

    def equation(self):
        return self._equation

    def ade_normal_form_type(self):
        r"""Return the selected ADE label when this equation is exactly a supported normal form.

        Equality is tested in the chosen polynomial coordinates.  No analytic,
        formal, contact, or right-equivalence algorithm is invoked here.
        """
        ring = self.polynomial_ring()
        assert int(_engine_ring(ring.base_ring()).characteristic()) == 0, (
            f"recognizing an ADE normal form of {self} uses the classification in characteristic "
            f"zero, but {ring.base_ring()} has characteristic "
            f"{_engine_ring(ring.base_ring()).characteristic()}"
        )
        if len(tuple(ring.algebra_generators())) != 2:
            return None
        milnor = int(self.milnor_number())
        candidates = [("A", milnor)]
        if milnor >= 4:
            candidates.append(("D", milnor))
        for exceptional in (6, 7, 8):
            if milnor == exceptional:
                candidates.append(("E", exceptional))
        for candidate in candidates:
            if self.equation() == _ade_normal_form_equation(ring, candidate):
                return candidate
        return None

    def linear_right_equivalence_to(self, target, forward_images, inverse_images):
        r"""Return an explicit linear right-equivalence to ``target``.

        ``forward_images`` and ``inverse_images`` are the images of the chosen
        polynomial generators under mutually inverse linear coordinate
        changes.  The algebra-Mor owner verifies the maps; the equivalence
        then verifies the inverse identities and the equation itself.
        """
        ring = self.polynomial_ring()
        assert target.polynomial_ring() is ring, (
            f"a linear right equivalence from {self} to {target} is a coordinate change of one "
            f"plane, but their equations lie in {ring} and {target.polynomial_ring()}"
        )
        forward = Algebras(ring.base_ring()).Associative().Unital().Mor(ring, ring)(forward_images)
        inverse = Algebras(ring.base_ring()).Associative().Unital().Mor(ring, ring)(inverse_images)
        return PlaneLinearRightEquivalence(self, target, forward, inverse)

    def ade_type_via_linear_right_equivalence(self, forward_images, inverse_images):
        r"""Recognize an ADE normal form after one supplied linear coordinate change.

        The changed equation is classified only when it is literally one of
        the selected ADE normal forms.  The returned object retains the
        coordinate-change morphism proving that statement.
        """
        ring = self.polynomial_ring()
        forward = Algebras(ring.base_ring()).Associative().Unital().Mor(ring, ring)(forward_images)
        changed = IsolatedHypersurfaceSingularity(ring, forward(self.equation()))
        ade_type = changed.ade_normal_form_type()
        if ade_type is None:
            return None
        target = IsolatedHypersurfaceSingularity(
            ring,
            _ade_normal_form_equation(ring, ade_type),
        )
        return self.linear_right_equivalence_to(
            target,
            forward_images,
            inverse_images,
        )

    def jacobian_generators(self):
        ring = self.polynomial_ring()
        labels = ring.algebra_generating_set()
        derivatives = tuple(
            _owned_engine_element(ring, value) for value in self._engine_derivatives
        )
        return finite_indexed_family(
            labels,
            lambda label: derivatives[int(labels.ranking_map()(label))],
            name="Jacobian generators indexed by coordinate variables",
        )

    def milnor_algebra(self):
        return (self.polynomial_ring()).quotient_by_relations(self.jacobian_generators())

    def milnor_number(self):
        return _owned_integers()(self._milnor_number)

    def tjurina_algebra(self):
        return (self.polynomial_ring()).quotient_by_relations((self.equation(), *self.jacobian_generators()),
        )

    def tjurina_number(self):
        engine = _engine_ring(self.polynomial_ring())
        ideal = engine.ideal(
            _engine_element(self.polynomial_ring(), relation)
            for relation in (self.equation(), *self.jacobian_generators())
        )
        dimension = ideal.vector_space_dimension()
        assert dimension in SageZZ, (
            f"{self} is not an isolated singularity: its Tjurina algebra is infinite-dimensional, "
            "so the Tjurina number is infinite"
        )
        return _owned_integers()(dimension)

    def completed_local_ring(self, *, precision=20):
        hypersurface = (self.polynomial_ring()).quotient_by_relations((self.equation(),))
        maximal = hypersurface.ideal(*tuple(hypersurface.algebra_generators()))
        return hypersurface.adic_completion(maximal, precision=precision)

    @cached_method
    def ambient_tangent_space(self):
        r"""Return the coordinate tangent space of the ambient affine space at the origin."""
        ring = self.polynomial_ring()
        return ring.base_ring()._fresh_free_module_on(ring.algebra_generating_set())

    @cached_method
    def differential_at_origin(self):
        r"""Return the differential ``df_0 : T_0 A^n -> k`` whose kernel is the Zariski tangent space.

        For a hypersurface ``f=0`` at the coordinate origin, ``df_0`` is the
        linear form whose coefficients are the constant terms of the partial
        derivatives of ``f``, and ``T_0 X = ker(df_0)``.
        """
        base = self.polynomial_ring().base_ring()
        ambient = self.ambient_tangent_space()
        values = base.free_module(1)
        value_generator = values.module_generator(next(iter(values.module_generating_set())))
        coefficients = dict(
            zip(
                tuple(ambient.module_generating_set()),
                (_owned_engine_element(base, derivative.constant_coefficient()) for derivative in self._engine_derivatives),
                strict=True,
            )
        )
        return ambient.module_category().Mor(ambient, values)(
            {label: values.scalar_multiple(coefficients[label], value_generator) for label in ambient.module_generating_set()}
        )

    @cached_method
    def zariski_tangent_space(self):
        r"""Return ``T_0 X = ker(df_0)``, a subobject of the ambient tangent space."""
        return self.differential_at_origin().kernel()

    @cached_method
    def zariski_tangent_embedding(self):
        r"""Return the inclusion ``T_0 X -> T_0 A^n`` of the kernel."""
        return self.zariski_tangent_space().inclusion()

    def is_regular_at_origin(self) -> bool:
        r"""Return the hypersurface Jacobian criterion at the selected origin."""
        return int(self.zariski_tangent_space().module_rank()) == len(
            tuple(self.polynomial_ring().algebra_generating_set())
        ) - 1

    def is_singular_at_origin(self) -> bool:
        return not self.is_regular_at_origin()

    def _plane_curve_origin_data(self):
        r"""Return Singular's local ``(delta, tau, branches)`` data at the origin.

        ``deltaLoc`` is a local plane-curve operation: its second input is the
        prime component of the singular locus selecting the point.  We select
        the coordinate origin by the maximal ideal generated by the two
        polynomial variables, so other singular points of the same affine
        equation do not contribute.
        """
        ring = self.polynomial_ring()
        generators = tuple(ring.algebra_generators())
        assert len(generators) == 2, (
            f"the delta invariant is computed only for plane curves, but {self} is a "
            f"hypersurface in {len(generators)} variables"
        )
        engine = _engine_ring(ring)
        equation = _engine_element(ring, self.equation())
        equation_ideal = engine.ideal(equation)
        assert equation_ideal.radical() == equation_ideal, (
            f"the delta invariant and the conductor are defined for reduced curves, but "
            f"{self.equation()} has a repeated factor"
        )
        if self.is_regular_at_origin():
            return 0, 0, 1
        origin = engine.ideal(*engine.gens())
        singular_lib("normal.lib")
        local_data = singular_function("deltaLoc")(equation, origin, ring=engine)
        return tuple(int(value) for value in local_data)

    def _plane_curve_prime_data(self, point):
        r"""Return local data at one represented closed prime of the plane.

        Singular ``deltaLoc`` accepts an irreducible prime component of the
        singular locus.  For a nonrational closed point it returns the sum over
        the conjugate geometric points.  We retain the original closed point
        and divide that total by its represented residue degree; multiplying
        the resulting local invariant back by the residue degree recovers the
        contribution over the ground field.
        """
        ring = self.polynomial_ring()
        assert point.parent().ring() is ring, (
            f"the point {point} is a point of the plane of {point.parent().ring()}, not of the "
            f"plane of {self}, whose coordinates lie in {ring}"
        )
        generators = tuple(ring.algebra_generators())
        assert len(generators) == 2, (
            f"the delta invariant is computed only for plane curves, but {self} is a "
            f"hypersurface in {len(generators)} variables"
        )
        engine = _engine_ring(ring)
        equation = _engine_element(ring, self.equation())
        equation_ideal = engine.ideal(equation)
        assert equation_ideal.radical() == equation_ideal, (
            f"the delta invariant and the conductor are defined for reduced curves, but "
            f"{self.equation()} has a repeated factor"
        )
        singular_lib("normal.lib")
        point_ideal = engine.ideal(
            tuple(
                _engine_element(ring, generator)
                for generator in point.ideal().ideal_generators()
            )
        )
        local_data = singular_function("deltaLoc")(
            equation,
            point_ideal,
            ring=engine,
        )
        total_delta, total_tjurina, total_branches = (
            int(value) for value in local_data
        )
        residue_degree = int(point.residue_degree())
        assert residue_degree > 0 and total_delta % residue_degree == 0, (
            f"the total delta invariant {total_delta} over the conjugates of {point} is not "
            f"divisible by its residue degree {residue_degree}"
        )
        return (
            total_delta // residue_degree,
            total_tjurina,
            total_branches,
            residue_degree,
        )

    def delta_invariant_at(self, point):
        r"""Return the local delta invariant at a represented closed point."""
        delta, _tjurina, _branches, _degree = self._plane_curve_prime_data(point)
        assert delta >= 0, f"the curve {self} has infinite delta invariant at {point}"
        return _owned_integers()(delta)

    def delta_contribution_over_base(self, point):
        r"""Return ``delta_p [kappa(p):k]`` without splitting the closed point."""
        delta, _tjurina, _branches, degree = self._plane_curve_prime_data(point)
        assert delta >= 0, f"the curve {self} has infinite delta invariant at {point}"
        return _owned_integers()(delta * degree)

    def delta_invariant(self):
        r"""Return the local plane-curve delta invariant at the selected origin.

        This is ``dim_k(normalization(A)/A)`` for the local curve ring.  The
        computation is Singular's ``deltaLoc`` from ``normal.lib`` and is
        therefore local at the chosen maximal ideal rather than a sum over all
        affine singularities.
        """
        ring = self.polynomial_ring()
        origin = ring.spectrum()(ring.ideal(*tuple(ring.algebra_generators())))
        return self.delta_invariant_at(origin)

    def local_tjurina_number(self):
        r"""Return the local Tjurina number from the same selected germ calculation."""
        _delta, tjurina, _branches = self._plane_curve_origin_data()
        return _owned_integers()(tjurina)

    def number_of_branches_at_origin(self):
        r"""Return the number of geometric branches of the reduced plane-curve germ."""
        _delta, _tjurina, branches = self._plane_curve_origin_data()
        return _owned_integers()(branches)

    def conductor_ideal_at_origin(self):
        r"""Return the conductor ideal in the local ring at the selected origin.

        Singular computes the conductor in the ambient polynomial ring.  Its
        extension to the prime localization at ``(x,y)`` is the conductor of
        the selected local curve germ, with contributions from unrelated
        affine singularities removed by localization.
        """
        ring = self.polynomial_ring()
        generators = tuple(ring.algebra_generators())
        assert len(generators) == 2, (
            f"the conductor is computed only for plane curves, but {self} is a hypersurface in "
            f"{len(generators)} variables"
        )
        engine = _engine_ring(ring)
        equation = _engine_element(ring, self.equation())
        equation_ideal = engine.ideal(equation)
        assert equation_ideal.radical() == equation_ideal, (
            f"the delta invariant and the conductor are defined for reduced curves, but "
            f"{self.equation()} has a repeated factor"
        )
        singular_lib("normal.lib")
        conductor_engine = singular_function("normalConductor")(equation_ideal, ring=engine)
        conductor = _from_engine_ideal(ring, conductor_engine)
        curve = (ring).quotient_by_relations((self.equation(),))
        curve_conductor = curve.ideal(
            *(curve(generator) for generator in conductor.ideal_generators())
        )
        origin = curve.ideal(*(curve(generator) for generator in generators))
        local_ring = curve.localize_at_prime(origin)
        return curve_conductor.extension_to_localization(local_ring)


__all__ = ["IsolatedHypersurfaceSingularity", "PlaneLinearRightEquivalence"]
