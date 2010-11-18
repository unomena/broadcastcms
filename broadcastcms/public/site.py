import types

class PublicSite(object):
    def register(self, model, view_class):
        model_attr_names = dir(model)
        view_attr_names = dir(view_class)

        for attr_name in view_attr_names:
            if attr_name not in model_attr_names:
                attr = getattr(view_class, attr_name)
                if isinstance(attr, types.UnboundMethodType):
                    # TODO: verify the method parameters and perhaps the name
                    setattr(model, attr_name, attr.im_func)

site = PublicSite()
