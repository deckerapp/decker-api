"""
Elastic License 2.0

Copyright Clack and/or licensed to Clack under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
"""

from datetime import datetime, timezone

from apiflask import APIBlueprint, HTTPError

from clack.database import (
    CategoryChannel,
    Channel,
    Event,
    Guild,
    Member,
    Message,
    Settings,
    TextChannel,
    dispatch_event,
    objectify,
)
from clack.enums import ChannelType, MessageType, PermissionBooler
from clack.users.routes import authorize
from clack.users.schemas import Authorization, AuthorizationObject

from ..enforgement import forger
from .schemas import CreateGuild, CreateGuildObject, FullGuild

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


def create_message(
    channel_id: int,
    content: str,
    author_id: int,
    tts: bool = False,
    mention_everyone: bool = False,
    type: int = MessageType.NORMAL,
    flags: int = 0,
    referenced_message_id: int | None = None,
) -> Message:
    message_id = forger.forge()

    return Message.create(
        id=message_id,
        channel_id=channel_id,
        bucket=forger.make_bucket(message_id),
        author_id=author_id,
        content=content,
        created_timestamp=datetime.now(timezone.utc),
        edited_timestamp=datetime.now(timezone.utc),
        tts=tts,
        mention_everyone=mention_everyone,
        pinned=False,
        type=type,
        flags=flags,
        referenced_message_id=referenced_message_id,
    )


@guilds.post('/guilds')
@guilds.input(CreateGuild)
@guilds.input(Authorization, 'headers')
@guilds.output(FullGuild)
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
    member = create_member(user_id=user.id, guild_id=guild.id, owner=True)

    # create essential channels
    es_tcs = create_channel('Text Channels', ChannelType.CATEGORY)

    m1 = CategoryChannel.create(channel_id=es_tcs.id, guild_id=guild.id, position=1)

    es_general = create_channel('general', ChannelType.TEXT)

    m2 = TextChannel.create(
        channel_id=es_general.id, guild_id=guild.id, position=1, parent_id=es_tcs.id
    )

    merged_category = dict(es_tcs) | m1
    merged_text_channel = dict(es_general) | m2

    message = create_message(
        channel_id=es_general.id,
        content=f'<@{user.id}>',
        author_id=user.id,
        type=MessageType.JOIN,
    )

    dispatch_event(
        'guilds', Event('GUILD_CREATE', objectify(dict(guild)), user_id=user.id)
    )
    dispatch_event(
        'channels', Event('CHANNEL_CREATE', objectify(merged_category), user_id=user.id)
    )
    dispatch_event(
        'channels',
        Event('CHANNEL_CREATE', objectify(merged_text_channel), user_id=user.id),
    )
    dispatch_event(
        'members', Event('MEMBER_JOIN', objectify(dict(member)), user_id=user.id)
    )
    dispatch_event(
        'messages', Event('MESSAGE_CREATE', objectify(dict(message)), user_id=user.id)
    )

    return objectify(dict(guild))
