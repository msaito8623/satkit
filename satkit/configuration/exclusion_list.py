#
# Copyright (c) 2019-2022 Pertti Palo, Scott Moisik, Matthew Faytak, and Motoki Saito.
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

# Built in packages
import csv
import logging
from contextlib import closing

_io_logger = logging.getLogger('satkit.io')

def set_exclusions_from_file(filename, recordings):
    """
    Read list of files (that is, recordings) to be excluded from processing
    and mark them as excluded in the array of recording objects.
    """
    if filename is not None:
        _io_logger.debug(
            "Setting exclusions from file %s.", filename)
        with closing(open(filename, 'r', encoding='utf-8')) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            # Throw away the second field - it is a comment for human readers.
            exclusion_list = [row[0] for row in reader if row]
            _io_logger.info('Read exclusion list %s with %s names.', 
                            filename, str(len(exclusion_list)))
    else:
        _io_logger.debug(
            "No exclusion file. Using an empty list.")
        exclusion_list = []

    # mark as excluded
    [recording.exclude() for recording in recordings
     if recording.basename in exclusion_list]


def read_file_exclusion_list(filename):
    """
    Read list of files (that is, recordings) to be excluded from processing.
    """
    if filename is not None:
        with closing(open(filename, 'r', encoding = 'utf-8')) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            # Throw away the second field - it is a comment for human readers.
            exclusion_list = [row[0] for row in reader]
            _io_logger.info('Read exclusion list {filename} with {length} names.', 
                        filename = filename, length = str(len(exclusion_list)))
    else:
        exclusion_list = []

    return exclusion_list