# Copyright 2017 The Forseti Security Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests the findings notification notifier."""

import datetime
import mock
import os

from google.cloud.forseti.notifier import notifier
from google.cloud.forseti.notifier.notifiers import findings
from google.cloud.forseti.services.scanner import dao as scanner_dao
from tests.services.scanner import scanner_dao_test
from tests.services.util.db import create_test_engine_with_file
from tests.unittest_utils import ForsetiTestCase


class FindingsNotifierTest(ForsetiTestCase):

    def setUp(self):
        """Setup method."""
        ForsetiTestCase.setUp(self)
        self.maxDiff=None
        self.engine, self.dbfile = create_test_engine_with_file()

    def tearDown(self):
        """Tear down method."""
        os.unlink(self.dbfile)
        ForsetiTestCase.tearDown(self)

    @mock.patch('google.cloud.forseti.common.util.date_time.'
                'get_utc_now_datetime')
    def test_can_convert_to_findings(self, mock_get_utc_now):
        fake_datetime = datetime.datetime(2010, 8, 28, 10, 20, 30, 0)
        mock_get_utc_now.return_value = fake_datetime

        expected_findings = [
            {'finding_id': '539cfbdb1113a74ec18edf583eada77ab1a60542c6edcb4120b50f34629b6b69041c13f0447ab7b2526d4c944c88670b6f151fa88444c30771f47a3b813552ff',
             'finding_summary': 'disallow_all_ports_111',
             'finding_source_id': 'FORSETI', 
             'finding_category': 'FIREWALL_BLACKLIST_VIOLATION_111', 
             'finding_asset_ids': 'full_name_111',
             'finding_time_event': '2010-08-28T10:20:30Z',
             'finding_callback_url': None,
             'finding_properties':
                 {'inventory_index_id': 'aaa',
                  'resource_id': 'fake_firewall_111',
                  'resource_data': 'inventory_data_111',
                  'rule_index': 111,
                  'violation_data': '{"policy_names": ["fw-tag-match_111"], "recommended_actions": {"DELETE_FIREWALL_RULES": ["fw-tag-match_111"]}}', 'resource_type': u'firewall_rule'},
             },
           {'finding_id': '3eff279ccb96799d9eb18e6b76055b2242d1f2e6f14c1fb3bb48f7c8c03b4ce4db577d67c0b91c5914902d906bf1703d5bbba0ceaf29809ac90fef3bf6aa5417',
            'finding_summary': 'disallow_all_ports_222',
            'finding_source_id': 'FORSETI',
            'finding_category': 'FIREWALL_BLACKLIST_VIOLATION_222',
            'finding_asset_ids': 'full_name_222',
            'finding_time_event': '2010-08-28T10:20:30Z',
            'finding_callback_url': None,
            'finding_properties':
                {'inventory_index_id': 'aaa',
                 'resource_id': 'fake_firewall_222',
                 'resource_data': 'inventory_data_222',
                 'rule_index': 222,
                 'violation_data': '{"policy_names": ["fw-tag-match_222"], "recommended_actions": {"DELETE_FIREWALL_RULES": ["fw-tag-match_222"]}}', 'resource_type': u'firewall_rule'},
            }
        ]

        violation_access, _ = scanner_dao_test.populate_db(self.engine)
        violations = violation_access.list()
        violations = notifier.convert_to_timestamp(violations)

        violations_as_dict = []
        for violation in violations:
            violations_as_dict.append(
                scanner_dao.convert_sqlalchemy_object_to_dict(violation))

        finding_results = (
            findings.Findingsnotifier()._transform_to_findings(
                violations_as_dict)
        )

        self.assertEquals(expected_findings, finding_results)
