# -*- coding: utf-8 -*-
import string
import sitebot_config


def uppercase_if_needed(field, values):
    """
    Uppercase each value in `values` if necessary.
    :param field: The field to check
    :type field: str
    :param values: One or more values that will be changed to uppercase if
    necessary
    :type values: list or str
    :return: The values either in uppercase or untouched
    :rtype: list
    """
    if field in sitebot_config.ALWAYS_UPPERCASE:
        if isinstance(values, list):
            return map(string.upper, values)
        return values.upper()
    return values
