import os, glob, random
from django.views.generic import list_detail
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from homebase.experiments.models import Experiment 
from homebase.samples.models import Sample 
from homebase.settings import EXPERIMENTS_DIR, PROJECT_DIR
from crysalis.synchronize import Dataset, IniFile, DatFile

def homepage(request):
	"""
	Homepage
	"""
	current_exp  = Experiment.objects.latest('start')
	return render_to_response('homepage.html',
							{'current_exp':current_exp},
							context_instance=RequestContext(request))	

def experiment_list(request,user=None):
	"""List all experiments"""
	if user:
		experiments = Experiment.objects.filter(origdir__icontains=user)	
	else:
		experiments = Experiment.objects.all()	
	return list_detail.object_list(request,
									   paginate_by=50,
									   queryset=experiments.order_by('-start'),
									   template_name='experiments/experiment_list.html')

def experiment_search(request):
	"""Search experiments 
	This view still interferes with pagination, as when the search returns more
	than on page of hits the pagination does not work as it uses the "page" key 
	"""
	exp_types = [e[0] for e in set(Experiment.objects.values_list('type'))]
	if request.GET:
		q = Q(name__startswith=request.GET['name__startswith'])
		q = q & Q(origdir__icontains=request.GET['origdir__icontains'])
		if not request.GET['type'] == '':
			q = q & Q(type__exact=request.GET['type'])
		experiments = Experiment.objects.filter(q)
		return list_detail.object_list(request,
										   paginate_by=20,
										   queryset=experiments.order_by('name'),
										   template_name='experiments/experiment_list.html',
										   extra_context={'user':request.user})
	else:
		return render_to_response('experiments/experiment_search.html',
								{'exp_types':exp_types},
								context_instance=RequestContext(request))

def experiment_search_cells(request):
	"""Search experiments 
	This view still interferes with pagination, as when the search returns more
	than on page of hits the pagination does not work as it uses the "page" key 
	"""
	if request.GET:
		a,b,c = map(float,(request.GET['a'],request.GET['b'],request.GET['c']))
		up = 1 + float(request.GET['tolerance'])/100.
		down = 1 - float(request.GET['tolerance'])/100.
		limits = ((a*down,a*up),(b*down,b*up),(c*down,c*up))
		experiments = Experiment.objects.filter(a__range=(str(a*down), str(a*up))).filter(b__range=(str(b*down), str(b*up))).filter(c__range=(str(c*down), str(c*up)))
		return list_detail.object_list(request,
										   queryset=experiments,
										   template_name='experiments/experiment_search_cell.html',
										   extra_context={'limits':limits})
	else:
		return render_to_response('experiments/experiment_search_cell.html',
								context_instance=RequestContext(request))

def experiment_frames(request,id):
	"""View experiment frames as flash swf files 
	"""
	exp = Experiment.objects.get(id=id)
	movies_glob = PROJECT_DIR + exp.frames_url() + '*.swf'
	movies = glob.glob(movies_glob)
	runs = map(os.path.basename,movies)
	runs.sort()
	return render_to_response('experiments/experiment_frames.html',
							{'exp':exp,'runs':runs},
							context_instance=RequestContext(request))

def experiment_stats(request,id,type=None):
	"""Testing flot plotting
	"""
	exp = Experiment.objects.get(id=id)
	ds = Dataset(exp.origdir)
	if not type:
		type = 'resolutionstats'
	d = DatFile(ds.get_dat_file(type))
	d = d.json()
	return render_to_response('experiments/experiment_stats.html',
							{'d':d,'exp':exp},
							context_instance=RequestContext(request))

def experiment_ini(request,id,ini_type):
	"""View experiment datacoll details 
	"""
	exp = Experiment.objects.get(id=id)
	ds = Dataset(exp.origdir)
	ini = ds.get_ini_file(ini_type)
	if ini:
		dic = IniFile(ini).as_dictionary()
	else:
		dic = {'ERROR':[('SORRY!', 'No %s type ini file in %s!'%(ini_type,exp.origdir))]}
	return render_to_response('experiments/experiment_ini.html',
							{'exp':exp,'dic':dic},
							context_instance=RequestContext(request))	

def cell_list(request,user=None):
	"""List all unit cells
	"""
	if user:
		experiments = Experiment.objects.filter(origdir__icontains=user)	
	else:
		experiments = Experiment.objects.all()	
	return list_detail.object_list(request,
									   paginate_by=50,
									   queryset= Experiment.objects.values_list('a','b','c','alpha','beta','gamma','volumen','sg').order_by('sg'),	
									   template_name='experiments/cell_list.html',
									   )

def assignsample(request,id):
	"""Assigns sample to the experiment
	"""
	exp = Experiment.objects.get(id=id)
	samples = Sample.objects.all()
	if request.method == "POST":
		exp.sample = Sample.objects.get(id=request.POST['sample_id'])
		exp.save()
		return redirect('/experiments/')
	return render_to_response('experiments/assignsample.html',
							{'exp':exp, 'samples':samples},
							context_instance=RequestContext(request))

def get_related(exp):
	import difflib
	s = difflib.SequenceMatcher()
	related = []
	for e in Experiment.objects.all():
		s.set_seqs(exp.name,e.name)
		if s.ratio() > 0.6:
			related.append((e,s.ratio()))
		related = sorted(related, key = lambda a: a[1], reverse = True)
	return related
	
def view_experiment(request,id):
	"""View information on particular experiment
	"""
	exp = Experiment.objects.get(id=id)
	possibly_related = get_related(exp)
	return list_detail.object_detail(request,
									queryset=Experiment.objects.filter(id=id),
									object_id=exp.id,
									template_name='experiments/experiment.html',
									extra_context= {"possibly_related" : possibly_related})

def getip(request):
	client_address = request.META['REMOTE_ADDR']
	return render_to_response('experiments/getip.html',{'ip':client_address})
	
