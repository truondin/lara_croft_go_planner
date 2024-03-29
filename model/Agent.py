import copy

from model.Objects import Object, Item, ItemType
from model.Tiles import DeadEndTile, Tile, MovingTile
from model.Trap import Trap
from enum import Enum, IntEnum


class Action(IntEnum):
    MOVE_UP = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4
    USE_ITEM = 5
    USE_LEVER = 6


def apply_traps_action(traps: list[Trap]):
    for trap in copy.copy(traps):
        if trap.current_position is None:
            traps.remove(trap)
            continue
        if trap.guarded_tile is not None and not trap.guarded_tile.is_guarded:
            trap.guarded_tile.is_guarded = True
        trap.trap_action()


class Agent(Object):
    def __init__(self):
        super().__init__()
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
        self.current_position.remove_agent()

        if tile.contains_trap() and tile.trap_on_tile.attack_able:
            trap = tile.trap_on_tile
            traps.remove(trap)
            trap.kill()
        if tile.contains_item() and not self.carries_item():
            self.pickup_item(tile)

        tile.agent_move_on(self)

        apply_traps_action(traps)

    @staticmethod
    def use_lever(lever):
        lever.use_lever()

    def use_item(self):
        return self.item.use(self)

    def apply_move_action(self, move_pos, traps: list[Trap]):
        if isinstance(move_pos, MovingTile):
            if move_pos.is_active:
                self.move_to_position(move_pos, traps)
                return True
            else:
                return False
        else:
            self.move_to_position(move_pos, traps)
            return True

    def apply_action(self, action: Action, traps: list[Trap]):
        if not isinstance(self.current_position, DeadEndTile):
            if action == Action.MOVE_UP and self.current_position.up is not None:
                return self.apply_move_action(self.current_position.up, traps)

            elif action == Action.MOVE_DOWN and self.current_position.down is not None:
                return self.apply_move_action(self.current_position.down, traps)

            elif action == Action.MOVE_LEFT and self.current_position.left is not None:
                return self.apply_move_action(self.current_position.left, traps)

            elif action == Action.MOVE_RIGHT and self.current_position.right is not None:
                return self.apply_move_action(self.current_position.right, traps)

            elif action == Action.USE_LEVER and self.current_position.contains_lever():
                self.use_lever(self.current_position.lever)
                return True
            elif action == Action.USE_ITEM and self.carries_item():
                return self.use_item()
        return False

    def __str__(self):
        add_str = ""
        if self.carries_item():
            add_str += " carried item: " + str(self.item.type)
        return "Agent" + add_str
    
    def __eq__(self, other):
        if isinstance(other, Agent):
            return super(Agent, self).__eq__(other) and self.item == other.item
        return False
