# Note, most initial contents were generated by ChatGPT
import random
from typing import List, Optional, Tuple

import networkx as nx

# Descriptive Type Aliases
Player = int
Team = List[Player]
Match = Tuple[Team, Team]

class BadmintonSchedulerGraph:
    def __init__(self, players: List[Player], courts: int = 3) -> None:
        """
        Initialize the scheduler with players and a fixed number of courts.

        :param players: List of player IDs (integers).
        :param courts: Number of courts available for matches, defaults to 3.
        """
        self.players: List[Player] = players
        self.active_players: List[Player] = players.copy()  # Active players who are currently playing
        self.inactive_players: List[Player] = []  # Players sitting out
        self.courts: int = courts
        self.graph: nx.Graph = nx.Graph()  # Graph to track who has played against whom
        self.graph.add_nodes_from(players)  # Add players as nodes

    def generate_initial_matches(self) -> List[Match]:
        """
        Generate the initial set of matches.

        :return: A list of matches where each match is a tuple of two teams (pairs or singles).
        """
        random.shuffle(self.active_players)
        matches: List[Match] = []
        i: int = 0

        # Generate doubles matches
        while i + 3 < len(self.active_players) and len(matches) < self.courts:
            pair1: Team = self.active_players[i:i+2]
            pair2: Team = self.active_players[i+2:i+4]
            matches.append((pair1, pair2))
            i += 4

        # If courts are available and not enough players for doubles, add a singles match
        if len(matches) < self.courts and len(self.active_players) - i >= 2:
            matches.append(([self.active_players[i]], [self.active_players[i+1]]))

        return matches

    def update_graph_with_matches(self, matches: List[Match]) -> None:
        """
        Update the internal graph with match data.

        :param matches: List of matches played in this round.
        """
        for match in matches:
            pair1, pair2 = match

            # Update teammate and opponent edges
            self.add_teammate_edges(pair1)
            self.add_teammate_edges(pair2)
            self.add_opponent_edges(pair1, pair2)

    def add_teammate_edges(self, team: Team) -> None:
        """
        Update or add teammate edges between players in a team.

        :param team: List of players in a team (can be one or more players).
        """
        # Handle singles as a special case (player is their own teammate)
        if len(team) == 1:
            player: Player = team[0]
            if self.graph.has_edge(player, player):
                self.graph[player][player]['teammate_weight'] += 1
            else:
                self.graph.add_edge(player, player, weight=0, teammate_weight=1)
        else:
            # Add edges between teammates in doubles
            for p1 in team:
                for p2 in team:
                    if p1 != p2:
                        if self.graph.has_edge(p1, p2):
                            self.graph[p1][p2]['teammate_weight'] += 1
                        else:
                            self.graph.add_edge(p1, p2, weight=0, teammate_weight=1)

    def add_opponent_edges(self, pair1: Team, pair2: Team) -> None:
        """
        Update or add opponent edges between two teams.

        :param pair1: First team (list of player IDs).
        :param pair2: Second team (list of player IDs).
        """
        for p1 in pair1:
            for p2 in pair2:
                if self.graph.has_edge(p1, p2):
                    self.graph[p1][p2]['weight'] += 1
                else:
                    self.graph.add_edge(p1, p2, weight=1, teammate_weight=0)

    def find_new_matches(self) -> List[Match]:
        """
        Find new matches for the current round based on the graph state.

        :return: A list of matches where each match is a tuple of two teams (pairs or singles).
        """
        random.shuffle(self.active_players)
        matches: List[Match] = []

        # Create doubles matches first
        i: int = 0
        while i + 3 < len(self.active_players) and len(matches) < self.courts:
            pair1: Team = [self.active_players[i], self.active_players[i+1]]
            pair2: Team = [self.active_players[i+2], self.active_players[i+3]]
            matches.append((pair1, pair2))
            i += 4

        # If courts are available, add a singles match
        if len(matches) < self.courts and len(self.active_players) - i >= 2:
            matches.append(([self.active_players[i]], [self.active_players[i+1]]))

        matches.sort(key=self.match_cost)
        return matches[:self.courts]

    def match_cost(self, match: Match) -> int:
        """
        Calculate the cost of a match based on the number of times players have faced each other.

        :param match: A tuple representing a match with two teams.
        :return: The total cost of the match (sum of opponent and teammate costs).
        """
        pair1, pair2 = match
        cost: int = 0

        # Calculate opponent cost
        for p1 in pair1:
            for p2 in pair2:
                if self.graph.has_edge(p1, p2):
                    cost += self.graph[p1][p2]['weight']

        # Add teammate cost
        cost += self.teammate_cost(pair1) + self.teammate_cost(pair2)
        return cost

    def teammate_cost(self, team: Team) -> int:
        """
        Calculate the cost for teammates playing together.

        :param team: List of player IDs in a team.
        :return: The total teammate cost.
        """
        cost: int = 0
        if len(team) == 1:  # Handle singles match as a special case
            player: Player = team[0]
            if self.graph.has_edge(player, player):
                cost += self.graph[player][player]['teammate_weight']
        else:
            for p1 in team:
                for p2 in team:
                    if p1 != p2 and self.graph.has_edge(p1, p2):
                        cost += self.graph[p1][p2]['teammate_weight']
        return cost

    def toggle_player(self, player: Player) -> None:
        """
        Toggle the player's active/inactive state.

        :param player: Player ID to toggle.
        """
        if player in self.active_players:
            self.active_players.remove(player)
            self.inactive_players.append(player)
            print(f"Player {player} is now inactive.")
        elif player in self.inactive_players:
            self.inactive_players.remove(player)
            self.active_players.append(player)
            print(f"Player {player} is now active again.")
        else:
            print(f"Player {player} is not part of the session.")

    def add_player(self, new_player: Player) -> None:
        """
        Add a new player to the session.

        :param new_player: New player ID to add.
        """
        self.players.append(new_player)
        self.active_players.append(new_player)
        self.graph.add_node(new_player)
        print(f"Player {new_player} has been added.")

    def drop_players(self, dropped_indices: List[int]) -> None:
        """
        Drop players from the session based on their indices.

        :param dropped_indices: List of indices representing the players to drop.
        """
        dropped_players = [self.active_players[i] for i in dropped_indices]
        for player in dropped_players:
            self.toggle_player(player)

    def get_resting_players(self, matches: List[Match]) -> List[Player]:
        """
        Get a list of players who are not playing in the current round.

        :param matches: List of current matches.
        :return: List of resting player IDs.
        """
        matched_players = {p for match in matches for pair in match for p in pair}
        return [p for p in self.active_players if p not in matched_players]

    def print_current_status(self) -> None:
        """
        Print the current status of active, resting, and inactive players.
        """
        total_players: int = len(self.players)
        print(f"Active players ({len(self.active_players)}/{total_players}): {sorted(self.active_players)}")
        print(f"Inactive players ({len(self.inactive_players)}/{total_players}): {sorted(self.inactive_players)}")

