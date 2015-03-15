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
