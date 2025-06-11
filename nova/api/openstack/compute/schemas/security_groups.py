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

import copy

from nova.api.validation import parameter_types

create = {
    'type': 'object',
    'properties': {
        'security_group': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'minLength': 0,
                    'maxLength': 255,
                },
                'description': {
                    'type': 'string',
                    'minLength': 0,
                    'maxLength': 255,
                },
            },
            'required': ['name', 'description'],
            # NOTE(stephenfin): Per gmann's note below
            'additionalProperties': True,
        },
    },
    'required': ['security_group'],
    # NOTE(stephenfin): Per gmann's note below
    'additionalProperties': True,
}

update = create

create_rules = {
    'type': 'object',
    'properties': {
        'security_group_rule': {
            'type': 'object',
            'properties': {
                'group_id': {'type': ['string', 'null'], 'format': 'uuid'},
                'parent_group_id': {'type': 'string', 'format': 'uuid'},
                # NOTE(stephenfin): We never validated these and we're not
                # going to add that validation now.
                'to_port': {},
                'from_port': {},
                'ip_protocol': {},
                'cidr': {},
            },
            'required': ['parent_group_id'],
            # NOTE(stephenfin): Per gmann's note below
            'additionalProperties': True,
        },
    },
    'required': ['security_group_rule'],
    # NOTE(stephenfin): Per gmann's note below
    'additionalProperties': True,

}

# TODO(stephenfin): Remove additionalProperties in a future API version
show_query = {
    'type': 'object',
    'properties': {},
    'additionalProperties': True,
}

index_query = {
    'type': 'object',
    'properties': {
        'limit': parameter_types.multi_params(
             parameter_types.non_negative_integer),
        'offset': parameter_types.multi_params(
             parameter_types.non_negative_integer),
        'all_tenants': parameter_types.multi_params({'type': 'string'})
    },
    # NOTE(gmann): This is kept True to keep backward compatibility.
    # As of now Schema validation stripped out the additional parameters and
    # does not raise 400. This API is deprecated in microversion 2.36 so we
    # do not to update the additionalProperties to False.
    'additionalProperties': True
}

# TODO(stephenfin): Remove additionalProperties in a future API version
index_server_query = {
    'type': 'object',
    'properties': {},
    'additionalProperties': True,
}

# TODO(stephenfin): Remove additionalProperties in a future API version
add_security_group = {
    'type': 'object',
    'properties': {
        'addSecurityGroup': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'minLength': 1,
                },
            },
            'required': ['name'],
            'additionalProperties': False
        }
    },
    'required': ['addSecurityGroup'],
    'additionalProperties': True,
}

# TODO(stephenfin): Remove additionalProperties in a future API version
remove_security_group = {
    'type': 'object',
    'properties': {
        'removeSecurityGroup': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'minLength': 1,
                },
            },
            'required': ['name'],
            'additionalProperties': False
        }
    },
    'required': ['removeSecurityGroup'],
    'additionalProperties': True,
}

_security_group_rule_response = {
    'type': 'object',
    'properties': {
        'from_port': {'type': ['integer', 'null'], 'minimum': -1},
        'group': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'tenant_id': parameter_types.project_id,
            },
            'required': [],
            'additionalProperties': False,
        },
        'id': {'type': 'string', 'format': 'uuid'},
        'ip_protocol': {'type': ['string', 'null']},
        'ip_range': {
            'type': 'object',
            'properties': {
                'cidr': {'type': 'string', 'format': 'cidr'},
            },
            'required': [],
            'additionalProperties': False,
        },
        'parent_group_id': {'type': 'string', 'format': 'uuid'},
        'to_port': {'type': ['integer', 'null'], 'minimum': -1},
    },
    'required': [
        'from_port',
        'group',
        'id',
        'ip_protocol',
        'ip_range',
        'parent_group_id',
        'to_port',
    ],
    'additionalProperties': False,
}

_security_group_response = {
    'type': 'object',
    'properties': {
        'description': {'type': ['string', 'null']},
        'id': {'type': 'string', 'format': 'uuid'},
        'name': {'type': 'string'},
        'rules': {'type': 'array', 'items': _security_group_rule_response},
        'tenant_id': parameter_types.project_id,
    },
    'required': [],
    'additionalProperties': False,

}

show_response = {
    'type': 'object',
    'properties': {
        'security_group': _security_group_response,
    },
    'required': ['security_group'],
    'additionalProperties': False,
}

delete_response = {'type': 'null'}

index_response = {
    'type': 'object',
    'properties': {
        'security_groups': {
            'type': 'array',
            'items': _security_group_response,
        },
    },
    'required': ['security_groups'],
    'additionalProperties': False,
}

create_response = copy.deepcopy(show_response)

update_response = copy.deepcopy(show_response)

create_rule_response = {
    'type': 'object',
    'properties': {
        'security_group_rule': _security_group_rule_response,
    },
    'required': ['security_group_rule'],
    'additionalProperties': False,
}

delete_rule_response = {'type': 'null'}

index_server_response = {
    'type': 'object',
    'properties': {
        'security_groups': {
            'type': 'array',
            'items': _security_group_response,
        },
    },
    'required': ['security_groups'],
    'additionalProperties': False,
}

add_security_group_response = {
    'type': 'null',
}

remove_security_group_response = {
    'type': 'null',
}
