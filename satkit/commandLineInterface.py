#
# Copyright (c) 2019-2021 Pertti Palo, Scott Moisik, and Matthew Faytak.
#
# This file is part of Speech Articulation ToolKIT 
# (see https://github.com/giuthas/satkit/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# The example data packaged with this program is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License. You should have received a
# copy of the Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License along with the data. If not,
# see <https://creativecommons.org/licenses/by-nc-sa/4.0/> for details.
#
# When using the toolkit for scientific publications, please cite the
# articles listed in README.markdown. They can also be found in
# citations.bib in BibTeX format.
#

import argparse
import logging
import os
import os.path
import sys
import time
import datetime 

# local modules
import satkit.pd as pd
import satkit.pd_annd_plot as pd_annd_plot
import satkit.io.AAA as satkit_AAA
import satkit.io as satkit_io


def widen_help_formatter(formatter, total_width=140, syntax_width=35):
    """Return a wider HelpFormatter for argparse, if possible."""
    try:
        # https://stackoverflow.com/a/5464440
        # beware: "Only the name of this class is considered a public API."
        kwargs = {'width': total_width, 'max_help_position': syntax_width}
        formatter(None, **kwargs)
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        warnings.warn("Widening argparse help formatter failed. Falling back on default settings.")
    return formatter


class BaseCLI():
    """
    This class is the root class for SATKIT commandline interfaces. 
    It is not fully functional by itself: It does not read files nor run any processing on files. 
    """

    def __init__(self, description):
        self.description = description
        
        self.parse_args()

        self.set_up_logging()

            
    ##
    ## Setting up and running the argument parser.
    ##
        
    def _init_parser(self):
        self.parser = argparse.ArgumentParser(description=self.description,
            formatter_class = widen_help_formatter(argparse.HelpFormatter,
                                                   total_width=100,
                                                   syntax_width=35))

        # mutually exclusive with reading previous results from a file
        helptext = (
            'Path containing the data to be read.'
            'Supported types are .pickle files, and directories containing files exported from AAA. '
            'Loading from .m, .json, and .csv are in the works.'
        )
        self.parser.add_argument("load_path", help=helptext)


    def _add_optional_arguments(self):
        helptext = (
            'Set verbosity of console output. Range is [0, 3], default is 1, '
            'larger values mean greater verbosity.'
        )
        self.parser.add_argument("-v", "--verbose",
                                 type=int, dest="verbose",
                                 default=1,
                                 help=helptext,
                                 metavar = "verbosity")
    

    def parse_args(self):
        """
        Create a parser for commandline arguments with argparse and 
        parse the arguments.

        """
        self._init_parser()
        self._add_optional_arguments()

        self.args = self.parser.parse_args()


    ##
    ## Setting up logging.
    ##  
    def set_up_logging(self):
        """
        Set up logging with the loggin module. Main thing to do is set the
        level of printed output based on the verbosity argument.

        """
        self.logger = logging.getLogger('satkit')
        self.logger.setLevel(logging.INFO)

        # also log to the console at a level determined by the --verbose flag
        console_handler = logging.StreamHandler() # sys.stderr

        # Set the level of logging messages that will be printed to
        # console/stderr.
        if not self.args.verbose:
            console_handler.setLevel('WARNING')
        elif self.args.verbose < 1:
            console_handler.setLevel('ERROR')
        elif self.args.verbose == 1:
            console_handler.setLevel('WARNING')
        elif self.args.verbose == 2:
            console_handler.setLevel('INFO')
        elif self.args.verbose >= 3:
            console_handler.setLevel('DEBUG')
        else:
            logging.critical("Unexplained negative argument " +
                             str(self.args.verbose) + " to verbose!")
        self.logger.addHandler(console_handler)

        self.logger.info('Data run started at ' + str(datetime.datetime.now()))


class RawCLI(BaseCLI):
    """
    Commandline interface for runnig metrics on raw ultrasound data.
    """

    def __init__(self, description, processing_functions, plot=True):
        """
        Setup and run the commandline interface.
        Description is what this version will be called if called with -h or --help.
        processing_functions is a dict of the callables that will be run on each recording.
        """
        super().__init__(description)

        if not os.path.exists(self.args.load_path):
            self.logger.critical('File or directory does not exist: ' + self.args.load_path)
            self.logger.critical('Exiting.')
            sys.exit()
        elif os.path.isdir(self.args.load_path): 
            exclusion_list_name = None
            if self.args.exclusion_filename:
                exclusion_list_name = self.args.exclusion_filename

            # this is the actual list of recordings that gets processed 
            # token_list includes meta data contained outwith the ult file
            self.recordings = satkit_AAA.get_recording_list(self.args.load_path,
                                                      self.args.exclusion_filename)

        elif os.path.splitext(self.args.load_path)[1] == '.pickle':
            self.recordings = satkit_io.load_pickled_data(self.args.load_path)
        elif os.path.splitext(self.args.load_path)[1] == '.json':
            self.recordings = satkit_io.load_json_data(self.args.load_path)
        else:
            self.logger.error('Unsupported filetype: ' + self.args.load_path + '.')

