# -*- coding: utf-8 -*-
import rethinkdb as r


class YoloDB(object):
    SITES_TABLE_NAME = 'sites'

    class AlreadyExistsError(Exception):
        """Raised when trying to add a site that already exists in the db"""
        pass

    def __init__(self, host, db_name):
        self.host = host
        self.db_name = db_name

        conn = r.connect(host, db=db_name)
        try:
            r.db_create(db_name).run(conn)
        except r.errors.RqlRuntimeError:
            # db already exists
            pass

        try:
            r.db(db_name).table_create(
                self.SITES_TABLE_NAME, primary_key='name'
            ).run(conn)
        except r.errors.RqlRuntimeError:
            # table already exists
            pass

    def connection(self):
        return r.connect(self.host, db=self.db_name)

    def add_site(self, site_name):
        """Adds a site to the database"""
        with self.connection() as conn:
            result = r.table(self.SITES_TABLE_NAME).insert(
                {'name': site_name}
            ).run(conn)

            if result['inserted'] != 1:
                raise self.AlreadyExistsError()

    def get_site(self, site_name):
        """Looks up a site from the database

        :param site_name: The name of the site
        :rtype : object
        """
        with self.connection() as conn:
            return r.table(self.SITES_TABLE_NAME).get(site_name).run(conn)

    def list_sites(self):
        """Returns all the sites in the database"""
        with self.connection() as conn:
            return r.table(self.SITES_TABLE_NAME).pluck('name').order_by(
                'name'
            ).run(conn)
