r"""The category of what each category's methods return, inferred from the value's class.

Ported from ``src/dzack_research/utilities/category_inference.py`` of
``dzackgarza/research`` at commit ``d62f344542``.  Its survey there was
:class:`dzack_research.utilities.megadoc.Survey`'s, which reads the research
session; the four services this needs are ported from that module at the same
commit -- :func:`_probe_arguments`, :func:`_build`, :func:`_own_member_names`
and :func:`_stable_runtime_text` -- and read this library's own session,
because the session a category is built in is ``sage_extensions.all`` and the
ring its parameters take is ``sage_extensions.rings.ZZ``.

Implementation classes are exactly a category's ``ParentMethods``,
``ElementMethods`` and ``MorphismMethods``, so the class of a returned value
names the category it lies in.  For every exported category the session can
build, each method the category defines that takes no arguments is called on
the category's example object (or an element of it), and the category read off
the returned value's class is recorded.  The result is JSON consumed by
``category_graph --format constructions --inferred FILE``.  Nothing here judges
a placement.
"""

from __future__ import annotations

import argparse
import inspect
import json
import re
import signal
from types import FrameType, ModuleType
from typing import Final

from sage.categories.category import Category
from sage.misc.abstract_method import AbstractMethod
from sage.misc.cachefunc import CachedMethod
from sage.structure.element import Element
from sage.structure.parent import Parent

from sage_extensions.categories.abstract_categories.mor_foundation import (
    ObjectLevelOperation,
)
from sage_extensions.categories.rings.ring_foundation import OwnedCategoryOverBaseRing
from sage_extensions.rings import ZZ

CALL_SECONDS = 10
SLOTS = (("parent_class", "ParentMethods"), ("element_class", "ElementMethods"))
RUNTIME_ADDRESS: Final = re.compile(r" at 0x[0-9A-Fa-f]+")
NO_SIGNATURE: Final = (TypeError, ValueError)


class CallTimedOut(Exception):
    r"""A call ran past ``CALL_SECONDS``."""


def _on_alarm(_signum: int, _frame: FrameType | None) -> None:
    raise CallTimedOut


def _value(thunk: object) -> tuple[bool, object]:
    signal.alarm(CALL_SECONDS)
    try:
        return True, thunk()  # type: ignore[operator]
    except Exception:  # noqa: BLE001 - a value that cannot be produced has no class to read
        return False, None
    finally:
        signal.alarm(0)


def _stable_runtime_text(text: str) -> str:
    r"""Remove process-local object addresses from recorded text."""
    return RUNTIME_ADDRESS.sub("", text)


def _session() -> ModuleType:
    r"""The session a category is built in, imported where it is asked for.

    Reading the session brings in every category, ring and engine this library
    publishes, so it is imported by the one call that needs it rather than when
    this module is read.
    """
    from sage_extensions import all as session

    return session


def _probe_arguments(klass: type) -> tuple[tuple[Parent, ...], str] | None:
    r"""What to build one from, read off the category's declared type.

    The declaration is the base class, never the parameter's name: a name is a
    string, and a string is not a type.  A category derived from
    ``OwnedCategoryOverBaseRing`` *is* declared to be over a base ring, so the
    session's ring is supplied.  Anything else -- a bare ``parameter``, or a
    second parameter with no annotation -- declares nothing, and there is
    nothing here to construct from: the survey does not guess.
    """
    if klass is OwnedCategoryOverBaseRing:
        return (), "abstract"
    try:
        signature = inspect.signature(klass)
    except NO_SIGNATURE:
        return None
    parameters = [
        parameter for name, parameter in signature.parameters.items() if name != "self"
    ]
    if not parameters:
        return (), "nullary"
    if len(parameters) == 1 and issubclass(klass, OwnedCategoryOverBaseRing):
        return (ZZ,), "parameterized"
    return None


