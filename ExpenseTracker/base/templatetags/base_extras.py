from django import template

register = template.Library()

# Help to combine django-filter with pagination. Removes excessive page additions as a result of the quickfix that I use
@register.filter
def remove_obsolete_pages(data):
	if 'page' in data:
		data._mutable = True
		data.pop('page')
		data._mutable = False
	return data.urlencode()