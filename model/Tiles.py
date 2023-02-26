class AbstractTile:
    def __init__(self, type_name):
        self.type: str = type_name
        self.left = None
        self.right = None
        self.up = None
        self.down = None

        self.item = None
        self.lever = None
        self.on_tile = None
        self.trap_on_tile = None

        self.is_goal = False
        self.is_guarded = False

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

    def contains_item(self):
        return self.item is not None

    def contains_lever(self):
        return self.lever is not None

    def contains_trap(self):
        return self.trap_on_tile is not None

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

    def agent_move_on(self, agent):
        pass

    def __str__(self):
        can_go = []
        if self.left is not None:
            can_go.append("LEFT")
        if self.right is not None:
            can_go.append("RIGHT")
        if self.up is not None:
            can_go.append("UP")
        if self.down is not None:
            can_go.append("DOWN")

        end_str = ", path to:"
        if len(can_go) == 0:
            end_str += " nothing"
        else:
            for path in can_go:
                end_str += " "
                end_str += path

        return "Tile: " + self.type + " -> is goal: " + str(self.is_goal) + end_str


class DeadEndTile(AbstractTile):
    def __init__(self):
        super().__init__("DEAD-END")

    def agent_move_on(self, agent):
        agent.set_position(self)


class Tile(AbstractTile):
    def __init__(self):
        super().__init__("NORMAL")

    def agent_move_on(self, agent):
        if not self.is_guarded:
            agent.set_position(self)

    def __str__(self):
        super_str = super().__str__()
        add_str = ", contains lever: " + str(self.contains_lever()) + ", contains item: " + str(self.contains_item())
        return super_str + add_str


class CrackedTile(AbstractTile):
    def __init__(self):
        super().__init__("CRACKED")
        self.is_cracked = False
        self.is_destroyed = False
        self.drop_on_tile = None

    def set_drop_on_tile(self, tile: AbstractTile):
        self.drop_on_tile: AbstractTile = tile

    def agent_move_on(self, agent):
        if not self.is_guarded and not self.is_destroyed:
            if self.is_cracked:
                if self.drop_on_tile is not None:
                    self.drop_on_tile.agent_move_on(agent)
                else:
                    dead_end = DeadEndTile()
                    dead_end.agent_move_on(agent)

                self.is_destroyed = True
            else:
                agent.set_position(self)
                self.is_cracked = True

    def __str__(self):
        super_str = super().__str__()
        add_str = ", is cracked: " + str(self.is_cracked) + " is destroyed: " + str(self.is_destroyed)
        return super_str + add_str


class MovingTile(AbstractTile):
    def __init__(self, is_active: bool):
        super().__init__("MOVING")
        self.is_active: bool = is_active
        self.lever = None

    def set_lever(self, lever):
        self.lever = lever

    def flip_is_active(self):
        self.is_active = not self.is_active

    def agent_move_on(self, agent):
        if not self.is_guarded and self.is_active:
            agent.set_position(self)

    def __str__(self):
        super_str = super().__str__()
        add_str = ", is active: " + str(self.is_active)
        return super_str + add_str
