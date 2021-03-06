#
# This file is part of Python Client Library for the LCCS Web Service.
# Copyright (C) 2019-2020 INPE.
#
# Python Client Library for the LCCS Web Service. is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Unit-test for Python Client Library for the LCCS Web Service operations."""

import json
import os
import re
from pathlib import Path

import pytest
from pkg_resources import resource_filename, resource_string

import lccs

url = os.environ.get('LCCS_SERVER_URL', 'http://localhost:5000')

match_url = re.compile(url)


@pytest.fixture
def requests_mock(requests_mock):
    requests_mock.get(re.compile('https://geojson.org/'), real_http=True)
    yield requests_mock


@pytest.fixture(scope='session')
def lccs_object():
    resource_package = __name__
    directory = resource_filename(resource_package, 'jsons/')
    files = dict()
    for path in Path(directory).rglob('*.json'):
        path = str(path)

        s = path.split('/')

        file_path = '/'.join(s[-2:])

        file = json.loads(resource_string(resource_package, file_path).decode('utf-8'))

        if s[-2] in files:
            files[s[-2]][s[-1]] = file
        else:
            files[s[-2]] = {s[-1]: file}

    return files


class TestLCCS:

    def test_lccs(self):
        service = lccs.LCCS(url)
        assert service.url == url
        assert repr(service) == 'lccs("{}")'.format(url)
        assert str(service) == '<LCCS [{}]>'.format(url)

    def test_classification_systems(self, lccs_object, requests_mock):
        for k in lccs_object:
            service = lccs.LCCS(url, True)

            requests_mock.get(match_url, json=lccs_object[k]['classification_systems.json'],
                              status_code=200,
                              headers={'content-type': 'application/json'})

            response = service.classification_systems

            assert list(response) == ['PRODES']

    def test_classification_system(self, lccs_object, requests_mock):
        for k in lccs_object:
            service = lccs.LCCS(url, True)

            requests_mock.get(match_url, json=lccs_object[k]['classification_system.json'],
                              status_code=200,
                              headers={'content-type': 'application/json'})

            class_system = service.classification_system(system_id='PRODES')

            assert class_system == lccs_object[k]['classification_system.json']

            assert class_system.id
            assert class_system.name
            assert class_system.description
            assert class_system.version
            assert class_system.links[0].href
            assert class_system.links[0].rel

    def teste_mappings(self, lccs_object, requests_mock):
        for k in lccs_object:
            service = lccs.LCCS(url, True)

            requests_mock.get(match_url, json=lccs_object[k]['mappings.json'],
                              status_code=200,
                              headers={'content-type': 'application/json'})

            available_mappings = service.available_mappings(system_id_source='TerraClass_AMZ')

            assert list(available_mappings) == ['PRODES']

    def teste_mapping(self, lccs_object, requests_mock):
        for k in lccs_object:
            service = lccs.LCCS(url, True)

            requests_mock.get(match_url, json=lccs_object[k]['mapping.json'],
                              status_code=200,
                              headers={'content-type': 'application/json'})

            mp = service.mappings(system_id_source='TerraClass_AMZ', system_id_target='PRODES')

            assert 'TerraClass_AMZ' == mp.source_classification_system
            assert 'PRODES' == mp.target_classification_system
            assert 'degree_of_similarity' in mp.mapping[0]
            assert 'description' in mp.mapping[0]
            assert 'links' in mp.mapping[0]
            assert 'source' in mp.mapping[0]
            assert 'source_id' in mp.mapping[0]
            assert 'target' in mp.mapping[0]
            assert 'target_id' in mp.mapping[0]


if __name__ == '__main__':
    pytest.main(['--color=auto', '--no-cov'])
