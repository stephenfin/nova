# Copyright 2011 Denali Systems, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from unittest import mock

from oslo_utils.fixture import uuidsentinel as uuids
import webob

from nova.api.openstack.compute import snapshots
from nova import exception
from nova import test
from nova.tests.unit.api.openstack import fakes
from nova.volume import cinder

FAKE_UUID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'


class SnapshotApiTestV21(test.NoDBTestCase):
    controller = snapshots.SnapshotController()
    validation_error = exception.ValidationError

    def setUp(self):
        super(SnapshotApiTestV21, self).setUp()
        fakes.stub_out_networking(self)
        self.stub_out("nova.volume.cinder.API.create_snapshot",
                      fakes.stub_snapshot_create)
        self.stub_out("nova.volume.cinder.API.create_snapshot_force",
                      fakes.stub_snapshot_create)
        self.stub_out("nova.volume.cinder.API.delete_snapshot",
                      fakes.stub_snapshot_delete)
        self.stub_out("nova.volume.cinder.API.get_snapshot",
                      fakes.stub_snapshot_get)
        self.stub_out("nova.volume.cinder.API.get_all_snapshots",
                      fakes.stub_snapshot_get_all)
        self.stub_out("nova.volume.cinder.API.get", fakes.stub_volume_get)
        self.req = fakes.HTTPRequest.blank('')

    def _test_snapshot_create(self, force):
        snapshot = {"volume_id": uuids.volume,
                    "force": force,
                    "display_name": "Snapshot Test Name",
                    "display_description": "Snapshot Test Desc"}
        body = dict(snapshot=snapshot)
        resp_dict = self.controller.create(self.req, body=body)
        self.assertIn('snapshot', resp_dict)
        self.assertEqual(snapshot['display_name'],
                         resp_dict['snapshot']['displayName'])
        self.assertEqual(snapshot['display_description'],
                         resp_dict['snapshot']['displayDescription'])
        self.assertEqual(snapshot['volume_id'],
                         resp_dict['snapshot']['volumeId'])

    def test_snapshot_create(self):
        self._test_snapshot_create(False)

    def test_snapshot_create_force(self):
        self._test_snapshot_create(True)

    def test_snapshot_create_invalid_force_param(self):
        body = {'snapshot': {'volume_id': '1',
                             'force': '**&&^^%%$$##@@'}}
        self.assertRaises(self.validation_error,
                          self.controller.create, self.req, body=body)

    def test_snapshot_delete(self):
        snapshot_id = uuids.snapshot
        delete = self.controller.delete
        result = delete(self.req, snapshot_id)

        # NOTE: on v2.1, http status code is set as wsgi_codes of API
        # method instead of status_int in a response object.
        if isinstance(self.controller, snapshots.SnapshotController):
            status_int = delete.wsgi_codes(self.req)
        else:
            status_int = result.status_int
        self.assertEqual(202, status_int)

    @mock.patch.object(cinder.API, 'delete_snapshot',
        side_effect=exception.SnapshotNotFound(snapshot_id=FAKE_UUID))
    def test_delete_snapshot_not_exists(self, mock_mr):
        self.assertRaises(webob.exc.HTTPNotFound, self.controller.delete,
                self.req, FAKE_UUID)

    def test_snapshot_delete_invalid_id(self):
        self.assertRaises(webob.exc.HTTPNotFound, self.controller.delete,
                self.req, '-1')

    def test_snapshot_show(self):
        snapshot_id = uuids.snapshot
        resp_dict = self.controller.show(self.req, snapshot_id)
        self.assertIn('snapshot', resp_dict)
        self.assertEqual(str(snapshot_id), resp_dict['snapshot']['id'])

    def test_snapshot_show_invalid_id(self):
        self.assertRaises(webob.exc.HTTPNotFound, self.controller.show,
                self.req, '-1')

    def test_snapshot_detail(self):
        resp_dict = self.controller.detail(self.req)
        self.assertIn('snapshots', resp_dict)
        resp_snapshots = resp_dict['snapshots']
        self.assertEqual(3, len(resp_snapshots))

        resp_snapshot = resp_snapshots.pop()
        self.assertEqual(uuids.snapshot_c, resp_snapshot['id'])

    def test_snapshot_detail_offset_and_limit(self):
        path = ('/v2/%s/os-snapshots/detail?offset=1&limit=1' %
                fakes.FAKE_PROJECT_ID)
        req = fakes.HTTPRequest.blank(path)
        resp_dict = self.controller.detail(req)
        self.assertIn('snapshots', resp_dict)
        resp_snapshots = resp_dict['snapshots']
        self.assertEqual(1, len(resp_snapshots))

        resp_snapshot = resp_snapshots.pop()
        self.assertEqual(uuids.snapshot_b, resp_snapshot['id'])

    def test_snapshot_index(self):
        resp_dict = self.controller.index(self.req)
        self.assertIn('snapshots', resp_dict)
        resp_snapshots = resp_dict['snapshots']
        self.assertEqual(3, len(resp_snapshots))

    def test_snapshot_index_offset_and_limit(self):
        path = ('/v2/%s/os-snapshots?offset=1&limit=1' %
                fakes.FAKE_PROJECT_ID)
        req = fakes.HTTPRequest.blank(path)
        resp_dict = self.controller.index(req)
        self.assertIn('snapshots', resp_dict)
        resp_snapshots = resp_dict['snapshots']
        self.assertEqual(1, len(resp_snapshots))

    def _test_list_with_invalid_filter(self, url):
        prefix = '/os-snapshots'
        req = fakes.HTTPRequest.blank(prefix + url)
        controller_list = self.controller.index
        if 'detail' in url:
            controller_list = self.controller.detail
        self.assertRaises(exception.ValidationError,
                          controller_list, req)

    def test_list_with_invalid_non_int_limit(self):
        self._test_list_with_invalid_filter('?limit=-9')

    def test_list_with_invalid_string_limit(self):
        self._test_list_with_invalid_filter('?limit=abc')

    def test_list_duplicate_query_with_invalid_string_limit(self):
        self._test_list_with_invalid_filter(
            '?limit=1&limit=abc')

    def test_detail_list_with_invalid_non_int_limit(self):
        self._test_list_with_invalid_filter('/detail?limit=-9')

    def test_detail_list_with_invalid_string_limit(self):
        self._test_list_with_invalid_filter('/detail?limit=abc')

    def test_detail_list_duplicate_query_with_invalid_string_limit(self):
        self._test_list_with_invalid_filter(
            '/detail?limit=1&limit=abc')

    def test_list_with_invalid_non_int_offset(self):
        self._test_list_with_invalid_filter('?offset=-9')

    def test_list_with_invalid_string_offset(self):
        self._test_list_with_invalid_filter('?offset=abc')

    def test_list_duplicate_query_with_invalid_string_offset(self):
        self._test_list_with_invalid_filter(
            '?offset=1&offset=abc')

    def test_detail_list_with_invalid_non_int_offset(self):
        self._test_list_with_invalid_filter('/detail?offset=-9')

    def test_detail_list_with_invalid_string_offset(self):
        self._test_list_with_invalid_filter('/detail?offset=abc')

    def test_detail_list_duplicate_query_with_invalid_string_offset(self):
        self._test_list_with_invalid_filter(
            '/detail?offset=1&offset=abc')

    def _test_list_duplicate_query_parameters_validation(self, url):
        params = {
            'limit': 1,
            'offset': 1
        }
        controller_list = self.controller.index
        if 'detail' in url:
            controller_list = self.controller.detail
        for param, value in params.items():
            req = fakes.HTTPRequest.blank(
                url + '?%s=%s&%s=%s' %
                (param, value, param, value))
            controller_list(req)

    def test_list_duplicate_query_parameters_validation(self):
        self._test_list_duplicate_query_parameters_validation('/os-snapshots')

    def test_detail_list_duplicate_query_parameters_validation(self):
        self._test_list_duplicate_query_parameters_validation(
            '/os-snapshots/detail')

    def test_list_with_additional_filter(self):
        req = fakes.HTTPRequest.blank(
            '/os-snapshots?limit=1&offset=1&additional=something')
        self.controller.index(req)

    def test_detail_list_with_additional_filter(self):
        req = fakes.HTTPRequest.blank(
            '/os-snapshots/detail?limit=1&offset=1&additional=something')
        self.controller.detail(req)


