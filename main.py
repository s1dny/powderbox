import pygame

from canvas import World, Dir
from tiles import TILES

pygame.init()

FONT = pygame.font.Font('font.ttf', 18)

FPS = 60
fpsClock = pygame.time.Clock()
WINDOW = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('powderbox')

COLORS = [
    (180, 180, 180),
    (140, 110, 90),
    (200, 160, 110),
    (90, 140, 220),
    (160, 160, 64),
    (100, 100, 100),
    (100, 200, 100)
]

paused_text = FONT.render("sim paused", False, (255, 255, 255))

print("""
Controls
- Left click: Add the selected block
- Right click: Delete the selected block
- Mouse wheel: Select different tiles
- Space: Pause / unpause the simulation
- ESC: Reset the canvas
""")
 
def render(world, selected_tile, mouse_position , paused, tiles_info):
    pygame.display.set_caption(f'powderbox {int(fpsClock.get_fps())} FPS')
    surface = pygame.Surface((world.width, world.height))
    for tile in world.tiles:
        surface.set_at((tile.x, tile.y), tile.color)
    surface.set_at(mouse_position, (255, 255, 255))
    scaled_surface = pygame.transform.scale(surface, WINDOW.get_size())
    tile_text = FONT.render(
        f" ({selected_tile + 1}/{len(TILES)}): {TILES[selected_tile].NAME}",
        False,
        COLORS[selected_tile]
    )
    scaled_surface.blit(tile_text, (10, 10))
    if paused:
        scaled_surface.blit(paused_text, (WINDOW.get_width() - paused_text.get_width() - 10, 10))
    WINDOW.blit(scaled_surface, (0, 0))
    pygame.display.flip()

def clamp(n, smallest, largest):
    small = [smallest, n, largest]
    small.sort()
    return small[1]

def get_mouse_world_position(world):
    window_size = WINDOW.get_size()
    mouse_pos = pygame.mouse.get_pos()
    mouse_x = clamp(int((mouse_pos[0] / window_size[0]) * world.width), 0, world.width - 1)
    mouse_y = clamp(int((mouse_pos[1] / window_size[1]) * world.height), 0, world.height - 1)
    return mouse_x, mouse_y

world = World(256, 256)
selected_tile = 0
pause = False
tiles_info = False
while True:
    mouse_position = get_mouse_world_position(world)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEWHEEL:
            if event.y == -1:
                if selected_tile == 0:
                    selected_tile = len(TILES) - 1
                else:
                    selected_tile -= 1
            else:
                if selected_tile == len(TILES) - 1:
                    selected_tile = 0
                else:
                    selected_tile += 1
        if event.type == pygame.KEYDOWN:
            if event.unicode == " ":
                pause = not pause
            elif event.scancode == 41:
                world = World(256, 256)
    if pygame.mouse.get_pressed()[0]:
        world.add_tile(TILES[selected_tile], mouse_position[0], mouse_position[1])
        for direction in Dir.ALL:
            world.add_tile(
                TILES[selected_tile],
                mouse_position[0] + direction[0],
                mouse_position[1] + direction[1]
            )
    elif pygame.mouse.get_pressed()[2]:
        world.delete_tile(mouse_position[0], mouse_position[1])
        for direction in Dir.ALL:
            world.delete_tile(
                mouse_position[0] + direction[0],
                mouse_position[1] + direction[1]
            )
    if not pause:
        world.update()
    render(world, selected_tile, mouse_position, pause, tiles_info)
    fpsClock.tick(FPS)