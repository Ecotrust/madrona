
@register
class {{model}}(FeatureCollection):
    description = models.TextField(null=True, blank=True)
    class Options:
        form = '{{app}}.forms.{{model}}Form'
        valid_children = (
            {{all_features}}
        )

