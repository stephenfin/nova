# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

import re

import os_resource_classes as orc
from oslo_config import cfg
from oslo_config import types as cfg_types


class UnifiedLimitsResource(cfg_types.String):

    # NOTE(melwitt): Attempting to import nova.limit.(local|placement) for
    # LEGACY_LIMITS resource names results in error:
    #       AttributeError: module 'nova' has no attribute 'conf'
    resources = {
        'server_metadata_items', 'server_injected_files',
        'server_injected_file_content_bytes',
        'server_injected_file_path_bytes', 'server_key_pairs', 'server_groups',
        'server_group_members', 'servers'}

    def __call__(self, value):
        super().__call__(value)
        valid_resources = self.resources
        valid_resources |= {f'class:{cls}' for cls in orc.STANDARDS}
        custom_regex = r'^class:CUSTOM_[A-Z0-9_]+$'
        if value in valid_resources or re.fullmatch(custom_regex, value):
            return value
        msg = (
            f'Value {value} is not a valid resource class name. Must be '
            f'one of: {valid_resources} or a custom resource class name '
            f'of the form {custom_regex[1:-1]}')
        raise ValueError(msg)


quota_group = cfg.OptGroup(
    name='quota',
    title='Quota Options',
    help="""
Quota options allow to manage quotas in openstack deployment.
""")

