#
# Copyright (c) 2019-2023
# Pertti Palo, Scott Moisik, Matthew Faytak, and Motoki Saito.
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
"""
Computation helper functions.
"""

import numpy as np


def _combine_coordinates(
        coord1: np.ndarray,
        coord2: np.ndarray) -> np.ndarray:
    """
    Concatenate the given coordinates by rows.

    Parameters
    ----------
    coord1 : np.ndarray
        data for first row. Has to be same length as coord2.
    coord2 : np.ndarray
        data for second row. Has to be same length as coord1.

    Returns
    -------
    np.ndarray
        The concatenation result: an array with 
        shape = ([length of coord1 and coord2], 2).
    """
    return np.concatenate(
        (coord1.reshape(-1, 1),
         coord2.reshape(-1, 1)),
        axis=1)


def cartesian_to_polar(xy_array: np.ndarray) -> np.ndarray:
    """
    Transform an array of 2D Cartesian coordinates to polar coordinates.

    Parameters
    ----------
    xy_array : np.ndarray
        x and y values in their own rows.

    Returns
    -------
    np.ndarray
        r and phi values in their own rows.
    """
    r = np.sqrt((xy_array**2).sum(1))
    phi = np.arctan2(xy_array[:, 1], xy_array[:, 0])
    return _combine_coordinates(r, phi)


def polar_to_cartesian(r_phi_array: np.ndarray) -> np.ndarray:
    """
    Transform an array of 2D polar coordinates to Cartesian coordinates.

    Parameters
    ----------
    r_phi_array : np.ndarray
        r and phi values in their own rows.

    Returns
    -------
    np.ndarray
        x and y values in their own rows.
    """
    x = r_phi_array[:, 0] * np.cos(r_phi_array[:, 1])
    y = r_phi_array[:, 0] * np.sin(r_phi_array[:, 1])
    return _combine_coordinates(x, y)
