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
import base64
import binascii
import os

import itsdangerous
from apiflask import HTTPError
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import columns, connection, management, models
from cassandra.io import asyncorereactor, geventreactor

from derailedapi.enforgement import forger

auth_provider = PlainTextAuthProvider(
    os.getenv('SCYLLA_USER'), os.getenv('SCYLLA_PASSWORD')
)


def get_hosts():
    hs = os.getenv('SCYLLA_HOSTS')

    return None if hs is None else hs.split(',')


def connect():
    connection_class = (
        geventreactor.GeventConnection
        if os.getenv('GEVENT') == 'true'
        else asyncorereactor.AsyncoreConnection
    )

    connection.setup(
        get_hosts(),
        'derailed',
        auth_provider=auth_provider,
        connect_timeout=100,
        retry_connect=True,
        connection_class=connection_class,
    )


class User(models.Model):
    __table_name__ = 'users'
    id: int = columns.BigInt(primary_key=True, partition_key=True, default=forger.forge)
    email: str = columns.Text(index=True)
    password: str = columns.Text()
    username: str = columns.Text(index=True)
    discriminator: str = columns.Text()
    avatar: str = columns.Text(default='')
    banner: str = columns.Text(default='')
    flags: int = columns.Integer(default=0)
    bot: bool = columns.Boolean(default=False)
    verified: bool | None = columns.Boolean(default=False)


class GuildPosition(models.Model):
    __table_name__ = 'guild_positions'
    user_id: int = columns.BigInt(primary_key=True)
    guild_id: int = columns.BigInt()
    folder: str = columns.Text()
    position: int = columns.Integer()


class Settings(models.Model):
    __table_name__ = 'settings'
    user_id: int = columns.BigInt(primary_key=True)
    locale: str = columns.Text(default='en-US')
    developer_mode: bool = columns.Boolean(default=False)
    theme: str = columns.Text(default='dark')
    status: str = columns.Text(default='invisible')
    mfa_enabled: bool = columns.Boolean(default=False)
    mfa_code: str = columns.Text()
    friend_requests_off: bool = columns.Boolean(default=False)


class RecoveryCode(models.Model):
    __table_name__ = 'recovery_codes'
    user_id: int = columns.BigInt(primary_key=True)
    code: str = columns.Text()


# NOTE:
# Max Outgoing Friend Requests and Incoming is 2000.
# Max Friends is set to 4000.
class Relationship(models.Model):
    __table_name__ = 'relationships'
    # the user id who created the relationship
    user_id: int = columns.BigInt(primary_key=True)
    # the user id who friended/blocked/etc the relationship
    target_id: int = columns.BigInt(index=True)
    # the type of relationship
    type: int = columns.Integer()


class Activity(models.Model):
    __table_name__ = 'activities'
    user_id: int = columns.BigInt(primary_key=True)
    type: int = columns.Integer(default=0)
    created_at: str = columns.DateTime()
    content: str = columns.Text()
    stream_url: str = columns.Text()
    emoji_id: int = columns.BigInt()


class Channel(models.Model):
    __table_name__ = 'channels'
    id: int = columns.BigInt(primary_key=True)
    type: int = columns.Integer()
    name: str = columns.Text()


class Recipient(models.Model):
    __table_name__ = 'recipients'
    channel_id: int = columns.BigInt(primary_key=True)
    user_id: int = columns.BigInt()


class GroupDMChannel(models.Model):
    __table_name__ = 'group_dm_channels'
    channel_id: int = columns.BigInt(primary_key=True)
    icon: str = columns.Text()
    owner_id: int = columns.BigInt()


def create_token(user_id: int, user_password: str) -> str:
    signer = itsdangerous.TimestampSigner(user_password)
    user_id = str(user_id)
    user_id = base64.b64encode(user_id.encode())

    return signer.sign(user_id).decode()


def verify_token(token: str | None):
    if token is None:
        raise HTTPError(401, 'Authorization is invalid')

    fragmented = token.split('.')
    user_id = fragmented[0]

    try:
        user_id = base64.b64decode(user_id.encode())
        user_id = int(user_id)
    except (ValueError, binascii.Error):
        raise HTTPError(401, 'Failed to get container volume for Authorization')

    try:
        user: User = User.objects(User.id == user_id).get()
    except:
        raise HTTPError(401, 'Object for Authorization not found')

    signer = itsdangerous.TimestampSigner(user.password)

    try:
        signer.unsign(token)

        return user
    except (itsdangerous.BadSignature):
        raise HTTPError(401, 'Signature on Authorization is Invalid')


def sync_tables():
    management.sync_table(User)
    management.sync_table(GuildPosition)
    management.sync_table(Settings)
    management.sync_table(RecoveryCode)
    management.sync_table(Relationship)
    management.sync_table(Activity)
    management.sync_table(Channel)
    management.sync_table(Recipient)
    management.sync_table(GroupDMChannel)
