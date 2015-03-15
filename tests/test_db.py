# -*- coding: utf-8 -*-
import configparser

import pytest
import rethinkdb as r

import db

TEST_DB = 'test'


@pytest.fixture(scope='function')
def yolodb():
    config = configparser.ConfigParser()
    config.read('config.ini')

    return db.YoloDB(config['bot']['db_host'], TEST_DB)


def teardown_function(function):
    """Runs after every test"""
    db_handle = db.YoloDB('localhost', TEST_DB)
    with db_handle.connection() as conn:
        try:
            r.table_drop('sites').run(conn)
        except r.errors.RqlRuntimeError:
            pass


def teardown_module():
    """Runs once after all tests have been run. Drops the test database."""
    db_handle = db.YoloDB('localhost', TEST_DB)
    with db_handle.connection() as conn:
        r.db_drop(TEST_DB).run(conn)


def test_site_should_get_persisted_to_database(yolodb):
    site_fixture = 'foo'
    yolodb.add_site(site_fixture)

    result = yolodb.get_site(site_fixture)
    assert result['name'] == site_fixture


def test_should_raise_exception_when_trying_to_add_existing_site(yolodb):
    site_fixture = 'foo'
    yolodb.add_site(site_fixture)

    with pytest.raises(db.YoloDB.AlreadyExistsError):
        yolodb.add_site(site_fixture)
