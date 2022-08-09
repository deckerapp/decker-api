"""
Elastic License 2.0

Copyright Discorse and/or licensed to Discorse under one
or more contributor license agreements. Licensed under the Elastic License;
you may not use this file except in compliance with the Elastic License.
"""
from typing import Any

from apiflask import APIBlueprint, HTTPError
from apiflask.schemas import EmptySchema

from ..database import (
    Event,
    NotFound,
    Relationship,
    Settings,
    User,
    dispatch_event,
    objectify,
)
from ..enums import Relation
from ..users.routes import authorize
from ..users.schemas import Authorization, AuthorizationObject
from .schemas import (
    MakeRelationship,
    MakeRelationshipData,
    ModifyRelationship,
    ModifyRelationshipData,
)
from .schemas import Relationship as RelationshipData

relationships = APIBlueprint('relationships', __name__)


# make sure these users have no passed their specific limit of 1000 relationships
def didnt_pass_max_relationships(user: User, target: User):
    target_setting: Settings = (
        Settings.objects(Settings.user_id == target.id)
        .only(['friend_requests_off'])
        .get()
    )

    if target_setting.friend_requests_off:
        raise HTTPError(400, 'This user has turned off friend requests')

    user_main_relationships: int = Relationship.objects(
        Relationship.user_id == user.id
    ).count()
    user_targeted_relationships: int = Relationship.objects(
        Relationship.target_id == user.id
    ).count()

    if user_main_relationships + user_targeted_relationships == 5000:
        raise HTTPError(400, 'You have reached your maximum relationship limit')

    target_main_relationships: int = Relationship.objects(
        Relationship.user_id == target.id
    ).count()
    target_targeted_relationships: int = Relationship.objects(
        Relationship.target_id == target.id
    ).count()

    if target_main_relationships + target_targeted_relationships == 5000:
        raise HTTPError(400, 'Target user has reached their maximum relationship limit')


# TODO: Implement events here.
@relationships.post('/users/@me/relationships')
@relationships.input(MakeRelationship)
@relationships.input(Authorization, 'headers')
@relationships.output(EmptySchema, 204)
@relationships.doc(tag='Relationships')
def create_relationship(json: MakeRelationshipData, headers: AuthorizationObject):
    peer = authorize(headers['authorization'])
    targets: list[User] = User.objects(
        User.username == json['username'],
    ).all()
    target: User | None = next(
        (ts for ts in targets if ts.discriminator == json['discriminator']),
        None,
    )

    if target is None:
        raise HTTPError(404, 'Target user does not exist')

    if target.id == peer.id:
        raise HTTPError(400, 'You cannot friend yourself')

    didnt_pass_max_relationships(user=peer, target=target)

    if json['type'] == Relation.FRIEND:
        try:
            peer_relation: Relationship = Relationship.objects(
                Relationship.user_id == peer.id, Relationship.target_id == target.id
            ).get()
        except NotFound:
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
        except NotFound:
            pass
        else:
            if current_relation.type == Relation.BLOCKED:
                raise HTTPError(401, 'This user has blocked you')
            elif current_relation.type == Relation.FRIEND:
                raise HTTPError(400, 'This user has already friended you')
    else:
        try:
            peer_relation: Relationship = Relationship.objects(
                Relationship.user_id == peer.id, Relationship.target_id == target.id
            ).get()
        except NotFound:
            peer_relation: Relationship = Relationship.create(
                user_id=peer.id, target_id=target.id, type=Relation.BLOCKED
            )
        else:
            if peer_relation.type == Relation.BLOCKED:
                raise HTTPError(400, 'This user is already blocked')
            elif peer_relation.type == Relation.FRIEND:
                raise HTTPError(400, 'This user is friended')

            peer_relation.update(type=Relation.BLOCKED)
            dispatch_event(
                'relationships',
                Event(
                    'RELATIONSHIP_UPDATE',
                    {'relator': peer.id, 'type': Relation.BLOCKED},
                    user_id=target.id,
                ),
            )

    # TODO: Send these as events
    Relationship.create(user_id=peer.id, target_id=target.id, type=Relation.OUTGOING)
    Relationship.create(user_id=target.id, target_id=peer.id, type=Relation.INCOMING)

    dispatch_event(
        'relationships',
        Event(
            'RELATIONSHIP_CREATE',
            {'type': Relation.INCOMING, 'relator': peer.id},
            user_id=target.id,
        ),
    )


