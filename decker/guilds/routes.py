"""
Elastic License 2.0

Copyright Decker and/or licensed to Decker under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
"""

from datetime import datetime, timezone
from typing import Any

from apiflask import APIBlueprint, HTTPError
from apiflask.schemas import EmptySchema

from decker.constants import MAX_GUILDS
from decker.database import (
    CategoryChannel,
    Channel,
    EmptyBucket,
    Event,
    Guild,
    Member,
    MemberRole,
    Message,
    NotFound,
    Role,
    Settings,
    TextChannel,
    dispatch_event,
    objectify,
)
from decker.enums import (
    ChannelType,
    MessageType,
    PermissionBooler,
    Value,
    get_core_value,
)
from decker.users.routes import authorize
from decker.users.schemas import Authorization, AuthorizationObject

from ..enforgement import forger
from .schemas import (
    CreateGuild,
    CreateGuildObject,
    EditGuild,
    EditGuildObject,
    FullGuild,
)

guilds = APIBlueprint('guilds', __name__)


def check_count(user_id: int) -> None:
    guild_count = Member.objects(Member.user_id == user_id).count()

    if guild_count == MAX_GUILDS:
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


def get_messages(
    msg: int | None,
    channel_id: int,
    multiply: bool = False,
    append_empty_buckets: bool = True,
) -> Message | list[Message]:
    empty_buckets = [
        bucket.bucket
        for bucket in EmptyBucket.objects(EmptyBucket.channel_id == channel_id).all()
    ]

    if multiply:
        messages = []
        for bucket in range(forger.make_bucket(msg)):
            if bucket in empty_buckets or bucket == 0:
                continue
            msgs: list[Message] = Message.objects(
                Message.channel_id == channel_id, Message.bucket == bucket
            ).all()

            if not msgs and append_empty_buckets:
                EmptyBucket.create(channel_id=channel_id, bucket=bucket)

            for msg in msgs:
                messages.append(msg)
                if msg and len(messages == msg):
                    break
        return messages
    else:
        for bucket in range(forger.make_bucket(msg)):
            if bucket in empty_buckets or bucket == 0:
                continue
            try:
                msg: Message = Message.objects(
                    Message.channel_id == channel_id,
                    Message.bucket == bucket,
                    Message.id == msg,
                ).get()
            except NotFound:
                continue
            else:
                return msg

        raise HTTPError(404, 'Message not found')


def get_member(user_id: int, guild_id: int, only: list[str] | None = None) -> Member:
    if only:
        return (
            Member.objects(Member.user_id == user_id, Member.guild_id == guild_id)
            .only(only)
            .get()
        )
    else:
        return Member.objects(
            Member.user_id == user_id, Member.guild_id == guild_id
        ).get()


def get_member_permissions(user_id: int, guild_id: int) -> PermissionBooler:
    values: list[Value] = []
    member_roles: list[MemberRole] = (
        MemberRole.objects(
            MemberRole.user_id == user_id, MemberRole.guild_id == guild_id
        )
        .only(['role_id'])
        .all()
    )

    for mrole in member_roles:
        role: Role = (
            Role.objects(Role.id == mrole.role_id, Role.guild_id == guild_id)
            .only(['position', 'permissions'])
            .get()
        )

        values.append(Value(position=role.position, value=role.permissions))

    return PermissionBooler(get_core_value(*values))


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
        owner_id=user.id,
        preferred_locale=locale,
        default_permissions=PermissionBooler.DEFAULT,
        system_channel_id=forger.forge(),
        system_channel_flags=1,
    )
    member = create_member(user_id=user.id, guild_id=guild.id, owner=True)

    # create essential channels
    m1: CategoryChannel = CategoryChannel.create(
        id=forger.forge(),
        name='Text Channels',
        guild_id=guild.id,
        position=1,
        type=ChannelType.CATEGORY,
    )
    m2: TextChannel = TextChannel.create(
        id=forger.forge(),
        name='general',
        guild_id=guild.id,
        position=1,
        parent_id=m1.id,
        type=ChannelType.TEXT,
    )

    message = create_message(
        channel_id=m1.id,
        content=f'<@{user.id}>',
        author_id=user.id,
        type=MessageType.JOIN,
    )

    dispatch_event(
        'guilds', Event('GUILD_CREATE', objectify(dict(guild)), user_id=user.id)
    )
    dispatch_event(
        'channels', Event('CHANNEL_CREATE', objectify(dict(m1)), user_id=user.id)
    )
    dispatch_event(
        'channels',
        Event('CHANNEL_CREATE', objectify(dict(m2)), user_id=user.id),
    )
    dispatch_event(
        'members', Event('MEMBER_JOIN', objectify(dict(member)), user_id=user.id)
    )
    dispatch_event(
        'messages', Event('MESSAGE_CREATE', objectify(dict(message)), user_id=user.id)
    )

    return objectify(dict(guild))


