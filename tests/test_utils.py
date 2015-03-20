import string

import yolo_utils


def test_should_uppercase_values_if_field_is_in_always_uppercase():
    fixture = ['test', 'foo', 'bar']
    result = yolo_utils.uppercase_if_needed('affils', fixture)
    assert result == map(string.upper, fixture)


def test_should_return_values_untouched_if_field_not_in_always_uppercase():
    fixture = ['TesT', 'FOo', 'BAR']
    result = yolo_utils.uppercase_if_needed('random_field', fixture)
    assert result == fixture