# Utility function to prompt user for player actions (toggle or add players)
def prompt_player_actions(scheduler: BadmintonSchedulerGraph) -> None:
    """
    Prompt the user for actions to toggle or add players.
    
    :param scheduler: The BadmintonSchedulerGraph instance.
    """
    scheduler.print_current_status()

    action_input = input("Enter player numbers (separated by spaces) to toggle or add (new numbers will be added): ")
    actions = [int(num) for num in action_input.split() if num.isdigit()]

    for player in actions:
        if player in scheduler.players:
            scheduler.toggle_player(player)
        else:
            scheduler.add_player(player)
# Main loop to run the scheduling
def main():
    initial_player_count = int(input("Enter the number of initial players: "))
    players = list(range(1, initial_player_count + 1))  # Player IDs start from 1
    courts = 3
    scheduler = BadmintonSchedulerGraph(players, courts)

    round_number = 1
    while len(sorted(scheduler.active_players)) > 3:  # Need at least 4 active players to continue matches
        print(f"\n--- Round {round_number} ---")

        # Generate initial matches or new matches based on remaining players
        if round_number == 1:
            matches = scheduler.generate_initial_matches()
        else:
            matches = scheduler.find_new_matches()

        print(f"Round {round_number} matches: {matches}")

        # Update the graph with new matches
        scheduler.update_graph_with_matches(matches)

        # Show resting players
        resting_players = sorted(scheduler.get_resting_players(matches))  # Sorting resting players
        if resting_players:
            print(f"Resting players ({len(resting_players)}): {resting_players}")
        else:
            print("No players are resting this round.")

        # Prompt for player actions (toggle or add players)
        prompt_player_actions(scheduler)

        # Update player list and courts for the next round
        round_number += 1

if __name__ == "__main__":
    main()
