from django import template

register = template.Library()

@register.filter(name='zip')
def zip_lists(a, b):
  return zip(a, b)

@register.filter(name='percent')
def percent(a, b):
  # Divides a by be then multiplies by 100
  if b != 0:
    return (int(a)/int(b))*100
  else:
    return 0

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

@register.filter(name='range')
def template_range(a, b):
  return range(a, b)

@register.filter(name='split')
def split_participants(list, section):
  # Splits participants list in half, returns 1st or 2nd based on section, if section is not 1 or 2 returns entire list
  if section == 1:
    return list[:5]
  elif section == 2:
    return list[5:]
  else:
    return list
  
@register.filter(name='splitZip')
def split_zip_participants(list):
  # Splits participants list in half, and zips them
  blue_team = list[:5]
  red_team = list[5:]
  return zip(blue_team, red_team)
  
  