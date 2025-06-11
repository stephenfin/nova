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
from nova.api.validation import response_types


create = {
    'type': 'object',
    'properties': {
        'metadata': parameter_types.metadata
    },
    'required': ['metadata'],
    'additionalProperties': False,
}

metadata_update = copy.deepcopy(parameter_types.metadata)
metadata_update.update({
    'minProperties': 1,
    'maxProperties': 1
})

update = {
    'type': 'object',
    'properties': {
        'meta': metadata_update
    },
    'required': ['meta'],
    'additionalProperties': False,
}

update_all = {
    'type': 'object',
    'properties': {
        'metadata': parameter_types.metadata
    },
    'required': ['metadata'],
    'additionalProperties': False,
}

# TODO(stephenfin): Remove additionalProperties in a future API version
index_query = {
    'type': 'object',
    'properties': {},
    'additionalProperties': True,
}

# TODO(stephenfin): Remove additionalProperties in a future API version
show_query = {
    'type': 'object',
    'properties': {},
    'additionalProperties': True,
}

index_response = {
    'type': 'object',
    'properties': {
        'metadata': response_types.metadata,
    },
    'required': ['metadata'],
    'additionalProperties': False,
}

create_response = copy.deepcopy(index_response)

update_response = {
    'type': 'object',
    'properties': {
        'meta': response_types.meta,
    },
    'required': ['meta'],
    'additionalProperties': False,
}

update_all_response = copy.deepcopy(index_response)

show_response = copy.deepcopy(update_response)

delete_response = {'type': 'null'}
