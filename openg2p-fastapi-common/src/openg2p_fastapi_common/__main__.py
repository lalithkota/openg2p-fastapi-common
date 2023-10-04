from .app import Initializer
from .context import extendable_registry

print(extendable_registry.get()._extendable_classes)
Initializer().main()
