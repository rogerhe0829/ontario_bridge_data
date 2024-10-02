"""Assignment 2: Bridges

The data used for this assignment is a subset of the data found in:
https://data.ontario.ca/dataset/bridge-conditions

This code is provided solely for the personal and private use of
students taking the CSCA08 course at the University of Toronto
Scarborough. Copying for purposes other than this use is expressly
prohibited. All forms of distribution of this code, whether as given
or with any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Anya Tafliovich, Mario Badr, Tom Fairgrieve, Sadia
Sharmin, and Jacqueline Smith

"""

import csv
from copy import deepcopy
from math import sin, cos, asin, radians, sqrt, inf
from typing import TextIO

from constants import (
    ID_INDEX, NAME_INDEX, HIGHWAY_INDEX, LAT_INDEX,
    LON_INDEX, YEAR_INDEX, LAST_MAJOR_INDEX,
    LAST_MINOR_INDEX, NUM_SPANS_INDEX,
    SPAN_DETAILS_INDEX, LENGTH_INDEX,
    LAST_INSPECTED_INDEX, BCIS_INDEX, FROM_SEP, TO_SEP,
    HIGH_PRIORITY_BCI, MEDIUM_PRIORITY_BCI,
    LOW_PRIORITY_BCI, HIGH_PRIORITY_RADIUS,
    MEDIUM_PRIORITY_RADIUS, LOW_PRIORITY_RADIUS,
    EARTH_RADIUS)
EPSILON = 0.01


# We provide this function for you to use as a helper.
def read_data(csv_file: TextIO) -> list[list[str]]:
    """Read and return the contents of the open CSV file csv_file as a
    list of lists, where each inner list contains the values from one
    line of csv_file.

    Docstring examples not given since the function reads from a file.

    """

    lines = csv.reader(csv_file)
    return list(lines)[2:]


# We provide this function for you to use as a helper.  This function
# uses the haversine function to find the distance between two
# locations. You do not need to understand why it works. You will just
# need to call this function and work with what it returns.  Based on
# https://en.wikipedia.org/wiki/Haversine_formula
# Notice how we use the built-in function abs and the constant EPSILON
# defined above to constuct example calls for the function that
# returns a float. We do not test with ==; instead, we check that the
# return value is "close enough" to the expected result.
def calculate_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """Return the distance in kilometers between the two locations defined by
    (lat1, lon1) and (lat2, lon2), rounded to the nearest meter.

    >>> abs(calculate_distance(43.659777, -79.397383, 43.657129, -79.399439)
    ...     - 0.338) < EPSILON
    True
    >>> abs(calculate_distance(43.42, -79.24, 53.32, -113.30)
    ...     - 2713.226) < EPSILON
    True
    """

    lat1, lon1, lat2, lon2 = (radians(lat1), radians(lon1),
                              radians(lat2), radians(lon2))

    haversine = (sin((lat2 - lat1) / 2) ** 2
                 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2)

    return round(2 * EARTH_RADIUS * asin(sqrt(haversine)), 3)


# We provide this sample data to help you set up example calls.
THREE_BRIDGES_UNCLEANED = [
    ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', '43.167233',
     '-80.275567', '1965', '2014', '2009', '4',
     'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012', '72.3', '',
     '72.3', '', '69.5', '', '70', '', '70.3', '', '70.5', '', '70.7', '72.9',
     ''],
    ['1 -  43/', 'WEST STREET UNDERPASS', '403', '43.164531', '-80.251582',
     '1963', '2014', '2007', '4',
     'Total=60.4  (1)=12.2;(2)=18;(3)=18;(4)=12.2;', '61', '04/13/2012',
     '71.5', '', '71.5', '', '68.1', '', '69', '', '69.4', '', '69.4', '',
     '70.3', '73.3', ''],
    ['2 -   4/', 'STOKES RIVER BRIDGE', '6', '45.036739', '-81.33579', '1958',
     '2013', '', '1', 'Total=16  (1)=16;', '18.4', '08/28/2013', '85.1',
     '85.1', '', '67.8', '', '67.4', '', '69.2', '70', '70.5', '', '75.1', '',
     '90.1', '']
]

