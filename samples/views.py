import os
from django.views.generic import list_detail
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from homebase.samples.models import Sample
from homebase.samples.forms import *
from homebase.settings import PROJECT_DIR,SAMPLES_DIR

# Use MarvinBeans utility 
MOLCONVERT='/usr/local/ChemAxon/MarvinBeans/bin/molconvert \"png:w%d,#ffffff\" %s/sketch.mrv -o %s/sketch%s.png'

def samples_list(request):
	"""Show a list of all samples"""
	samples = Sample.objects.order_by('date_added')
	return list_detail.object_list(request,
									#paginate_by=10,
									queryset=samples,
									template_name='samples/samples_list.html',extra_context={'samples_dir':SAMPLES_DIR})

def delete_all_samples(request):
	"""XXX Delete all samples, use with caution!"""
	samples = Sample.objects.all()
	for s in samples:
		delete_sample(request,s.id)
	return HttpResponseRedirect('/samples/')

def view_sample(request,sample_id):
	"""Show sample details"""
	sample = SmallMolecule.objects.get(id=sample_id)
	return render_to_response('samples/view_sample.html',
							{'sample':sample},
							context_instance=RequestContext(request))	

def new_small(request):
	if request.method == 'POST':
		form = SmallMoleculeForm(request.POST)
		if form.is_valid():
			sample = SmallMolecule()
			for k,v in form.cleaned_data.items():
				sample.__setattr__(k,v)
			for att in ['mol', 'formula', 'atomcount', 'mass']:
				sample.__setattr__(att,request.POST[att])
			sample.added_by = request.user
			sample.save()
			# create sampledir and molecular formula sketch
			sampledir = os.path.join(SAMPLES_DIR,str(sample.id))
			if not os.path.exists(sampledir):
				os.mkdir(sampledir)
			mfile = open(sampledir+'/sketch.mrv','w')
			mfile.write(request.POST['mol'])
			mfile.close()
			# convert to PNG
			os.system(MOLCONVERT %(200,sampledir,sampledir,''))
			os.system(MOLCONVERT %(500,sampledir,sampledir,'_big'))
			return HttpResponseRedirect('/samples/')
		else:
			return HttpResponseRedirect('/samples/new_small/')
	else:
		form = SmallMoleculeForm(instance=SmallMolecule())
	return render_to_response('samples/new_small.html',
						{'form':form,'user':request.user},
							context_instance=RequestContext(request))	

def new_protein(request):
	if request.method == 'POST':
		form = ProteinForm(request.POST)
		if form.is_valid():
			sample = Protein()
			for k,v in form.cleaned_data.items():
				sample.__setattr__(k,v)
			sample.added_by = request.user
			sample.save()
			sampledir = os.path.join(SAMPLES_DIR,str(sample.id))
			if not os.path.exists(sampledir):
				os.mkdir(sampledir)
			return HttpResponseRedirect('/samples/')
		else:
			return HttpResponseRedirect('/samples/new_protein/')
	else:
		form = ProteinForm(instance=Protein())
	return render_to_response('samples/new_protein.html',
						{'form':form,'user':request.user},
						context_instance=RequestContext(request))	

def edit_sample(request,sample_id):
	# Creating a form to change an existing sample.
	if request.method == 'POST':
		sample = Sample.objects.get(pk=sample_id)
		form = SampleForm(request.POST,instance=sample)
		if form.is_valid():
			for k,v in form.cleaned_data.items():
				sample.__setattr__(k,v)
			for att in ['mol', 'formula', 'atomcount', 'mass']:
				sample.__setattr__(att,request.POST[att])
			sample.save()
			sampledir = os.path.join(SAMPLES_DIR,str(sample.id))
			mfile = open(sampledir+'/sketch.mrv','w')
			mfile.write(request.POST['mol'])
			mfile.close()
			os.system(MOLCONVERT %(200,sampledir,sampledir,''))
			os.system(MOLCONVERT %(500,sampledir,sampledir,'_big'))
			return HttpResponseRedirect('/samples/')
		else:
			return HttpResponseRedirect('.')
	else:
		sample = Sample.objects.get(pk=sample_id)
		form = SampleForm(instance=sample)
		return render_to_response('samples/edit_sample.html',
							{'form':form, 'sample':sample},
							context_instance=RequestContext(request))	

def delete_sample(request,sample_id):
	# Deleteing an existing sample.
	sample = Sample.objects.get(pk=sample_id)
	# First delete the directories and files belonging to the sample
	sampledir = os.path.join(SAMPLES_DIR,str(sample.id))
	if os.path.isdir(sampledir):
		for f in os.listdir(sampledir):
			os.remove(os.path.join(sampledir,f))
		os.rmdir(sampledir)
	sample.delete() # Finally delete the sample from the database
	return HttpResponseRedirect('/samples/')

def samples_added_by(request,name):
	"""
	Show a list of all samples added by user "name"
	"""
	samples = Sample.objects.filter(added_by__username=name).order_by('date_added')
	return list_detail.object_list(request,
									queryset=samples,
									template_name='samples/samples_added_by.html',
									extra_context={'name':name,'samples_dir':SAMPLES_DIR})
