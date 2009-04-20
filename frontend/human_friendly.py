

def render_timedelta(td):
  from datetime import datetime, timedelta 

  seconds = td.seconds % 60
  minutes = (td.seconds // 60) % 60
  hours = td.seconds // (60*60)
  days = td.days % 365
  
  if(td < timedelta(0)):
    return "The FUTURE!"

  ret_val = ""
  if td < timedelta(0, 60*4): #short enough that we care about seconds
    if seconds == 1:
      ret_val = "1 second"
    else:
      ret_val = str(seconds) + " seconds"
          
  if td < timedelta(0, 60*60*4) and td > timedelta(0,60): #short enough that we care about minutes
    if len(ret_val) > 0:
      ret_val = ", " + ret_val
    if minutes == 1:
      ret_val = "1 minute" + ret_val
    else:
      ret_val = str(minutes) + " minutes" + ret_val

  if td < timedelta(3) and td > timedelta(0,60*60): #short enough that we care about hours
    if len(ret_val) > 0:
      ret_val = ", " + ret_val
    if hours == 1:
      ret_val = "1 hour" + ret_val
    else:
      ret_val = str(hours) + " hours" + ret_val
  
  if td > timedelta(1):
    if len(ret_val) > 0:
      ret_val = ", " + ret_val
    if hours == 1:
      ret_val = "1 day" + ret_val
    else:
      ret_val =  str(days) + " days" + ret_val
  
  return ret_val
