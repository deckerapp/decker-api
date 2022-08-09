"""
Elastic License 2.0

Copyright Discend and/or licensed to Discend under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired

from apiflask import Schema
from apiflask.fields import Boolean, Email, Integer, Nested, String
from apiflask.validators import Length, Regexp

discriminatoregex = re.compile(r'^[0-9]{4}$')


class CreateUser(Schema):
    email: str = Email(required=True, validate=Length(5, 200))
    username: str = String(required=True, validate=Length(1, 20))
    password: str = String(required=True, validate=Length(1, 128))


class CreateUserObject(TypedDict):
    email: str
    username: str
    password: str


class Register(Schema):
    token: str = String()


class EditUser(Schema):
    email: str = String(validate=Length(5, 200))
    username: str = String(validate=Length(1, 20))
    password: str = String()
    discriminator: str = String(validate=Regexp(discriminatoregex))
    mfa_code: int = Integer()


class EditUserObject(TypedDict):
    email: NotRequired[str]
    username: NotRequired[str]
    password: NotRequired[str]
    discriminator: NotRequired[str]
    mfa_code: NotRequired[str]


class Authorization(Schema):
    authorization: str = String(required=True)


class AuthorizationObject(TypedDict):
    authorization: str


class PublicUserObject(Schema):
    id: str = String()
    username: str = String()
    discriminator: str = String()
    avatar: str = String()
    banner: str = String()
    flags: int = Integer()
    bot: bool = Boolean()


class UserObject(PublicUserObject):
    email: str = String()


class CreateToken(Schema):
    email: str = Email(required=True)
    password: str = String(required=True, validate=Length(1, 128))
    mfa_code: str = String()


class CreateTokenObject(TypedDict):
    email: str
    password: str
    mfa_code: NotRequired[str]


class SessionLimit(Schema):
    total = Integer()
    remaining = Integer()
    max_concurrency = Integer()


class Gateway(Schema):
    url = String()
    shards = Integer()
    session_start_limit = Nested(SessionLimit)


class Note(Schema):
    user_id = Integer()
    content = String(required=True, validate=(Length(1, 1000)))


class NoteObject(TypedDict):
    user_id: int
    content: str
