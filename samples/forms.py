from django.forms import ModelForm
from homebase.samples.models import *


class SampleForm(ModelForm):
	class Meta:
		model = Sample

class SmallMoleculeForm(SampleForm):
	class Meta:
		model = SmallMolecule
		exclude = ('code','status')

class ProteinForm(SampleForm):
	class Meta:
		model = Protein
		exclude = ('code','status')
