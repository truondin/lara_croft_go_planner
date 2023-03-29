import unittest, random

from main import Solver
from model.Agent import Agent, Action
from model.Game import Game
from model.Objects import Lever
from model.Tiles import Tile


def generate_goal_curr_agent_tiles():
    goal = Tile(1)
    current = Tile(2)
    agent = Agent()

    goal.set_coords(random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10))
    current.set_coords(random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10))
    agent.set_position(current)
    tiles = {1: goal, 2: current}

    return goal, current, agent, tiles


class SolverTest(unittest.TestCase):

    def test_heuristic(self):
        test_solver = Solver()
        goal, current, agent, tiles = generate_goal_curr_agent_tiles()

        state = Game()
        state.tiles = tiles
        state.agent = agent
        state.goal = goal

        result = 1 * (abs(current.x - goal.x) + abs(current.y - goal.y) + abs(current.z - goal.z))
        self.assertEqual(test_solver.heuristic(state), result, "Test heuristic with random numbers")  # add assertion here

    def test_get_neighbor_state_non_states(self):
        test_solver = Solver()
        goal, current, agent, tiles = generate_goal_curr_agent_tiles()

        state = Game()
        state.tiles = tiles
        state.agent = agent

        self.assertEqual(test_solver.get_neighbor_state(state), [], "Test get_neighbor_state should be empty")

    def test_get_neighbor_state_get_states(self):
        test_solver = Solver()
        goal, current, agent, tiles = generate_goal_curr_agent_tiles()

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
        goal, current, agent, tiles = generate_goal_curr_agent_tiles()

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


if __name__ == '__main__':
    unittest.main()
