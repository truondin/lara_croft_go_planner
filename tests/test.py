import unittest
import random

from main import Solver
from model.Agent import Agent, Action
from model.Game import Game
from model.Objects import Lever, ItemType, Item
from model.Tiles import Tile, DeadEndTile
from model.Trap import Trap, SnakeStrategy, SawStrategy, TrapMovingAction, SpiderStrategy, LizardStrategy


class SolverTest(unittest.TestCase):

    @staticmethod
    def generate_goal_curr_agent_tiles():
        goal = Tile(1)
        current = Tile(2)
        agent = Agent()

        goal.set_coords(random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10))
        current.set_coords(random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10))
        agent.set_position(current)
        tiles = {1: goal, 2: current}

        return goal, current, agent, tiles

    def test_heuristic(self):
        test_solver = Solver()
        goal, current, agent, tiles = self.generate_goal_curr_agent_tiles()

        state = Game()
        state.tiles = tiles
        state.agent = agent
        state.goal = goal

        result = 1 * (abs(current.x - goal.x) + abs(current.y - goal.y) + abs(current.z - goal.z))
        self.assertEqual(test_solver.heuristic(state), result, "Test heuristic with random numbers")  # add assertion here

    def test_get_neighbor_state_non_states(self):
        test_solver = Solver()
        goal, current, agent, tiles = self.generate_goal_curr_agent_tiles()

        state = Game()
        state.tiles = tiles
        state.agent = agent

        self.assertEqual(test_solver.get_neighbor_state(state), [], "Test get_neighbor_state should be empty")

    def test_get_neighbor_state_get_states(self):
        test_solver = Solver()
        goal, current, agent, tiles = self.generate_goal_curr_agent_tiles()

        t1 = Tile(3)
        t2 = Tile(4)
        lever = Lever()

        lever.set_position(current)
        current.set_path(t1, None, t2, None)
        state = Game()
        state.tiles = tiles
        state.agent = agent

        self.assertEqual(len(test_solver.get_neighbor_state(state)), 3, "Test get_neighbor_state should get states")

    def test_is_forbidden_action(self):
        test_solver = Solver()
        goal, current, agent, tiles = self.generate_goal_curr_agent_tiles()

        state = Game()
        state.tiles = tiles
        state.agent = agent
        state.goal = goal

        test_solver.forbidden_pos.append((current.x, current.y + 1, current.z))
        test_solver.forbidden_pos.append((current.x + 1, current.y, current.z))

        self.assertEqual(test_solver.is_forbidden_action(Action.MOVE_UP, state), True)
        self.assertEqual(test_solver.is_forbidden_action(Action.MOVE_RIGHT, state), True)
        self.assertEqual(test_solver.is_forbidden_action(Action.MOVE_DOWN, state), False)
        self.assertEqual(test_solver.is_forbidden_action(Action.MOVE_LEFT, state), False)
        self.assertEqual(test_solver.is_forbidden_action(Action.USE_LEVER, state), False)
        self.assertEqual(test_solver.is_forbidden_action(Action.USE_ITEM, state), False)


