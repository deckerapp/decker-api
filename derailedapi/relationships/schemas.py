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
from typing import TYPE_CHECKING, TypedDict
from apiflask import Schema
from apiflask.fields import Integer, String, Boolean
from apiflask.validators import Length, Regexp, OneOf
from ..users.schemas import discriminatoregex

if TYPE_CHECKING:
    from typing_extensions import NotRequired


class MakeRelationship(Schema):
    type: int = Integer(validate=OneOf([0, 1]), required=True)
    username: str = String(validate=Length(1, 20))
    discriminator: str = String(validate=Regexp(discriminatoregex))
    accept: bool = Boolean()


class MakeRelationshipData(TypedDict):
    type: int
    username: str
    discriminator: str
    accept: NotRequired[bool]
