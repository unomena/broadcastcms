import types
import inspect

class PublicSite(object):
    def register(self, model, view_class):
        view_class_methods = inspect.getmembers(view_class, inspect.ismethod)

        for method in view_class_methods:
            name = method[0]
            attr = method[1]
            if isinstance(attr, types.UnboundMethodType):
                setattr(model, name, attr.im_func)

site = PublicSite()
