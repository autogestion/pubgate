import pytest


def s2s_follow(user, remote_user, id):
    return {
        '@context': ['https://www.w3.org/ns/activitystreams',
                    'https://w3id.org/security/v1',
                     {'Hashtag': 'as:Hashtag', 'sensitive': 'as:sensitive'}],
        'actor': user,
        'id': id,
        'object': remote_user,
        'type': 'Follow'
    }
