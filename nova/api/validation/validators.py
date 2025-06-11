# Copyright 2013 NEC Corporation.  All rights reserved.
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
"""
Internal implementation of request Body validating middleware.

"""

import re

import jsonschema
from jsonschema import exceptions as jsonschema_exc
import netaddr
from oslo_serialization import base64
from oslo_utils import timeutils
from oslo_utils import uuidutils
import rfc3986

from nova.api.validation import parameter_types
from nova import exception
from nova.i18n import _


_FORMAT_CHECKER = jsonschema.FormatChecker()


@_FORMAT_CHECKER.checks('regex')
def _validate_regex_format(instance):
    # format checks constrain to the relevant primitive type
    # https://github.com/OAI/OpenAPI-Specification/issues/3148
    if not isinstance(instance, str):
        return True

    # the empty string is a valid regex but doesn't give us anything to match
    # on
    if not instance:
        return False

    try:
        re.compile(instance)
    except re.error:
        return False
    return True


@_FORMAT_CHECKER.checks('date-time')
def _validate_datetime_format(instance):
    # format checks constrain to the relevant primitive type
    # https://github.com/OAI/OpenAPI-Specification/issues/3148
    if not isinstance(instance, str):
        return True

    try:
        timeutils.parse_isotime(instance)
    except ValueError:
        return False
    else:
        return True


@_FORMAT_CHECKER.checks('base64')
def _validate_base64_format(instance):
    # format checks constrain to the relevant primitive type
    # https://github.com/OAI/OpenAPI-Specification/issues/3148
    if not isinstance(instance, str):
        return True

    try:
        if isinstance(instance, str):
            instance = instance.encode('utf-8')
        base64.decode_as_bytes(instance)
    except TypeError:
        # The name must be string type. If instance isn't string type, the
        # TypeError will be raised at here.
        return False

    return True


@_FORMAT_CHECKER.checks('cidr')
def _validate_cidr_format(instance):
    # format checks constrain to the relevant primitive type
    # https://github.com/OAI/OpenAPI-Specification/issues/3148
    if not isinstance(instance, str):
        return True

    try:
        netaddr.IPNetwork(instance)
    except netaddr.AddrFormatError:
        return False

    if '/' not in instance:
        return False

    if re.search(r'\s', instance):
        return False

    return True


@_FORMAT_CHECKER.checks('uuid')
def _validate_uuid_format(instance):
    # format checks constrain to the relevant primitive type
    # https://github.com/OAI/OpenAPI-Specification/issues/3148
    if not isinstance(instance, str):
        return True

    return uuidutils.is_uuid_like(instance)


@_FORMAT_CHECKER.checks('uri')
def _validate_uri(instance):
    # format checks constrain to the relevant primitive type
    # https://github.com/OAI/OpenAPI-Specification/issues/3148
    if not isinstance(instance, str):
        return True

    uri = rfc3986.uri_reference(instance)
    validator = rfc3986.validators.Validator().require_presence_of(
        'scheme', 'host',
    ).check_validity_of(
        'scheme', 'userinfo', 'host', 'path', 'query', 'fragment',
    )
    try:
        validator.validate(uri)
    except rfc3986.exceptions.RFC3986Exception:
        return False

    return True


@_FORMAT_CHECKER.checks('name_with_leading_trailing_spaces',
                        exception.InvalidName)
def _validate_name_with_leading_trailing_spaces(instance):
    regex = parameter_types.valid_name_leading_trailing_spaces_regex
    try:
        if re.search(regex.regex, instance):
            return True
    except TypeError:
        # The name must be string type. If instance isn't string type, the
        # TypeError will be raised at here.
        pass
    raise exception.InvalidName(reason=regex.reason)


@_FORMAT_CHECKER.checks('name', exception.InvalidName)
def _validate_name(instance):
    regex = parameter_types.valid_name_regex
    try:
        if re.search(regex.regex, instance):
            return True
    except TypeError:
        # The name must be string type. If instance isn't string type, the
        # TypeError will be raised at here.
        pass
    raise exception.InvalidName(reason=regex.reason)


@_FORMAT_CHECKER.checks('az_name_with_leading_trailing_spaces',
                        exception.InvalidName)
def _validate_az_name_with_leading_trailing_spaces(instance):
    regex = parameter_types.valid_az_name_leading_trailing_spaces_regex
    try:
        if re.search(regex.regex, instance):
            return True
    except TypeError:
        # The name must be string type. If instance isn't string type, the
        # TypeError will be raised at here.
        pass
    raise exception.InvalidName(reason=regex.reason)


@_FORMAT_CHECKER.checks('az_name', exception.InvalidName)
def _validate_az_name(instance):
    regex = parameter_types.valid_az_name_regex
    try:
        if re.search(regex.regex, instance):
            return True
    except TypeError:
        # The name must be string type. If instance isn't string type, the
        # TypeError will be raised at here.
        pass
    raise exception.InvalidName(reason=regex.reason)


