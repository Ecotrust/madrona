from lingcod.array.forms import ArrayForm as BaseArrayForm
from mlpa.models import MpaArray
from mlpa.models import MlpaMpa
from lingcod.mpa.forms import MpaForm as BaseMpaForm
from lingcod.array.forms import ArrayForm as BaseArrayForm
from django import forms
from mlpa.models import GoalCategory, GoalObjective
from itertools import chain
from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape


class ArrayForm(BaseArrayForm):
    class Meta(BaseArrayForm.Meta):
        model = MpaArray

        
class GoalObjectivesWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = ['<p class="help_text">Please select one or more regional objectives below to which this MPA contributes.</p>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        checkboxes = dict()
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # print option_value, option_label
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            checkboxes[option_value] = u'<label%s>%s %s</label>' % (label_for, rendered_cb, option_label)
        for category in GoalCategory.objects.all():
            output.append(u'<ul>')
            output.append(u'<h4>%s</h4><p>%s</p>' % (category.name, category.description))
            for objective in category.goalobjective_set.all():
                # print checkboxes[str(objective.pk)]
                output.append(u'<li>')
                output.append(checkboxes[str(objective.pk)])
                output.append(u'<p>%s</p>' % objective.description)
                output.append(u'</li>')
            output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))
        
class MpaForm(BaseMpaForm):
    goal_objectives = forms.ModelMultipleChoiceField(GoalObjective.objects, widget=GoalObjectivesWidget, required=False)

    class Meta:
        model = MlpaMpa
        # fields = ('user', 'name', 'geometry_orig', 'geometry_final')
        exclude = ('content_type', 'object_id', 'cluster_id', 'is_estuary', 'group_before_edits', )
