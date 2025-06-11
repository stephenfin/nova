# Copyright 2015 NEC Corporation. All rights reserved.
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

import copy

from nova.api.validation import parameter_types

create = {
    'type': ['object', 'null'],
    'properties': {
        'pool': {
            'type': ['string', 'null'],
        },
    },
}

add_floating_ip = {
    'type': 'object',
    'properties': {
        'addFloatingIp': {
            'type': 'object',
            'properties': {
                'address': parameter_types.ip_address,
                'fixed_address': parameter_types.ip_address
            },
            'required': ['address'],
            'additionalProperties': False
        }
    },
    'required': ['addFloatingIp'],
    'additionalProperties': False
}

remove_floating_ip = {
    'type': 'object',
    'properties': {
        'removeFloatingIp': {
            'type': 'object',
            'properties': {
                'address': parameter_types.ip_address
            },
            'required': ['address'],
            'additionalProperties': False
        }
    },
    'required': ['removeFloatingIp'],
    'additionalProperties': False
}

# NOTE(stephenfin): These schemas are intentionally empty since these APIs are
# deprecated proxy APIs
show_query = {}
index_query = {}

_floating_ip_response = {
    'type': 'object',
    'properties': {
        'fixed_ip': {
            'type': ['string', 'null'],
            'anyOf': [{'format': 'ipv4'}, {'format': 'ipv6'}],
        },
        'id': {'type': 'string', 'format': 'uuid'},
        'instance_id': {'type': ['string', 'null'], 'format': 'uuid'},
        'ip': {
            'type': 'string',
            'anyOf': [{'format': 'ipv4'}, {'format': 'ipv6'}],
        },
        'pool': {'type': 'string'},
    },
    'required': ['fixed_ip', 'id', 'instance_id', 'ip', 'pool'],
    'additionalProperties': False
}

show_response = {
    'type': 'object',
    'properties': {
        'floating_ip': _floating_ip_response,
    },
    'required': ['floating_ip'],
    'additionalProperties': False,
}

index_response = {
    'type': 'object',
    'properties': {
        'floating_ips': {
            'type': 'array',
            'items': _floating_ip_response,
        },
    },
    'required': ['floating_ips'],
    'additionalProperties': False,
}

create_response = copy.deepcopy(show_response)

delete_response = {'type': 'null'}

add_floating_ip_response = {
    'type': 'null',
}

remove_floating_ip_response = {
    'type': 'null',
}
