# -*- coding: utf-8 -*-

"""convert csv file into catchpy webannotation json format"""
import copy
import csv
import json
import mimetypes
import re
from datetime import datetime
from dateutil import tz


# catchpy webannotation
CATCH_CURRENT_SCHEMA_VERSION = '1.1.0'
CATCH_DEFAULT_PLATFORM_NAME = 'edX'
CATCH_JSONLD_CONTEXT_IRI = 'http://catchpy.harvardx.harvard.edu.s3.amazonaws.com/jsonld/catch_context_jsonld.json' # no-op

# csv headers
START = 'Start Time'
END = 'End Time'
ANN = 'Annotation Text'
TAGS = 'Tags'
SOURCE = 'Video Link'

# regex to match a video timestamp in the format "hh:mm:ss"
TIME_REGEX = re.compile(
    r'^(?:(?:(\d?\d):)??(?:(\d?\d):)??)(\d?\d)$'
)

ANNJS_TEMPLATE = {
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
        "container": "video1",
        "ext": "Youtube",
        "src": "https://www.youtube.com/watch?v=fake"
    },
    'totalComments': 0,
    'updated': None,
    'uri': 123,
    'user': {
        'id': 'admin',
        'name': 'admin',
    }
}

WEBANN_TEMPLATE = {
    '@context': CATCH_JSONLD_CONTEXT_IRI,
    'id': '1',
    'type': 'Annotation',
    'schema_version': CATCH_CURRENT_SCHEMA_VERSION,
    'created': None,
    'modified': None,
    'creator': {
        'id': 'admin',
        'name': 'admin'
    },
    'permissions': {
        'can_read': [],
        'can_update': ['admin'],
        'can_delete': ['admin'],
        'can_admin': ['admin'],
    },
    'platform': {
        'platform_name': CATCH_DEFAULT_PLATFORM_NAME,
        'context_id': 'None',
        'collection_id': 'None',
        'target_source_id': '123',
    },
    'body': {
        'type': 'List',
        'items': [{
            'type': 'TextualBody',
            'purpose': 'commenting',
            'value': ''
        }],
    },
    'target': {
        'type': 'List',
        'items': [{
            'type': 'Video',
            'format': 'video/youtube',
            'source': "https://www.youtube.com/watch?v=fake",
            'selector': {
                'type': 'List',
                'items': [{
                    'type': 'FragmentSelector',
                    'conformsTo': 'http://www.w3.org/TR/media-frags/',
                    'value': 't=0,1',
                    'refinedBy': [{
                        'type': 'CssSelector',
                        'value': '#video1',
                    }],
                }]
            }
        }],
    }
}


class HxannError(Exception):
    pass


def time_in_secs(time_as_string):
    matches = TIME_REGEX.findall(time_as_string)
    if len(matches) > 0:
        seconds = sum([
            a*b for a, b in zip(
                [3600, 60, 1],
                map(lambda x: int(x) if x and x.isdigit() else 0, matches[0])
            )
        ])
        return seconds

    return None


def convert(csv_input, fmt='webann'):
    reader = csv.DictReader(csv_input, delimiter=',', quotechar='"')
    anns = []
    index = 1
    for record in reader:
        index += 1  # record 1 is the csv header
        record['id'] = index
        translated = translate_record(record, fmt=fmt)
        if translated is not None:  # skip empty records
            anns.append(translated)

    search_result = {
        'limit': '-1',
        'offset': '0',
        'rows': anns,
        'size': len(anns),
        'total': len(anns),
    }
    return json.dumps(search_result, indent=4, sort_keys=True)


def translate_record(record, fmt):
    # record is a dict that corresponds to a row from input csv file.

    # checks required keys
    if START not in record or END not in record:
        raise HxannError(
            'missing start or end times in row({})'.format(record))
    if SOURCE not in record:
        raise HxannError(
            'missing video link in row({})'.format(record))

    # check if required keys have a value
    if (not record[START].strip() and not record[END].strip() and not \
            record[SOURCE].strip()):
        return None  # record is considered empty

    # validate mimetype
    mimetype, _ = mimetypes.guess_type(record[SOURCE])
    if mimetype is None:
        raise HxannError(
            'unknown video mimetype for link({})'.format(record))
    record['mimetype'] = mimetype

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
            raise HxannError(
                'malformed start time({}) in row({})'.format(
                    record[START], record['id']))
        else:
            record[START] = start

    # if end time blank, assumes same as start
    if not record[END]:
        record[END] = record[START]
    else:
        end = time_in_secs(record[END])
        if end is None:
            raise HxannError(
                'malformed end time({}) in row({})'.format(
                    record[END], record['id']))
        if end < record[START]:
            raise HxannError(
                'end time({}) before start time({}) in row({})'.format(
                    record[END], record[START], record['id']))
        else:
            record[END] = end

    if TAGS not in record:
        record[TAGS] = []
    else:
        if record[TAGS]:
            tags = [x.strip() for x in record[TAGS].split(',')]
            record[TAGS] = tags
        else:
            record[TAGS] = []

    if ANN not in record:
        record[ANN] = ''

    datetime_now = datetime.now(tz.tzutc()).replace(microsecond=0).isoformat()
    record['created'] = datetime_now
    record['updated'] = datetime_now

    if fmt == 'annjs':
        return annjs_record(record)
    else:
        return webann_record(record)


def annjs_record(record):
    result = copy.deepcopy(ANNJS_TEMPLATE)
    result['id'] = record['id']
    result['created'] = record['created']
    result['rangeTime'] = {'start': record[START], 'end': record[END]}
    result['tags'] = record[TAGS]
    result['text'] = record[ANN]
    result['updated'] = record['updated']
    _, result['target']['ext'] = record['mimetype'].split('/')
    result['target']['src'] = record[SOURCE]
    return result


def webann_record(record):
    result = copy.deepcopy(WEBANN_TEMPLATE)
    result['id'] = record['id']
    result['created'] = record['created']
    result['body']['items'][0]['value'] = record[ANN]
    result['modified'] = record['updated']
    if record[TAGS]:
        for t in record[TAGS]:
            result['body']['items'].append({
                'type': 'TextualBody',
                'purpose': 'tagging',
                'value': t
            })
    result['target']['items'][0]['selector']['items'][0]['value'] = \
            't={},{}'.format(record[START], record[END])
    result['target']['items'][0]['format'] = record['mimetype']
    result['target']['items'][0]['source'] = record[SOURCE]
    return result