class TestSnapshotAPIDeprecation(test.NoDBTestCase):

    def setUp(self):
        super(TestSnapshotAPIDeprecation, self).setUp()
        self.controller = snapshots.SnapshotController()
        self.req = fakes.HTTPRequest.blank('', version='2.36')

    def test_all_apis_return_not_found(self):
        self.assertRaises(exception.VersionNotFoundForAPIMethod,
            self.controller.show, self.req, fakes.FAKE_UUID)
        self.assertRaises(exception.VersionNotFoundForAPIMethod,
            self.controller.delete, self.req, fakes.FAKE_UUID)
        self.assertRaises(exception.VersionNotFoundForAPIMethod,
            self.controller.index, self.req)
        self.assertRaises(exception.VersionNotFoundForAPIMethod,
            self.controller.create, self.req, {})
        self.assertRaises(exception.VersionNotFoundForAPIMethod,
            self.controller.detail, self.req)


class BadRequestSnapshotTestCaseV21(test.NoDBTestCase):
    """Tests of places we throw 400 Bad Request from"""

    def setUp(self):
        super().setUp()
        self.controller = snapshots.SnapshotController()

    def _bad_request_create(self, body):
        req = fakes.HTTPRequest.blank(
            '/v2/%s/os-snapshots' % (fakes.FAKE_PROJECT_ID))
        req.method = 'POST'

        self.assertRaises(exception.ValidationError,
                          self.controller.create, req, body=body)

    def test_create_no_body(self):
        self._bad_request_create(body=None)

    def test_create_missing_volume(self):
        body = {'foo': {'a': 'b'}}
        self._bad_request_create(body=body)

    def test_create_malformed_entity(self):
        body = {'snapshot': 'string'}
        self._bad_request_create(body=body)
