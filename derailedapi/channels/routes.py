"""
Copyright 2021-2022 Derailed.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from apiflask import APIBlueprint, HTTPError

from ..database import Channel, GroupDMChannel, Recipient, Relationship
from ..enforgement import forger
from ..enums import ChannelType, Relation
from ..users.routes import authorize
from ..users.schemas import Authorization, AuthorizationObject
from .schemas import Channel as ChannelObject

channels = APIBlueprint('channels', __name__)


@channels.get('/channels/<int:channel_id>')
@channels.input(Authorization, 'headers')
@channels.output(ChannelObject)
@channels.doc(tag='Channels')
def get_channel(channel_id: int, headers: AuthorizationObject):
    user = authorize(headers['authorization'])

    try:
        channel: Channel = Channel.objects(Channel.id == channel_id).get()
    except:
        raise HTTPError(404, 'Channel not found')

    channel_data = dict(channel)

    if channel.type in (ChannelType.DIRECT_MESSAGE, ChannelType.GROUP_DIRECT_MESSAGE):
        recipients: list[Recipient] = Recipient.objects(
            Recipient.channel_id == channel.id
        ).all()

        rids = [recipient.user_id for recipient in recipients]

        if user.id not in rids:
            raise HTTPError(403, 'You are not a recipient of this channel')

    if channel.type == ChannelType.DIRECT_MESSAGE:
        return channel_data

    elif channel.type == ChannelType.GROUP_DIRECT_MESSAGE:
        group_channel: GroupDMChannel = GroupDMChannel.objects(
            GroupDMChannel.channel_id == channel.id
        ).get()
        gc = dict(group_channel)
        gc.pop('channel_id')
        channel_data.update(gc)

        return channel_data

    raise HTTPError(400, 'This version does not support this type of channel')


# NOTE: Just for easier management, routes for both types of DM Channels are here.


def create_dm_channel(user_id: int, recipient_id: int):
    try:
        r: Relationship = Relationship.objects(
            Relationship.user_id == recipient_id, Relationship.target_id == user_id
        ).get()
    except:
        pass
    else:
        if r.type == Relation.BLOCKED:
            raise HTTPError(400, 'This user has you blocked')

    try:
        r: Relationship = Relationship.objects(
            Relationship.user_id == user_id, Relationship.target_id == recipient_id
        ).get()
    except:
        pass
    else:
        if r.type == Relation.BLOCKED:
            raise HTTPError(400, 'You have this user blocked')

    channel: Channel = Channel.create(
        id=forger.forge(), type=ChannelType.DIRECT_MESSAGE
    )

    Recipient.create(channel_id=channel.id, user_id=user_id)
    Recipient.create(channel_id=channel.id, user_id=recipient_id)

    return channel
