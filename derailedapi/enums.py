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
