from django import template

register = template.Library()

@register.filter(name='zip')
def zip_lists(a, b):
  return zip(a, b)

@register.filter(name='percent')
def percent(a, b):
  # Divides a by be then multiplies by 100
  return (int(a)/int(b))*100

@register.filter(name='div')
def div(a, b):
  return int(a)/int(b)

@register.filter(name='time')
def time(a):
  m, s = divmod(a, 60)
  h, m = divmod(m, 60)
  if h == 0:
    return f'{m}m{s}s'
  return f'{h}h{m}m{s}s'
  