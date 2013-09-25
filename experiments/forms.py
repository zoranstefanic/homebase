from django.forms import Form

class ExperimentSearch(Form):
	type = forms.ChoiceField(max_length=100)
    name = forms.TextField()
