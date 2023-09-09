from basicgame.utils import get_player_name_from_cookie
from basicgame.tests.unit.base import TripleTest


class TestGetPlayerFromCookie(TripleTest):
    """
    Function takes asgi scope dictionary and game name.
    Should find cookie and retrieve player name from it.
    Should have no side effects.
    """

    def test_finds_cookie(self):
        game_name = "fish_apple"
        scope = {
            "type": "websocket",
            "path": "/ws/lobby/mole_cover/",
            "raw_path": b"/ws/lobby/mole_cover/",
            "headers": [
                (b"host", b"127.0.0.1:8000"),
                (b"connection", b"Upgrade"),
                (b"pragma", b"no-cache"),
                (b"cache-control", b"no-cache"),
                (
                    b"user-agent",
                    b"Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
                ),
                (b"upgrade", b"websocket"),
                (b"origin", b"http://127.0.0.1:8000"),
                (b"sec-websocket-version", b"13"),
                (b"accept-encoding", b"gzip, deflate, br"),
                (b"accept-language", b"en-GB,en-US;q=0.9,en;q=0.8"),
                (
                    b"cookie",
                    b"csrftoken=mVAO9YJLUnc1fQcWZA85DcdvJWVxKA5K; condor_essay=Jakef9aPP2Zr; python_park=Jakeqef5f8Ma; mole_cover=JakeffyyEcLQ",
                ),
                (b"sec-websocket-key", b"rR/vSi0kqXUWqH1VTauhDA=="),
                (
                    b"sec-websocket-extensions",
                    b"permessage-deflate; client_max_window_bits",
                ),
            ],
            "query_string": b"",
            "client": ["127.0.0.1", 61286],
            "server": ["127.0.0.1", 8000],
            "subprotocols": [],
            "asgi": {"version": "3.0"},
            "cookies": {
                "csrftoken": "mVAO9YJLUnc1fQcWZA85DcdvJWVxKA5K",
                "condor_essay": "testuser22345678",
                "fish_apple": "testuser12345678",
                "mole_cover": "testuser32345678",
            },
            "path_remaining": "",
            "url_route": {"args": (), "kwargs": {"game_name": "mole_cover"}},
        }
        self.assertEqual(
            get_player_name_from_cookie(scope, game_name), "testuser12345678"
        )

    def test_should_return_none_if_no_cookie_found(self):
        scope1 = {}
        scope2 = {"cookies": {}}
        self.assertEqual(get_player_name_from_cookie(scope1, "dogs"), None)
        self.assertEqual(get_player_name_from_cookie(scope2, "dogs"), None)

    def test_should_not_mutate_scope(self):
        scope = {"cookies": {"testgame": "cookie"}}
        scope_copy = {"cookies": {"testgame": "cookie"}}
        get_player_name_from_cookie(scope, "testgame")
        self.assertEqual(scope, scope_copy)