quota_opts = [
    cfg.IntOpt('instances',
        min=-1,
        default=10,
        deprecated_group='DEFAULT',
        deprecated_name='quota_instances',
        help="""
The number of instances allowed per project.

Possible Values

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.IntOpt('cores',
        min=-1,
        default=20,
        deprecated_group='DEFAULT',
        deprecated_name='quota_cores',
        help="""
The number of instance cores or vCPUs allowed per project.

Possible values:

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.IntOpt('ram',
        min=-1,
        default=50 * 1024,
        deprecated_group='DEFAULT',
        deprecated_name='quota_ram',
        help="""
The number of megabytes of instance RAM allowed per project.

Possible values:

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.IntOpt('metadata_items',
        min=-1,
        default=128,
        deprecated_group='DEFAULT',
        deprecated_name='quota_metadata_items',
        help="""
The number of metadata items allowed per instance.

Users can associate metadata with an instance during instance creation. This
metadata takes the form of key-value pairs.

Possible values:

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.IntOpt('injected_files',
        min=-1,
        default=5,
        deprecated_group='DEFAULT',
        deprecated_name='quota_injected_files',
        help="""
The number of injected files allowed.

File injection allows users to customize the personality of an instance by
injecting data into it upon boot. Only text file injection is permitted: binary
or ZIP files are not accepted. During file injection, any existing files that
match specified files are renamed to include ``.bak`` extension appended with a
timestamp.

Possible values:

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.IntOpt('injected_file_content_bytes',
        min=-1,
        default=10 * 1024,
        deprecated_group='DEFAULT',
        deprecated_name='quota_injected_file_content_bytes',
        help="""
The number of bytes allowed per injected file.

Possible values:

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.IntOpt('injected_file_path_length',
        min=-1,
        default=255,
        deprecated_group='DEFAULT',
        deprecated_name='quota_injected_file_path_length',
        help="""
The maximum allowed injected file path length.

Possible values:

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.IntOpt('key_pairs',
        min=-1,
        default=100,
        deprecated_group='DEFAULT',
        deprecated_name='quota_key_pairs',
        help="""
The maximum number of key pairs allowed per user.

Users can create at least one key pair for each project and use the key pair
for multiple instances that belong to that project.

Possible values:

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.IntOpt('server_groups',
        min=-1,
        default=10,
        deprecated_group='DEFAULT',
        deprecated_name='quota_server_groups',
        help="""
The maximum number of server groups per project.

Server groups are used to control the affinity and anti-affinity scheduling
policy for a group of servers or instances. Reducing the quota will not affect
any existing group, but new servers will not be allowed into groups that have
become over quota.

Possible values:

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.IntOpt('server_group_members',
        min=-1,
        default=10,
        deprecated_group='DEFAULT',
        deprecated_name='quota_server_group_members',
        help="""
The maximum number of servers per server group.

Possible values:

* A positive integer or 0.
* -1 to disable the quota.
"""),
    cfg.StrOpt('driver',
        default='nova.quota.DbQuotaDriver',
        choices=[
            ('nova.quota.DbQuotaDriver', '(deprecated) Stores quota limit '
             'information in the database and relies on the ``quota_*`` '
             'configuration options for default quota limit values. Counts '
             'quota usage on-demand.'),
            ('nova.quota.NoopQuotaDriver', 'Ignores quota and treats all '
             'resources as unlimited.'),
            ('nova.quota.UnifiedLimitsDriver', 'Uses Keystone unified limits '
             'to store quota limit information and relies on resource '
             'usage counting from Placement. Counts quota usage on-demand. '
             'Resources missing unified limits in Keystone will be treated '
             'as a quota limit of 0, so it is important to ensure all '
             'resources have registered limits in Keystone. The ``nova-manage '
             'limits migrate_to_unified_limits`` command can be used to copy '
             'existing quota limits from the Nova database to Keystone '
             'unified limits via the Keystone API. Alternatively, unified '
             'limits can be created manually using the OpenStackClient or '
             'by calling the Keystone API directly.'),
        ],
        help="""
Provides abstraction for quota checks. Users can configure a specific
driver to use for quota checks.
"""),
    cfg.BoolOpt('recheck_quota',
        default=True,
        help="""
Recheck quota after resource creation to prevent allowing quota to be exceeded.

This defaults to True (recheck quota after resource creation) but can be set to
False to avoid additional load if allowing quota to be exceeded because of
racing requests is considered acceptable. For example, when set to False, if a
user makes highly parallel REST API requests to create servers, it will be
possible for them to create more servers than their allowed quota during the
race. If their quota is 10 servers, they might be able to create 50 during the
burst. After the burst, they will not be able to create any more servers but
they will be able to keep their 50 servers until they delete them.

The initial quota check is done before resources are created, so if multiple
parallel requests arrive at the same time, all could pass the quota check and
create resources, potentially exceeding quota. When recheck_quota is True,
quota will be checked a second time after resources have been created and if
the resource is over quota, it will be deleted and OverQuota will be raised,
usually resulting in a 403 response to the REST API user. This makes it
impossible for a user to exceed their quota with the caveat that it will,
however, be possible for a REST API user to be rejected with a 403 response in
the event of a collision close to reaching their quota limit, even if the user
has enough quota available when they made the request.
"""),
    cfg.BoolOpt(
        'count_usage_from_placement',
        default=False,
        help="""
Enable the counting of quota usage from the placement service.

Starting in Train, it is possible to count quota usage for cores and ram from
the placement service and instances from the API database instead of counting
from cell databases.

This works well if there is only one Nova deployment running per placement
deployment. However, if an operator is running more than one Nova deployment
sharing a placement deployment, they should not set this option to True because
currently the placement service has no way to partition resource providers per
Nova deployment. When this option is left as the default or set to False, Nova
will use the legacy counting method to count quota usage for instances, cores,
and ram from its cell databases.

Note that quota usage behavior related to resizes will be affected if this
option is set to True. Placement resource allocations are claimed on the
destination while holding allocations on the source during a resize, until the
resize is confirmed or reverted. During this time, when the server is in
VERIFY_RESIZE state, quota usage will reflect resource consumption on both the
source and the destination. This can be beneficial as it reserves space for a
revert of a downsize, but it also means quota usage will be inflated until a
resize is confirmed or reverted.

Behavior will also be different for unscheduled servers in ERROR state. A
server in ERROR state that has never been scheduled to a compute host will
not have placement allocations, so it will not consume quota usage for cores
and ram.

Behavior will be different for servers in SHELVED_OFFLOADED state. A server in
SHELVED_OFFLOADED state will not have placement allocations, so it will not
consume quota usage for cores and ram. Note that because of this, it will be
possible for a request to unshelve a server to be rejected if the user does not
have enough quota available to support the cores and ram needed by the server
to be unshelved.

The ``populate_queued_for_delete`` and ``populate_user_id`` online data
migrations must be completed before usage can be counted from placement. Until
the data migration is complete, the system will fall back to legacy quota usage
counting from cell databases depending on the result of an EXISTS database
query during each quota check, if this configuration option is set to True.
Operators who want to avoid the performance hit from the EXISTS queries should
wait to set this configuration option to True until after they have completed
their online data migrations via ``nova-manage db online_data_migrations``.
"""),
    cfg.StrOpt(
        'unified_limits_resource_strategy',
        default='require',
        choices=[
            ('require', 'Require the resources in '
             '``unified_limits_resource_list`` to have registered limits set '
             'in Keystone'),
            ('ignore', 'Ignore the resources in '
             '``unified_limits_resource_list`` if they do not have registered '
             'limits set in Keystone'),
        ],
        help="""
Specify the semantics of the ``unified_limits_resource_list``.

When the quota driver is set to the ``UnifiedLimitsDriver``, resources may be
specified to ether require registered limits set in Keystone or ignore if they
do not have registered limits set.

When set to ``require``, if a resource in ``unified_limits_resource_list`` is
requested and has no registered limit set, the quota limit for that resource
will be considered to be 0 and all requests to allocate that resource will be
rejected for being over quota.

When set to ``ignore``, if a resource in ``unified_limits_resource_list`` is
requested and has no registered limit set, the quota limit for that resource
will be considered to be unlimited and all requests to allocate that resource
will be accepted.

Related options:

* ``unified_limits_resource_list``: This must contain either resources for
  which to require registered limits set or resources to ignore if they do not
  have registered limits set. It can also be set to an empty list.
"""),
    cfg.ListOpt(
        'unified_limits_resource_list',
        item_type=UnifiedLimitsResource(),
        default=['servers'],
        help="""
Specify a list of resources to require or ignore registered limits.

When the quota driver is set to the ``UnifiedLimitsDriver``, require or ignore
resources in this list to have registered limits set in Keystone.

When ``unified_limits_resource_strategy`` is ``require``, if a resource in this
list is requested and has no registered limit set, the quota limit for that
resource will be considered to be 0 and all requests to allocate that resource
will be rejected for being over quota.

When ``unified_limits_resource_strategy`` is ``ignore``, if a resource in this
list is requested and has no registered limit set, the quota limit for that
resource will be considered to be unlimited and all requests to allocate that
resource will be accepted.

The list can also be set to an empty list.

Valid list item values are:

* ``servers``

* ``class:<Placement resource class name>``

* ``server_key_pairs``

* ``server_groups``

* ``server_group_members``

* ``server_metadata_items``

* ``server_injected_files``

* ``server_injected_file_content_bytes``

* ``server_injected_file_path_bytes``

Related options:

* ``unified_limits_resource_strategy``: This must be set to ``require`` or
  ``ignore``
"""),
]


def register_opts(conf):
    conf.register_group(quota_group)
    conf.register_opts(quota_opts, group=quota_group)


def list_opts():
    return {quota_group: quota_opts}
