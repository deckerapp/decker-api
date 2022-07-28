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
from __future__ import annotations

import re
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing_extensions import NotRequired

from apiflask import Schema
from apiflask.fields import Boolean, Email, Integer, String
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


class UserObject(Schema):
    id: int = Integer()
    email: str = String()
    username: str = String()
    discriminator: str = String()
    avatar: str = String()
    banner: str = String()
    flags: int = Integer()
    bot: bool = Boolean()


class CreateToken(Schema):
    email: str = Email(required=True)
    password: str = String(validate=Length(1, 128))
    mfa_code: str = String()


class CreateTokenObject(TypedDict):
    email: str
    password: str
    mfa_code: NotRequired[str]
