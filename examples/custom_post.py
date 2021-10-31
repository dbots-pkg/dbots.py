import dbots

client_id = '1234567890'


def server_count():
    return 100


def user_count():
    return 100


def voice_connections():
    return 0


def custom_post(poster, server_count, user_count, voice_connections):
    print(
        f'[CUSTOM_POST] Poster: {poster}, ServerCount: {server_count},',
        f'UserCount: {user_count}, VConnections: {voice_connections}'
    )


poster = dbots.Poster(
    client_id, server_count, user_count, voice_connections,
    on_custom_post=custom_post,
    api_keys={
        'customservice': '…'
    }
)
