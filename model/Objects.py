from enum import Enum, IntEnum
from model.Tiles import AbstractTile, Tile, MovingTile


class Object:
    def __init__(self):
        self.current_position = None

    def set_position(self, tile: AbstractTile):
        pass

    def __eq__(self, other):
        if isinstance(other, Object):
            if self.current_position is not None and other.current_position is not None:
                return self.current_position.id == other.current_position.id

        return False


class Lever(Object):
    def __init__(self):
        super().__init__()
        self.activates = set()

    def set_position(self, tile: AbstractTile):
        self.current_position = tile
        tile.set_lever(self)

    def assign_tile(self, tile: MovingTile):
        self.activates.add(tile)

    def use_lever(self):
        for tile in self.activates:
            tile.flip_is_active()

    def __eq__(self, other):
        if super.__eq__(self, other) and isinstance(other, Lever):
            if len(self.activates) != len(other.activates):
                return False

            other_activates_id = []
            for t in other.activates:
                other_activates_id.append(t.id)

            for t in self.activates:
                if t.id not in other_activates_id:
                    return False
            return True

        return False


class ItemType(IntEnum):
    SPEAR = 1


class Item(Object):
    def __init__(self, item_type: ItemType):
        super().__init__()
        self.type = item_type
        self.is_carried = False

    def set_position(self, tile: AbstractTile):
        self.current_position = tile
        tile.set_item(self)

    def pickup(self):
        self.is_carried = True
        self.current_position = None

    def use(self, agent):
        if self.type == ItemType.SPEAR:
            return self.use_spear(agent)

    @staticmethod
    def use_spear(agent):
        pos = agent.current_position
        if pos.contains_air_connection():
            enemy_tile: AbstractTile = pos.pop_air_connection()
            if enemy_tile.contains_trap():
                trap = enemy_tile.trap_on_tile
                if trap.kill():
                    agent.item = None
                    return True
        return False

    def __eq__(self, other):
        if isinstance(other, Item):
            return super.__eq__(self, other) and (self.type, self.is_carried) == (other.type, other.is_carried)
