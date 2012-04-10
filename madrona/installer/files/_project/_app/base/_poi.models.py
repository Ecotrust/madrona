
@register
class _model(PointFeature):
    description = models.TextField(null=True, blank=True)
    class Options:
        form = '_app.forms._modelForm'