class TrapTest(unittest.TestCase):

    def generate_game_state(self):
        game = Game()
        tiles = {}
        for i in range(0, 11):
            tiles.update({i: Tile(i)})

        tiles[0].set_path(None, tiles[1], None, None)
        tiles[1].set_path(tiles[0], tiles[2], tiles[5], tiles[8])
        tiles[2].set_path(tiles[1], tiles[3], tiles[6], tiles[9])
        tiles[3].set_path(tiles[2], tiles[4], tiles[7], tiles[10])
        tiles[4].set_path(tiles[3], None, None, None)
        tiles[5].set_path(None, tiles[6], None, tiles[1])
        tiles[6].set_path(tiles[5], tiles[7], None, tiles[2])
        tiles[7].set_path(tiles[6], None, None, tiles[3])
        tiles[8].set_path(None, tiles[9], tiles[1], None)
        tiles[9].set_path(tiles[8], tiles[10], tiles[2], None)
        tiles[10].set_path(tiles[9], None, tiles[3], None)
        tiles[10].set_as_goal()

        agent = Agent()
        agent.set_position(tiles[0])

        game.tiles = tiles
        game.agent = agent
        game.goal = tiles[10]
        self.game_state = game

    def test_kill_trap(self):
        self.generate_game_state()

        snake_trap = Trap(True)
        snake_trap.set_position(self.game_state.tiles[3])
        snake_trap.set_trap(self.game_state.tiles[4], SnakeStrategy())
        self.game_state.traps.append(snake_trap)

        agent = self.game_state.agent
        for i in range(0, 3):
            agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)

        self.assertEqual(agent.current_position, self.game_state.tiles[3], "Agent should be on tile 3")
        self.assertEqual(self.game_state.tiles[4].is_guarded, False, "Tile 4 should not be guarded")
        self.assertEqual(snake_trap.current_position, None, "Trap is not in game")
        self.assertEqual(snake_trap.guarded_tile, None, "Trap does not guard tile")

    def test_get_killed_by_trap(self):
        self.generate_game_state()

        snake_trap = Trap(True)
        snake_trap.set_position(self.game_state.tiles[3])
        snake_trap.set_trap(self.game_state.tiles[2], SnakeStrategy())
        self.game_state.traps.append(snake_trap)

        agent = self.game_state.agent
        for i in range(0, 3):
            agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)

        self.assertEqual(snake_trap.current_position, self.game_state.tiles[3], "Trap is in game")
        self.assertEqual(snake_trap.guarded_tile, self.game_state.tiles[2], "Trap does guard tile")
        self.assertEqual(isinstance(agent.current_position, DeadEndTile), True, "Agent is in dead-end")
        self.assertEqual(self.game_state.tiles[3].contains_trap(), True, "Tile contains trap")
        self.assertEqual(self.game_state.tiles[2].is_guarded, True, "Tile is guarded")

    def test_saw_and_spider_move(self):
        self.generate_game_state()
        trap_move_seq = [TrapMovingAction.DOWN, TrapMovingAction.UP, TrapMovingAction.UP, TrapMovingAction.DOWN]

        saw_trap = Trap(False)
        saw_trap.set_position(self.game_state.tiles[7])
        saw_trap.set_trap(self.game_state.tiles[3], SawStrategy(trap_move_seq))
        self.game_state.traps.append(saw_trap)

        spider_trap = Trap(True)
        spider_trap.set_position(self.game_state.tiles[6])
        spider_trap.set_trap(self.game_state.tiles[2], SpiderStrategy(trap_move_seq))
        self.game_state.traps.append(spider_trap)

        agent = self.game_state.agent

        agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)

        self.assertEqual(self.game_state.tiles[7].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[6].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[3].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[2].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[9].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[10].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[9].is_guarded, True)
        self.assertEqual(self.game_state.tiles[10].is_guarded, True)

        agent.apply_action(Action.MOVE_LEFT, self.game_state.traps)

        self.assertEqual(self.game_state.tiles[3].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[2].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[9].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[10].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[3].is_guarded, True)
        self.assertEqual(self.game_state.tiles[2].is_guarded, True)

        agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)

        self.assertEqual(self.game_state.tiles[9].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[10].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[3].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[2].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[7].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[6].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[7].is_guarded, True)
        self.assertEqual(self.game_state.tiles[6].is_guarded, True)

        agent.apply_action(Action.MOVE_LEFT, self.game_state.traps)

        self.assertEqual(self.game_state.tiles[3].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[2].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[7].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[6].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[3].is_guarded, True)
        self.assertEqual(self.game_state.tiles[2].is_guarded, True)

        agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)

        self.assertEqual(self.game_state.tiles[7].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[6].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[3].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[2].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[9].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[10].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[9].is_guarded, True)
        self.assertEqual(self.game_state.tiles[10].is_guarded, True)

    def test_kill_moving_trap(self):
        self.generate_game_state()
        trap_move_seq = [TrapMovingAction.DOWN, TrapMovingAction.UP, TrapMovingAction.UP, TrapMovingAction.DOWN]

        spider_trap = Trap(True)
        spider_trap.set_position(self.game_state.tiles[6])
        spider_trap.set_trap(self.game_state.tiles[2], SpiderStrategy(trap_move_seq))
        self.game_state.traps.append(spider_trap)

        agent = self.game_state.agent

        for i in range(0, 2):
            agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)

        self.assertEqual(agent.current_position, self.game_state.tiles[2], "Agent should be on tile 2")
        self.assertEqual(spider_trap.current_position, None, "Trap does not have position")
        self.assertEqual(spider_trap.guarded_tile, None, "Trap does not guards position")
        for tile in self.game_state.tiles.values():
            self.assertEqual(tile.contains_trap(), False, "Tile " + str(tile.id) + "does not contain trap")
            self.assertEqual(tile.is_guarded, False, "Tile " + str(tile.id) + "is not guarded")

    def test_lizard_movement(self):
        self.generate_game_state()

        lizard_trap = Trap(True)
        lizard_trap.set_position(self.game_state.tiles[3])
        lizard_trap.set_trap(self.game_state.tiles[2], LizardStrategy(self.game_state.tiles[1], self.game_state.agent))
        self.game_state.traps.append(lizard_trap)

        agent = self.game_state.agent

        self.assertEqual(lizard_trap.trap_strategy.is_active, False)

        agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)

        self.assertEqual(lizard_trap.trap_strategy.is_active, True)

        agent.apply_action(Action.MOVE_DOWN, self.game_state.traps)
        self.assertEqual(lizard_trap.current_position, self.game_state.tiles[2])
        self.assertEqual(lizard_trap.guarded_tile, self.game_state.tiles[1])
        self.assertEqual(self.game_state.tiles[3].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[2].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[1].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[1].is_guarded, True)
        self.assertEqual(lizard_trap.trap_strategy.next_tile, self.game_state.tiles[8])

        agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)
        self.assertEqual(lizard_trap.current_position, self.game_state.tiles[1])
        self.assertEqual(lizard_trap.guarded_tile, self.game_state.tiles[8])
        self.assertEqual(self.game_state.tiles[2].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[1].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[8].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[8].is_guarded, True)
        self.assertEqual(lizard_trap.trap_strategy.next_tile, self.game_state.tiles[9])

        agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)
        self.assertEqual(lizard_trap.current_position, self.game_state.tiles[8])
        self.assertEqual(lizard_trap.guarded_tile, self.game_state.tiles[9])
        self.assertEqual(self.game_state.tiles[1].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[8].contains_trap(), True)
        self.assertEqual(self.game_state.tiles[9].contains_trap(), False)
        self.assertEqual(self.game_state.tiles[9].is_guarded, True)
        self.assertEqual(lizard_trap.trap_strategy.next_tile, self.game_state.tiles[10])

    def test_spear_kill(self):
        self.generate_game_state()

        lizard_trap = Trap(True)
        lizard_trap.set_position(self.game_state.tiles[3])
        lizard_trap.set_trap(self.game_state.tiles[2],
                             LizardStrategy(self.game_state.tiles[1], self.game_state.agent))
        self.game_state.traps.append(lizard_trap)

        spear = Item(ItemType.SPEAR)
        spear.set_position(self.game_state.tiles[1])
        self.game_state.tiles[1].add_air_connection(self.game_state.tiles[3])
        agent = self.game_state.agent

        self.assertEqual(agent.carries_item(), False)
        agent.apply_action(Action.MOVE_RIGHT, self.game_state.traps)
        agent.apply_action(Action.USE_ITEM, self.game_state.traps)

        self.assertEqual(lizard_trap.current_position, None)
        self.assertEqual(lizard_trap.guarded_tile, None)
        for tile in self.game_state.tiles.values():
            self.assertEqual(tile.contains_trap(), False)
            self.assertEqual(tile.is_guarded, False)


