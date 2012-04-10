
@register
class _model(PolygonFeature):
    description = models.TextField(null=True, blank=True)
    class Options:
        form = '_app.forms._modelForm'

