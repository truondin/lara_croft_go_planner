from typing import Dict, List

from model.Agent import Agent, Action
from model.Tiles import Tile, CrackedTile, MovingTile, AbstractTile
from model.Objects import Lever, Item, ItemType
from model.Trap import Trap, SawStrategy, TrapMovingAction, SnakeStrategy
import json, copy


def parse_json(path_file):
    file = open(path_file, "r")
    return json.loads(file.read())


def create_tile(t_json):
    tile_type = t_json['type']
    t_id = t_json['id']
    if tile_type == "Tile":
        return Tile(t_id)
    elif tile_type == "CrackedTile":
        return CrackedTile(t_id)
    elif tile_type == "MovingTile":
        return MovingTile(t_id, t_json['active'])


def create_tiles(tiles_json, agent):
    tiles = {}
    goal = None

    for tile in tiles_json:
        t_id = tile['id']
        tiles[t_id] = create_tile(tile)

    for tile in tiles_json:
        t_id = tile['id']
        # print(tile)

        tile_obj = tiles.get(t_id)
        left, right, up, down = tile['left'], tile['right'], tile['up'], tile['down']

        if left is not None:
            left = tiles.get(left)
        if right is not None:
            right = tiles.get(right)
        if up is not None:
            up = tiles.get(up)
        if down is not None:
            down = tiles.get(down)

        tile_obj.set_path(left, right, up, down)

        if tile['type'] == "CrackedTile" and tile["drop"] is not None:
            tile_obj.set_drop_on_tile(tiles.get(tile["drop"]))

        if tile['is_goal']:
            tile_obj.set_as_goal()
            goal = tile_obj

        for i in tile["air_connect"]:
            tile_obj.add_air_connection(tiles.get(i))

    start = tiles.get(agent["pos"])
    set_tiles_coords(tiles, start.id)
    return tiles, goal


def set_tiles_coords(tiles, start_id):
    queue: List[(int, int, AbstractTile)] = [(0, 0, 0, start_id)]
    visited = []

    while len(queue) > 0:
        x, y, z, curr_id = queue.pop()
        curr: AbstractTile = tiles.get(curr_id)

        if curr_id in visited:
            continue

        curr.set_coords(x, y, z)
        visited.append(curr.id)
        if curr.left is not None and curr.left.id not in visited:
            queue.append((x - 1, y, z, curr.left.id))
        if curr.right is not None and curr.right.id not in visited:
            queue.append((x + 1, y, z, curr.right.id))
        if curr.up is not None and curr.up.id not in visited:
            queue.append((x, y + 1, z, curr.up.id))
        if curr.down is not None and curr.down.id not in visited:
            queue.append((x, y - 1, z, curr.down.id))
        if isinstance(curr, CrackedTile) and curr.drop_on_tile is not None and curr.drop_on_tile.id not in visited:
            queue.append((x, y, z - 1, curr.drop_on_tile.id))


def create_traps(traps_json, tiles: Dict[int, AbstractTile]):
    traps = []
    for trap_json in traps_json:
        trap = Trap(trap_json["can_attack"])
        trap.set_position(tiles.get(trap_json["pos"]))

        if trap_json["type"] == "Snake":
            trap.set_trap(tiles.get(trap_json["guards"]), SnakeStrategy())
        elif trap_json["type"] == "Saw":
            mov_seq = []
            for m in trap_json["moving_seq"]:
                if m == TrapMovingAction.UP.value:
                    mov_seq.append(TrapMovingAction.UP)
                elif m == TrapMovingAction.DOWN.value:
                    mov_seq.append(TrapMovingAction.DOWN)
                elif m == TrapMovingAction.LEFT.value:
                    mov_seq.append(TrapMovingAction.LEFT)
                elif m == TrapMovingAction.RIGHT.value:
                    mov_seq.append(TrapMovingAction.RIGHT)
            trap.set_trap(tiles.get(trap_json["guards"]), SawStrategy(mov_seq))

        traps.append(trap)
    return traps


def create_items(items_json, tiles: Dict[int, AbstractTile]):
    for item_j in items_json:
        item = None
        if item_j["type"] == "Spear":
            item = Item(ItemType.SPEAR)

        item.set_position(tiles.get(item_j["pos"]))


def create_levers(levers_json, tiles: Dict[int, AbstractTile]):
    for lever_j in levers_json:
        lever = Lever()
        for pos_id in lever_j["pos"]:
            lever.set_position(tiles.get(pos_id))
        for assigned_id in lever_j["tiles"]:
            lever.assign_tile(tiles.get(assigned_id))


class Game:
    def __init__(self):
        self.goal = None
        self.agent = None
        self.traps = []
        self.tiles = None

    def load_game(self, path):
        json_obj = parse_json(path)

        tiles, self.goal = create_tiles(json_obj["tiles"], json_obj["agent"])
        self.traps = create_traps(json_obj["traps"], tiles)
        create_items(json_obj["items"], tiles)
        create_levers(json_obj["levers"], tiles)

        agent = Agent()
        agent.set_position(tiles.get(json_obj["agent"]["pos"]))
        self.agent = agent
        self.tiles = tiles

    def play(self, level_path):
        self.load_game(level_path)

    def clone(self):
        clone = copy.deepcopy(self)
        return clone

    def __eq__(self, other):
        if isinstance(other, Game):
            if self.agent != other.agent:
                return False

            if len(self.traps) != len(other.traps):
                return False

            for id, self_tile in self.tiles.items():
                if self_tile != other.tiles[id]:
                    return False
            return True

        return False

