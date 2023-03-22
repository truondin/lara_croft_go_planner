from queue import PriorityQueue
from typing import List

from model.Agent import Action
from model.Game import Game
import sys, copy

from model.Tiles import CrackedTile, AbstractTile, MovingTile


def is_cracked_tile_dead_end(tile: CrackedTile):
    return tile.is_cracked and tile.trap_on_tile is None


class Solver:
    def __init__(self):
        self._state_id = 0

        self.have_used_lever = False
        self.cracked_tiles_pos = []
        self.forbidden_pos = []

    def heuristic(self, state: Game):
        goal_pos: AbstractTile = state.goal
        curr_pos: AbstractTile = state.agent.current_position

        g_x, g_y, g_z = goal_pos.x, goal_pos.y, goal_pos.z
        x, y, z = curr_pos.x, curr_pos.y, curr_pos.z

        dx = abs(x - g_x)
        dy = abs(y - g_y)
        dz = abs(z - g_z)
        return 1 * (dx + dy + dz)

    def search(self, game: Game) -> List[Action]:
        state_id = copy.deepcopy(self._state_id)
        states = {state_id: game}

        queue = PriorityQueue()
        s_h = self.heuristic(game)
        queue.put((0 + s_h, s_h, state_id, []))
        closed = []

        while not queue.empty():
            f, h, curr_id, actions = queue.get()
            g = f - h

            curr = states.get(curr_id)
            closed.append(curr)

            if curr.agent.current_position.is_goal:
                return actions

            for action, neighbor in self.get_neighbor_state(curr):
                self._state_id += 1
                neighbor_id = self._state_id
                states.update({neighbor_id: neighbor})

                if neighbor in closed:
                    continue

                neighbor_h = self.heuristic(neighbor)
                neighbor_g = g + 1
                neighbor_f = neighbor_h + neighbor_g
                neighbor_actions = actions.copy()
                neighbor_actions.append(action)

                queue.put((neighbor_f, neighbor_h, neighbor_id, neighbor_actions))

        return None

    def get_neighbor_state(self, state: Game):
        neighbor_states = []
        self.set_forbidden_pos(state)

        for action in Action:
            n = state.clone()
            if not self.is_forbidden_action(action, n) and n.agent.apply_action(action, n.traps):
                # n.agent.apply_action(action, n.traps)
                neighbor_states.append((action, n))

                n_tile = n.agent.current_position

                if action == Action.USE_LEVER:
                    self.have_used_lever = True

                if isinstance(n_tile, CrackedTile) and is_cracked_tile_dead_end(n_tile):
                    self.cracked_tiles_pos.append((n.agent.current_position.x, n.agent.current_position.y, n.agent.current_position.z))

        return neighbor_states

    def set_forbidden_pos(self, state: Game):
        self.forbidden_pos = copy.deepcopy(self.cracked_tiles_pos)

        for tile in state.tiles.values():
            if tile.is_guarded:
                self.forbidden_pos.append((tile.x, tile.y, tile.z))

    def is_forbidden_action(self, action: Action, state: Game) -> bool:
        if action == Action.MOVE_UP:
            if self.have_used_lever:
                self.have_used_lever = False
            return (state.agent.current_position.x, state.agent.current_position.y + 1) in self.forbidden_pos
        elif action == Action.MOVE_DOWN:
            if self.have_used_lever:
                self.have_used_lever = False
            return (state.agent.current_position.x, state.agent.current_position.y - 1) in self.forbidden_pos
        elif action == Action.MOVE_RIGHT:
            if self.have_used_lever:
                self.have_used_lever = False
            return (state.agent.current_position.x + 1, state.agent.current_position.y) in self.forbidden_pos
        elif action == Action.MOVE_LEFT:
            if self.have_used_lever:
                self.have_used_lever = False
            return (state.agent.current_position.x - 1, state.agent.current_position.y) in self.forbidden_pos
        elif action == Action.USE_LEVER:
            return self.have_used_lever

        return False


def main():
    game = Game()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        game.load_game(path)

        solver = Solver()
        plan = solver.search(game)
        print(plan)

    else:
        print("Error: Missing argument of path to json representation of level to solve")
        # game.play("./levels/level1.json")
    pass


if __name__ == '__main__':
    main()

