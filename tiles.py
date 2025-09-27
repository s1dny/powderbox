from canvas import Tile, GasTile, World, LiquidTile, SemiSolidTile, SolidTile, CustomTile, Dir

import random
TILES = []

def add_tile(tile):
    TILES.append(tile)
    return tile

@add_tile
class ConcreteTile(SolidTile):

    NAME = "Concrete"

    def __init__(self, world, x, y):
        super().__init__(
            (128+random.randrange(0, 16), 128+random.randrange(0, 16), 128),
            1024,
            world,
            x,
            y
        )

@add_tile
class WoodTile(SolidTile):

    NAME = "Wood"

    def __init__(self, world, x, y):
        super().__init__(
            (90+random.randrange(0, 8), 70+random.randrange(0, 16), 64),
            1024,
            world,
            x,
            y,
        )

@add_tile
class SandTile(SemiSolidTile):

    NAME = "Sand"

    def __init__(self, world, x, y):
        super().__init__(
            (180+random.randrange(0, 16), 150+random.randrange(0, 32), 110),
            16,
            world,
            x,
            y,
        )

@add_tile
class WaterTile(LiquidTile):

    NAME = "Water"

    def __init__(self, world, x, y):
        super().__init__(
            (90, 130+random.randrange(0, 32), 210+random.randrange(0, 32)),
            4,
            world,
            x,
            y,
        )

@add_tile
class OilTile(LiquidTile):

    NAME = "Oil"

    def __init__(self, world, x, y):
        super().__init__(
            (160+random.randrange(0, 20), 160+random.randrange(0, 20), 64+random.randrange(0, 16)),
            2,
            world,
            x,
            y,
        )

@add_tile
class SmokeTile(GasTile):

    NAME = "Smoke"

    def __init__(self, world, x, y):
        super().__init__(
            (32+random.randrange(0, 8), 32+random.randrange(0, 8), 32+random.randrange(0, 8)),
            0,
            world,
            x,
            y,

        )

@add_tile
class AcidTile(LiquidTile, CustomTile):

    NAME = "Acid"

    def __init__(self, world, x, y):
        super().__init__(
            (100, 200 + random.randrange(0, 32), 100),
            0,
            world,
            x,
            y
        )

    def custom_update(self):
        if random.randrange(0, 16) != 0:
            return
        for direction in Dir.ALL:
            tile: Tile | None = self.get_neighbour_tile(direction)
            if tile and (type(tile) != AcidTile):
                tile.remove()
                self.remove()
                return