### this is broken. it does not care if data has been read or not.
        # calculate the metrics
        self.data = []
        for recording in self.recordings:
            datum = {}
            for key in processing_functions.keys():
                # only run the metric calculations if the results do not already exist
                if key not in datum:
                    datum[key] = processing_functions[key](recording)
            self.data.append(datum)
        # the metric functions should maybe be wrapped as objects so
        # that we can access names on other things via names and
        # what not instead of wrapping them in a dict
            
        # Plot the data into files if asked to.
        if plot:
            self.logger.info("Drawing ISSP 2020 plot.")
            pd_annd_plot.ISSP2020_plots(self.recordings, self.data, self.args.figure_dir)

        if self.args.output_filename:
            if os.path.splitext(self.args.output_filename)[1] == '.pickle':
                pd.save2pickle((self.recordings, self.data), self.args.output_filename)
                self.logger.info("Wrote data to file " + self.args.output_filename + ".")
            elif os.path.splitext(self.args.output_filename)[1] == '.json':
                self.logger.error('Unsupported filetype: ' + self.args.output_filename + '.')
            else:
                self.logger.error('Unsupported filetype: ' + self.args.output_filename + '.')

        self.logger.info('Data run ended at ' + str(datetime.datetime.now()))

        
    def process_recordings(self, processing_functions):
        

    def _add_optional_arguments(self):
        self.parser.add_argument("-e", "--exclusion_list", dest="exclusion_filename",
                                 help="Exclusion list of data files that should be ignored.",
                                 metavar="file")

        helptext = (
            'Save metrics to file. '
            'Supported type is .pickle. '
            'Saving to .json, .csv., and .m may be possible in the future.'
        )
        self.parser.add_argument("-o", "--output", dest="output_filename",
                                 help=helptext, metavar="file")

        helptext = (
            'Destination directory for generated figures.'
        )
        self.parser.add_argument("-f", "--figures", dest="figure_dir",
                                 default="figures",
                                 help=helptext, metavar="dir")

        # Adds the verbosity argument.
        super()._add_optional_arguments()


        
class RawAndSplineCLI(RawCLI):

    def __init__(self, description, processing_functions, plot=True):
        super().__init__(description, processing_functions, plot=plot)
        self.parse_args()

        if not os.path.exists(self.args.load_path):
            self.logger.critical('File or directory doesn not exist: ' + self.args.load_path)
            self.logger.critical('Exiting.')
            sys.exit()
        elif os.path.isdir(self.args.load_path): 
            exclusion_list_name = None
            if self.args.exclusion_filename:
                exclusion_list_name = self.args.exclusion_filename

            # this is the actual list of recordings that gets processed 
            # recording_list includes meta data contained outwith the ult file
            recording_list = satkit_AAA.get_recording_list(self.args.load_path,
                                                       self.args.exclusion_filename,
                                                       self.args.spline_file)

            # calculate the metrics
            data = []
            for recording in recording_list:
                datum = {}
                for key in processing_functions.keys():
                    datum[key] = processing_functions[key](recording)
                data.append(datum)
            # the metric functions should maybe be wrapped as objects so
            # that we can access names on other things via names and
            # what not instead of wrapping them in a dict

            #data = [datum for datum in data if not datum is None]
        elif os.path.splitext(self.args.load_path)[1] == '.pickle':
            recording_list, data = satkit_io.load_pickled_data(self.args.load_path)
        elif os.path.splitext(self.args.load_path)[1] == '.json':
            recording_list, data = satkit_io.load_json_data(self.args.load_path)
        else:
            self.logger.error('Unsupported filetype: ' + self.args.load_path + '.')

        # Plot the data if asked to.
        if plot:
            self.logger.info("Drawing ISSP 2020 plot.")
            pd_annd_plot.ISSP2020_plots(recording_list, data, self.args.figure_dir)
            #pd_annd_plot.ultrafest2020_plots(recording_list, data, self.args.figure_dir)

        if self.args.output_filename:
            if os.path.splitext(self.args.output_filename)[1] == '.pickle':
                pd.save2pickle((recording_list, data), self.args.output_filename)
                self.logger.info("Wrote data to file " + self.args.output_filename + ".")
            elif os.path.splitext(self.args.output_filename)[1] == '.json':
                self.logger.error('Unsupported filetype: ' + self.args.output_filename + '.')
            else:
                self.logger.error('Unsupported filetype: ' + self.args.output_filename + '.')

        self.logger.info('Data run ended at ' + str(datetime.datetime.now()))

        self.recordings = recording_list
        self.data = data

        
    def parse_args(self):
        """
        Create a parser for commandline arguments with argparse and 
        parse the arguments.

        """
        super()._init_parser()

        helptext = (
            'Name of the spline file.'
            'Should be a .csv (you may need to change the file ending) file exported from AAA.'
        )
        self.parser.add_argument("spline_file",
                            help=helptext, metavar="file")

        super()._add_optional_arguments()
        
        self.args = self.parser.parse_args()
