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
import random
import secrets

import jwt
import pyotp
from apiflask import APIBlueprint, HTTPError
from argon2 import PasswordHasher

from ..database import RecoveryCode, Settings, Token, User
from ..ratelimiter import limiter
from .schemas import (
    Authorization,
    AuthorizationObject,
    CreateUser,
    CreateUserObject,
    EditUser,
    EditUserObject,
    Register,
    UserObject,
)

users = APIBlueprint('users', __name__, tag='users')
hasher = PasswordHasher()
AUTH_KEY = None


def new_code() -> str:
    return secrets.token_hex(70)


def is_too_used(username: str):
    used: int = User.objects(User.username == username).count()

    if used > 9000:
        raise HTTPError(400, 'Too many people are using this username.')


def roll_discriminator() -> str:
    discriminator_number = random.randint(1, 9999)
    return '%04d' % discriminator_number


def get_recoveries(user_id: int) -> list[str]:
    codes: list[RecoveryCode] = RecoveryCode.objects(
        RecoveryCode.user_id == user_id
    ).all()
    return [c.code for c in codes]


def get_available_discriminator(username: str):
    is_too_used(username=username)

    for _ in range(10):
        discriminator = roll_discriminator()

        try:
            User.objects(
                User.username == username, User.discriminator == discriminator
            ).get()
        except:
            return discriminator
        else:
            continue

    return None


def is_available(username: str, discriminator: int):
    try:
        User.objects(
            User.username == username, User.discriminator == discriminator
        ).get()
    except:
        return
    else:
        raise HTTPError(400, 'Discriminator is already taken')


def authorize(token: str) -> User:
    try:
        real_token = jwt.decode(token, AUTH_KEY, ['HS256'])
    except:
        raise HTTPError(401, 'Authorization is Invalid.')

    # make sure token wasn't deleted
    # queries through several large pieces of data to avoid collision
    try:
        tok: Token = Token.objects(
            Token.token == real_token['token'], Token.user_id == real_token['user_id']
        ).get()
    except Exception as e:
        print(e)
        raise HTTPError(401, 'Authorization is Invalid.')

    # any deleted user would be stripped of their
    # tokens, so this should be error-safe.
    return User.objects(User.id == tok.user_id).get()


@users.post('/register')
@limiter.limit('2/hour')
@users.input(CreateUser)
@users.output(
    Register, 201, description='The token which you will use for authentication'
)
def register(json: CreateUserObject):
    discriminator = get_available_discriminator(username=json['username'])

    if discriminator is None:
        raise HTTPError(400, 'Too many people are using this username.')

    password = hasher.hash(json['password'])

    user: User = User.create(
        username=json['username'],
        email=json['email'],
        password=password,
        discriminator=discriminator,
    )
    Settings.create(user_id=user.id)

    token = Token.create(token=new_code(), user_id=user.id, type=0)
    tk = jwt.encode(dict(token), AUTH_KEY)

    return {'token': tk}


@users.get('/users/@me')
@users.input(Authorization, 'headers')
@users.output(UserObject)
def get(headers: AuthorizationObject):
    u = dict(authorize(headers['authorization']))
    u.pop('password')
    return u


@users.patch('/users/@me')
@limiter.limit('10/second')
@users.input(EditUser)
@users.input(Authorization, 'headers')
@users.output(UserObject)
def edit(json: EditUserObject, headers: AuthorizationObject):
    user = authorize(headers['authorization'])

    setting: Settings = (
        Settings.objects(Settings.user_id == user.id)
        .only(['mfa_enabled', 'mfa_code'])
        .get()
    )

    mfa = json.get('mfa_code')

    recoveries = get_recoveries(user_id=user.id)

    if setting.mfa_enabled:
        totp = pyotp.TOTP(setting.mfa_code)

        if not mfa:
            raise HTTPError(403, 'mfa_code is a required field for users with mfa.')

        if mfa not in recoveries or mfa != totp.now():
            raise HTTPError(403, 'mfa code is invalid.')

    email = json.get('email')
    discriminator = json.get('discriminator')
    username = json.get('username')
    password = json.get('password')

    query = {}

    if email:
        query['email'] = email

    if discriminator:
        is_available(username=user.username, discriminator=discriminator)

        query['discriminator'] = discriminator

    if username:
        is_available(
            username=username, discriminator=discriminator or user.discriminator
        )

        query['username'] = username

    if password:
        query['password'] = hasher.hash(password=password)

    update = user.update(**query)
    ret = dict(update)
    ret.pop('password')
    return ret
