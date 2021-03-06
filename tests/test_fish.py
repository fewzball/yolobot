# -*- coding: utf-8 -*-
import configparser

import pytest

import yolofish


@pytest.fixture(scope='module')
def fish():
    config = configparser.ConfigParser()
    config.read('config.ini')

    return yolofish.YoloFish(config['bot']['fish_key'])


def test_encrypting_a_long_string_should_work(fish):
    fixture = 'this is a test' * 22
    encrypted = fish.encrypt(fixture)

    final_string = ' '.join(fish.decrypt(msg[4:])for msg in encrypted)
    assert final_string == fixture
