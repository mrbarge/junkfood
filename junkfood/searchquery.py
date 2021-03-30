import datetime
import shlex
import collections

EPISODE_PREFIX = 'episode:'
SINCE_PREFIX = 'since:'
UNTIL_PREFIX = 'until:'
SPEAKER_PREFIX = 'speaker:'

EPISODE_KEY = 'episode'
SINCE_KEY = 'since'
UNTIL_KEY = 'until'
SPEAKER_KEY = 'speaker'
PHRASE_KEY = 'phrase'


def parse_episode(e):
    try:
        return int(e) > 0
    except ValueError:
        return False


def parse_date(d):
    format = "%Y-%m-%d"
    try:
        datetime.datetime.strptime(d, format)
        return True
    except ValueError:
        return False


def parse_query(query):
    query_components = collections.defaultdict(list)

    elements = shlex.split(query)
    for elem in elements:
        if elem.startswith(EPISODE_PREFIX):
            subelem = elem[len(EPISODE_PREFIX):]
            if parse_episode(subelem):
                query_components[EPISODE_KEY].append(subelem)
        elif elem.startswith(SINCE_PREFIX):
            subelem = elem[len(SINCE_PREFIX):]
            if parse_date(subelem):
                query_components[SINCE_KEY] = [subelem]
        elif elem.startswith(UNTIL_PREFIX):
            subelem = elem[len(UNTIL_PREFIX):]
            if parse_date(subelem):
                query_components[UNTIL_KEY] = [subelem]
        elif elem.startswith(SPEAKER_PREFIX):
            subelem = elem[len(SPEAKER_PREFIX):]
            query_components[SPEAKER_KEY] = [subelem]
        else:
            query_components[PHRASE_KEY].append(elem)
    return query_components
