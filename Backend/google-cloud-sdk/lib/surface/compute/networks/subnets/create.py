# -*- coding: utf-8 -*- #
# Copyright 2014 Google LLC. All Rights Reserved.
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
"""Command for creating subnetworks."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import utils as compute_api
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.networks import flags as network_flags
from googlecloudsdk.command_lib.compute.networks.subnets import flags
from googlecloudsdk.command_lib.util.apis import arg_utils
import six


def _AddArgs(cls, parser, include_beta=False, include_alpha=False):
  """Add subnetwork create arguments to parser."""
  cls.SUBNETWORK_ARG = flags.SubnetworkArgument()
  cls.NETWORK_ARG = network_flags.NetworkArgumentForOtherResource(
      'The network to which the subnetwork belongs.')
  cls.SUBNETWORK_ARG.AddArgument(parser, operation_type='create')
  cls.NETWORK_ARG.AddArgument(parser)

  parser.add_argument(
      '--description', help='An optional description of this subnetwork.')

  parser.add_argument(
      '--range',
      required=True,
      help='The IP space allocated to this subnetwork in CIDR format.')

  parser.add_argument(
      '--enable-private-ip-google-access',
      action='store_true',
      default=False,
      help=('Enable/disable access to Google Cloud APIs from this subnet for '
            'instances without a public ip address.'))

  parser.add_argument(
      '--secondary-range',
      type=arg_parsers.ArgDict(min_length=1),
      action='append',
      metavar='PROPERTY=VALUE',
      help="""\
      Adds a secondary IP range to the subnetwork for use in IP aliasing.

      For example, `--secondary-range range1=192.168.64.0/24` adds
      a secondary range 192.168.64.0/24 with name range1.

      * `RANGE_NAME` - Name of the secondary range.
      * `RANGE` - `IP range in CIDR format.`
      """)

  parser.add_argument(
      '--enable-flow-logs',
      action='store_true',
      default=None,
      help=('Enable/disable VPC flow logging for this subnet. More information '
            'for VPC flow logs can be found at '
            'https://cloud.google.com/vpc/docs/using-flow-logs.'))

  if include_beta:
    messages = apis.GetMessagesModule('compute',
                                      compute_api.COMPUTE_BETA_API_VERSION)

    flags.AddLoggingAggregationInterval(parser, messages)

    parser.add_argument(
        '--logging-flow-sampling',
        type=arg_parsers.BoundedFloat(lower_bound=0.0, upper_bound=1.0),
        help="""\
        Can only be specified if VPC flow logging for this subnetwork is
        enabled. The value of the field must be in [0, 1]. Set the sampling rate
        of VPC flow logs within the subnetwork where 1.0 means all collected
        logs are reported and 0.0 means no logs are reported. Default is 0.5
        which means half of all collected logs are reported.
        """)

    flags.AddLoggingMetadata(parser, messages)

  if include_alpha:
    messages = apis.GetMessagesModule('compute',
                                      compute_api.COMPUTE_ALPHA_API_VERSION)

    parser.add_argument(
        '--purpose',
        choices={
            'PRIVATE':
                'Regular user created or automatically created subnet.',
            'INTERNAL_HTTPS_LOAD_BALANCER':
                'Reserved for Internal HTTP(S) Load Balancing.'
        },
        type=lambda x: x.replace('-', '_').upper(),
        help='The purpose of this subnetwork.')

    parser.add_argument(
        '--role',
        choices={
            'ACTIVE': 'The ACTIVE subnet that is currently used.',
            'BACKUP': 'The BACKUP subnet that could be promoted to ACTIVE.'
        },
        type=lambda x: x.replace('-', '_').upper(),
        help=('The role of subnetwork. This field is only used when'
              'purpose=INTERNAL_HTTPS_LOAD_BALANCER. The value can be set to '
              'ACTIVE or BACKUP. An ACTIVE subnetwork is one that is currently '
              'being used for Internal HTTP(S) Load Balancing. A BACKUP '
              'subnetwork is one that is ready to be promoted to ACTIVE or is '
              'currently draining.'))

    flags.AddLoggingAggregationIntervalAlpha(parser, messages)

    parser.add_argument(
        '--flow-sampling',
        type=arg_parsers.BoundedFloat(lower_bound=0.0, upper_bound=1.0),
        help="""\
        Can only be specified if VPC flow logging for this subnetwork is
        enabled. The value of the field must be in [0, 1]. Set the sampling rate
        of VPC flow logs within the subnetwork where 1.0 means all collected
        logs are reported and 0.0 means no logs are reported. Default is 0.5
        which means half of all collected logs are reported.
        """)

    flags.AddLoggingMetadataAlpha(parser, messages)

    parser.add_argument(
        '--enable-private-ipv6-access',
        action='store_true',
        default=None,
        help=('Enable/disable private IPv6 access for the subnet.'))

    GetPrivateIpv6GoogleAccessTypeFlagMapper(messages).choice_arg.AddToParser(
        parser)


def GetPrivateIpv6GoogleAccessTypeFlagMapper(messages):
  return arg_utils.ChoiceEnumMapper(
      '--private-ipv6-google-access-type',
      messages.Subnetwork.PrivateIpv6GoogleAccessValueValuesEnum,
      custom_mappings={
          'DISABLE_GOOGLE_ACCESS':
              'disable',
          'ENABLE_BIDIRECTIONAL_ACCESS_TO_GOOGLE':
              'enable-bidirectional-access',
          'ENABLE_OUTBOUND_VM_ACCESS_TO_GOOGLE':
              'enable-outbound-vm-access'
      },
      help_str='The private IPv6 google access type for the VMs in this subnet.'
  )


@base.ReleaseTracks(base.ReleaseTrack.GA)
class Create(base.CreateCommand):
  """Define a subnet for a network in custom subnet mode.

  Define a subnet for a network in custom subnet mode. Subnets must be uniquely
  named per region.
  """

  NETWORK_ARG = None
  SUBNETWORK_ARG = None

  @classmethod
  def Args(cls, parser):
    parser.display_info.AddFormat(flags.DEFAULT_LIST_FORMAT)
    _AddArgs(cls, parser)
    parser.display_info.AddCacheUpdater(network_flags.NetworksCompleter)

  def _CreateSubnetwork(self, messages, subnet_ref, network_ref, args):
    subnetwork = messages.Subnetwork(
        name=subnet_ref.Name(),
        description=args.description,
        network=network_ref.SelfLink(),
        ipCidrRange=args.range,
        privateIpGoogleAccess=args.enable_private_ip_google_access,
        enableFlowLogs=args.enable_flow_logs)

    return subnetwork

  def Run(self, args):
    """Issues a list of requests necessary for adding a subnetwork."""
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    network_ref = self.NETWORK_ARG.ResolveAsResource(args, holder.resources)
    subnet_ref = self.SUBNETWORK_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client))

    request = client.messages.ComputeSubnetworksInsertRequest(
        subnetwork=self._CreateSubnetwork(client.messages, subnet_ref,
                                          network_ref, args),
        region=subnet_ref.region,
        project=subnet_ref.project)

    secondary_ranges = []
    if args.secondary_range:
      for secondary_range in args.secondary_range:
        for range_name, ip_cidr_range in sorted(six.iteritems(secondary_range)):
          secondary_ranges.append(
              client.messages.SubnetworkSecondaryRange(
                  rangeName=range_name, ipCidrRange=ip_cidr_range))

    request.subnetwork.secondaryIpRanges = secondary_ranges
    return client.MakeRequests([(client.apitools_client.subnetworks, 'Insert',
                                 request)])


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  """Define a subnet for a network in custom subnet mode.

  Define a subnet for a network in custom subnet mode. Subnets must be uniquely
  named per region.
  """

  @classmethod
  def Args(cls, parser):
    parser.display_info.AddFormat(flags.DEFAULT_LIST_FORMAT)
    _AddArgs(cls, parser, include_beta=True)
    parser.display_info.AddCacheUpdater(network_flags.NetworksCompleter)

  def _CreateSubnetwork(self, messages, subnet_ref, network_ref, args):
    subnetwork = super(CreateBeta, self)._CreateSubnetwork(
        messages, subnet_ref, network_ref, args)

    if (args.enable_flow_logs is not None or
        args.logging_aggregation_interval is not None or
        args.logging_flow_sampling is not None or
        args.logging_metadata is not None):
      log_config = messages.SubnetworkLogConfig(enable=args.enable_flow_logs)
      if args.logging_aggregation_interval:
        log_config.aggregationInterval = flags.GetLoggingAggregationIntervalArg(
            messages).GetEnumForChoice(args.logging_aggregation_interval)
      if args.logging_flow_sampling is not None:
        log_config.flowSampling = args.logging_flow_sampling
      if args.logging_metadata:
        log_config.metadata = flags.GetLoggingMetadataArg(
            messages).GetEnumForChoice(args.logging_metadata)
      subnetwork.logConfig = log_config

    return subnetwork


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(Create):
  """Define a subnet for a network in custom subnet mode.

  Define a subnet for a network in custom subnet mode. Subnets must be uniquely
  named per region.
  """

  @classmethod
  def Args(cls, parser):
    parser.display_info.AddFormat(flags.DEFAULT_LIST_FORMAT)
    _AddArgs(cls, parser, include_alpha=True)
    parser.display_info.AddCacheUpdater(network_flags.NetworksCompleter)

  def _CreateSubnetwork(self, messages, subnet_ref, network_ref, args):
    subnetwork = super(CreateAlpha, self)._CreateSubnetwork(
        messages, subnet_ref, network_ref, args)

    if (args.enable_flow_logs is not None or
        args.aggregation_interval is not None or
        args.flow_sampling is not None or args.metadata is not None):
      log_config = messages.SubnetworkLogConfig(enable=args.enable_flow_logs)
      if args.aggregation_interval:
        log_config.aggregationInterval = (
            flags.GetLoggingAggregationIntervalArgAlpha(
                messages).GetEnumForChoice(args.aggregation_interval))
      if args.flow_sampling is not None:
        log_config.flowSampling = args.flow_sampling
      if args.metadata:
        log_config.metadata = flags.GetLoggingMetadataArgAlpha(
            messages).GetEnumForChoice(args.metadata)
      subnetwork.logConfig = log_config

    if getattr(args, 'role', None):
      subnetwork.role = messages.Subnetwork.RoleValueValuesEnum(args.role)

    if args.enable_private_ipv6_access is not None:
      subnetwork.enablePrivateV6Access = args.enable_private_ipv6_access
    if args.private_ipv6_google_access_type is not None:
      subnetwork.privateIpv6GoogleAccess = (
          flags.GetPrivateIpv6GoogleAccessTypeFlagMapper(
              messages).GetEnumForChoice(args.private_ipv6_google_access_type))

    if args.purpose:
      subnetwork.purpose = messages.Subnetwork.PurposeValueValuesEnum(
          args.purpose)
    if (subnetwork.purpose == messages.Subnetwork.PurposeValueValuesEnum.
        INTERNAL_HTTPS_LOAD_BALANCER):
      # Clear unsupported fields in the subnet resource
      subnetwork.privateIpGoogleAccess = None
      subnetwork.enableFlowLogs = None
      subnetwork.logConfig = None

    return subnetwork
