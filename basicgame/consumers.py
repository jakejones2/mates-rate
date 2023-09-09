import json
import asyncio
import logging
from typing import List, Dict, Optional
from async_property import async_property  # type: ignore
from channels.generic.websocket import AsyncWebsocketConsumer  # type: ignore
from basicgame import utils
from basicgame.set_interval import setIntervalAsync
import time


logger = logging.getLogger(__name__)


class LobbyConsumer(AsyncWebsocketConsumer):

    """Handles websocket messages from the lobby."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(args, kwargs)
        self.game_name: str
        self.game_id: int
        self.group_name: str
        self.player_name: str
        self.starting: bool = False

    async def broadcast_player_list_html(self) -> None:
        """Retrieves players in the game from db and sends html string to all in lobby."""
        player_list_html: str = await utils.produce_player_list_html(self.game_id)
        await self.channel_layer.group_send(
            self.group_name, {"type": "player_list", "player_list": player_list_html}
        )

    async def connect(self) -> None:
        """
        (1) Finds and assigns game_name via url.
        (2) Retrieves and assigns matching game_id from db.
        (3) Creates group "lobby_{game_id}" and adds current channel.
        (4) Retrieves player_name (e.g. nickname12345678) from cookie.
        (5) Ensures player with matching nickname is in the db.
        (6) Broadcasts a html string containing all players currently in the game.
        """
        self.game_name = self.scope["url_route"]["kwargs"]["game_name"]
        self.game_id = await utils.get_game_id(self.game_name)
        self.group_name = f"lobby_{self.game_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        player_name = utils.get_player_name_from_cookie(self.scope, self.game_name)
        if player_name:
            self.player_name = player_name
            await utils.ensure_player_in_game_db(self.player_name, self.game_id)
            await self.broadcast_player_list_html()
        else:
            await self.disconnect("bad cookie")

    async def disconnect(self, close_code) -> None:
        """
        Upon websocket disconnect, player is removed from db
        and updated player_list_html broadcast to all channels.
        """
        if not self.starting:
            await utils.remove_player_from_db(self.player_name)
            await self.broadcast_player_list_html()
            logger.warning(close_code)

    async def receive(self, text_data) -> None:
        """Handles incoming websocket messages."""
        text_data_json: dict = json.loads(text_data)
        if text_data_json.get("chat_message"):
            message_html: str = text_data_json["chat_message"]
            await self.channel_layer.group_send(
                self.group_name, {"type": "chat_message", "chat_message": message_html}
            )
        elif text_data_json.get("startgame"):
            await utils.change_game_progress(self.game_id, 1)
            await self.channel_layer.group_send(self.group_name, {"type": "start_game"})

    async def chat_message(self, event) -> None:
        """Sends chat messages received from channel group"""
        message: str = event["chat_message"]
        await self.send(text_data=json.dumps({"message": message}))

    async def player_list(self, event) -> None:
        """Sends player_list_html messages received from channel group"""
        player_list_html: str = event["player_list"]
        await self.send(text_data=json.dumps({"playerList": player_list_html}))

    async def start_game(self, *args) -> None:
        """Sends start_game messages received from channel group"""
        self.starting = True
        await self.send(text_data=json.dumps({"startGame": True}))


class GameConsumer(AsyncWebsocketConsumer):

    """Handles websocket messages from the game page."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(args, kwargs)
        self.game_name: str
        self.game_id: int
        self.group_name: str
        self.player_name: str
        self.wait_time: int = 6
        # functionless interval for type checking, never gets started
        self.broadcast: setIntervalAsync = setIntervalAsync(lambda *args: None, 1, 2, 0)
        self.sequence: List[str]
        self.results_sequence: asyncio.Task

    async def connect(self) -> None:
        """
        (1) Finds and assigns game_name via url.
        (2) Retrieves and assigns matching game_id from db.
        (3) Creates group "game_{game_id}" and adds current channel.
        (4) Retrieves player_name (e.g. nickname12345678) from cookie.
        (5) Ensures player with matching nickname is in the game db.
        (6) Assigns game sequence.
        (7) Sends game json depending on current game progress.
        (8) If data cannot be processed, round is skipped.
        """
        self.game_name = self.scope["url_route"]["kwargs"]["game_name"]
        self.game_id = await utils.get_game_id(self.game_name)
        self.group_name = f"game_{self.game_id}"

        player_name = utils.get_player_name_from_cookie(self.scope, self.game_name)
        if player_name:
            self.player_name = player_name
            await utils.ensure_player_in_game_db(self.player_name, self.game_id)
            self.sequence = await utils.generate_game_sequence_async(self.game_name)

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            try:
                view_type = await self.current_view
                json_string: str = await utils.generate_round_json(
                    view_type, self.game_id
                )
                await self.send(text_data=json_string)
            except ValueError:
                self.game_error()
        else:
            await self.disconnect("cannot find cookie")

    async def disconnect(self, close_code) -> None:
        """Removes player from channel group upon disconnection."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if getattr(self.broadcast, "has_started", False):
            await self.broadcast.stop()
            logger.warning(close_code)

    @async_property
    async def game_progress(self) -> Optional[int]:
        return await utils.get_game_progress(self.game_id)

    @async_property
    async def current_view(self) -> str:
        sequence: List[str] = self.sequence
        progress = await self.game_progress
        return sequence[progress]

    async def game_error(self):
        if hasattr(self, "results_sequence"):
            self.results_sequence.cancel()
        logger.warning("game data corrupted:")
        logger.warning(f"players = {utils.get_players(self.game_name)}")
        logger.warning(f"progress: {await self.game_progress}")
        logger.warning(f"category: {await utils.get_category(self.game_id)}")
        asyncio.create_task(self.begin_skip_round_sequence())

    async def broadcast_data_for_all(self, message=False, next=None):
        """
        Broadcasts json and images to all members of channel group.
        If passed no message, json is generated based on the current view type.
        Json is sent periodically via the setIntervalAsync class.
        The broadcast is assigned to self.broadcast and can be cancelled with self.broadcast.stop().
        Broadcasting also times out after a given limit of broadcasts (default = 30).
        """
        if getattr(self.broadcast, "has_started", False):
            await self.broadcast.stop()
        if message:
            progress = message["type"]
            message = message
        else:
            view_type = await self.current_view
            json_string: str = await utils.generate_round_json(
                view_type, self.game_id, next
            )
            progress = await self.game_progress
            message = {"type": "game_update", "json": json_string}
        message["sender"] = self.player_name

        async def send_json() -> None:
            logger.info(f"{self.player_name} broadcasted: {message}")
            await self.channel_layer.group_send(self.group_name, message)

        self.broadcast = setIntervalAsync(send_json, progress)
        await self.broadcast.start()

    async def begin_results_sequence(self):
        """
        Coordinates timed reel of winner view, results view, and leaderboard view.
        Sends updated json for broadcast and mutates game data as neccessary.
        """
        # View 2 - Winner shown
        await utils.advance_progress(self.game_id, "winner", self.sequence)
        pause_time = self.wait_time * 1.5
        next_view_time = time.time() + pause_time
        await self.broadcast_data_for_all(next=next_view_time)
        await asyncio.sleep(pause_time)
        # View 3 - Results shown
        await utils.advance_progress(self.game_id, "results", self.sequence)
        scores: Dict[str, float] = await utils.create_average_score_dict(self.game_id)
        await utils.update_player_points(scores, self.game_id)
        pause_time = self.wait_time + (len(scores) / 2)
        next_view_time = time.time() + pause_time
        await self.broadcast_data_for_all(next=next_view_time)
        await asyncio.sleep(pause_time)
        # View 4 - Leaderboard shown
        await utils.advance_progress(self.game_id, "leaderboard", self.sequence)
        next_view_time = time.time() + pause_time
        await self.broadcast_data_for_all(next=next_view_time)
        await asyncio.sleep(pause_time)
        # Go to next round or end
        await utils.advance_progress(self.game_id, "submission", self.sequence)
        await utils.reset_submissions_and_votes(self.game_id)
        await self.broadcast_data_for_all()
        finished = await utils.delete_game_if_finished(self.game_id)
        if finished and getattr(self.broadcast, "has_started", None):
            logger.info("closing final broadcast")
            await asyncio.sleep(5)
            await self.broadcast.stop()

    async def begin_skip_round_sequence(self):
        """
        Coordinates timed reel of skip round view and the next round.
        Sends updated json for broadcast and mutates game data as neccessary.
        """
        skip_message = {"type": "skip_round"}
        await self.broadcast_data_for_all(skip_message)
        await asyncio.sleep(3)
        next_round: int = await utils.next_round(self.game_id, self.sequence)
        await utils.change_game_progress(self.game_id, next_round)
        await utils.reset_submissions_and_votes(self.game_id)
        await self.broadcast_data_for_all()
        finished = await utils.delete_game_if_finished(self.game_id)
        if finished:
            await asyncio.sleep(5)
            await self.broadcast.stop()

    async def receive(self, text_data: str) -> None:
        """
        Receives websocket communications from the game and handles game flow.

        Submission:
            Upon a 'submission' message, this function collects all player submissions
            (characters and one category), and adds them to the db. The final client to
            add a submission advances the game progress, and broadcasts new game json to
            all those in the channel group.

        Vote:
            Same structure as submission (see above), but collects votes. Once all votes
            are collected, the timed results sequence is initiated as a background asycio task.
            This task is assigned to self.results_sequence so it can be cancelled if needed.

        Category:
            Only used in boring mode. The category is added to the db, game progress is
            advanced, and new game json is broadcasted.

        Force Next:
            Upon a 'force_next' message, this function checks whether there are enough
            submissions to continue as normal, and if so, advances the game progress and
            calls the broadcasting function, or starts the results sequence if appropriate.
            If there is not enough data, or if data processing fails during the results
            sequence, or if the results sequence is in progress, the function begins the
            skip-round sequence as a background asyncio task.
        """
        text_data_json: dict = json.loads(text_data)
        logger.info(f"received message: {text_data_json}")
        latter_views = ["vote", "winner", "results", "leaderboard"]
        view = await self.current_view

        if text_data_json.get("submission"):
            if view in latter_views:
                return
            submission_data: Optional[Dict[str, str]] = text_data_json.get("submission")
            if not submission_data:
                return  # redundant but keeps mypy happy
            submission: Optional[str] = submission_data["text"]
            name: Optional[str] = submission_data["name"]
            if not submission or not name:
                return
            to_voting: bool = await utils.collected_and_added_all_input_data(
                player_name=name,
                field="submission",
                data=submission,
                game_id=self.game_id,
            )
            # broadcasting stops after successful submission
            if getattr(self.broadcast, "has_started", None):
                await self.broadcast.stop()
            if to_voting:
                if not await utils.enough_submissions(self.game_id):
                    self.game_error()
                    return
                await utils.advance_progress(self.game_id, "vote", self.sequence)
                try:
                    await self.broadcast_data_for_all()
                except ValueError:
                    self.game_error()

        elif text_data_json.get("vote"):
            if view != "vote":
                return
            vote_data: Optional[Dict[str, str | Dict[str, int]]] = text_data_json.get(
                "vote"
            )
            if not vote_data:
                return  # redundant but keeps mypy happy
            player_name = vote_data["name"]
            if not player_name:
                return
            to_results_sequence: bool = await utils.collected_and_added_all_input_data(
                player_name=player_name,
                field="votes",
                data=text_data,
                game_id=self.game_id,
            )
            if getattr(self.broadcast, "has_started", None):
                await self.broadcast.stop()
            if to_results_sequence and view == "vote":
                if not await utils.enough_votes(self.game_id):
                    self.game_error()
                try:
                    self.results_sequence = asyncio.create_task(
                        self.begin_results_sequence()
                    )
                except ValueError:
                    self.game_error()

        elif text_data_json.get("category"):
            wrong_views = latter_views.copy()
            wrong_views.append("character")
            if view in wrong_views:
                return
            data: Optional[Dict[str, str]] = text_data_json.get("category")
            if not data:
                return  # redundant but keeps mypy happy
            await utils.add_category(self.game_id, data["name"], data["text"])
            await utils.advance_progress(self.game_id, "character", self.sequence)
            await self.broadcast_data_for_all()

        elif text_data_json.get("force_next"):
            if view == "vote" and await utils.enough_votes(self.game_id):
                try:
                    self.results_sequence = asyncio.create_task(
                        self.begin_results_sequence()
                    )
                except ValueError:
                    self.game_error()
            elif view not in latter_views and await utils.enough_submissions(
                self.game_id
            ):
                await utils.advance_progress(self.game_id, "vote", self.sequence)
                try:
                    await self.broadcast_data_for_all()
                except ValueError:
                    self.game_error()
            else:
                asyncio.create_task(self.begin_skip_round_sequence())

    async def game_update(self, event) -> None:
        """
        If the current player is broadcasting and receives another player's
        broadcast, it checks if this broadcast represents a higher progress value,
        and if so, cancels the lower-progress broadcast and results sequence task
        if present. If both broadcasts represent the same information, the sender
        with the 'biggest' name continues to broadcast (name are unique). If either
        of these conditions succeed, game data is subsequently sent to the client.
        If the broadcast is behind the current progress, no action is taken.
        """
        if getattr(self.broadcast, "has_started", None):
            new_progress = json.loads(event["json"])["progress"]
            logger.info(f"{self.player_name} received {new_progress}")
            logger.info(f"{self.player_name} is {self.broadcast.progress}")
            if self.broadcast.progress < new_progress:
                await self.broadcast.stop()
                if hasattr(self, "results_sequence"):
                    self.results_sequence.cancel()
            elif self.broadcast.progress > new_progress:
                return
            elif self.broadcast.progress == new_progress:
                if event["sender"] > self.player_name:
                    await self.broadcast.stop()
                    if hasattr(self, "results_sequence"):
                        self.results_sequence.cancel()
        await self.send(text_data=event["json"])

    async def skip_round(self, event) -> None:
        """
        Cancels any in-progress results sequence, and any broadcast that is
        not 'skip_round'. Sends skip message to client.
        """
        if hasattr(self, "results_sequence"):
            self.results_sequence.cancel()
        if getattr(self.broadcast, "has_started", None):
            if self.broadcast.progress != "skip_round":
                await self.broadcast.stop()
        await self.send(text_data=json.dumps({"view": "skip"}))
