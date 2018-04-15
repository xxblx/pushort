# -*- coding: utf-8 -*-

import os
from hashlib import blake2b
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urljoin

from tornado.gen import coroutine
from tornado.concurrent import run_on_executor
from tornado.web import RequestHandler, HTTPError

from pymongo.errors import DuplicateKeyError


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def executor(self):
        return self.application.executor

    @property
    def short_domain(self):
        return self.application.short_domain

    @coroutine
    def get_short_url(self, long_url, expires_in=None):
        """ Get the short version for the long url

        :param long_url: [:class:`str`] original long url
        :expires_in: [:class:`int`] expires time in seconds from creation
        :return: [:class:`str`] the short version for the long url
        """

        long_url = long_url.strip('/')

        # Calc expires time in utc datetime
        if not expires_in:
            expires_time = None
        else:
            if isinstance(expires_in, str):
                expires_in = int(expires_in)
            expires_time = datetime.utcnow() + timedelta(seconds=expires_in)

        url_dct = self.get_url_dct(long_url)

        if expires_time is not None:
            short_part = self.create_short_part(long_url, url_dct,
                                                expires_time)
            return urljoin(self.short_domain, url_dct['short_part'])

        # If no expires time try to find already created url in the db
        res = yield self.find_short_url(url_dct)
        if res is not None:
            short_part = res['short_part']
        else:
            short_part = yield self.create_short_part(long_url, url_dct,
                                                      expires_time)

        return urljoin(self.short_domain, short_part)

    @coroutine
    def find_short_url(self, url_dct):
        """ Search for url_dct in the database """

        dct = url_dct.copy()
        for k in dct:
            _v = dct[k]
            dct[k] = {'$eq': _v}
        result = yield self.db.urls.find_one(dct)
        return result

    @coroutine
    def create_short_part(self, long_url, url_dct, expires_time):
        """ Create short version for original url and insert
        the short part in the database

        :param long_url: [:class:`str`] the original long url
        :param url_dct: [:class:`dict`] the dict with the params of the url
        :param expires_time: [:class:`int`]
        :return: [:class:`str`] the short part without domain
        """

        if expires_time:
            url_dct['expires_time'] = expires_time

        url_inserted = False
        add_rand = False  # additional randomization
        while not url_inserted:
            try:
                short_part = yield self.get_url_hash(
                    long_url,
                    use_key=add_rand,
                    use_salt=add_rand,
                    use_person=add_rand
                )
                url_dct['short_part'] = short_part
                url_dct['short_part_block'] = short_part[:2]
                yield self.db.urls.insert(url_dct)
                url_inserted = True
            except DuplicateKeyError:
                # TODO: exception to logfile
                add_rand = True

        return short_part

    def get_url_dct(self, long_url):
        """ Make dictionary with description of the long url

        :param long_url: [:class:`str`] original long url
        :return: [:class:`dict`] the dict with original long url params
        """

        parse_res = urlparse(long_url)
        dct = {'long_url': long_url, 'url_len': len(long_url)}

        # Domain details
        domain = parse_res.netloc
        domain_split = domain.split('.')
        dct['domain'] = domain
        dct['domain_level'] = len(domain_split)
        dct['base_domain'] = '.'.join(domain_split[-2:])

        # Query params details
        params = parse_qs(parse_res.query)
        dct['params_count'] = len(params)
        if params:
            dct['params'] = parse_res.query

        # Path details
        dct['path_level'] = len(parse_res.path.split('/'))
        if parse_res.path and parse_res.path != '/':
            dct['path'] = parse_res.path

        return dct

    @run_on_executor
    def get_url_hash(self, url, digest_size=5, use_key=None, use_salt=None,
                     use_person=None):
        """ Generate blake2b hash for the url

        :param digest_size: [:class:`int`] digest size
        :param use_key: [`bool`] does the hasher need to use
            a random key
        :param use_salt: [`bool`] does the hasher need to use
            a random salt
        :param use_person: [`bool`] doest the hasher need to use
            a random personalization
        :return: [:class:`str`] hex encoded short part for the url
        """

        kwargs = {'digest_size': digest_size}
        if use_key:
            kwargs['key'] = os.urandom(blake2b.MAX_KEY_SIZE)
        if use_salt:
            kwargs['salt'] = os.urandom(blake2b.SALT_SIZE)
        if use_person:
            kwargs['person'] = os.urandom(blake2b.PERSON_SIZE)

        hasher = blake2b(**kwargs)
        hasher.update(url.encode())
        return hasher.hexdigest()

    @coroutine
    def find_long_url(self, short_part):
        """ Search in the database for the short part """

        dct = {'short_part': {'$eq': short_part}}
        res = yield self.db.urls.find_one(dct)
        return res


class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html', short_url=None)

    @coroutine
    def post(self):
        long_url = self.get_argument('long_url')
        expires_in = self.get_argument('expires_in', default=None)
        short_url = yield self.get_short_url(long_url, expires_in)
        self.render('index.html', short_url=short_url)


class ApiHandler(BaseHandler):
    @coroutine
    def post(self):
        long_url = self.get_argument('long_url')
        expires_in = self.get_argument('expires_in', default=None)
        short_url = yield self.get_short_url(long_url, expires_in)
        self.write({'short_url': short_url})


class RedirectHandler(BaseHandler):
    @coroutine
    def get(self):
        short_part = self.request.path.strip('/')
        url_dct = yield self.find_long_url(short_part)
        if url_dct is None:
            raise HTTPError(404)
        self.redirect(url_dct['long_url'])
