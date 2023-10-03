"""Module from initializing Component Class"""

from extendable import ExtendableMeta

from .context import component_registry


class BaseComponent(metaclass=ExtendableMeta):
    def __init__(self, name=""):
        self.name = name
        if component_registry.get():
            component_registry.get().append(self)


def get_component(cls, name="", strict=True):
    for component in component_registry.get():
        result = None
        if strict:
            if cls is type(component):
                result = component
        else:
            if isinstance(component, cls):
                result = component

        if result:
            if name:
                if name == result.name:
                    return result
            else:
                return result
    return None
