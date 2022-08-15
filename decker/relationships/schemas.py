"""
Elastic License 2.0

Copyright Decker and/or licensed to Decker under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
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
