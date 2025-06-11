# Copyright 2014 NEC Corporation.  All rights reserved.
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

# NOTE(stephenfin): This schema is intentionally empty since the action has
# been removed
reset_network = {}

# TODO(stephenfin): Restrict the value to 'null' in a future API version
inject_network_info = {
    'type': 'object',
    'properties': {
        'injectNetworkInfo': {},
    },
    'required': ['injectNetworkInfo'],
    'additionalProperties': False,
}

reset_state = {
    'type': 'object',
    'properties': {
        'os-resetState': {
            'type': 'object',
            'properties': {
                'state': {
                    'type': 'string',
                    'enum': ['active', 'error'],
                },
            },
            'required': ['state'],
            'additionalProperties': False,
        },
    },
    'required': ['os-resetState'],
    'additionalProperties': False,
}

# NOTE(stephenfin): This schema is intentionally empty since the action has
# been removed
reset_network_response = {}

inject_network_info_response = {
    'type': 'null',
}

reset_state_response = {
    'type': 'null',
}
