from model.Objects import Object
from model.Tiles import AbstractTile, DeadEndTile
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


class SnakeStrategy(TrapStrategy):
    def __init__(self):
        return

    def execute(self, trap):
        return


def trap_move(dir: TrapMovingAction, trap: Trap):
    trap.current_position.trap_on_tile = None
    trap.guarded_tile.is_guarded = False
    trap.guarded_tile.trap_on_tile = True
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


class SawStrategy(TrapStrategy):
    def __init__(self, guarded_tile_moving_seq):
        self.guarded_tile_moving_seq = guarded_tile_moving_seq
        self.curr = 0
        return

    def execute(self, trap):
        trap_move(self.guarded_tile_moving_seq[self.curr], trap)
        self.curr += 1

        if self.curr == len(self.guarded_tile_moving_seq):
            self.curr = 0

        if trap.guarded_tile.on_tile is not None:
            agent = trap.guarded_tile.on_tile
            dead_end = DeadEndTile()
            dead_end.agent_move_on(agent)

    def __str__(self):
        return "current number: " + str(self.curr)


class SpiderStrategy(TrapStrategy):
    def __init__(self, guarded_tile_moving_seq):
        self.guarded_tile_moving_seq = guarded_tile_moving_seq
        self.curr = 0
        return

    def execute(self, trap):
        trap_move(self.guarded_tile_moving_seq[self.curr], trap)
        self.curr += 1

        if self.curr == len(self.guarded_tile_moving_seq):
            self.curr = 0

        if trap.guarded_tile.on_tile is not None:
            agent = trap.guarded_tile.on_tile
            dead_end = DeadEndTile()
            dead_end.agent_move_on(agent)


class LizardStrategy(TrapStrategy):
    def __init__(self):
        return

    def execute(self, trap):
        pass
