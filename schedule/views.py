from calendar import HTMLCalendar
from itertools import groupby
from datetime import datetime, timedelta, date

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape as esc
from django.shortcuts import render_to_response
from django.template import RequestContext

from homebase.samples.models import Sample
from homebase.experiments.models import Experiment

class ExperimentCalendar(HTMLCalendar):
	def __init__(self, experiments):
		super(ExperimentCalendar, self).__init__()
		self.experiments = self.group_by_day(experiments)

	def formatday(self, day, weekday):
		if day != 0:
			cssclass = self.cssclasses[weekday]
			if date.today() == date(self.year, self.month, day):
				cssclass += ' today'
			if day in self.experiments:
				cssclass += ' filled'
				body = ['']
				for experiment in self.experiments[day]:
					body.append('<a href="%s">' % experiment.get_absolute_url())
					body.append(esc(experiment.name))
					body.append('</a> ')
				#body.append('')
				return self.day_cell(cssclass, '<h2>%d</h2> %s' % (day, ''.join(body)))
			return self.day_cell(cssclass, day)
		return self.day_cell('noday', '&nbsp;')

	def formatmonth(self, year, month):
		self.year, self.month = year, month
		return super(ExperimentCalendar, self).formatmonth(year, month)

	def formatmonthinyear(self,year,month):
		v = []
		a = v.append
		a('<table border="0" cellpadding="0" cellspacing="0" class="year">')
		a('\n')
		a('<tr><th colspan="7"><a href="./%s">%s</a></th></tr>' %(month,month))
		for week in self.monthdays2calendar(year,month):
			a('<tr>')
			for day in week:
				if day[0] != 0:
					cssclass = self.cssclasses[day[1]]
					if Experiment.objects.filter(start__range=start_end_of_date(date(year,month,day[0]))):
						cssclass += ' filled'
					a(self.day_cell(cssclass, '%s' % day[0]))
				else:
					a(self.day_cell('noday','&nbsp;' ))
			a('</tr>')
			a('\n')
		a('</table>')
		a('\n')
		return ''.join(v)

	def formatyear(self, theyear):
		"""
		Return a formatted year as a table of tables.
		"""
		v = []
		a = v.append
		a('<table border="0" cellpadding="0" cellspacing="0" class="year">')
		a('\n')
		a('<tr><th>%s</th></tr>' %  theyear)
		for m in range(1, 13):
			a('<tr>')
			a('<td>')
			a(self.formatmonthinyear(theyear, m))
			a('</td>')
			a('</tr>')
		a('</table>')
		return ''.join(v)

	def group_by_day(self, experiments):
		field = lambda experiment: experiment.start.day
		return dict(
			[(day, list(items)) for day, items in groupby(experiments, field)]
		)

	def day_cell(self, cssclass, body):
		return '<td class="%s">%s</td>' % (cssclass, body)

def calendar_month(request, year, month):
	year, month = map(int,(year,month))
	my_experiments = Experiment.objects.order_by('start').filter(
								start__year=year, start__month=month
								)
	cal = ExperimentCalendar(my_experiments).formatmonth(year, month)
	return render_to_response('schedule/calendar_month.html', 
							{'calendar': mark_safe(cal), 'month':month, 'year':year},
							context_instance=RequestContext(request))	

def calendar_year(request,year):
	year = int(year)
	my_experiments = Experiment.objects.order_by('start').filter(start__year=year)
	cal = ExperimentCalendar(my_experiments).formatyear(year)
	return render_to_response('schedule/calendar_year.html', {'calendar': mark_safe(cal),'year':year},
							context_instance=RequestContext(request))	

def start_end_of_date(date):
    start = datetime.min.replace(year=date.year, month=date.month,
        day=date.day)
    end = (start + timedelta(days=1)) - timedelta.resolution
    return (start, end)

def schedule(request,status):
	"""
	Schedule of the samples by order of their addition.
	"""
	now = datetime.today()
	sched = Sample.objects.all()
	if status:
		sched = Sample.objects.filter(status=status)
	sched = sched.order_by('date_added')
	sched = [(now + timedelta(i+1), s) for i,s in enumerate(sched)]
	return render_to_response('schedule/schedule.html', 
							{'sched': sched},
							context_instance=RequestContext(request))	
