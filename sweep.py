#!/usr/bin/env python

import argparse
import datetime
import operator
import subprocess
import sys

import dateutil.parser


def last_used_date(filename):
  try:
    mdls_result = subprocess.check_output(['mdls', '-name', 'kMDItemLastUsedDate', filename])
    [_, date_str] = mdls_result.split(' = ')
    return dateutil.parser.parse(date_str)
  except:
    return None


def is_older_than(age, fn=operator.gt, verbose=False):
  def age_in_days(filename, last_used):
    if last_used is None:
      return False

    tz_info = last_used.tzinfo

    now = datetime.datetime.now(tz_info)
    delta = now - last_used
    return delta.days

    if verbose:
      print str(delta.days) + " days\t\t" + filename

  return lambda filename, last_used: \
    fn(age_in_days(filename, last_used), age)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Sweeps files under the rug")
  parser.add_argument("directory",
                      help="directory in which to scan for files which have not been recently used",
                      type=str)
  parser.add_argument("--age",
                      help="the age in days after which a file is considered to be not recently used",
                      type=int)
  parser.add_argument("--verbose",
                      help="show age of files in columnar format",
                      action='store_true')
  parser.add_argument("--newer",
                      help="output files used more recently than cut off age",
                      action='store_true')
  parser.set_defaults(directory='.', arg=7)
  args = parser.parse_args()

  files = subprocess.check_output(
    ["find", args.directory, "-type", "f", "-depth", "1"], stderr=sys.stderr).split("\n")

  filemap = {filename: last_used_date(filename) for filename in files}
  old_filenames = [k for k,v in filemap.iteritems()
                   if is_older_than(age=args.age,
                                    fn=(operator.lt if args.newer else operator.gt),
                                    verbose=args.verbose)(k, v)]
  print("\n".join(old_filenames))
