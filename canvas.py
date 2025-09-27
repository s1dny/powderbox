import random

class Dir:
    UP = 0, -1
    DOWN = 0, 1,
    LEFT = -1, 0,
    RIGHT = 1, 0
    UP_LEFT = -1, -1
    UP_RIGHT = 1, -1
    DOWN_LEFT = -1, 1
    DOWN_RIGHT = 1, 1

    ALL = (
        DOWN,
        DOWN_LEFT,
        DOWN_RIGHT,
        LEFT,
        UP_LEFT,
        UP,
        UP_RIGHT,
        RIGHT,
    )

class NextPosition:

    def __init__(self, x, y, valid):
        self.x = x
        self.y = y
        self.valid = valid

class Tile:

    def __init__(self, color, density, world: "World", x, y):
        self.color = color
        self.density = density
        self.x = x
        self.y = y
        self.world = world
        self.active = True
        self.last_update = 0

    def remove(self):
        if self.active:
            self.world.tiles_to_delete.append(self)
            self.active = False
            return True
        return False

    def add(self):
        self.world.tiles.append(self)
        self.world.spatial_matrix[self.y][self.x] = self

    def delete(self):
        self.world.tiles.remove(self)
        self.world.spatial_matrix[self.y][self.x] = None

    def get_next_pos(self, relative_vector):
        next_x = self.x + relative_vector[0]
        if not 0 <= next_x < self.world.width:
            return NextPosition(0, 0, False)
        next_y = self.y + relative_vector[1]
        if not 0 <= next_y < self.world.height:
            return NextPosition(0, 0, False)
        return NextPosition(next_x, next_y, True)

    def get_neighbour_tile(self, direction):
        next_pos = self.get_next_pos(direction)
        if not next_pos.valid:
            return None
        checked_tile = self.world.spatial_matrix[next_pos.y][next_pos.x]
        if not checked_tile:
            return None
        return checked_tile
    
class MovingTile(Tile):

    def __init__(self, color, density, world: "World", x, y):
        super().__init__(color, density, world, x, y)
        self._skip_update = 0
        self._cooldown = 0

    def add(self):
        super().add()
        self.world.moving_tiles.append(self)

    def delete(self):
        super().delete()
        self.world.moving_tiles.remove(self)

    def move(self, new_x, new_y, replacement_tile: "Tile | None"):
        self.world.spatial_matrix[self.y][self.x] = replacement_tile
        self.x = new_x
        self.y = new_y
        self.world.spatial_matrix[self.y][self.x] = self

    def try_move(self, direction):
        next_pos = self.get_next_pos(direction)
        if not next_pos.valid:
            return False
        checked_tile = self.world.spatial_matrix[next_pos.y][next_pos.x]
        if not checked_tile:
            self.move(next_pos.x, next_pos.y, None)
            return True
        elif checked_tile.density < self.density:
            checked_tile.x = self.x
            checked_tile.y = self.y
            checked_tile.last_update = self.world.update_count
            self.move(next_pos.x, next_pos.y, None)
            return True
        return False

    def check_directions(self, directions):
        if self._cooldown == 0:
            for direction in directions:
                if self.try_move(direction):
                    self._skip_update = 0
                    self.last_update = self.world.update_count
                    return
        else:
            self._cooldown -= 1
            return
        if self._skip_update != 3:
            self._skip_update += 1
        self._cooldown = self._skip_update

    def update_position(self):
        pass

class StationaryTile(Tile):
    pass

class CustomTile(Tile):

    def add(self):
        super().add()
        self.world.custom_tiles.append(self)

    def delete(self):
        super().delete()
        self.world.custom_tiles.remove(self)

    def custom_update(self):
        pass


class GenericSystem:
    def __init__(self, world: "World"):
        self.world = world

    def update(self):
        pass


class MovementSystem(GenericSystem):

    def update(self):
        for tile in self.world.moving_tiles:
            if tile.last_update != self.world.update_count:
                tile.update_position()

class CustomTileSystem(GenericSystem):

    def update(self):
        for tile in self.world.custom_tiles:
            tile.custom_update()


class World:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = []
        self.moving_tiles = []
        self.heat_tiles = []
        self.custom_tiles = []
        self.tiles_to_delete = []
        self.tiles_to_add = []
        init_matrix = []
        for i in range(height):
            init_matrix.append([None for i in range(width)])
        self.spatial_matrix = tuple(init_matrix)
        self.systems = (
            MovementSystem(self),
            CustomTileSystem(self)
        )
        self.update_count = 0

    def add_tile(self, tile_type, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        new_tile: Tile = tile_type(self, x, y)
        if not self.spatial_matrix[y][x]:
            new_tile.add()
        return new_tile

    def delete_tile(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        tile = self.spatial_matrix[y][x]
        if tile:
            tile.remove()
        return tile

    def update(self):
        for system in self.systems:
            system.update()
        if self.tiles_to_delete:
            for tile in self.tiles_to_delete:
                tile.delete()
                del tile
            self.tiles_to_delete.clear()
        if self.tiles_to_add:
            for tile in self.tiles_to_add:
                tile.add()
                del tile
            self.tiles_to_add.clear()
        self.update_count += 1

class SolidTile(StationaryTile):
    def update_temperature2(self):
        pass

class SemiSolidTile(StationaryTile, MovingTile):
    DIRECTIONS = (Dir.DOWN, Dir.DOWN_LEFT, Dir.DOWN_RIGHT)

    def update_position(self):
        self.check_directions(self.DIRECTIONS)

class LiquidTile(StationaryTile, MovingTile):
    DIRECTIONS = (
        (Dir.DOWN, Dir.DOWN_LEFT, Dir.LEFT, Dir.DOWN_RIGHT, Dir.RIGHT),
        (Dir.DOWN, Dir.DOWN_RIGHT, Dir.RIGHT, Dir.DOWN_LEFT, Dir.LEFT)
    )

    def update_position(self):
        self.check_directions(self.DIRECTIONS[random.randrange(0, 2)])

class GasTile(StationaryTile, MovingTile):
    DIRECTIONS = (
        (Dir.UP, Dir.UP_LEFT, Dir.LEFT, Dir.UP_RIGHT, Dir.RIGHT),
        (Dir.UP, Dir.UP_RIGHT, Dir.RIGHT, Dir.UP_LEFT, Dir.LEFT)
    )

    def update_position(self):
        self.check_directions(self.DIRECTIONS[random.randrange(0, 2)])