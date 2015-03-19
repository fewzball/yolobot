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


def test_should_list_all_sites_in_the_database(yolodb):
    sites = ['foo', 'bar', 'baz']
    for site in sites:
        yolodb.add_site(site)

    # results should also be in alphabetical order
    sites.sort()
    results = yolodb.list_sites()
    assert [site['name'] for site in results] == sites


def test_should_set_value_successfully(yolodb):
    yolodb.add_site('foo')
    result = yolodb.set_value('foo', 'comment', 'this is a comment')
    assert result['replaced'] == 1


def test_should_raise_exception_if_given_invalid_field(yolodb):
    yolodb.add_site('foo')
    with pytest.raises(db.YoloDB.InvalidField):
        yolodb.set_value('foo', 'invalid', 'barf')


def test_should_raise_exception_if_passed_invalid_type_for_field(yolodb):
    yolodb.add_site('foo')
    with pytest.raises(db.YoloDB.InvalidType):
        yolodb.set_value('foo', 'speed', 'some string')


def test_should_convert_list_fields_to_lists(yolodb):
    yolodb.add_site('foo')
    yolodb.set_value('foo', 'users', ['user1', 'user2'])
    site = yolodb.get_site('foo')
    assert isinstance(site['users'], list)


def test_add_value_should_set_value_if_field_doesnt_exist_yet(yolodb):
    yolodb.add_site('foo')
    # Also tests that it can accept type set
    fixture = set(['username1', 'username2'])
    yolodb.add_value('foo', 'users', fixture)
    assert yolodb.get_site('foo')['users'] == list(fixture)


def test_adding_duplicate_value_should_be_thrown_out(yolodb):
    yolodb.add_site('foo')
    yolodb.set_value('foo', 'users', ['user1', 'user2'])
    assert yolodb.add_value('foo', 'users', ['user1', 'user3']) == \
           ['user1', 'user2', 'user3']


def test_delsite_should_remove_site_from_the_database(yolodb):
    yolodb.add_site('foo')
    response = yolodb.delete_site('foo')
    assert response['deleted'] == 1