@relationships.patch('/users/@me/relationships')
@relationships.input(ModifyRelationship, 'json')
@relationships.input(Authorization, 'headers')
@relationships.output(EmptySchema, 204)
@relationships.doc(tag='Relationships')
def modify_relationship(json: ModifyRelationshipData, headers: AuthorizationObject):
    peer = authorize(headers['authorization'], ['id'])

    try:
        target: User = User.objects(User.id == json['user_id']).get()
    except NotFound:
        raise HTTPError(400, 'Target user does not exist')

    try:
        peer_relationship: Relationship = Relationship.objects(
            Relationship.user_id == peer.id, Relationship.target_id == target.id
        ).get()
    except NotFound:
        raise HTTPError(400, 'You do not have a relationship with this user')

    if peer_relationship.type == Relation.INCOMING:
        target_relationship: Relationship = Relationship.objects(
            Relationship.user_id == target.id, Relationship.target_id == peer.id
        ).get()

        target_relationship.update(type=Relation.FRIEND)
        peer_relationship.update(type=Relation.FRIEND)

        dispatch_event(
            'relationships',
            Event(
                'RELATIONSHIP_UPDATE',
                {'type': Relation.FRIEND, 'relator': target.id},
                user_id=peer.id,
            ),
        )
        dispatch_event(
            'relationships',
            Event(
                'RELATIONSHIP_UPDATE',
                {'type': Relation.FRIEND, 'relator': peer.id},
                user_id=target.id,
            ),
        )
    else:
        raise HTTPError(400, 'You cannot modify this type of relationship')

    return ''


@relationships.delete('/users/@me/relationships/<int:user_id>')
@relationships.input(Authorization, 'headers')
@relationships.output(EmptySchema, 204)
@relationships.doc(tag='Relationships')
def remove_relationship(user_id: int, headers: AuthorizationObject):
    peer = authorize(headers['authorization'], ['id'])

    try:
        target: User = User.objects(User.id == user_id).get()
    except NotFound:
        raise HTTPError(404, 'Target user does not exist')

    try:
        peer_relation: Relationship = Relationship.objects(
            Relationship.user_id == peer.id, Relationship.target_id == target.id
        ).get()
    except NotFound:
        raise HTTPError(400, 'You don\'t have a relationship with this user')
    else:
        peer_relation.delete()
        dispatch_event(
            'relationships',
            Event('RELATIONSHIP_REMOVE', {'relator': target.id, 'remover': True}),
        )

    try:
        target_relationship: Relationship = Relationship.objects(
            Relationship.user_id == target.id, Relationship.target_id == peer.id
        ).get()
    except NotFound:
        # blocked users
        pass
    else:
        if target_relationship.type != Relation.BLOCKED:
            target_relationship.delete()
            dispatch_event(
                'relationships',
                Event('RELATIONSHIP_REMOVE', {'relator': peer.id, 'remover': False}),
            )

    return ''


def easily_productionify_relationship(relationship: Relationship) -> dict[Any, Any]:
    ret = dict(relationship)

    ret.pop('user_id')

    target: User = User.objects(User.id == ret.pop('target_id')).get()
    dtarg = dict(target)

    dtarg.pop('email')
    dtarg.pop('password')
    dtarg.pop('verified')

    ret['user'] = dtarg
    return ret


@relationships.get('/users/@me/relationships')
@relationships.input(Authorization, 'headers')
@relationships.output(RelationshipData(many=True), description='Your relationships')
@relationships.doc(tag='Relationships')
def get_relationships(headers: AuthorizationObject):
    me = authorize(headers['authorization'], ['id'])
    relationships: list[Relationship] = Relationship.objects(
        Relationship.user_id == me.id
    ).all()

    return objectify(
        [easily_productionify_relationship(relationship=pr) for pr in relationships]
    )
