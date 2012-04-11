
@register
class {{model}}(LineFeature):
    description = models.TextField(null=True, blank=True)
    class Options:
        form = '{{app}}.forms.{{model}}Form'

