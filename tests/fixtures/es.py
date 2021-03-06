import time

import elasticsearch
import pytest
import timeout_decorator

from tests.utils import getElasticsearchURL


@pytest.fixture(scope="session")
def es():
    class Elasticsearch(object):
        def __init__(self, url):
            self.es = elasticsearch.Elasticsearch([url])
            self.index = "apm-*"

        def clean(self):
            self.es.indices.delete(self.index)
            self.es.indices.refresh()

        def term_q(self, filters):
            clauses = []
            for field, value in filters:
                if isinstance(value, list):
                    clause = {"terms": {field: value}}
                else:
                    clause = {"term": {field: {"value": value}}}
                clauses.append(clause)
            return {"query": {"bool": {"must": clauses}}}

        @timeout_decorator.timeout(10)
        def count(self, q):
            ct = 0
            while ct == 0:
                time.sleep(3)
                s = self.es.count(index=self.index, body=q)
                ct = s['count']
            return ct

    return Elasticsearch(getElasticsearchURL())
