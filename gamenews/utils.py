
class DataMixin:
    def get_mixin_context( self, context, **kwargs):
        context['itemX'] = "ITEM X"
        context.update(kwargs)
        return context