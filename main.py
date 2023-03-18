from typing import List

from model.Agent import Action
from model.Game import Game
import sys, copy

from model.Tiles import CrackedTile


def is_cracked_tile_dead_end(tile: CrackedTile):
    return tile.is_cracked and tile.trap_on_tile is None


class Solver:
    def __init__(self):
        self.cracked_tiles_pos = []
        self.forbidden_pos = []

    def heuristic(self):
        pass

    def search(self) -> List[Action]:
        pass

    def get_neighbor_state(self, state: Game):
        neighbor_states = []
        self.set_forbidden_pos(state)

        for action in Action:
            n = state.clone()
            if not self.is_forbidden_action(action, n):
                n.agent.apply_action(action)
                neighbor_states.append(n)

                n_tile = n.agent.current_position
                if isinstance(n_tile, CrackedTile) and is_cracked_tile_dead_end(n_tile):
                    self.cracked_tiles_pos.append((n.agent.current_position.x, n.agent.current_position.y))

        return neighbor_states

    def set_forbidden_pos(self, state: Game):
        self.forbidden_pos = copy.deepcopy(self.cracked_tiles_pos)

        for tile in state.tiles.values():
            if tile.is_guarded:
                self.forbidden_pos.append((tile.x, tile.y))

    def is_forbidden_action(self, action: Action, state: Game) -> bool:
        if action == Action.MOVE_UP:
            return (state.agent.current_position.x, state.agent.current_position.y + 1) in self.forbidden_pos
        elif action == Action.MOVE_DOWN:
            return (state.agent.current_position.x, state.agent.current_position.y - 1) in self.forbidden_pos
        elif action == Action.MOVE_RIGHT:
            return (state.agent.current_position.x + 1, state.agent.current_position.y) in self.forbidden_pos
        elif action == Action.MOVE_LEFT:
            return (state.agent.current_position.x - 1, state.agent.current_position.y) in self.forbidden_pos

        return False


def main():
    game = Game()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        game.load_game(path)

        solver = Solver()
        solver.set_forbidden_pos(game)

    else:
        print("Error: Missing argument of path to json representation of level to solve")
        # game.play("./levels/level1.json")
    pass


if __name__ == '__main__':
    main()

