```
usage: DoFcalc [-h] [-o OUTPUT] -l LENGTH --max-aperture MAX_APERTURE [--min-dist MIN_DIST] [--fmt {csv}]
               [-f FILENAME] [-c CIRCLE]

What DoFcalc does, DoFcalc does best.

You supply the basic lens specs. Example: 105mm f/2 becomes
"--max 2 --len 105". If you know the minimum focus distance, you
can supply it as --min 2.0 for 2.0 meters. The default is 1 meter.

You can also supply the circle of confusion in microns, but the
default of --circle 15.0 is suitable for most modern cameras.

The result is a chart-able csv file or a pandas data frame if
you have pandas installed on this computer.

A typical line of output looks like this for an 85mm lens:

f-stop|  dist|     near|   far
------+------+---------+----------
7.1   |  5.4 |   -0.393|   0.46

which means that an 85mm lens focused at 5.4 meters and
stopped down to f/7.1 will have a DoF that goes from
5.007 meters to 5.86 meters.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file name
  -l LENGTH, --length LENGTH
                        Focal length of the lens in mm.
  --max-aperture MAX_APERTURE
                        f-stop when the lens is wide open.
  --min-dist MIN_DIST   Minimum focus distance. Defaults to 1 meter.
  --fmt {csv}           Output format: csv
  -f FILENAME, --filename FILENAME
  -c CIRCLE, --circle CIRCLE
                        Circle of confusion. Default: 15 microns
```