@guilds.patch('/guilds/<int:guild_id>')
@guilds.input(EditGuild)
@guilds.input(Authorization, 'headers')
@guilds.output(FullGuild)
def edit_guild(guild_id: int, json: EditGuildObject, headers: AuthorizationObject):
    user = authorize(headers['authorization'], 'id')

    try:
        member = get_member(user_id=user.id, guild_id=guild_id, only=['owner'])
    except NotFound:
        raise HTTPError(403, 'You are not a member of this Guild')

    if not member.owner:
        permissions = get_member_permissions(user_id=user.id, guild_id=guild_id)

        if not permissions.manage_guild:
            raise HTTPError(
                403, 'MANAGE_GUILD permissions are required for this action.'
            )

    changes: dict[str, Any] = {}

    if json.get('name'):
        changes['name'] = json.pop('name')

    if json.get('default_permissions'):
        changes['default_permissions'] = json.pop('default_permissions')

    if json.get('default_notification_level'):
        changes['default_message_notification_level'] = json.pop(
            'default_notification_level'
        )

    if json.get('default_permissions'):
        changes['default_permissions'] = json.pop('default_permissions')

    guild: Guild = Guild.objects(Guild.id == guild_id).get()
    guild = guild.update(**changes)
    guild_data = dict(guild)

    dispatch_event('guilds', Event(name='GUILD_UPDATE', data=guild_data, guild_id=guild.id))

    return guild_data


@guilds.delete('/guilds/<int:guild_id>')
@guilds.input(Authorization, 'headers')
@guilds.output(EmptySchema, 204)
def delete_guild(guild_id: int, headers: AuthorizationObject):
    user = authorize(headers['authorization'], fields='id')

    try:
        guild: Guild = Guild.objects(Guild.id == guild_id).get()
    except NotFound:
        raise HTTPError(404, 'Guild not found')

    if guild.owner_id != user.id:
        raise HTTPError(403, 'You are not owner of this Guild')

    # TODO: Make it so Guilds above a certain member count cannot be deleteed
    text_channels: list[TextChannel] = TextChannel.objects(
        TextChannel.guild_id == guild.id
    ).all()
    category_channels: list[CategoryChannel] = CategoryChannel.objects(
        CategoryChannel.guild_id == guild.id
    ).all()

    for text_channel in text_channels:
        messages = get_messages(
            None,
            channel_id=text_channel.channel_id,
            multiply=True,
            append_empty_buckets=False,
        )

        for message in messages:
            message.delete()

        empty_buckets: list[EmptyBucket] = EmptyBucket.objects(
            EmptyBucket.channel_id == text_channel.channel_id
        ).all()

        for bucket in empty_buckets:
            bucket.delete()

        text_channel.delete()

    for category_channel in category_channels:
        messages = get_messages(
            None,
            channel_id=category_channel.channel_id,
            multiply=True,
            append_empty_buckets=False,
        )

        for message in messages:
            message.delete()

        empty_buckets: list[EmptyBucket] = EmptyBucket.objects(
            EmptyBucket.channel_id == category_channel.channel_id
        ).all()

        for bucket in empty_buckets:
            bucket.delete()

        category_channel.delete()

    members: list[Member] = Member.objects(Member.guild_id == guild.id).all()

    for member in members:
        member.delete()

    dispatch_event(
        'guilds', Event('GUILD_DELETE', {'id': str(guild.id)}, guild_id=guild.id)
    )
