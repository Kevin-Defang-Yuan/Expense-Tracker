from django import template

register = template.Library()

@register.filter
def remove_obsolete_pages(data):
	if 'page' in data:
		data._mutable = True
		data.pop('page')
		data._mutable = False
	return data.urlencode()