r"""Orbit-generated submodules and integral forms on their retained inclusions.

The finite closure calculation is the span construction used in
sage-indefinite-port at 709f81a, groups/integral_structures.py. A finite
group gives a finite generating family. A supplied finitely generated
containing module over a PID bounds the ascending chain; leaving that
bound proves that the orbit-generated module is not contained in it.
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.functors.group_actions import GroupActionFunctor
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing, PrincipalIdealDomains
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of


class OrbitSpanConstructions(OwnedCategoryOverBaseRing):
    r"""The least stable submodule containing a given module inclusion."""

    def super_categories(self):
        return [Sets()]

    def _call_(self, action, seed, *, containing=None):
        ring = self.base_ring()
        group = action.group()
        ambient = action.underlying_object()
        if seed.codomain() is not ambient or ambient.base_ring() is not ring:
            raise ValueError("the seed and action must share an ambient module over the scalar ring")
        if ring not in PrincipalIdealDomains():
            raise NotImplementedError("the selected finite-span realization requires a PID")
        if not seed.domain().module_generating_set().cardinality().is_finite():
            raise NotImplementedError("orbit-span computation requires a finite seed generating set")
        arrows = group.classifying_category().Mor(
            group.classifying_category().an_object(), group.classifying_category().an_object()
        )

        # One arrow of BG per acting element: constructing it admits the
        # element into the group, which is decided once, not per vector.
        def acting_maps(elements):
            return tuple(action(arrows(element)) for element in elements)

        generators = tuple(seed(vector) for vector in seed.domain().module_generators())
        if group.is_finite() is True and containing is None:
            span = ambient.subobject_on(tuple(act(vector) for act in acting_maps(group) for vector in generators))
        else:
            if containing is None:
                raise NotImplementedError("an infinite-group orbit span requires a finite containing bound")
            if containing.codomain() is not ambient or not containing.domain().module_generating_set().cardinality().is_finite():
                raise ValueError("the containing bound must be a finitely generated submodule of the same ambient module")
            if not group.has_selected_finite_group_generating_set():
                raise NotImplementedError("bounded orbit closure requires a finite group generating set")
            steps = tuple(group.group_generators())
            steps = acting_maps(steps + tuple(~g for g in steps))
            span = ambient.subobject_on(generators)
            while True:
                current = tuple(span.inclusion()(v) for v in span.module_generators())
                if any(not containing.is_in_image(v) for v in current):
                    raise ValueError("the orbit-generated submodule leaves the specified containing bound")
                images = tuple(act(v) for act in steps for v in current)
                if all(span.inclusion().is_in_image(v) for v in images):
                    break
                span = ambient.subobject_on(current + images)
        if containing is not None and any(
            not containing.is_in_image(span.inclusion()(v)) for v in span.module_generators()
        ):
            raise ValueError("the orbit-generated submodule leaves the specified containing bound")
        return _object_of(self, ambient_action=action, seed=seed, containing=containing, span=span)

    class ParentMethods:
        def __init__(self, ambient_action, seed, containing, span, **rest):
            self._ambient_action = ambient_action
            self._seed = seed
            self._containing = containing
            self._span = span
            super().__init__(**rest)

        def object(self):
            return self._span

        def inclusion(self):
            return self.object().inclusion()

        def ambient_action(self):
            return self._ambient_action

        def seed(self):
            return self._seed

        def containing_bound(self):
            return self._containing

        def seed_factorization(self):
            return self.seed().factor_through_or_none(self.inclusion())

        @cached_method
        def action_functor(self):
            group = self.ambient_action().group()
            point = group.classifying_category().an_object()
            arrows = group.classifying_category().Mor(point, point)
            module = self.object()
            return GroupActionFunctor(
                group, Modules(self.base_ring()), module,
                lambda g: (self.ambient_action()(arrows(g)) * self.inclusion()).factor_through_or_none(self.inclusion()),
            )


class OrbitSpanLattices(OwnedCategoryOverBaseRing):
    r"""Integral forms on an orbit-generated module, retaining its construction."""

    def super_categories(self):
        from sage_extensions.categories.lattices import Lattices

        return [Lattices(self.base_ring())]

    def _call_(self, construction, rational_form):
        from sage_extensions.categories.modules.framed.formed.form_modules import FormModules

        ring = self.base_ring()
        span = construction.object()
        ambient = construction.inclusion().codomain()
        if ambient.module_over_extension() is not rational_form:
            raise ValueError("the form must be stated on the orbit span's rational ambient space")

        def pairing(left, right):
            value = rational_form.b(
                construction.inclusion()(left).underlying_element(),
                construction.inclusion()(right).underlying_element(),
            )
            if value not in ring:
                raise ValueError("the orbit span has a nonintegral pairing, so no integral invariant overlattice contains it")
            return ring(value)

        for left in span.module_generators():
            for right in span.module_generators():
                pairing(left, right)
        form = span.bilinear_forms(ring)(pairing)

        def inclusion(source):
            linear = Modules(ring).Mor(source, ambient)(
                lambda label: construction.inclusion()(span.module_generator(label))
            )
            return Modules(ring).Mono(source, ambient)._subobject_inclusion(
                linear, lift=lambda value: source(construction.inclusion().lift(value))
                if construction.inclusion().is_in_image(value) else None,
            )

        return FormModules(ring)(
            form, _extra_categories=(self,),
            _extra_construction_data={"orbit_span": construction, "gram_tensor": form.gram_tensor()},
            _subobject_ambient=ambient, _subobject_inclusion_factory=inclusion,
        )

    class ParentMethods:
        def __init__(self, orbit_span, **rest):
            self._orbit_span = orbit_span
            super().__init__(**rest)

        def orbit_span_construction(self):
            return self._orbit_span

        def seed_inclusion(self):
            return self.orbit_span_construction().seed().factor_through_or_none(self.inclusion())

        @cached_method
        def action_functor(self):
            from sage_extensions.categories.lattices import Lattices

            construction = self.orbit_span_construction()
            action = construction.action_functor()
            group = action.group()
            point = group.classifying_category().an_object()
            arrows = group.classifying_category().Mor(point, point)
            return GroupActionFunctor(
                group, Lattices(self.base_ring()), self,
                lambda g: self.Aut()(lambda label: self(
                    action(arrows(g))(construction.object().module_generator(label))
                )),
            )
