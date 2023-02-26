from model.Objects import Object
from model.Tiles import AbstractTile


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

    def set_trap(self, tile: AbstractTile, trap_strategy: TrapStrategy):
        self.guarded_tile = tile
        self.trap_strategy = trap_strategy

    def trap_action(self):
        self.trap_strategy.execute(self)

    def kill(self):
        if self.attack_able:
            self.guarded_tile.is_guarded = False
            self.current_position.trap_on_tile = None
            self.current_position = None


class SnakeStrategy(TrapStrategy):
    def __init__(self):
        return

    def execute(self, trap):
        return


class SawStrategy(TrapStrategy):
    def __init__(self):
        return

    def execute(self, trap):
        pass


class SpiderStrategy(TrapStrategy):
    def __init__(self):
        return

    def execute(self, trap):
        pass


class LizardStrategy(TrapStrategy):
    def __init__(self):
        return

    def execute(self, trap):
        pass
