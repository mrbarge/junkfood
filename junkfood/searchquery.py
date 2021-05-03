import datetime
import shlex
import collections

EPISODE_PREFIX = 'episode:'
SINCE_PREFIX = 'since:'
UNTIL_PREFIX = 'until:'
SPEAKER_PREFIX = 'speaker:'
SHOW_PREFIX = 'show:'

EPISODE_KEY = 'episode'
SINCE_KEY = 'since'
UNTIL_KEY = 'until'
SPEAKER_KEY = 'speaker'
PHRASE_KEY = 'phrase'
SHOW_KEY = 'show'


def parse_episode(e):
    try:
        return int(e) > 0
    except ValueError:
        return False


def parse_show(e):
    try:
        return str.lower(e) in ['film junk', 'ball junk', 'cantankerous', 'game junk']
    except ValueError:
        return False


def parse_date(d):
    for fmt in ('%Y-%m-%d', '%Y-%m', '%Y'):
        try:
            return datetime.datetime.strptime(d, fmt)
        except ValueError:
            pass
    raise ValueError('date format invalid')


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
            try:
                parsed_date = parse_date(subelem)
                query_components[SINCE_KEY] = [parsed_date]
            except ValueError:
                pass
        elif elem.startswith(UNTIL_PREFIX):
            subelem = elem[len(UNTIL_PREFIX):]
            try:
                parsed_date = parse_date(subelem)
                query_components[UNTIL_KEY] = [parsed_date]
            except ValueError:
                pass
        elif elem.startswith(SPEAKER_PREFIX):
            subelem = elem[len(SPEAKER_PREFIX):]
            query_components[SPEAKER_KEY] = [subelem]
        elif elem.startswith(SHOW_PREFIX):
            subelem = elem[len(SHOW_PREFIX):]
            if parse_show(subelem):
                query_components[SHOW_KEY] = [subelem]
        else:
            query_components[PHRASE_KEY].append(elem)
    return query_components
