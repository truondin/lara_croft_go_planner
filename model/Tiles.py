class AbstractTile:
    def __init__(self, type_name, id_num):
        self.type: str = type_name
        self.id: int = id_num
        self.left = None
        self.right = None
        self.up = None
        self.down = None
        self.x, self.y, self.z = 0, 0, 0

        self.item = None
        self.lever = None
        self.on_tile = None
        self.trap_on_tile = None

        self.air_connection = []
        self.is_goal = False
        self.is_guarded = False

    def set_coords(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def set_trap(self, trap):
        self.trap_on_tile = trap

    def set_path(self, left, right, up, down):
        self.left: Tile = left
        self.right: Tile = right
        self.up: Tile = up
        self.down: Tile = down

    def set_as_goal(self):
        self.is_goal = True

    def is_goal(self):
        return self.is_goal

    def add_air_connection(self, tile):
        self.air_connection.append(tile)

    def pop_air_connection_index(self, index):
        return self.air_connection.pop(index)

    def pop_air_connection(self):
        return self.air_connection.pop()

    def contains_air_connection(self):
        return len(self.air_connection) != 0

    def contains_item(self):
        return self.item is not None

    def contains_lever(self):
        return self.lever is not None

    def contains_trap(self):
        return self.trap_on_tile is not None

    def remove_item(self):
        self.item.current_position = None
        self.item = None

    def remove_on_tile(self):
        self.on_tile = None

    def is_empty(self):
        return self.on_tile is None

    def set_lever(self, lever):
        self.lever = lever

    def set_item(self, item):
        self.item = item

    def set_agent(self, agent):
        if self.is_empty():
            self.on_tile = agent

    def can_move_on(self):
        pass

    def agent_move_on(self, agent):
        pass

    def __eq__(self, other):
        if isinstance(other, AbstractTile):
            self_info = (self.type, self.id, self.x, self.y, self.z, self.item, self.lever, self.trap_on_tile, self.air_connection, self.is_goal, self.is_guarded)
            other_info = (other.type, other.id, other.x, other.y, self.z, other.item, other.lever, other.trap_on_tile, other.air_connection, other.is_goal, other.is_guarded)
            return self_info == other_info
        return False

    def __hash__(self):
        return hash((self.type, self.id, self.x, self.y, self.z))

    def __str__(self):
        return "Tile" + str(self.id) + ": " + self.type + " -> is goal: " + str(self.is_goal) + ", coords x= " + str(self.x) + " y=" + str(self.y) + " z=" + str(self.z)


class DeadEndTile(AbstractTile):
    def __init__(self):
        super().__init__("DEAD-END", 0)

    def agent_move_on(self, agent):
        agent.set_position(self)

    def can_move_on(self):
        return True

    def __hash__(self):
        return super.__hash__(self)


class Tile(AbstractTile):
    def __init__(self, num):
        super().__init__("NORMAL", num)

    def agent_move_on(self, agent):
        if not self.is_guarded:
            agent.set_position(self)

    def can_move_on(self):
        return True

    def __str__(self):
        super_str = super().__str__()
        add_str = ", contains lever: " + str(self.contains_lever()) + ", contains item: " + str(self.contains_item())
        return super_str + add_str

    def __hash__(self):
        return super.__hash__(self)


class CrackedTile(AbstractTile):
    def __init__(self, num):
        super().__init__("CRACKED", num)
        self.is_cracked = False
        self.is_destroyed = False
        self.drop_on_tile = None

    def set_drop_on_tile(self, tile: AbstractTile):
        self.drop_on_tile: AbstractTile = tile

    def agent_move_on(self, agent):
        if not self.is_destroyed:
            if self.is_cracked:
                if self.drop_on_tile is not None:
                    if isinstance(self.drop_on_tile, MovingTile):
                        if self.drop_on_tile.is_active:
                            self.drop_on_tile.agent_move_on(agent)
                        else:
                            dead_end = DeadEndTile()
                            dead_end.agent_move_on(agent)
                    else:
                        self.drop_on_tile.agent_move_on(agent)
                else:
                    dead_end = DeadEndTile()
                    dead_end.agent_move_on(agent)

                self.is_destroyed = True
            else:
                agent.set_position(self)
                self.is_cracked = True
        else:
            dead_end = DeadEndTile()
            dead_end.agent_move_on(agent)

    def is_cracked_without_drop_tile(self):
        return self.is_cracked and self.drop_on_tile is None

    def can_move_on(self):
        return True

    def __str__(self):
        super_str = super().__str__()
        add_str = ", is cracked: " + str(self.is_cracked) + " is destroyed: " + str(self.is_destroyed)
        return super_str + add_str

    def __eq__(self, other):
        if isinstance(other, CrackedTile):
            if not super.__eq__(self, other):
                return False
            elif (self.is_cracked, self.is_destroyed) != (other.is_cracked, other.is_destroyed):
                return False

            if self.drop_on_tile is not None and other.drop_on_tile is not None:
                if self.drop_on_tile.id != other.drop_on_tile.id:
                    return False
                else:
                    return True
            elif self.drop_on_tile is None and other.drop_on_tile is None:
                return True

        return False

    def __hash__(self):
        return super.__hash__(self)


class MovingTile(AbstractTile):
    def __init__(self, num, is_active: bool):
        super().__init__("MOVING", num)
        self.is_active: bool = is_active

    def flip_is_active(self):
        self.is_active = not self.is_active

    def agent_move_on(self, agent):
        if not self.is_guarded and self.is_active:
            agent.set_position(self)

    def can_move_on(self):
        return self.is_active

    def __str__(self):
        super_str = super().__str__()
        add_str = ", is active: " + str(self.is_active)
        return super_str + add_str

    def __eq__(self, other):
        if isinstance(other, MovingTile):
            return super.__eq__(self, other) and self.is_active == other.is_active

        return False

    def __hash__(self):
        return super.__hash__(self)
