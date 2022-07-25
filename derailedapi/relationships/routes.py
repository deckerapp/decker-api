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
from apiflask import APIBlueprint, HTTPError

from ..database import Relationship, User
from ..enums import Relation
from ..users.routes import authorize
from ..users.schemas import Authorization, AuthorizationObject
from .schemas import MakeRelationship, MakeRelationshipData

relationships = APIBlueprint('relationships', __name__, tag='users')


# TODO: Implement events here.
@relationships.post('/users/@me/relationships')
@relationships.input(MakeRelationship)
@relationships.input(Authorization, 'headers')
@relationships.output('', 204)
def create_relationship(json: MakeRelationshipData, headers: AuthorizationObject):
    peer = authorize(headers['authorization'])
    try:
        target: User = User.objects(
            User.username == json['username'],
            User.discriminator == json['discriminator'],
        ).get()
    except:
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

        # TODO: Send these as events
        Relationship.create(
            user_id=peer.id, target_id=target.id, type=Relation.OUTGOING
        )
        Relationship.create(
            user_id=target.id, target_id=peer.id, type=Relation.INCOMING
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


@relationships.delete('/users/@me/relationships/<int:user_id>')
@relationships.input(Authorization, 'headers')
@relationships.output('', 204)
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
