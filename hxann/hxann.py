# -*- coding: utf-8 -*-

"""convert csv file into catchpy webannotation json format"""

import csv
from datetime import datetime
from dateutil import tz
import json
import re

# csv headers
START = 'Start Time'
END = 'End Time'
ANN = 'Annotation Text'
TAGS = 'Tags'

# regex to match a video timestamp in the format "hh:mm:ss"
time_regex = re.compile(
    r'^(?:(?:(\d?\d):)??(?:(\d?\d):)??)(\d?\d)$'
)

# all entries get the same created and updated timestamp
datetime_now= datetime.now(tz.tzutc()).replace(microsecond=0).isoformat()

annjs_template = {
    'archived': False,
    'citation': "None",
    'collectionId': 'None',
    'contextId': 'None',
    'deleted': False,
    'created': None,
    'id': 1,
    'media': "video",
    'parent': "0",
    'permissions': {
        'admin': ['admin'],
        'delete': ['admin'],
        'read': [],
        "update": ['admin'],
    },
    'quote': '',
    'ranges': [],
    'target': {
        "container": "vid1",
        "ext": "Youtube",
        "src": "https://www.youtube.com/watch?v=fake"
    },
    'totalComments': 0,
    'updated': None,
    'uri': 123
    'user': {
        'id': 'admin',
        'name': 'admin',
    }
}

def time_in_secs(time_as_string):
    matches = time_regex.findall(time_as_string)
    if len(matches) > 0:
        seconds = sum([
            a*b for a,b in zip(
                [3600, 60, 1],
                map(lambda x: int(x) if x is not None else 0, matches[0])
            )
        ])
        return seconds
    else:
        return None  # maybe raise exception for parsing error


def convert(csv_input):
    reader = csv.DictReader(csv_input, delimiter=',')
    result = []
    for row in reader:
        result.append(row)

    return json.dumps(result, indent=4, sort_keys=True)


def translate_record(record, fmt='annjs'):
    # record is a dict that corresponds to a row from input csv file.

    # checks required keys
    if START not in record or END not in record:
        return None

    # if start time blank, set to 00
    if not record[START]:
        record[START] = 0
    else:
        # if '-' in start time, consider it a range, and ignore end time
        if '-' in record[START]:
            start, end = record[START].split('-')
            record[START] = start
            record[END] = end

            start = time_in_secs(record[START])
            if start is None:
                return None
            else:
                record[START] = start

    # if end time blank, assumes same as start
    if not record[END]:
        record[END] = record[START]
    else:
        end = time_in_secs(record[END])
        if end is None or end > record[START]:
            return None
        else:
            record[END] = end


    if TAGS in record:
        pass
    else:
        record[TAGS] = ''

    if ANN not in record:
        record[ANN] = ''


def annjs_record(record):
    result = annjs_template.copy()
    result['id'] = record['id']
    result['created'] = record['created']
    result['rangeTime'] = {'start': record[START], 'end': record[END]}
    result['tags'] = record[TAGS]
    result['text'] = record['text']
    result['updated'] = record['updated']
    return result



def convert2(csv_input):
    csv_reader = csv.reader(csv_input, delimiter=',', quotechar='"')
    index = 0
    annotations = []
    csv_reader.__next__()
    complete_tags = set([])
    for row in csv_reader:
        annotation = {
            'archived': False,
            'citation': "None",
            'collectionId': 'None',
            'contextId': 'None',
            'created': datetime.now().isoformat(),
            'deleted': False,
            'id': index,
            'media': "video",
            'parent': "0",
            'permissions': {
                "update": ['admin'],
                'admin': ['admin'],
                'read': [],
                'delete': ['admin'],
            },
            'quote': '',
            'ranges': [],
            'totalComments': 0,
            'updated': datetime.now().isoformat(),
            'user': {
                'id': 'fakeid',
                'name': 'Course',
            }
        }
        index = index + 1

        # if start time blank, set to 00
        if not row[0].strip():
            row[0] = '0'

        # range in start time, split and ignore end time
        if '-' in row[0]:
            start, end = row[0].split('-')
            row[0] = start
            row[1] = end
        if not row[1].strip():
            row[1] = row[0]


        def time_in_secs(time):
            total = 0
            if ':' in time:
                sects = time.split(':')
                start_time = 1
                while len(sects) > 0:
                    curr = sects.pop()
                    total += float(curr) * start_time
                    start_time *= 60
            elif 's' in time or 'm' in time or 'h' in time:
                found = re.search('([0-9])+?( )?[s]', time)
                if found:
                    total += float(found.group(1))
                found = re.search('([0-9])+?( )?[m]', time)
                if found:
                    total += float(found.group(1)) * 60.0
                found = re.search('([0-9])+?( )?[h]', time)
                if found:
                    total += float(found.group(1)) * 60.0 * 60.0
            else:
                try:
                    total = float(time)
                except ValueError as e:
                    print('error for ({}|{}): {}'.format(index, time, e))
                    print('--- {}'.format(row))
                except Error as e:
                    raise(e)
            return total
        range_start = time_in_secs(row[0])
        range_end = time_in_secs(row[1])
        tags = row[2]
        text = row[3]
        source = row[4]
        ext = row[5]
        complete_tags.add(tags + ":yellow")
        annotation.update({'rangeTime': {'start': float(range_start), 'end': float(range_end)}})
        annotation.update({'text': text})
        annotation.update({'tags': tags.split(' ')})
        annotation.update({'uri': source})
        annotation.update({'target': {'container': "vid1", "src": source, "ext": ext}})
        annotations.append(annotation)


    json_data = {
        "limit": "-1",
        "offset": "0",
        "rows": annotations,
        "size": len(annotations),
        "total": len(annotations),
    }

    return json.dumps(json_data, indent=4, sort_keys=True)








