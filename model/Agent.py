from model.Objects import Object, Item
from model.Tiles import DeadEndTile, Tile
from model.Trap import Trap
from enum import Enum


class Action(Enum):
    MOVE_UP = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4
    USE_ITEM = 5
    USE_LEVER = 6


def apply_traps_action(traps: list[Trap]):
    for trap in traps:
        trap.trap_action()


class Agent(Object):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.item: Item = None

    def carries_item(self):
        return self.item is not None

    def set_position(self, tile):
        if tile.is_empty():
            self.current_position = tile
            tile.set_agent(self)

    def pickup_item(self, tile: Tile):
        self.item = tile.item
        self.item.pickup()
        tile.remove_item()

    def move_to_position(self, tile: Tile, traps: list[Trap]):
        self.current_position.remove_on_tile()

        if tile.is_guarded:
            dead_end = DeadEndTile()
            dead_end.agent_move_on(self)
        else:
            if tile.contains_trap() and tile.trap_on_tile.attack_able:
                trap = tile.trap_on_tile
                trap.trap_on_tile.kill()
                traps.remove(trap)
            if tile.contains_item() and not self.carries_item():
                self.pickup_item(tile)

            tile.agent_move_on(self)

        apply_traps_action(traps)

    @staticmethod
    def use_lever(lever):
        lever.use_lever()

    def use_item(self):
        self.item.use(self)
        #todo - implementovat
        self.item = None

    def apply_action(self, action: Action, traps: list[Trap]):
        if not isinstance(self.current_position, DeadEndTile):
            if action == Action.MOVE_UP and self.current_position.up is not None:
                self.move_to_position(self.current_position.up, traps)
            elif action == Action.MOVE_DOWN and self.current_position.down is not None:
                self.move_to_position(self.current_position.down, traps)
            elif action == Action.MOVE_LEFT and self.current_position.left is not None:
                self.move_to_position(self.current_position.left, traps)
            elif action == Action.MOVE_RIGHT and self.current_position.right is not None:
                self.move_to_position(self.current_position.right, traps)
            elif action == Action.USE_LEVER and self.current_position.contains_lever():
                self.use_lever(self.current_position.lever)
            elif action == Action.USE_ITEM and self.carries_item() and self.current_position.contains_air_connection():
                self.use_item()

    def __str__(self):
        add_str = ""
        if self.carries_item():
            add_str += " carried item: " + str(self.item.type)
        return "Agent" + add_str
