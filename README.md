# Sweep

```
usage: sweep.py [-h] [-a AGE] [-v] [--newer] [-n] [-o OUTPUT_DIR] [--version]
                input_dir

Sweeps files under the rug which haven't been used in a while where used is
defined in terms of the macOS metadata field kMDItemLastUsedDate. Note that
this is *not* the same thing as the filesystem access time stamp. The 'rug' is
a metaphor for some directory where you don't have to think about it.

positional arguments:
  input_dir             directory in which to scan for files which have not
                        been recently used

optional arguments:
  -h, --help            show this help message and exit
  -a AGE, --age AGE     the age in days after which a file is considered to be
                        not recently used. default is 7 days
  -v, --verbose         show age of files in columnar format
  --newer               invert the set of files to be swept to be files used
                        more recently than cut off age
  -n, --dry-run         dry run. do not sweep files 'under the rug'.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        directory into which files will be swept. defaults to
                        input_dir/rug
  --version             show program's version number and exit
```

Use this script with launchd, automator, cron, etc to keep your desktop
tidy.

