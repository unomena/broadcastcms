import types


class PublicSite(object):
    def register(self, model, view_class):
        for attr_name in dir(view_class):
            attr = getattr(view_class, attr_name)
            if isinstance(attr, types.UnboundMethodType):
                # todo: verify the method parameters and perhaps the name
                # todo: check if the view method does not already exist
                setattr(model, attr_name, attr.im_func)

site = PublicSite()
