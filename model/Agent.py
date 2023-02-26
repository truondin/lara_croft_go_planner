from model.Objects import Object
from enum import Enum


class Action(Enum):
    MOVE_UP = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4
    PICKUP_ITEM = 5
    USE_ITEM = 6
    ATTACK_CLOSE = 7
    USE_LEVER = 8


class Agent(Object):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.carried_item = None

    def set_position(self, tile):
        if tile.is_empty():
            self.current_position = tile
            tile.set_agent(self)

    def move_to_position(self, tile):
        self.current_position.remove_on_tile()
        tile.agent_move_on(self)

    @staticmethod
    def use_lever(lever):
        lever.use_lever()

    def apply_action(self, action: Action):
        if action == Action.MOVE_UP and self.current_position.up is not None:
            self.move_to_position(self.current_position.up)
        elif action == Action.MOVE_DOWN and self.current_position.down is not None:
            self.move_to_position(self.current_position.down)
        elif action == Action.MOVE_LEFT and self.current_position.left is not None:
            self.move_to_position(self.current_position.left)
        elif action == Action.MOVE_RIGHT and self.current_position.right is not None:
            self.move_to_position(self.current_position.right)
        elif action == Action.USE_LEVER and self.current_position.contains_lever():
            self.use_lever(self.current_position.lever)

    def __str__(self):
        return "Agent"
