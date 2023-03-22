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
        if isinstance(curr, CrackedTile) and curr.drop_on_tile is not None:
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
        lever.set_position(tiles.get(lever_j["pos"]))
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
        # print(agent)
        # print(agent.current_position)
        # print(self.goal)
        # print(self.start)

    def play(self, level_path):
        # self.test3()
        self.load_game(level_path)
        return

    def clone(self):
        clone = copy.deepcopy(self)
        return clone

    def __eq__(self, other):
        if isinstance(other, Game):
            return (self.agent, self.traps, self.tiles, self.goal) == (other.agent, other.traps, other.tiles, other.goal)

        return False

    def test2(self):
        tile1 = Tile(1)
        tile2 = Tile(2)
        tile3 = Tile(3)
        tile4 = Tile(4)
        tile5 = Tile(5)
        tile6 = Tile(6)

        agent = Agent()
        saw = Trap(False)

        saw.set_position(tile3)
        saw.set_trap(tile4, SawStrategy(
            [TrapMovingAction.DOWN, TrapMovingAction.DOWN, TrapMovingAction.UP, TrapMovingAction.UP,
             TrapMovingAction.UP, TrapMovingAction.DOWN]))

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

        agent = Agent()

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

    def test3(self):
        tile1 = Tile(1)
        tile2 = Tile(2)
        tile3 = Tile(3)
        tile4 = Tile(4)
        tile5 = Tile(5)
        tile6 = Tile(6)

        agent = Agent()
        snake = Trap(True)
        spear = Item(ItemType.SPEAR)

        spear.set_position(tile2)
        snake.set_position(tile4)
        snake.set_trap(tile3, SnakeStrategy())
        tile2.add_air_connection(tile4)
        tile3.add_air_connection(tile4)

        tile1.set_path(None, None, None, tile2)
        tile2.set_path(None, None, tile1, tile3)
        tile3.set_path(None, None, tile2, tile4)
        tile4.set_path(None, None, tile3, tile5)
        tile5.set_path(None, None, tile4, tile6)
        tile6.set_path(None, None, tile5, None)

        agent.set_position(tile1)

        self.start = tile1
        self.agent = agent
        self.traps.append(snake)


