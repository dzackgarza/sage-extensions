'Lazy public aggregation for finitely_generated.'

from importlib import import_module as _import_module

_EXPORTS = {'FinitelyGeneratedModules': ('sage_extensions.categories.modules.pure.modules',
                              'FinitelyGeneratedModules')}

__all__ = ['FinitelyGeneratedModules']

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
