#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient


def create_indexes():
    db = MongoClient('127.0.0.1')['pushort']
    db.urls.create_index('short_part', unique=True)
    db.urls.create_index('short_part_block')

    # Sparse indexes for quick navigations between url with/without
    # params and paths after domain
    db.urls.create_index('params', sparse=True)
    db.urls.create_index('path', sparse=True)

    # Setup TTL index for auto deletions of expired items
    db.urls.create_index('expire_time', expireAfterSeconds=0)


if __name__ == '__main__':
    create_indexes()
