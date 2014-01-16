from django.shortcuts import render_to_response
from django.views.generic import list_detail
from django.template import RequestContext
from crysalis.models import *
from itertools import groupby

def dataset_list(request,name):
	"""List all experiments"""
	datasets = LogDataset.objects.all()
	if name:
		datasets = LogDataset.objects.filter(name=name)	
	return list_detail.object_list(request,
								   paginate_by=50,
								   queryset=datasets.order_by('-start'),
								   template_name='crysalis/dataset_list.html')

def duplicates(request):
	"""List all experiments with duplicate names"""
	all_datasets = LogDataset.objects.all()
	names = [name[0] for name in LogDataset.objects.values_list('name')]
	def more_than_one(name):
		return LogDataset.objects.filter(name=name).count() > 1
	multiple_names = filter(more_than_one,names)
	multiple_names = list(set(multiple_names))
	result={}
	for name in multiple_names:
		result[name] = LogDataset.objects.filter(name=name)
	return render_to_response('crysalis/duplicates.html', {'datasets':result})

def historylog(request):
	"""Show history log file"""
	hlog = HistoryLog()
	dcs = hlog.datacollections()
	return render_to_response('crysalis/historylog.html',
							{'dcs':dcs},
							context_instance=RequestContext(request)
							)

def ccdlogs(request):
	"""Return a list of ccd log files"""
	ld = LogDir.objects.get(pk = LOG_FILE_DIR)
	ld.update()
	ccds = ld.logfile_set.all()
	ccds = ccds.order_by('-date')
	return render_to_response('crysalis/ccdlogs.html',
							{'ccds':ccds},
							context_instance=RequestContext(request)
							)

def current(request):
	"""Return a list of ccd log files"""
	ld = LogDir.objects.get(pk = LOG_FILE_DIR)
	ld.update()
	log = LogFile()
	last = ld.logs[-1]
	log.create(last)
	log.create_datasets()
	tail = log.as_pre(num=10)
	#datasets = ccd.unique_datasets()
	return render_to_response('crysalis/current.html',
							{'last':log,'tail':tail},
							context_instance=RequestContext(request),	
							)

def viewlog(request,log):
	"""View ccd log file as text"""
	lf = LogFile()
	lf.create(log)
	lf.create_datasets()
	return render_to_response('crysalis/viewlog.html',
							{'lines':lf.as_pre()},
							context_instance=RequestContext(request)
							)

from reportlab.pdfgen import canvas
from django.http import HttpResponse

def create_pdf(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response
