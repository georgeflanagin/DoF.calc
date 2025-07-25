# -*- coding: utf-8 -*-
import typing
from   typing import *

###
# Standard imports, starting with os and sys
###
min_py = (3, 11)
import os
import sys
if sys.version_info < min_py:
    print(f"This program requires Python {min_py[0]}.{min_py[1]}, or higher.")
    sys.exit(os.EX_SOFTWARE)

###
# Other standard distro imports
###
import argparse
from   collections.abc import *
import contextlib
import csv
import getpass
import logging
from   logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
import math

###
# Installed libraries like numpy, pandas, paramiko
###
import numpy
import pandas

###
# From hpclib
###
import linuxutils
from   urdecorators import trap
from   urlogger import URLogger

###
# imports and objects that were written for this project.
###

###
# Global objects
###
logger = None
f_stops = ( 1.0, 1.4, 1.8, 2.0, 
            2.4, 2.8, 3.5, 4.0, 
            5.6, 6.3, 7.1, 8.0, 
            11.0, 16.0, 22.0)


###
# Credits
###
__author__ = 'George Flanagin'
__copyright__ = 'Copyright 2025'
__credits__ = None
__version__ = 0.1
__maintainer__ = 'George Flanagin'
__email__ = 'gflanagin@richmond.edu'
__status__ = 'in progress'
__license__ = 'MIT'


@trap
def hyperfocal(focal_len:float, f:float, circle:float) -> float:
    return focal_len * focal_len / f / circle


def intervals(hyperfocal:float, min_dist:float, n:int) -> tuple:
    multiplier = math.pow(hyperfocal/min_dist, 1/float(n))
    yield from ( min_dist * math.pow(multiplier, i) 
        for i in range(0, n))

@trap
def normalize_units(myargs:argparse.Namespace) -> argparse.Namespace:

    # Convert mm to m.
    myargs.length /= 1000
    myargs.min_dist = max(myargs.min_dist, 2*myargs.length)
    
    # Most of the time, the circle of confusion dimensions are given
    # in mm, and everything else is in m, so we need to convert.
    myargs.circle = myargs.circle/1000

    print(f"{myargs=}")

    return myargs


@trap
def thin_lens(length:float,
        max_aperture:float,
        circle:float,
        min_dist:float,
        ) -> Iterator[tuple]:
    """
    Return a data frame containing near and far focus limits 
    across the parameters given.
    """
    global f_stops

    for stop in ( x for x in f_stops if not x < max_aperture):
        H = hyperfocal(length, stop, circle)
        for s in intervals(H, min_dist, 20):
            numerator = s * (H - length)
            d_near = numerator / ( H + (s - 2 * length))
            d_far  = numerator / ( H - s )

            yield stop, round(H,2), round(s,2), round(d_near,3), round(d_far,3)


@trap
def DoFcalc_main(myargs:argparse.Namespace) -> int:
    """
    Step 1 is the normalization of the different units of measure.
        We are going to put everything in millimeters.
    """
    myargs = normalize_units(myargs)

    columns=['f-stop', 'hyperfocal', 'subj-dist', 'near-limit', 'far-limit']
    if myargs.fmt == 'csv': 
        with open(f"{myargs.filename}.csv", 'w', newline='') as f:
            writer=csv.writer(f)
            writer.writerow(columns)
            writer.writerows(thin_lens(myargs.length, myargs.max_aperture, 
                    myargs.circle, myargs.min_dist))
    else:
        frame = pandas.DataFrame(
            thin_lens(myargs.length, myargs.max_aperture, 
                    myargs.circle, myargs.min_dist), 
                columns)
        
    return os.EX_OK


if __name__ == '__main__':

    here       = os.getcwd()
    progname   = os.path.basename(__file__)[:-3]
    configfile = f"{here}/{progname}.toml"
    logfile    = f"{here}/{progname}.log"
    lockfile   = f"{here}/{progname}.lock"
    
    parser = argparse.ArgumentParser(prog="DoFcalc", 
        description="""
What DoFcalc does, DoFcalc does best. 

You supply the basic lens specs. Example: 105mm f/2 as 
--max 2 --len 105. If you know the minimum focus distance, you 
can supply it as --min 2.0 for 2.0 meters. The default is 1 meter.

You can also supply the circle of confusion in microns, but the
default of --circle 15.0 is suitable for most modern cameras.

The result is a chart-able csv file or a pandas data frame if
you have pandas installed on this computer.

""")


    # Standard arguments.
    parser.add_argument('--log-level', type=int, default=INFO,
        choices=(CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET),
        help=f"Logging level, defaults to {logging.INFO}")

    parser.add_argument('-o', '--output', type=str, default="",
        help="Output file name")
    
    parser.add_argument('-z', '--zap', action='store_true', 
        help="Remove old log file and create a new one.")


    # Arguments for this program.
    parser.add_argument('-l', '--length', type=int, required=True,
        help="Focal length of the lens in mm.")

    parser.add_argument('--max-aperture', type=float, required=True,
        help="f-stop when the lens is wide open.")

    parser.add_argument('--min-dist', type=float, default=1.0, 
        help="Minimum focus distance. Defaults to 1 meter.")

    parser.add_argument('--fmt', type=str, default='csv',
        choices=('csv', 'pandas'),
         help="Output format: csv or pandas.")

    parser.add_argument('-f', '--filename', default='DoFcalc')

    parser.add_argument('-c', '--circle', type=float, default=15.0,
        help="Circle of confusion. Default: 15 microns")

    myargs = parser.parse_args()
    if myargs.zap:
        try:
            unlink(logfile)
        except:
            pass


    logger = URLogger(logfile=logfile, level=myargs.log_level)

    try:
        outfile = sys.stdout if not myargs.output else open(myargs.output, 'w')
        with contextlib.redirect_stdout(outfile):
            sys.exit(globals()[f"{progname}_main"](myargs))

    except Exception as e:
        print(f"Escaped or re-raised exception: {e}")

