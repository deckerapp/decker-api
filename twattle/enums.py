"""
Copyright 2021-2022 twattle, Inc.

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
import functools


def flagged(value: int, visible: int) -> bool:
    return bool(value & visible)


class Relation:
    FRIEND = 0
    BLOCKED = 1
    INCOMING = 2
    OUTGOING = 3


class ActivityType:
    GAME = 0
    STREAM = 1
    LISTENING = 3
    CUSTOM = 4


class ChannelType:
    TEXT = 0
    DIRECT_MESSAGE = 1
    GROUP_DIRECT_MESSAGE = 2
    VOICE = 3
    CATEGORY = 4


class NotificationLevel:
    ALL = 0
    MENTIONS = 1


class ContentFilterLevel:
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL = 2


class VerificationLevel:
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class NSFWLevel:
    UNKNOWN = 0
    SAFE = 1
    EXPLICIT = 2
    AGE_RESTRICTED = 3


class MFALevel:
    NONE = 0
    ELEVATED = 1


class MessageType:
    NORMAL = 0
    JOIN = 1


class Permission:
    CREATE_INSTANT_INVITE = 1 << 0
    KICK_MEMBERS = 1 << 1
    BAN_MEMBERS = 1 << 2
    ADMINISTRATOR = 1 << 3
    MANAGE_CHANNELS = 1 << 4
    MANAGE_GUILD = 1 << 5
    ADD_REACTIONS = 1 << 6
    VIEW_AUDIT_LOG = 1 << 7
    PRIORITY_SPEAKER = 1 << 8
    STREAM = 1 << 9
    VIEW_CHANNEL = 1 << 10
    SEND_MESSAGES = 1 << 11
    SEND_TTS_MESSAGES = 1 << 12
    MANAGE_MESSAGES = 1 << 13
    EMBED_LINKS = 1 << 14
    ATTACH_FILES = 1 << 15
    READ_MESSAGE_HISTORY = 1 << 16
    MENTION_EVERYONE = 1 << 17
    USE_EXTERNAL_EMOJIS = 1 << 18
    VIEW_GUILD_INSIGHTS = 1 << 19
    CONNECT = 1 << 20
    SPEAK = 1 << 21
    MUTE_MEMBERS = 1 << 22
    DEAFEN_MEMBERS = 1 << 23
    MOVE_MEMBERS = 1 << 24
    USE_VAD = 1 << 25
    CHANGE_NICKNAME = 1 << 26
    MANAGE_NICKNAMES = 1 << 27
    MANAGE_ROLES = 1 << 28
    MANAGE_WEBHOOKS = 1 << 29
    MANAGE_EMOJIS_AND_STICKERS = 1 << 30
    USE_APPLICATION_COMMANDS = 1 << 31
    REQUEST_TO_SPEAK = 1 << 32
    MANAGE_EVENTS = 1 << 33
    MANAGE_THREADS = 1 << 34
    CREATE_PUBLIC_THREADS = 1 << 35
    CREATE_PRIVATE_THREADS = 1 << 36
    USE_EXTERNAL_STICKERS = 1 << 37
    SEND_MESSAGES_IN_THREADS = 1 << 38
    USE_EMBEDDED_ACTIVITIES = 1 << 39
    MODERATE_MEMBERS = 1 << 40


class PermissionBooler:
    DEFAULT = (
        Permission.VIEW_CHANNEL
        | Permission.VIEW_AUDIT_LOG
        | Permission.VIEW_GUILD_INSIGHTS
        | Permission.CREATE_INSTANT_INVITE
        | Permission.CHANGE_NICKNAME
        | Permission.MANAGE_NICKNAMES
        | Permission.SEND_MESSAGES
        | Permission.SEND_MESSAGES_IN_THREADS
        | Permission.CREATE_PUBLIC_THREADS
        | Permission.CREATE_PRIVATE_THREADS
        | Permission.EMBED_LINKS
        | Permission.ATTACH_FILES
        | Permission.ADD_REACTIONS
        | Permission.USE_EXTERNAL_EMOJIS
        | Permission.USE_EXTERNAL_STICKERS
        | Permission.MENTION_EVERYONE
        | Permission.READ_MESSAGE_HISTORY
        | Permission.SEND_TTS_MESSAGES
        | Permission.USE_APPLICATION_COMMANDS
        | Permission.CONNECT
        | Permission.SPEAK
        | Permission.STREAM
        | Permission.USE_VAD
        | Permission.REQUEST_TO_SPEAK
    )

    def __init__(self, permissions: int):
        partial = functools.partial(flagged, permissions)

        self.create_instant_invite = partial(Permission.CREATE_INSTANT_INVITE)
        self.kick_members = partial(Permission.KICK_MEMBERS)
        self.ban_members = partial(Permission.BAN_MEMBERS)
        self.administrator = partial(Permission.ADMINISTRATOR)
        self.manage_channels = partial(Permission.MANAGE_CHANNELS)
        self.manage_guild = partial(Permission.MANAGE_GUILD)
        self.add_reactions = partial(Permission.ADD_REACTIONS)
        self.view_audit_log = partial(Permission.VIEW_AUDIT_LOG)
        self.priority_speaker = partial(Permission.PRIORITY_SPEAKER)
        self.stream = partial(Permission.STREAM)
        self.view_channel = partial(Permission.VIEW_CHANNEL)
        self.send_messages = partial(Permission.SEND_MESSAGES)
        self.send_tts_messages = partial(Permission.SEND_TTS_MESSAGES)
        self.manage_messages = partial(Permission.MANAGE_MESSAGES)
        self.embed_links = partial(Permission.EMBED_LINKS)
        self.attach_files = partial(Permission.ATTACH_FILES)
        self.read_message_history = partial(Permission.READ_MESSAGE_HISTORY)
        self.mention_everyone = partial(Permission.MENTION_EVERYONE)
        self.use_external_emojis = partial(Permission.USE_EXTERNAL_EMOJIS)
        self.view_guild_insights = partial(Permission.VIEW_GUILD_INSIGHTS)
        self.connect = partial(Permission.CONNECT)
        self.speak = partial(Permission.SPEAK)
        self.mute_members = partial(Permission.MUTE_MEMBERS)
        self.deafen_members = partial(Permission.DEAFEN_MEMBERS)
        self.move_members = partial(Permission.MOVE_MEMBERS)
        self.use_vad = partial(Permission.USE_VAD)
        self.change_nickname = partial(Permission.CHANGE_NICKNAME)
        self.manage_nicknames = partial(Permission.MANAGE_NICKNAMES)
        self.manage_roles = partial(Permission.MANAGE_ROLES)
        self.manage_webhooks = partial(Permission.MANAGE_WEBHOOKS)
        self.manage_emojis_and_stickers = partial(Permission.MANAGE_EMOJIS_AND_STICKERS)
        self.use_application_commands = partial(Permission.USE_APPLICATION_COMMANDS)
        self.request_to_speak = partial(Permission.REQUEST_TO_SPEAK)
        self.manage_events = partial(Permission.MANAGE_EVENTS)
        self.manage_threads = partial(Permission.MANAGE_THREADS)
        self.create_public_threads = partial(Permission.CREATE_PUBLIC_THREADS)
        self.create_private_threads = partial(Permission.CREATE_PRIVATE_THREADS)
        self.use_external_stickers = partial(Permission.USE_EXTERNAL_STICKERS)
        self.send_messages_in_threads = partial(Permission.SEND_MESSAGES_IN_THREADS)
        self.use_embedded_activities = partial(Permission.USE_EMBEDDED_ACTIVITIES)
        self.moderate_members = partial(Permission.MODERATE_MEMBERS)
