"""Module from initializing Component Class"""

from .context import component_registry


class BaseComponent:
    def __init__(self, name=""):
        super().__init__(name=name)
        if component_registry.get():
            component_registry.get().append(self)

    @classmethod
    def get_component(cls, name="", strict=False):
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
