from model.Objects import Object
from model.Tiles import AbstractTile, DeadEndTile, MovingTile, CrackedTile
from enum import Enum


class TrapMovingAction(Enum):
    UP = 'u'
    DOWN = 'd'
    LEFT = 'l'
    RIGHT = 'r'


class TrapStrategy:
    def execute(self, trap):
        pass


class Trap(Object):
    def __init__(self, attack_able: bool):
        super().__init__()
        self.guarded_tile: AbstractTile = None
        self.trap_strategy: TrapStrategy = None
        self.attack_able: bool = attack_able

    def set_position(self, tile: AbstractTile):
        self.current_position = tile
        tile.set_trap(self)

    def set_trap(self, tile: AbstractTile, trap_strategy: TrapStrategy):
        self.guarded_tile = tile
        self.guarded_tile.is_guarded = True
        self.trap_strategy = trap_strategy

    def trap_action(self):
        self.trap_strategy.execute(self)

    def kill(self):
        if self.attack_able:
            self.guarded_tile.is_guarded = False
            self.current_position.trap_on_tile = None
            self.current_position = None
            self.guarded_tile = None
            return True
        else:
            return False

    def __eq__(self, other):
        if isinstance(other, Trap):
            return super().__eq__(other) and self.attack_able == other.attack_able and self.trap_strategy == self.trap_strategy
        return False


def can_trap_move(dir: TrapMovingAction, trap: Trap):
    if isinstance(trap.current_position, MovingTile) and not trap.current_position.is_active:
        return False

    next_guarded_tile = None
    if dir == TrapMovingAction.DOWN:
        next_guarded_tile = trap.guarded_tile.down
    elif dir == TrapMovingAction.UP:
        next_guarded_tile = trap.guarded_tile.up
    elif dir == TrapMovingAction.LEFT:
        next_guarded_tile = trap.guarded_tile.left
    elif dir == TrapMovingAction.RIGHT:
        next_guarded_tile = trap.guarded_tile.right

    if next_guarded_tile is None:
        return False
    else:
        if isinstance(next_guarded_tile, MovingTile) and not next_guarded_tile.is_active:
            return False
        return True


def trap_move(dir: TrapMovingAction, trap: Trap):
    trap.current_position.trap_on_tile = None
    trap.guarded_tile.is_guarded = False
    trap.set_position(trap.guarded_tile)

    next_guarded_tile = None
    if dir == TrapMovingAction.DOWN:
        next_guarded_tile = trap.guarded_tile.down
    elif dir == TrapMovingAction.UP:
        next_guarded_tile = trap.guarded_tile.up
    elif dir == TrapMovingAction.LEFT:
        next_guarded_tile = trap.guarded_tile.left
    elif dir == TrapMovingAction.RIGHT:
        next_guarded_tile = trap.guarded_tile.right

    next_guarded_tile.is_guarded = True
    trap.guarded_tile = next_guarded_tile


class SnakeStrategy(TrapStrategy):
    def __init__(self):
        return

    def execute(self, trap):
        return

    def __eq__(self, other):
        if isinstance(other, SnakeStrategy):
            return True
        return False


class SawStrategy(TrapStrategy):
    def __init__(self, guarded_tile_moving_seq):
        self.guarded_tile_moving_seq = guarded_tile_moving_seq
        self.curr = 0
        return

    def execute(self, trap):

        if can_trap_move(self.guarded_tile_moving_seq[self.curr], trap):
            trap_move(self.guarded_tile_moving_seq[self.curr], trap)
            self.curr += 1

            if self.curr == len(self.guarded_tile_moving_seq):
                self.curr = 0

        if trap.guarded_tile.on_tile is not None or trap.current_position.on_tile is not None:
            agent = trap.guarded_tile.on_tile
            dead_end = DeadEndTile()
            dead_end.agent_move_on(agent)

        other_trap: Trap = trap.guarded_tile.trap_on_tile
        if other_trap is not None and other_trap.attack_able:
            other_trap.kill()

    def __str__(self):
        return "current number: " + str(self.curr)

    def __eq__(self, other):
        if isinstance(other, SawStrategy):
            return True
        return False


class SpiderStrategy(TrapStrategy):
    def __init__(self, guarded_tile_moving_seq):
        self.guarded_tile_moving_seq = guarded_tile_moving_seq
        self.curr = 0
        return

    def execute(self, trap):
        if can_trap_move(self.guarded_tile_moving_seq[self.curr], trap):
            trap_move(self.guarded_tile_moving_seq[self.curr], trap)
            self.curr += 1

            if self.curr == len(self.guarded_tile_moving_seq):
                self.curr = 0
        if isinstance(trap.current_position, CrackedTile) and trap.current_position.is_cracked_without_drop_tile():
            trap.current_position.is_destroyed = True

        if trap.guarded_tile.on_tile is not None:
            agent = trap.guarded_tile.on_tile
            dead_end = DeadEndTile()
            dead_end.agent_move_on(agent)

    def __eq__(self, other):
        if isinstance(other, SpiderStrategy):
            return True
        return False


class LizardStrategy(TrapStrategy):
    def __init__(self, activating_tile: AbstractTile, agent):
        self.next_tile = activating_tile
        self.agent = agent
        self.is_active = False

    def execute(self, trap):
        if self.is_active:
            if not isinstance(self.agent.current_position, DeadEndTile):
                trap.current_position.trap_on_tile = None
                trap.guarded_tile.is_guarded = False
                trap.set_position(trap.guarded_tile)
                self.next_tile.is_guarded = True
                trap.guarded_tile = self.next_tile

                self.next_tile = self.agent.current_position
        else:
            if self.agent.current_position == self.next_tile:
                self.is_active = True

    def __eq__(self, other):
        if isinstance(other, LizardStrategy):
            return True
        return False