def _build(factory: object, arguments: tuple[Parent, ...]) -> object:
    r"""Construct one, or report why it would not build.

    Reaching an arbitrary owned constructor reaches GAP, PARI and every
    category in the tree, so the raise is unbounded.  The failure is returned
    rather than swallowed: it is recorded in the entry.
    """
    try:
        return factory(*arguments)  # type: ignore[operator]
    except Exception as error:  # noqa: BLE001 - see the docstring
        return _stable_runtime_text(f"{type(error).__name__}: {error}")


def _own_member_names(klass: type) -> list[str]:
    r"""The public members a class itself defines, descriptors included.

    Sage keeps a method behind ``cached_method`` and ``abstract_method``, and
    installs object operations as ``ObjectLevelOperation``, so a member is not
    always something ``callable``; the descriptor's own class is what says it
    is one.  ``vars`` is the class's own body: an inherited member belongs to
    its owner, and the walk in :func:`_own_names` is what asks the owner.
    """
    names: list[str] = []
    for name, value in sorted(vars(klass).items()):
        if name.startswith("_"):
            continue
        if not (
            callable(value)
            or isinstance(
                value, (CachedMethod, AbstractMethod, property, ObjectLevelOperation)
            )
        ):
            continue
        names.append(name)
    return names


def _category_of_class(value: object) -> str | None:
    r"""The category named by the class of ``value``: an object's, or an element's parent's."""
    match value:
        case Parent():
            return _stable_runtime_text(repr(value.category()))
        case Element():
            return "an element of an object of " + _stable_runtime_text(
                repr(value.parent().category())
            )
        case bool():
            return "a truth value, not an object"
    return None


def _required(method: object) -> bool:
    r"""Whether calling ``method`` takes a required argument, so it answers nothing yet."""
    try:
        signature = inspect.signature(method)  # type: ignore[arg-type]
    except NO_SIGNATURE:
        return False
    return any(
        parameter.default is inspect.Parameter.empty
        and parameter.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }
        for parameter in signature.parameters.values()
    )


def _own_names(instance: Category, slot: str, owner: str) -> list[str]:
    r"""The methods the category ``owner`` itself installs through one dynamic slot."""
    dynamic = getattr(instance, slot, None)
    if dynamic is None:
        return []
    names: dict[str, None] = {}
    for klass in dynamic.__mro__:
        if klass.__qualname__.split(".")[0] == owner:
            for member in _own_member_names(klass):
                if not isinstance(getattr(klass, member, None), type):
                    names[member] = None
    return list(names)


def infer() -> dict[str, dict[str, dict[str, str]]]:
    r"""Every exported category the session builds, and what its methods return."""
    session = _session()
    signal.signal(signal.SIGALRM, _on_alarm)
    inferred: dict[str, dict[str, dict[str, str]]] = {}
    for name in [name for name in dir(session) if not name.startswith("_")]:
        klass = getattr(session, name)
        if not (inspect.isclass(klass) and issubclass(klass, Category)):
            continue
        probe = _probe_arguments(klass)
        if probe is None or probe[1] == "abstract":
            continue
        instance = _build(klass, probe[0])
        if isinstance(instance, str):
            continue
        built, subject = _value(lambda: instance.an_object())
        if not built:
            continue
        subjects = {"ParentMethods": subject}
        got, element = _value(lambda: subject.an_element())
        if got:
            subjects["ElementMethods"] = element
        for slot, container in SLOTS:
            if container not in subjects:
                continue
            for method_name in _own_names(instance, slot, name):
                got, bound = _value(lambda: getattr(subjects[container], method_name))
                if not got:
                    continue
                if callable(bound):
                    if _required(bound):
                        continue
                    got, bound = _value(bound)
                    if not got:
                        continue
                category = _category_of_class(bound)
                if category is not None:
                    inferred.setdefault(name, {}).setdefault(container, {})[
                        method_name
                    ] = category
    return inferred


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-o", "--output", required=True)
    arguments = parser.parse_args(argv)
    inferred = infer()
    with open(arguments.output, "w", encoding="utf-8") as handle:
        json.dump(inferred, handle, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
