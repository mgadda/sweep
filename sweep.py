#!/usr/bin/env python
import subprocess
import dateutil.parser
import datetime

files = subprocess.check_output(
  ["find", "/Users/mgadda/Desktop", "-type", "f", "-depth", "1"]).split("\n")


#cmd = make_ccmd('mdls -name kMDItemLastUsedDate').and_then('awk -F " = " \'{ print $2 }\'').and_then('date -j -f "%Y-%m-%d %H:%M:%S %z" "2013-01-09 20:48:27 +0000" "+%s"')

def last_used_date(filename):
  try:
    mdls_result = subprocess.check_output(['mdls', '-name', 'kMDItemLastUsedDate', filename])
    [_, date_str] = mdls_result.split(' = ')
    return dateutil.parser.parse(date_str)
  except:
    return None


filemap = {filename: last_used_date(filename) for filename in files}

def is_old(filename, last_used):
  if last_used is None:
    return False

  tz_info = last_used.tzinfo

  now = datetime.datetime.now(tz_info)
  delta = now - last_used
  print filename + " was last accessed " + str(delta.days) + " days ago"

  return delta.days > 5

  #

  #diff = datetime.datetime.now(tz_info) - your_timezone_aware_variable

old_filenames = [k for k,v in filemap.iteritems() if is_old(k, v)]
print("\n".join(old_filenames))
