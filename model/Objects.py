from enum import Enum
from model.Tiles import AbstractTile, Tile, MovingTile


class Object:
    def __init__(self):
        self.current_position = None

    def set_position(self, tile: AbstractTile):
        pass


class Lever(Object):
    def __init__(self):
        super().__init__()
        self.activates = set()

    def set_position(self, tile: Tile):
        self.current_position = tile
        tile.set_lever(self)

    def assign_tile(self, tile: MovingTile):
        self.activates.add(tile)
        tile.set_lever(self)

    def use_lever(self):
        for tile in self.activates:
            tile.flip_is_active()


class ItemType(Enum):
    SPEAR = 1


class Item(Object):
    def __init__(self, item_type: ItemType):
        super().__init__()
        self.type = item_type
        self.is_carried = False

    def set_position(self, tile: Tile):
        self.current_position = tile
        tile.set_item(self)