# NOTE(stephenfin): Be careful with this method: it doesn't work with oneOf. If
# you have multiple schemas, this method will delete properties that are not
# allowed against earlier subschemas even if they're allowed (or even required)
# by later subschemas.
def _soft_validate_additional_properties(validator,
                                         additional_properties_value,
                                         instance,
                                         schema):
    """This validator function is used for legacy v2 compatible mode in v2.1.
    This will skip all the additional properties checking but keep check the
    'patternProperties'. 'patternProperties' is used for metadata API.

    If there are not any properties on the instance that are not specified in
    the schema, this will return without any effect. If there are any such
    extra properties, they will be handled as follows:

    - if the validator passed to the method is not of type "object", this
      method will return without any effect.
    - if the 'additional_properties_value' parameter is True, this method will
      return without any effect.
    - if the schema has an additionalProperties value of True, the extra
      properties on the instance will not be touched.
    - if the schema has an additionalProperties value of False and there
      aren't patternProperties specified, the extra properties will be stripped
      from the instance.
    - if the schema has an additionalProperties value of False and there
      are patternProperties specified, the extra properties will not be
      touched and raise validation error if pattern doesn't match.
    """
    if (not validator.is_type(instance, "object") or
            additional_properties_value):
        return

    properties = schema.get("properties", {})
    patterns = "|".join(schema.get("patternProperties", {}))
    extra_properties = set()
    for prop in instance:
        if prop not in properties:
            if patterns:
                if not re.search(patterns, prop):
                    extra_properties.add(prop)
            else:
                extra_properties.add(prop)

    if not extra_properties:
        return

    if patterns:
        error = "Additional properties are not allowed (%s %s unexpected)"
        if len(extra_properties) == 1:
            verb = "was"
        else:
            verb = "were"
        yield jsonschema_exc.ValidationError(
            error % (", ".join(repr(extra) for extra in extra_properties),
                     verb))
    else:
        for prop in extra_properties:
            del instance[prop]


class _SchemaValidator(object):
    """A validator class

    This class is changed from Draft202012Validator to validate minimum/maximum
    value of a string number(e.g. '10'). This changes can be removed when
    we tighten up the API definition and the XML conversion.
    Also FormatCheckers are added for checking data formats which would be
    passed through nova api commonly.

    """
    validator = None
    validator_org = jsonschema.Draft202012Validator

    def __init__(self, schema, relax_additional_properties=False,
                 is_body=True):
        self.is_body = is_body
        validators = {
            'minimum': self._validate_minimum,
            'maximum': self._validate_maximum,
        }
        if relax_additional_properties:
            validators[
                'additionalProperties'] = _soft_validate_additional_properties

        validator_cls = jsonschema.validators.extend(self.validator_org,
                                                     validators)
        self.validator = validator_cls(schema, format_checker=_FORMAT_CHECKER)

    def validate(self, *args, **kwargs):
        try:
            self.validator.validate(*args, **kwargs)
        except jsonschema.ValidationError as ex:
            if isinstance(ex.cause, exception.InvalidName):
                detail = ex.cause.format_message()
            elif len(ex.path) > 0:
                if self.is_body:
                    # NOTE: For whole OpenStack message consistency, this error
                    #       message has been written as the similar format of
                    #       WSME.
                    detail = _("Invalid input for field/attribute %(path)s. "
                               "Value: %(value)s. %(message)s") % {
                        'path': ex.path.pop(),
                        'value': ex.instance,
                        'message': ex.message}
                else:
                    # NOTE: Use 'ex.path.popleft()' instead of 'ex.path.pop()',
                    #       due to the structure of query parameters is a dict
                    #       with key as name and value is list. So the first
                    #       item in the 'ex.path' is the key, and second item
                    #       is the index of list in the value. We need the
                    #       key as the parameter name in the error message.
                    #       So pop the first value out of 'ex.path'.
                    detail = _("Invalid input for query parameters %(path)s. "
                               "Value: %(value)s. %(message)s") % {
                        'path': ex.path.popleft(),
                        'value': ex.instance,
                        'message': ex.message}
            else:
                detail = ex.message
            raise exception.ValidationError(detail=detail)
        except TypeError as ex:
            # NOTE: If passing non string value to patternProperties parameter,
            #       TypeError happens. Here is for catching the TypeError.
            detail = str(ex)
            raise exception.ValidationError(detail=detail)

    def _number_from_str(self, instance):
        try:
            value = int(instance)
        except (ValueError, TypeError):
            try:
                value = float(instance)
            except (ValueError, TypeError):
                return None
        return value

    def _validate_minimum(self, validator, minimum, instance, schema):
        instance = self._number_from_str(instance)
        if instance is None:
            return
        return self.validator_org.VALIDATORS['minimum'](validator, minimum,
                                                        instance, schema)

    def _validate_maximum(self, validator, maximum, instance, schema):
        instance = self._number_from_str(instance)
        if instance is None:
            return
        return self.validator_org.VALIDATORS['maximum'](validator, maximum,
                                                        instance, schema)
