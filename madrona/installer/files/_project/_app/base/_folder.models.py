
@register
class _model(FeatureCollection):
    description = models.TextField(null=True, blank=True)
    class Options:
        form = '_app.forms._modelForm'
        valid_children = (
            _all_features
        )

