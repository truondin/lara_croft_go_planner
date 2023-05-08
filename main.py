from queue import PriorityQueue
from typing import List, Tuple

from model.Agent import Action
from model.Game import Game
from model.Tiles import CrackedTile, AbstractTile, MovingTile
import sys
import copy
import time

from model.Trap import SawStrategy


class Solver:
    def __init__(self):
        self._state_id = 0

        self.forbidden_pos = []

    @staticmethod
    def heuristic(state: Game):
        goal_pos: AbstractTile = state.goal
        curr_pos: AbstractTile = state.agent.current_position

        g_x, g_y, g_z = goal_pos.x, goal_pos.y, goal_pos.z
        x, y, z = curr_pos.x, curr_pos.y, curr_pos.z

        dx = abs(x - g_x)
        dy = abs(y - g_y)
        dz = abs(z - g_z)
        return 1 * (dx + dy + dz)

    def search(self, game: Game) -> Tuple[List[Action], int]:
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
                return actions, len(closed)

            prev_action = None
            if len(actions) != 0:
                prev_action = actions[-1]

            for action, neighbor in self.get_neighbor_state(curr, prev_action):
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
        return [], len(closed)

    def get_neighbor_state(self, state: Game, prev_action: Action):
        neighbor_states = []
        self.set_forbidden_pos(state)

        for action in Action:
            n = state.clone()
            if not self.is_forbidden_action(action, n, prev_action) and n.agent.apply_action(action, n.traps):
                neighbor_states.append((action, n))

        return neighbor_states

    def set_forbidden_pos(self, state: Game):
        self.forbidden_pos = []

        for tile in state.tiles.values():
            if isinstance(tile, CrackedTile) and tile.is_cracked_without_drop_tile():
                self.forbidden_pos.append((tile.x, tile.y, tile.z))
            if tile.trap_on_tile is not None:
                trap = tile.trap_on_tile
                if isinstance(trap.trap_strategy, SawStrategy):
                    self.forbidden_pos.append((tile.x, tile.y, tile.z))
                elif trap.attack_able and trap.guarded_tile is not None:
                    self.forbidden_pos.append((trap.guarded_tile.x, trap.guarded_tile.y, trap.guarded_tile.z))

    def is_forbidden_action(self, action: Action, state: Game, prev_action: Action) -> bool:
        x, y, z = state.agent.current_position.x, state.agent.current_position.y, state.agent.current_position.z
        if action == Action.MOVE_UP:
            return (x, y + 1, z) in self.forbidden_pos
        elif action == Action.MOVE_DOWN:
            return (x, y - 1, z) in self.forbidden_pos
        elif action == Action.MOVE_RIGHT:
            return (x + 1, y, z) in self.forbidden_pos
        elif action == Action.MOVE_LEFT:
            return (x - 1, y, z) in self.forbidden_pos
        elif action == Action.USE_LEVER:
            return prev_action == Action.USE_LEVER

        return False


def main():
    game = Game()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        game.play(path)

        solver = Solver()
        start = time.time()
        plan, expanded_states = solver.search(game)
        end = time.time()
        if len(plan) > 0:
            print("Number of expanded states: " + str(expanded_states))
            print("Solving time: " + str(end - start) + " seconds")
            print("Plan for solving level " + path + ": ")
            for ac in plan:
                print("\t" + str(ac))
        else:
            print("Could not solve the level")

    else:
        print("Error: Missing argument of path to json representation of level to solve")
        # game.play("./levels/level1.json")
    pass


if __name__ == '__main__':
    main()
