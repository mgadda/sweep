#!/usr/bin/env python

import argparse
import datetime
import operator
import os
import subprocess
from fnmatch import fnmatch

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

    if verbose:
      print str(delta.days) + " days\t\t" + filename

    return delta.days

  return lambda filename, last_used: \
    fn(age_in_days(filename, last_used), age)


CEND      = '\33[0m'
CRED    = '\33[31m'
CYELLOW = '\33[33m'


def warn(str):
  print(CYELLOW + str + CEND)


def error(str):
  print(CRED + str + CEND)


if __name__ == "__main__":
  desc = (
    "Sweeps files under the rug which haven't been used in a while where used is "
    "defined in terms of the macOS metadata field kMDItemLastUsedDate. Note that "
    "this is *not* the same thing as the filesystem access time stamp. The "
    "'rug' is a metaphor for some directory where you don't have to think about "
    "it."
  )

  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument("input_dir",
                      help="directory in which to scan for files which have not been recently used",
                      type=str)
  parser.add_argument("-a", "--age",
                      help="the age in days after which a file is considered to be not recently used. default is 7 days",
                      type=int)
  verbose_action = parser.add_argument("-v", "--verbose",
                      help="show age of files in columnar format",
                      action='store_true')
  parser.add_argument("--newer",
                      help="invert the set of files to be swept to be files used more recently than cut off age",
                      action='store_true')
  parser.add_argument("-n", "--dry-run",
                      help="dry run. do not sweep files 'under the rug'.",
                      action='store_true')
  parser.add_argument("-o", "--output-dir",
                      help="directory into which files will be swept. defaults to input_dir/rug",
                      dest='output_dir')
  parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
  parser.set_defaults(age=7, output_dir=None)
  args = parser.parse_args()

  # TODO: Implement policy for directories such that they will be
  # considered fresh even if their metadata indicates otherwise, so long as
  # there exists a descendent file or directory which satisfies our age
  # requirements

  input_dir = os.path.abspath(args.input_dir)

  if args.output_dir is None:
    output_dir = os.path.normpath(os.path.join(input_dir, "rug"))
  else:
    output_dir = os.path.abspath(args.output_dir)

  if output_dir == input_dir or (os.path.exists(output_dir) and os.path.samefile(input_dir, output_dir)):
    error("ERROR: Input and output directories cannot be the same.")
    exit(1)

  common_ancestor = os.path.commonprefix([input_dir, output_dir])
  head = None
  if common_ancestor != "/":
    head = os.path.relpath(output_dir, common_ancestor).split('/')[0]

  files = [os.path.join(input_dir, file) for file in os.listdir(input_dir)
           if not (head is not None and fnmatch(file, head) or fnmatch(file, ".DS_Store"))]

  filemap = {filename: last_used_date(filename) for filename in files}
  old_filenames = [k for k,v in filemap.iteritems()
                   if is_older_than(age=args.age,
                                    fn=(operator.lt if args.newer else operator.gt),
                                    verbose=args.verbose)(k, v)]

  for filename in old_filenames:
    file = os.path.basename(filename)
    src = os.path.normpath(filename)
    dst = os.path.normpath(os.path.join(output_dir, file))

    if args.verbose:
      print "mv %s -> %s" % (src, dst)

    if not args.dry_run:
      os.renames(src, dst)

  if args.dry_run:
    warn("\n*** This was a dry run. no files have been harmed. ***")
