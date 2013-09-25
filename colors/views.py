from django.shortcuts import render_to_response
import random 

theme = 'all' 
def random_color():
	c = [random.randrange(0,255) for i in range(2)]
	c = tuple(c)
	if theme == 'green':
		color = '#%02x66%02x' % c
	elif theme == 'blue':
		color = '#%02x%02xaa' % c
	elif theme == 'red':
		color = '#ff%02x%02x' % c
	else:
		c = tuple([random.randrange(0,230) for i in range(3)])
		color = '#%02x%02x%02x' % c
	return color

def random_list(n=100):
	return [random_color() for i in range(n)]


def colors(request,num=10):
	list = random_list(int(num))
	return render_to_response( 'colors/colors.html',{'list':list,'bglist':[1,2,3,4,5,6]})


def colors1(request,num=10):
	list = random_list(int(num))
	return render_to_response( 'colors/colors1.html',{'list':list})
