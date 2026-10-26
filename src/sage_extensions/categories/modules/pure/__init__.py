"Lazy public aggregation for pure."

from importlib import import_module as _import_module

_EXPORTS = {
    "Modules": ("sage_extensions.categories.modules.pure.modules", "Modules"),
    "VectorSpaces": ("sage_extensions.categories.modules.pure.modules", "VectorSpaces"),
    "FreeModules": ("sage_extensions.categories.modules.pure.modules", "FreeModules"),
    "ProjectiveModules": ("sage_extensions.categories.modules.pure.modules", "ProjectiveModules"),
    "TorsionModules": ("sage_extensions.categories.modules.pure.modules", "TorsionModules"),
}

__all__ = [
    "FreeModules",
    "Modules",
    "ProjectiveModules",
    "TorsionModules",
    "VectorSpaces",
]


def __getattr__(name):
    try:
        module_name, attribute = _EXPORTS[name]
    except KeyError as error:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from error
    value = getattr(_import_module(module_name), attribute)
    globals()[name] = value
    return value


def __dir__():
    return sorted((*globals(), *__all__))