class AgentTest(unittest.TestCase):

    def test_move_left(self):
        start = Tile(1)
        left = Tile(2)

        start.set_path(left, None, None, None)
        left.set_path(None, start, None, None)

        agent = Agent()
        agent.set_position(start)

        self.assertEqual(agent.current_position, start)
        self.assertEqual(agent.apply_action(Action.MOVE_LEFT, []), True)
        self.assertEqual(agent.current_position, left)
        self.assertEqual(start.on_tile, None)
        self.assertEqual(left.on_tile, agent)

    def test_move_right(self):
        start = Tile(1)
        right = Tile(2)

        start.set_path(None, right, None, None)
        right.set_path(start, None, None, None)

        agent = Agent()
        agent.set_position(start)

        self.assertEqual(agent.current_position, start)
        self.assertEqual(agent.apply_action(Action.MOVE_RIGHT, []), True)
        self.assertEqual(agent.current_position, right)
        self.assertEqual(start.on_tile, None)
        self.assertEqual(right.on_tile, agent)

    def test_move_up(self):
        start = Tile(1)
        up = Tile(2)

        start.set_path(None, None, up, None)
        up.set_path(None, None, None, start)

        agent = Agent()
        agent.set_position(start)

        self.assertEqual(agent.current_position, start)
        self.assertEqual(agent.apply_action(Action.MOVE_UP, []), True)
        self.assertEqual(agent.current_position, up)
        self.assertEqual(start.on_tile, None)
        self.assertEqual(up.on_tile, agent)

    def test_move_down(self):
        start = Tile(1)
        down = Tile(2)

        start.set_path(None, None, None, down)
        down.set_path(None, None, start, None)

        agent = Agent()
        agent.set_position(start)

        self.assertEqual(agent.current_position, start)
        self.assertEqual(agent.apply_action(Action.MOVE_DOWN, []), True)
        self.assertEqual(agent.current_position, down)
        self.assertEqual(start.on_tile, None)
        self.assertEqual(down.on_tile, agent)


if __name__ == '__main__':
    unittest.main()
