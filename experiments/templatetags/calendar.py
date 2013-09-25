from datetime import datetime

def calendar_table(value, arg):
  cal = {}
  dates = value.keys()
  dates.sort()
  for date in value:
    d, m, y = date.day, date.month, date.year
    if y not in cal:
      cal[y] = {}
    if m not in cal[y]:
      cal[y][m] = []
    cal[y][m].append(d)
  result = ''
  
  for y in cal:
    result += "<h2 style=\"clear: left\">%d</h2>" % y
    for m in cal[y]:
      sd = datetime(y, m, 1)
      result += sd.strftime("<div class=\"month\"><h3>%B</h3>")
      result += '<table><thead><tr><th>M</th><th>T</th><th>W</th><th>T</th><th>F</th><th>S</th><th>S</th></tr></thead><tbody><tr>'
      days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m]
      if m == 2 and y % 4 == 0 and (y % 100 <> 0 or y % 400 == 0):
        days_in_month += 1
      w = sd.weekday()
      for i in range(w):
        result += '<td></td>'
        
      for i in range(days_in_month):
        if i in cal[y][m]:
          s = arg.replace('[Y]', "%.4d" % y).replace('[m]', "%.2d" % m).replace('[d]', "%.2d" % d)
          result += "<td><a href=\"%s\">%d</a></td>" % (s, i + 1)
        else:
          result += "<td>%d</td>" % (i + 1)
        w = (w + 1) % 7
        if w == 0 and i + 1 < days_in_month:
          result += "</tr><tr>"

      for i in range(w,7):
        result += '<td></td>'

      result += '</tr></tbody></table></div>'
  return result

