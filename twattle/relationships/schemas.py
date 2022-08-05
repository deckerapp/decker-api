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

from __future__ import annotations

from typing import TypedDict

from apiflask import Schema
from apiflask.fields import Boolean, Integer, Nested, String
from apiflask.validators import Length, OneOf, Regexp

from ..users.schemas import PublicUserObject, discriminatoregex


class MakeRelationship(Schema):
    type: int = Integer(validate=OneOf([0, 1]), required=True)
    username: str = String(required=True, validate=Length(1, 20))
    discriminator: str = String(required=True, validate=Regexp(discriminatoregex))


class ModifyRelationship(Schema):
    user_id: int = Integer(required=True)
    accept: bool = Boolean(required=True)


class ModifyRelationshipData(TypedDict):
    accept: bool


class MakeRelationshipData(TypedDict):
    type: int
    username: str
    discriminator: str


class Relationship(Schema):
    type: int = Integer()
    user: PublicUserObject = Nested(PublicUserObject)
