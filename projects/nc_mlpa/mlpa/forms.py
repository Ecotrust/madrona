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
from mlpa.models import AllowedUse, AllowedMethod, AllowedPurpose, AllowedTarget, DesignationsPurposes
from django.utils import simplejson as json
from django.conf import settings
from lingcod.common.forms import ShortTextarea

class ArrayForm(BaseArrayForm):
    class Meta(BaseArrayForm.Meta):
        model = MpaArray
        widgets = {
            'description': ShortTextarea(),
        }

        
class GoalObjectivesWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = ['<p class="help_text">Please select one or more MLPA goals below to which this MPA contributes.</p>']
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
            # Goal -> Objective heirarchy not used anymore
            # output.append(u'<h4>%s</h4><p>%s</p>' % (category.name, category.description))
            for objective in category.goalobjective_set.all():
                # print checkboxes[str(objective.pk)]
                output.append(u'<li>')
                output.append(checkboxes[str(objective.pk)])
                output.append(u'<p>%s</p>' % objective.description)
                output.append(u'</li>')
            output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

class AllowedUsesWidget(forms.SelectMultiple):
    def render(self, *args, **kwargs):
        data = {
            'allowed_uses': {},
            'methods': {},
            'targets': {},
            'purposes': {},
            'designations-purposes': {},
        }
        for use in AllowedUse.objects.all():
            data['allowed_uses'][use.pk] = {
                'pk': use.pk,
                'method': use.method_id,
                'target': use.target_id,
                'purpose': use.purpose_id,
            }
        for method in AllowedMethod.objects.all():
            data['methods'][method.pk] = {
                'pk': method.pk, 
                'name': method.name
            }
        for target in AllowedTarget.objects.all():
            data['targets'][target.pk] = {
                'pk': target.pk,
                'name': target.name
            }
        for purpose in AllowedPurpose.objects.all():
            data['purposes'][purpose.pk] = {
                'pk': purpose.pk,
                'name': purpose.name
            }
        for mapping in DesignationsPurposes.objects.all():
            data['designations-purposes'][mapping.designation_id] = list(mapping.purpose.values_list('pk', flat=True))
        
        json_string = json.dumps(data)
        output = super(AllowedUsesWidget, self).render(*args, **kwargs)
        return output + mark_safe("""
        <p class="help_text">
            The list of allowed uses has been updated as of 2/19/2009. To ensure that the most accurate level of protection information is provided, allowed uses selections have been updated with information specific to the north coast Study Region. The allowed uses list now includes only uses that the North Coast Science Advisory Team has assigned a level of protection. If you indicate an allowed use that is not listed below, MLPA Initiative staff may forward this allowed use to the Science Advisory Team so that it can be assigned a level of protection.
        </p>
        <p class="help_text">
            To add allowed uses, choose a combination of Target, Method, and Use Type. <strong>Please note</strong>, some options may be disabled depending on your choices. For example, if you choose Salmon from the Target menu, you will not be able to select "Hand Harvest" from the Method menu.
        </p>
        <p class="help_text">
            If you would like to propose an allowed use not listed above, please contact: <a href="mailto:help@marinemap.org">help@marinemap.org</a>
        </p>
        <table class="allowed_uses marinemap-table">
            <thead>
                <tr class="headers">
                    <th>Target</th>
                    <th>Method</th>
                    <th colspan="2">Purpose</th>
                </tr>
                <tr class="form">
                    <th class="target"></th>
                    <th class="method"></th>
                    <th class="purpose"></th>
                    <th class="add"><a href="#"><img src="%s/common/images/silk/add.png" width="16" height="16" /></a></th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
        <br />
        <p style="display:none;" id="allowed_uses_json">%s</p>
        """ % (settings.MEDIA_URL, json_string, ))
        

class MpaForm(BaseMpaForm):
    goal_objectives = forms.ModelMultipleChoiceField(GoalObjective.objects, widget=GoalObjectivesWidget, required=False)
    allowed_uses = forms.ModelMultipleChoiceField(AllowedUse.objects, widget=AllowedUsesWidget, required=False)
    
    class Meta:
        model = MlpaMpa
        fields = ('user', 'geometry_orig', 'geometry_final',
            'name', 'designation', 'allowed_uses', 'other_allowed_uses',
            'other_regulated_activities', 'specific_objective', 
            'goal_objectives', 'design_considerations', 
            'boundary_description', 'evolution')
        widgets = {
            'other_allowed_uses': ShortTextarea(), # limit defaults to 1024 char
            'other_regulated_activities': ShortTextarea(),
            'specific_objective': ShortTextarea(limit=600), # about 2-3 sentences
            'design_considerations': ShortTextarea(),
            'boundary_description': ShortTextarea(),
            'evolution': ShortTextarea(),
        }

