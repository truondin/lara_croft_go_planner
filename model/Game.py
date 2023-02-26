from model.Agent import Agent, Action
from model.Tiles import Tile, CrackedTile, MovingTile
from model.Objects import Lever


class Game:
    def __init__(self):
        self.start = None
        self.agent = None

        tile1 = Tile()
        tile2 = Tile()
        tile3 = MovingTile(False)
        tile4 = Tile()
        tile5 = CrackedTile()
        tile6 = Tile()

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

        print(self.agent.current_position)
        print("move down")
        self.agent.apply_action(Action.MOVE_DOWN)
        print(self.agent.current_position)

        print("lever activate")
        self.agent.apply_action(Action.USE_LEVER)

        print("move down")
        self.agent.apply_action(Action.MOVE_DOWN)
        print(self.agent.current_position)

        print("move down")
        self.agent.apply_action(Action.MOVE_DOWN)
        print(self.agent.current_position)

        print("move down")
        self.agent.apply_action(Action.MOVE_DOWN)
        print(self.agent.current_position)

        print("move down")
        self.agent.apply_action(Action.MOVE_DOWN)
        print(self.agent.current_position)

        print("move up")
        self.agent.apply_action(Action.MOVE_UP)
        print(self.agent.current_position)
        return

