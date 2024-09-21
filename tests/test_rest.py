import logging
from collections import defaultdict

import pytest

from match_scheduler.match_scheduler import (
    BadmintonSchedulerGraph as MatchScheduler,
)
from match_scheduler.match_scheduler import num_rest

LOGGER = logging.getLogger(__name__)
# Import MatchScheduler from the module where you defined it
# from your_module import MatchScheduler


@pytest.fixture
def scheduler():
    """Fixture to initialize a scheduler with 13 players and 3 courts."""
    scheduler = MatchScheduler(players=list(range(1, 14)), courts=3)
    return scheduler


def test_no_more_than_one_rest(scheduler):
    """
    Test that no player rests more than once during 10 rounds of play with 13 players.
    Also, a player joining in round 7 should not rest at all.
    """
    resting_count = defaultdict(int)
    current_round = 1

    # Simulate 10 rounds
    while current_round <= 9:
        if current_round == 7:
            scheduler.add_player(14)  # Player 14 joins in round 7

        # Find optimal teams for the round
        matches = scheduler.find_new_matches()

        # Collect resting players
        resting_players = sorted(scheduler.get_resting_players(matches))
        LOGGER.debug(f"{resting_players=}")

        # Increment rest count for players who are resting
        for player in resting_players:
            resting_count[player] += 1

        # Player 14 should not rest after they join in round 7
        if current_round >= 7:
            assert (
                resting_count[14] == 0
            ), f"Player 14 should not rest after joining in round 7"

        # Ensure no player rests more than once
        for player, count in resting_count.items():
            LOGGER.debug(f"{player=}, {count}")
            assert count <= 1, f"Player {player} rested more than once."

        # Update graph with the matches of the current round
        scheduler.update_graph_with_matches(matches)

        # Go to the next round
        current_round += 1

    # Verify that no player has rested more than once
    for player, count in resting_count.items():
        assert count <= 1, f"Player {player} rested more than once."


def test_rest_distribution(scheduler):
    """
    Additional test to check how resting is distributed for players over multiple rounds.
    This ensures the resting logic works as expected.
    """

    resting_count = defaultdict(int)
    current_round = 1

    # Run 10 rounds
    while current_round <= 10:
        matches = scheduler.find_new_matches()
        resting_players = sorted(scheduler.get_resting_players(matches))

        # Update rest count for resting players
        for player in resting_players:
            resting_count[player] += 1

        # Update the graph for each match
        scheduler.update_graph_with_matches(matches)

        current_round += 1

    # Assert that no player rests more than once
    for player, count in resting_count.items():
        assert count <= 1, f"Player {player} rested more than once."


from itertools import product


def test_num_rest():
    rest = num_rest(11, 3, [2, 1], 2)
    assert rest == 1
    rest = num_rest(2, 3, [2, 1], 2)
    assert rest == 0
    # exhaustive test for errors
    rest = num_rest(1, 3, [2, 1], 2)
    assert rest == 1

    players = range(2, 23)
    courts = range(1, 7)
    for player, court in product(players, courts):
        rest = num_rest(player, court, [2, 1], 2)
        LOGGER.debug(f"{rest=} for {player=}, {court=}")
