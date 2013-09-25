from django import template
import random
register = template.Library()


def colorramp(value,max_value):
	if not value:
		return 'yellow'
	value = float(value)
	max_value = float(max_value)
	i = min(value,max_value)/max_value
	c = (int(i*255),100,int((1-i)*255))
	color = '#%02x%02x%02x' % c
	return color

register.filter('colorramp', colorramp)
