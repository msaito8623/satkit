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

import logging
import sys
import time

from PyQt5 import QtWidgets

# local modules
from satkit.commandLineInterface import Old_Style_3D_CLI
from satkit.qt_annotator import Pd3dQtAnnotator
from satkit.io.ThreeD_ultrasound import ThreeD_Ultrasound
from satkit import pd


def main():
    t = time.time()

    # Run the command line interface.
    #function_dict = {'pd':pd.pd, 'annd':annd.annd}
    function_dict = {'PD': (pd.addPD, [ThreeD_Ultrasound])}
    cli = Old_Style_3D_CLI("PD 3D annotator", function_dict, plot=False)

    elapsed_time = time.time() - t
    logging.info('Elapsed time ' + str(elapsed_time))

    # Get the GUI running.
    app = QtWidgets.QApplication(sys.argv)
    annotator = Pd3dQtAnnotator(cli.recordings, cli.args)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()