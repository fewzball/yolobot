# -*- coding: utf-8 -*-
"""
You can customize the bots output and desired sitebot fields here.
"""

FIELDS = {
    'Name': {
        'type': str,
        'column_name': 'name'
    },
    'Country': {
        'type': str,
        'column_name': 'country'
    },
    'Affils': {
        'type': list,
        'column_name': 'affils'
    },
    'Speed': {
        'type': int,
        'column_name': 'speed'
    },
    'Size': {
        'type': float,
        'column_name': 'size'
    },
    'Users': {
        'type': list,
        'column_name': 'users'
    },
    'Allows': {
        'type': list,
        'column_name': 'allows'
    },
    'Filters': {
        'type': list,
        'column_name': 'filters'
    },
    'Banned': {
        'type': list,
        'column_name': 'banned'
    },
    'Imdb': {
        'type': list,
        'column_name': 'imdb'
    },
    'Comment': {
        'type': str,
        'column_name': 'comment'
    }
}

# Maps column map name to its type
COLUMN_MAPPING = {each['column_name']: each['type'] for each in FIELDS.values()}
VALID_FIELDS = [field['column_name'] for field in FIELDS.itervalues()]

LAYOUT = (
    # Each tuple represents one row in the bots output
    # Don't forget the trailing comma, even for single element tuples
    ('Name',),
    ('Country', 'Speed', 'Size'),
    ('Affils',),
    ('Users',),
    ('Allows',),
    ('Filters',),
    ('Banned',),
    ('Imdb',),
    ('Comment',),
)

# Anything that you are going to search on you probably want to list here,
# unless you are fine with the search being case sensitive. This has the side
# effect of converting all values to uppercase before saving them to the
# database.
ALWAYS_UPPERCASE = (
    'affils',
    'allows',
    'country',
    'name',
)