"""
Elastic License 2.0

Copyright Decker and/or licensed to Decker under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
"""
from typing import Literal, TypedDict

from apiflask import Schema
from apiflask.fields import Boolean, DateTime, Integer, Nested, String
from apiflask.validators import Length, OneOf
from typing_extensions import NotRequired

from decker.users.schemas import PublicUserObject


class CreateGuild(Schema):
    name = String(
        required=True,
        validate=[Length(2, 100)],
    )
    icon = String()
    default_message_notifications = Integer(validate=OneOf([0, 1]))


class EditGuild(Schema):
    name = String(validate=[Length(2, 100)])
    icon = String()
    banner = String()
    default_permissions = Integer()
    default_notification_level = Integer(validate=OneOf([0, 1]))
    mfa_level = Integer(validate=OneOf([0, 1]))


class EditGuildObject(TypedDict):
    name: NotRequired[str]
    icon: NotRequired[str]
    banner: NotRequired[str]
    default_permissions: NotRequired[int]
    default_notification_level: NotRequired[Literal[0, 1]]
    mfa_level: NotRequired[Literal[0, 1]]


class CreateGuildObject(TypedDict):
    name: str
    icon: NotRequired[str]
    default_message_notifications: NotRequired[Literal[0] | Literal[1]]


class PartialGuild(Schema):
    id = String()
    name = String()
    owner_id = String()


class PreviewGuild(PartialGuild):
    icon: str = String()
    max_members = Integer()


class FullGuild(PreviewGuild):
    default_permissions = String()
    default_message_notification_level = Integer()
    mfa_level = Integer()
    vanity_url_code = String()
    description = String()
    banner = String()
    preferred_locale = String()


class GuildChannel(Schema):
    channel_id = String()
    guild_id = String()
    position = Integer()
    parent_id = String()
    nsfw = Boolean()


class TextChannel(GuildChannel):
    rate_limit_per_user = Integer()
    topic = String()
    last_message_id = String()


class Member(Schema):
    guild_id = String()
    user: Nested(PublicUserObject)
    nick = String()
    avatar = String()
    joined_at = DateTime('iso')
    deaf: bool = Boolean()
    mute: bool = Boolean()
    pending: bool = Boolean()
    communication_disabled_until: str = DateTime('iso')
    owner: bool = Boolean()
