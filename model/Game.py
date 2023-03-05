from model.Agent import Agent, Action
from model.Tiles import Tile, CrackedTile, MovingTile
from model.Objects import Lever
from model.Trap import Trap, SawStrategy, TrapMovingAction


class Game:
    def __init__(self):
        self.start = None
        self.agent = None
        self.traps = []

    def test2(self):
        tile1 = Tile(1)
        tile2 = Tile(2)
        tile3 = Tile(3)
        tile4 = Tile(4)
        tile5 = Tile(5)
        tile6 = Tile(6)

        agent = Agent(self)
        saw = Trap(False)

        saw.set_position(tile3)
        saw.set_trap(tile4, SawStrategy([TrapMovingAction.DOWN, TrapMovingAction.DOWN, TrapMovingAction.UP, TrapMovingAction.UP, TrapMovingAction.UP, TrapMovingAction.DOWN]))

        self.traps.append(saw)

        tile1.set_path(None, None, None, tile2)
        tile2.set_path(None, None, tile1, tile3)
        tile3.set_path(None, None, tile2, tile4)
        tile4.set_path(None, None, tile3, tile5)
        tile5.set_path(None, None, tile4, tile6)
        tile6.set_path(None, None, tile5, None)

        agent.set_position(tile1)

        self.start = tile1
        self.agent = agent

    def test1(self):
        tile1 = Tile(1)
        tile2 = Tile(2)
        tile3 = MovingTile(3, False)
        tile4 = Tile(4)
        tile5 = CrackedTile(5)
        tile6 = Tile(6)

        # drop = Tile('7')
        lever = Lever()
        lever.assign_tile(tile3)
        lever.set_position(tile2)

        agent = Agent(self)

        tile4.set_as_goal()

        tile1.set_path(None, None, None, tile2)
        tile2.set_path(None, None, None, tile3)
        tile3.set_path(None, None, None, tile4)
        tile4.set_path(None, None, None, tile5)
        tile5.set_path(None, None, None, tile6)
        tile6.set_path(None, None, tile5, None)
        # tile5.set_drop_on_tile(drop)
        agent.set_position(tile1)

        self.start = tile1
        self.agent = agent

    def play(self):
        self.test2()

        # print(self.traps[0].current_position)
        # self.agent.apply_action(Action.MOVE_DOWN, self.traps)
        # print(self.traps[0].current_position)
        # self.agent.apply_action(Action.MOVE_DOWN, self.traps)
        # print(self.traps[0].current_position)
        # self.agent.apply_action(Action.MOVE_DOWN, self.traps)
        # print(self.traps[0].current_position)

        for i in range(3):
            print("trap pos:" + str(self.traps[0].current_position))
            print("guarded tile pos:" + str(self.traps[0].guarded_tile))
            print(self.traps[0].trap_strategy)
            print("agent pos: " + str(self.agent.current_position))
            print("")
            self.agent.apply_action(Action.MOVE_DOWN, self.traps)

        for i in range(4):
            print("trap pos:" + str(self.traps[0].current_position))
            print("guarded tile pos:" + str(self.traps[0].guarded_tile))
            print(self.traps[0].trap_strategy)
            print("agent pos: " + str(self.agent.current_position))
            print("")
            self.agent.apply_action(Action.MOVE_UP, self.traps)

        return

