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
from typing import Any

from apiflask import APIBlueprint, HTTPError
from apiflask.schemas import EmptySchema

from ..database import Relationship, User
from ..enums import Relation
from ..users.routes import authorize
from ..users.schemas import Authorization, AuthorizationObject
from .schemas import MakeRelationship, MakeRelationshipData, Relationship as RelationshipData

relationships = APIBlueprint('relationships', __name__, tag='User')


# TODO: Implement events here.
@relationships.post('/users/@me/relationships')
@relationships.input(MakeRelationship)
@relationships.input(Authorization, 'headers')
@relationships.output(EmptySchema, 204)
def create_relationship(json: MakeRelationshipData, headers: AuthorizationObject):
    peer = authorize(headers['authorization'])
    targets: list[User] = User.objects(
        User.username == json['username'],
    ).all()
    target: User = None

    for ts in targets:
        if ts.discriminator == json['discriminator']:
            target = ts

    if target is None:
        raise HTTPError(404, 'Target user does not exist')

    if json['type'] == Relation.FRIEND:
        try:
            peer_relation: Relationship = Relationship.objects(
                Relationship.user_id == peer.id, Relationship.target_id == target.id
            ).get()
        except:
            peer_relation = None
        else:
            if peer_relation.type == Relation.BLOCKED:
                raise HTTPError(400, 'You have blocked this user')
            elif peer_relation.type == Relation.FRIEND:
                raise HTTPError(400, 'You have already friended this user')
            elif peer_relation.type == Relation.OUTGOING:
                raise HTTPError(400, 'You already sent a friend request to this user')

        try:
            # check if this user was blocked or is already friended
            current_relation: Relationship = Relationship.objects(
                Relationship.user_id == target.id, Relationship.target_id == peer.id
            ).get()
        except:
            pass
        else:
            if current_relation.type == Relation.BLOCKED:
                raise HTTPError(401, 'This user has blocked you')
            elif current_relation.type == Relation.FRIEND:
                raise HTTPError(400, 'This user has already friended you')
            elif current_relation.type == Relation.INCOMING and json['accept'] is False:
                current_relation.delete()

                if peer_relation:
                    peer_relation.delete()

                return ''
            elif current_relation.type == Relation.INCOMING and json['accept'] is True:
                current_relation = current_relation.update(type=Relation.FRIEND)

                if peer_relation:
                    peer_relation = peer_relation.update(type=Relation.FRIEND)
                else:
                    peer_relation = Relationship.create(
                        user_id=peer.id, target_id=target.id, type=Relation.FRIEND
                    )

                return ''

    elif json['type'] == Relation.BLOCKED:
        try:
            peer_relation: Relationship = Relationship.objects(
                Relationship.user_id == peer.id, Relationship.target_id == target.id
            ).get()
        except:
            peer_relation: Relationship = Relationship.create(
                user_id=peer.id, target_id=target.id, type=Relation.BLOCKED
            )
        else:
            if peer_relation.type == Relation.BLOCKED:
                raise HTTPError(400, 'This user is already blocked')
            elif peer_relation.type == Relation.FRIEND:
                raise HTTPError(400, 'This user is friended')

            peer_relation.update(type=Relation.BLOCKED)

    # TODO: Send these as events
    Relationship.create(
        user_id=peer.id, target_id=target.id, type=Relation.OUTGOING
    )
    Relationship.create(
        user_id=target.id, target_id=peer.id, type=Relation.INCOMING
    )

    return ''


@relationships.delete('/users/@me/relationships/<int:user_id>')
@relationships.input(Authorization, 'headers')
@relationships.output(EmptySchema, 204)
def remove_relationship(user_id: int, headers: AuthorizationObject):
    peer = authorize(headers['authorization'])

    try:
        target: User = User.objects(User.id == user_id).get()
    except:
        raise HTTPError(404, 'Target user does not exist')

    try:
        peer_relation: Relationship = Relationship.objects(
            Relationship.user_id == peer.id, Relationship.target_id == target.id
        ).get()
    except:
        raise HTTPError(400, 'You don\'t have a relationship with this user')
    else:
        peer_relation.delete()

    try:
        target_relationship: Relationship = Relationship.objects(
            Relationship.user_id == target.id, Relationship.target_id == peer.id
        ).get()
    except:
        # blocked users
        pass
    else:
        if target_relationship.type != Relation.BLOCKED:
            target_relationship.delete()

    return ''


def easily_productionify_relationship(
    relationship: Relationship, peer: bool
) -> dict[Any, Any]:
    ret = dict(relationship)

    if peer:
        ret.pop('user_id')

        target: User = User.objects(User.id == ret.pop('target_id')).get()
        dtarg = dict(target)
        dtarg.pop('email')
        dtarg.pop('password')
        dtarg.pop('verified')

        ret['user'] = dtarg
        return ret
    else:
        ret.pop('target_id')

        peer_user: User = User.objects(User.id == ret.pop('user_id')).get()
        dtarg = dict(peer_user)
        dtarg.pop('email')
        dtarg.pop('password')
        dtarg.pop('verified')

        ret['user'] = dtarg
        return ret


@relationships.get('/users/@me/relationships')
@relationships.input(Authorization, 'headers')
@relationships.output(RelationshipData(many=True), description='Your relationships')
def get_relationships(headers: AuthorizationObject):
    peer = authorize(headers['authorization'])
    ret = []

    peers_relationships: list[Relationship] = Relationship.objects(
        Relationship.user_id == peer.id
    ).all()

    for pr in peers_relationships:
        ret.append(easily_productionify_relationship(relationship=pr, peer=True))

    return ret
