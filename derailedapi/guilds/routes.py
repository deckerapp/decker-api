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

from datetime import datetime, timezone

from apiflask import APIBlueprint, HTTPError

from derailedapi.database import (
    CategoryChannel,
    Channel,
    Guild,
    Member,
    Settings,
    TextChannel,
    objectify,
)
from derailedapi.enums import ChannelType, PermissionBooler
from derailedapi.users.routes import authorize
from derailedapi.users.schemas import Authorization, AuthorizationObject

from ..enforgement import forger
from .schemas import CreatedGuild, CreateGuild, CreateGuildObject

guilds = APIBlueprint('guilds', __name__)


def check_count(user_id: int) -> None:
    guild_count = Member.objects(Member.user_id == user_id).count()

    if guild_count == 200:
        raise HTTPError(400, 'Maximum Guilds Reached')


def create_member(
    user_id: int, guild_id: int, pending: bool = False, owner: bool = False
) -> Member:
    return Member.create(
        user_id=user_id,
        guild_id=guild_id,
        pending=pending,
        owner=owner,
        joined_at=datetime.now(timezone.utc),
    )


def create_channel(name: str | None, type: int) -> Channel:
    return Channel.create(id=forger.forge(), name=name, type=type)


@guilds.post('/guilds')
@guilds.input(CreateGuild)
@guilds.input(Authorization, 'headers')
@guilds.output(CreatedGuild)
@guilds.doc(tag='Guilds')
def create_guild(json: CreateGuildObject, headers: AuthorizationObject):
    user = authorize(headers['authorization'], ['id', 'bot'])

    if not user.bot:
        check_count(user.id)
    else:
        raise HTTPError(403, 'This bot has passed its maximum owned guilds limit')

    locale: str = (
        Settings.objects(Settings.user_id == user.id).only(['locale']).get().locale
    )

    guild: Guild = Guild.create(
        id=forger.forge(),
        name=json['name'],
        default_message_notification_level=json.get('default_message_notifications', 0),
        explicit_content_filter=json.get('explicit_content_filter', 0),
        verification_level=json.get('verification_level', 0),
        owner_id=user.id,
        preferred_locale=locale,
        default_permissions=PermissionBooler.DEFAULT,
        system_channel_id=forger.forge(),
        system_channel_flags=1,
    )
    soul = create_member(user_id=user.id, guild_id=guild.id, owner=True)

    # create essential channels
    es_tcs = create_channel('Text Channels', ChannelType.CATEGORY)

    text_channels: CategoryChannel = CategoryChannel.create(
        channel_id=es_tcs.id, guild_id=guild.id, position=1
    )

    es_general = create_channel('general', ChannelType.TEXT)

    general: TextChannel = TextChannel.create(
        channel_id=es_general.id, guild_id=guild.id, position=1, parent_id=es_tcs.id
    )

    # TODO: Send Join Message in #general

    return objectify(
        {
            'guild': dict(guild),
            'categories': [dict(text_channels)],
            'channels': [dict(general)],
            'owner': dict(soul),
        }
    )