THREE_BRIDGES = [
    [1, 'Highway 24 Underpass at Highway 403', '403', 43.167233, -80.275567,
     '1965', '2014', '2009', 4, [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
     [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]],
    [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582,
     '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0, '04/13/2012',
     [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]],
    [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579,
     '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013',
     [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]]
]


# We provide the header and doctring for this function to help get you
# started.
def get_bridge(bridge_data: list[list], bridge_id: int) -> list:
    """Return the data for the bridge with id bridge_id from bridge data
    bridge_data. If there is no bridge with id bridge_id, return [].

    >>> result = get_bridge(THREE_BRIDGES, 1)
    >>> result == [
    ...    1, 'Highway 24 Underpass at Highway 403', '403', 43.167233,
    ...    -80.275567, '1965', '2014', '2009', 4,
    ...    [12.0, 19.0, 21.0, 12.0], 65.0, '04/13/2012',
    ...    [72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]]
    True
    >>> get_bridge(THREE_BRIDGES, 42)
    []
    """

    for sublist in bridge_data:
        if sublist[ID_INDEX] == bridge_id:
            return sublist
    return []


def get_average_bci(bridge_data: list[list], bridge_id: int) -> float:
    """Return the average bci of the bridge in the bridge_data given its
    bridge_id. If no bridge is found with the given id, return 0. If no BCIs
    for the bridge with the given id, return 0.

    >>> get_average_bci(THREE_BRIDGES, 1)
    70.88571428571429
    >>> get_average_bci(THREE_BRIDGES, 0)
    0
    """
    total = 0
    count = 0
    if get_bridge(bridge_data, bridge_id) != []:
        if get_bridge(bridge_data, bridge_id)[BCIS_INDEX] != []:
            for num in get_bridge(bridge_data, bridge_id)[BCIS_INDEX]:
                total += num
                count += 1
            return total / count
        return total
    return total


def get_total_length_on_hwy(bridge_data: list[list], highway: str) -> float:
    """Return the total length of bridges in bridge_data that are on the
    highway. If there are no bridges on the given highway, return 0.

    >>> get_total_length_on_hwy(THREE_BRIDGES, '403')
    126.0
    >>> get_total_length_on_hwy(THREE_BRIDGES, '401')
    0.0
    """

    length = 0.0
    for sublist in bridge_data:
        if sublist[HIGHWAY_INDEX] == highway:
            length += sublist[LENGTH_INDEX]
    return length


def get_distance_between(bridge1: list, bridge2: list) -> float:
    """Return the difference between the length of bridge1 and length of
    bridge2. Answer will be rounded to 3 decimal places.

    >>> get_distance_between(get_bridge(THREE_BRIDGES, 1), \
                             get_bridge(THREE_BRIDGES, 2))
    1.968
    """

    return round(calculate_distance(bridge1[LAT_INDEX], bridge1[LON_INDEX],
                                    bridge2[LAT_INDEX], bridge2[LON_INDEX]), 3)
    # Pythagorean theorem is incorrect. Thecorrect method/equation in the helper
    # function is not required to understand.


def get_closest_bridge(bridge_data: list[list], bridge_id: int) -> int:
    """Return the id of the bridge in the bridge_data that is the closest to the
    bridge given its id bridge_id. The return id of the bridge cannot be the
    same as bridge_id.

    Precondition: the bridge of bridge_id is in the bridge_data. There are at
    least 2 bridges in brige_data.

    >>> get_closest_bridge(THREE_BRIDGES, 2)
    1
    """
    diff = 40075
    the_id = 0
    for sublist in bridge_data:
        if (get_distance_between(sublist, get_bridge(bridge_data, bridge_id))
            < diff
            and get_distance_between(sublist,
                                     get_bridge(bridge_data, bridge_id)) != 0):
            diff = get_distance_between(sublist,
                                        get_bridge(bridge_data, bridge_id))
            the_id = sublist[ID_INDEX]
    return the_id


def get_bridges_in_radius(bridge_data: list[list], lat: float, lon: float,
                          radius: float) -> list[int]:
    """Return a list of id of briges which the distance between it and the given
    latitude lat and longitude lon is under the given range radius.

    >>> get_bridges_in_radius(THREE_BRIDGES, 43.10, -80.15, 50)
    [1, 2]

    """
    id_list = []
    for sublist in bridge_data:
        if calculate_distance(sublist[LAT_INDEX],
                              sublist[LON_INDEX],
                              lat,
                              lon
                              ) <= radius:
            id_list.append(sublist[ID_INDEX])
    return id_list


def get_bridges_with_bci_below(bridge_data: list[list], bridge_ids: list[int],
                               limit: float) -> list[int]:
    """Return a new list of ids of bridges from bridge_data with their ids
    listed in bridge_ids which the most recent bci is lower than the given
    index limit.

    >>> get_bridges_with_bci_below(THREE_BRIDGES, [1, 2], 72)
    [2]
    """
    new_list = []
    for sublist in bridge_data:
        if sublist[ID_INDEX] in bridge_ids and sublist[BCIS_INDEX][0] <= limit:
            new_list.append(sublist[ID_INDEX])
    return new_list


def get_bridges_containing(bridge_data: list[list], search: str) -> list[int]:
    """

    >>> get_bridges_containing(THREE_BRIDGES, 'underpass')
    [1, 2]
    >>> get_bridges_containing(THREE_BRIDGES, 'pass')
    [1, 2]
    """
    new_list = []
    for sublist in bridge_data:
        if search.lower() in sublist[NAME_INDEX].lower():
            new_list.append(sublist[ID_INDEX])
    return new_list


# We provide the header and doctring for this function to help get you
# started. Note the use of the built-in function deepcopy (see
# help(deepcopy)!): since this function modifies its input, we do not
# want to call it with THREE_BRIDGES, which would interfere with the
# use of THREE_BRIDGES in examples for other functions.
def inspect_bridges(bridge_data: list[list], bridge_ids: list[int], date: str,
                    bci: float) -> None:
    """Update the bridges in bridge_data with id in bridge_ids with the new
    date and BCI score for a new inspection.

    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> inspect_bridges(bridges, [1], '09/15/2018', 71.9)
    >>> bridges == [[1, 'Highway 24 Underpass at Highway 403', '403', \
                     43.167233, -80.275567, '1965', '2014', '2009', 4, \
                     [12.0, 19.0, 21.0, 12.0], 65, '09/15/2018', \
                     [71.9, 72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]], \
                    [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582, \
                     '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61, \
                     '04/13/2012', [71.5, 68.1, 69.0, 69.4, 69.4, \
                     70.3, 73.3]], [3, 'STOKES RIVER BRIDGE', '6', 45.036739, \
                     -81.33579, '1958', '2013', '', 1, [16.0], 18.4, \
                     '08/28/2013', [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, \
                     90.1]] \
                   ]
    True

    """

    for bridge in bridge_data:
        if bridge[ID_INDEX] in bridge_ids:
            bridge[LAST_INSPECTED_INDEX] = date
            bridge[BCIS_INDEX].insert(0, bci)


def add_rehab(bridge_data: list[list],
              bridge_id: int,
              date: str,
              severity: bool) -> None:
    """Modity the bridge in bridge_data with the date of its major or minor
    rehab date. The majority or minority depends on the severity. If no bridge
    is found based on the given bridgeID, the function has no effect.

    >>> bridges = deepcopy(THREE_BRIDGES)
    >>> bridges = [[1, 'Highway 24 Underpass at Highway 403', '403', \
                    43.167233, -80.275567, '1965', '2014', '2009', 4, \
                    [12.0, 19.0, 21.0, 12.0], 65, '09/15/2023', \
                    [71.9, 72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]], \
                   [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582, \
                    '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], 61.0, \
                    '04/13/2012', [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]], \
                   [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579, \
                    '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013', \
                    [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]] \
                    ]
    >>> add_rehab(bridges, 1, '09/15/2023', False)
    >>> bridges == [[1, 'Highway 24 Underpass at Highway 403', '403', \
                     43.167233, -80.275567, '1965', '2014', '2023', 4, \
                     [12.0, 19.0, 21.0, 12.0], 65, '09/15/2023', \
                     [71.9, 72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9]], \
                    [2, 'WEST STREET UNDERPASS', '403', 43.164531, -80.251582, \
                     '1963', '2014', '2007', 4, [12.2, 18.0, 18.0, 12.2], \
                     61.0, '04/13/2012', \
                     [71.5, 68.1, 69.0, 69.4, 69.4, 70.3, 73.3]], \
                    [3, 'STOKES RIVER BRIDGE', '6', 45.036739, -81.33579, \
                     '1958', '2013', '', 1, [16.0], 18.4, '08/28/2013', \
                     [85.1, 67.8, 67.4, 69.2, 70.0, 70.5, 75.1, 90.1]] \
                    ]
    True
    """
    for bridge in bridge_data:
        if bridge[ID_INDEX] == bridge_id and severity is True:
            bridge[LAST_MAJOR_INDEX] = date[-4:]
        elif bridge[ID_INDEX] == bridge_id and severity is False:
            bridge[LAST_MINOR_INDEX] = date[-4:]

def format_index(bridge_record: list) -> None:
    """Modify the index of the bridges in the bridge_data based on their index
    in bridge_data.


    """
    for bridge in bridge_record:
        bridge[ID_INDEX] = bridge_record.index(bridge)

# We provide the header and doctring for this function to help get you started.
def format_data(data: list[list[str]]) -> None:
    """Modify the uncleaned bridge data data, so that it contains proper
    bridge data, i.e., follows the format outlined in the 'Data
    formatting' section of the assignment handout.

    >>> d = THREE_BRIDGES_UNCLEANED
    >>> format_data(d)
    >>> d == THREE_BRIDGES
    True
    """

    for bridge in data:
        format_index(bridge)
        format_location(bridge)
        format_spans(bridge)
        format_bcis(bridge)
        format_length(bridge)
        bridge[NUM_SPANS_INDEX] = int(bridge[NUM_SPANS_INDEX])


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_location(bridge_record: list) -> None:
    """Format latitude and longitude data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', \
                  '43.167233', '-80.275567', '1965', '2014', '2009', '4', \
                  'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', \
                  '04/13/2012', '72.3', '', '72.3', '', '69.5', '', '70', '', \
                  '70.3', '', '70.5', '', '70.7', '72.9', '' \
                  ]
    >>> format_location(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', \
                  43.167233, -80.275567, '1965', '2014', '2009', '4', \
                  'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', \
                  '04/13/2012', '72.3', '', '72.3', '', '69.5', '', '70', '', \
                  '70.3', '', '70.5', '', '70.7', '72.9', '' \
                  ]
    True
    """

    if bridge_record[LAT_INDEX] != '' and bridge_record[LON_INDEX] != '':
        bridge_record[LAT_INDEX] = float(bridge_record[LAT_INDEX])
        bridge_record[LON_INDEX] = float(bridge_record[LON_INDEX])


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_spans(bridge_record: list) -> None:
    """Format the bridge spans data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', \
                  '43.167233', '-80.275567', '1965', '2014', '2009', '4', \
                  'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', \
                  '04/13/2012', '72.3', '', '72.3', '', '69.5', '', '70', '', \
                  '70.3', '', '70.5', '', '70.7', '72.9', '' \
                 ]
    >>> format_spans(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', \
                   '43.167233', '-80.275567', '1965', '2014', '2009', '4', \
                   [12.0, 19.0, 21.0, 12.0], '65', '04/13/2012', \
                   '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '', \
                   '70.5', '', '70.7', '72.9', '' \
                  ]
    True
    """
    span_lengths = []
    spans = bridge_record[SPAN_DETAILS_INDEX]
    spans = spans.split(' ', 1)[1]
    for length in spans.split(';'):
        if length != '':
            span_lengths.append(float(length.split('=')[1]))
    bridge_record[SPAN_DETAILS_INDEX] = span_lengths


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_length(bridge_record: list) -> None:
    """Format the bridge length data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...           '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...           'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', '04/13/2012',
    ...           '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...           '70.5', '', '70.7', '72.9', '']
    >>> format_length(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403',
    ...            '43.167233', '-80.275567', '1965', '2014', '2009', '4',
    ...            'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', 65, '04/13/2012',
    ...            '72.3', '', '72.3', '', '69.5', '', '70', '', '70.3', '',
    ...            '70.5', '', '70.7', '72.9', '']
    True

    """

    bridge_record[LENGTH_INDEX] = float(bridge_record[LENGTH_INDEX])


# This is a suggested helper function for format_data. We provide the
# header and doctring for this function to help you structure your
# solution.
def format_bcis(bridge_record: list) -> list:
    """Format the bridge BCI data in the bridge record bridge_record.

    >>> record = ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', \
                  '43.167233', '-80.275567', '1965', '2014', '2009', '4', \
                  'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', '65', \
                  '04/13/2012', '72.3', '', '72.3', '', '69.5', '', '70', '', \
                  '70.3', '', '70.5', '', '70.7', '72.9', '' \
                 ]
    >>> format_bcis(record)
    >>> record == ['1 -  32/', 'Highway 24 Underpass at Highway 403', '403', \
                   '43.167233', '-80.275567', '1965', '2014', '2009', '4', \
                   'Total=64  (1)=12;(2)=19;(3)=21;(4)=12;', \
                   '65', '04/13/2012', \
                   [72.3, 72.3, 69.5, 70.0, 70.3, 70.5, 70.7, 72.9] \
                  ]
    True
    """

    bci_list = []
    for bci in bridge_record[BCIS_INDEX:]:
        if bci != '':
            bci_list.append(float(bci))
    bridge_record[BCIS_INDEX:] = [bci_list]


# Helper functions
def high_bridges(bridge_data: list[list], ins_lat: float,
                 ins_lon: float) -> list[int]:
    """Return a list of ids of bridges from bridge_data that is within the
    high priority bci range and is within the high_priority radius from the
    location of the inspector, given its latitude ins_lat and longitude ins_lon.




    """
    list1 = []
    list2 = sorted(get_bridges_in_radius(bridge_data, ins_lat, ins_lon,
                                         HIGH_PRIORITY_RADIUS))
    for bridge_id in list2:
        if (get_bridge(bridge_data, bridge_id)[BCIS_INDEX][0]
                <= HIGH_PRIORITY_BCI):
            list1.append(bridge_id)
    return list1


def medium_bridges(bridge_data: list[list], ins_lat: float,
                   ins_lon: float) -> list[int]:
    """Return a list of ids of bridges from bridge_data that is within the
    medium_priority radius from the location of the inspector, given its
    latitude ins_lat and longitude ins_lon.




    """

    list1 = []
    list2 = sorted(get_bridges_in_radius(bridge_data, ins_lat, ins_lon,
                                         MEDIUM_PRIORITY_RADIUS))
    for bridge_id in list2:
        if (HIGH_PRIORITY_BCI
            < get_bridge(bridge_data, bridge_id)[BCIS_INDEX][0]
                <= MEDIUM_PRIORITY_BCI):
            list1.append(bridge_id)
    return list1


def low_bridges(bridge_data: list[list], ins_lat: float,
                ins_lon: float) -> list[int]:
    """Return a list of ids of bridges from bridge_data that is within the
    medium_priority radius from the location of the inspector, given its
    latitude ins_lat and longitude ins_lon.




    """

    list1 = []
    list2 = sorted(get_bridges_in_radius(bridge_data, ins_lat, ins_lon,
                                         LOW_PRIORITY_RADIUS))
    for bridge_id in list2:
        if (MEDIUM_PRIORITY_BCI
            < get_bridge(bridge_data, bridge_id)[BCIS_INDEX][0]
                <= LOW_PRIORITY_BCI):
            list1.append(bridge_id)
    return list1


# We provide the header and doctring for this function to help get you started.
def assign_inspectors(bridge_data: list[list], inspectors: list[list[float]],
                      max_bridges: int) -> list[list[int]]:
    """Return a list of bridge IDs from bridge data bridge_data, to be
    assigned to each inspector in inspectors. inspectors is a list
    containing (latitude, longitude) pairs representing each
    inspector's location. At most max_bridges are assigned to each
    inspector, and each bridge is assigned once (to the first
    inspector that can inspect that bridge).

    See the "Assigning Inspectors" section of the handout for more details.

    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15], [42.10, -81.15]], 0)
    [[], []]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 1)
    [[1]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 2)
    [[1, 2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.10, -80.15]], 3)
    [[1, 2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [43.10, -80.15]], 1)
    [[1], [2]]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [43.10, -80.15]], 2)
    [[1, 2], []]
    >>> assign_inspectors(THREE_BRIDGES, [[43.20, -80.35], [45.0368, -81.34]],
    ...                   2)
    [[1, 2], [3]]
    >>> assign_inspectors(THREE_BRIDGES, [[38.691, -80.85], [43.20, -80.35]],
    ...                   2)
    [[], [1, 2]]

    """

    output = []
    assigned = []

    for inspector in inspectors:
        output.append([])
        for bridge_id in high_bridges(bridge_data, inspector[0], inspector[1]):
            if bridge_id not in assigned and len(output[-1]) != max_bridges:
                output[-1].append(bridge_id)
                assigned.append(bridge_id)
        for bridge_id in medium_bridges(bridge_data, inspector[0],
                                        inspector[1]):
            if bridge_id not in assigned and len(output[-1]) != max_bridges:
                output[-1].append(bridge_id)
                assigned.append(bridge_id)
        for bridge_id in low_bridges(bridge_data, inspector[0], inspector[1]):
            if bridge_id not in assigned and len(output[-1]) != max_bridges:
                output[-1].append(bridge_id)
                assigned.append(bridge_id)
    return output


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    # To test your code with larger lists, you can uncomment the code below to
    # read data from the provided CSV file.
    # with open('bridge_data.csv', encoding='utf-8') as bridge_data_file:
    #     BRIDGES = read_data(bridge_data_file)
    # format_data(BRIDGES)

    # For example:
    # print(get_bridge(BRIDGES, 3))
    # EXPECTED = [3, 'NORTH PARK STEET UNDERPASS', '403', 43.165918, -80.263791,
    #             '1962', '2013', '2009', 4, [12.2, 18.0, 18.0, 12.2], 60.8,
    #             '04/13/2012', [71.4, 69.9, 67.7, 68.9, 69.1, 69.9, 72.8]]
    # print('Testing get_bridge: ', get_bridge(BRIDGES, 3) == EXPECTED)
