"""Sprites pixel art artesanales (escala 2x2 nitida) para Terraza de los Michis."""


def draw_sprite_2x(lz, cx, cy, grid, cmap, shadow_col='#081407', shadow_alpha=0.35):
    """Dibuja un sprite pixel-art en bloques 2x2 centrado horizontalmente en cx y apoyado en cy."""
    h = len(grid)
    w = len(grid[0]) if h else 0
    x0 = int(cx - w)
    y0 = int(cy - h * 2)
    if shadow_col:
        for ry in range(max(0, h - 5), h):
            for rx, ch in enumerate(grid[ry]):
                if ch != '.':
                    sx = x0 + rx * 2
                    sy = y0 + ry * 2 + 3
                    for dy in range(2):
                        for dx in range(2):
                            lz.over(sx + dx, sy + dy, shadow_col, shadow_alpha)
    for ry, row in enumerate(grid):
        py = y0 + ry * 2
        for rx, ch in enumerate(row):
            if ch == '.':
                continue
            col = cmap.get(ch)
            if not col:
                continue
            px = x0 + rx * 2
            lz.put(px, py, col)
            lz.put(px + 1, py, col)
            lz.put(px, py + 1, col)
            lz.put(px + 1, py + 1, col)


# Michi Crema & Blanco panza arriba (44 x 32 bloques -> 88 x 64 px)
SPR_CREAM_BELLYUP = [
    '.......k........k...........................',
    '......kmk......kmk..........................',
    '.....kmpk......kpmk.........................',
    '.....kmhhkkkkkkhhmk.........................',
    '....kmhhhhhhhhhhhhmk........................',
    '....kmmhhhhhhhhhhmmk........................',
    '...kmmhkkhhhhhhkkhmmk.......................',
    '...kmhhWWWWppWWWWhhmk.......................',
    '....kmhWWWWWWWWWWmhmk.......................',
    '.....kkWWWWWWWWWWkkk........................',
    '....khhmWWWWWWWWmhhk........................',
    '...kmhhWWkWWWWkWWhhmk.......................',
    '...kmhhWWkWWWWkWWhhmk.......................',
    '....kkkmmWWWWWWmmkkk........................',
    '.......kmWWWWWWWWmk.........................',
    '......kmhWWWWWWWWmhmk.......................',
    '......kdmhWWWWWWWWWmhmk.....................',
    '.......kdmWWWWWWWWWWmhmk....................',
    '.......kddmWWWWWWWWWWWmhmk..................',
    '........kddmWWWWWWWWWWWmhmk.....kkkkkk......',
    '.........kddmWWWWWWWWWWmhhmk..kkmmmmddk.....',
    '..........kddmmWWWWWWWWWmmmkkkmmmdddkk......',
    '...........kdddmmWWWWWWWWmmmmmmmddkk........',
    '............kkdddmmWWWWWWmmdmmmddk..........',
    '..............kkkddmmmmmmkkmddmmmk..........',
    '................kddmmkddmk..kmddmmWWk.......',
    '................kdmmdk.kk....kkmmWWWWk......',
    '................kdmWWk.........kkkkkkk......',
    '.................kWWWk......................',
    '..................kkk.......................',
]

# Michi Gris & Blanco tumbado de lado mirando atento (48 x 35 bloques -> 96 x 70 px)
SPR_GRAY_LOUNGE = [
    '...........K..........K.........................',
    '..........KgK........KgK........................',
    '.........KgpK........KpgK.......................',
    '.........KgpggKKKKKKggpgK.......................',
    '........KgllllllllllllllgK......................',
    '........KglLLllllllllLLlgK......................',
    '.......KglgllllllllllllglgK.....................',
    '.......KglgAAaPlgglPAaAgllK.....................',
    '.......KglgAAAPgWWgPAAAgllK.....................',
    '.......KgllgggWWWWWWgggllgK.....................',
    '........KglllWWppppWWlllgK......................',
    '........KKgllWWWWWWWWllgKK......................',
    '.........KWggWWWWWWWWggWK.......................',
    '........KWWggWWWWWWWWggGGKK.....................',
    '.......KWWWWWWWWWWWWggGGGllgKK..................',
    '......KWWWWWWWWWWWWggGGllllllggKK...............',
    '..KKKKKWWWWWWWWWWWgGGlllllllllllggK.............',
    '.KWWWWbK.KWWWWWWWgGllllGGGllllGGllgK............',
    '.KWWWbbK..KWWWWWgGlllGGlllGGllGGlllgK...........',
    '..KKKKK...KWWWWggGllGllllllGllGllllgK...........',
    '....KKKKKKWWWWWgGllGllllllllGllllllgK...........',
    '...KWWWWggWWWWgGllllllllllllllllllggK...........',
    '..KWWWWWWggWWwgGlllllllllllllllllggK............',
    '...KKKKKK.KWWwggGGlllllllllllllgggKK............',
    '........KKWWWWwwgggGGGGgggggggggKKgKK...........',
    '.......KWWWWWWWWwwwggggggggggggKK..KgK..........',
    '.......KWWWWWWwwwwwwKKKKKKKKKKK.....KgK.........',
    '........KKKKKKK......................KggK.......',
    '......................................KgGK......',
    '.......................................KgGK.....',
    '........................................KgGK....',
    '.........................................KgGK...',
    '..........................................KGGK..',
    '...........................................KK...',
]

# Michi Gris sentado arriba en el rascador (22 x 28 bloques -> 44 x 56 px)
SPR_GRAY_SIT = [
    '....K........K........',
    '...KgK......KgK.......',
    '...KgpK....KpgK.......',
    '..KgllgKKKKgllgK......',
    '..KgllllllllllgK......',
    '.KglLLllllllLLlgK.....',
    '.KglAAPllllPAAlgK.....',
    '.KglAAPlgglPAAlgK.....',
    '.KglllgWWWWglllgK.....',
    '..KglWWppppWWlgK......',
    '..KKgWWWWWWWWgKK......',
    '...KWgWWWWWWgWK.......',
    '..KggWWWWWWWWggK......',
    '.KgglWWWWWWWWlggK.....',
    '.KglgWWWWWWWWglgK.....',
    '.KglgWWWWWWWWglgK.....',
    '.KgglWWWWWWWWlggK.....',
    '..KgllWWWWWWllgK......',
    '..KgglWWWWWWlggK......',
    '...KWWKWWWWKWWK.......',
    '...KWWK.KK.KWWK.......',
    '....KK......KK........',
    '..............KK......',
    '...............KgK....',
    '................KgK...',
    '................KGGK..',
    '.................KGGK.',
    '..................KK..',
]

# Michi Crema agazapado jugando con la pelotita (34 x 21 bloques -> 68 x 42 px)
SPR_CREAM_PLAY = [
    '......k......k....................',
    '.....kmk....kmk...................',
    '.....kmpkkkkpmk...................',
    '....kmhhhhhhhhmk..................',
    '...kmhhhhhhhhhhmk.................',
    '...kmhAeekkeeAhmkk................',
    '...kmhAeWWWWeehmhhkk..............',
    '...kmhWWppppWWhmhhhhkkk...........',
    '....kkWWWWWWWWmhhhhhhhhmmkk.......',
    '.....kmWWWWWWmhhhhhhhhhhmmk.......',
    '...kmhhWWWWWWmhhhhhhhhhhmmmk...kkk',
    '..kWWmmWWWWWWmmhhhhdddhhmmmk..kmmk',
    '.kWWWmkWWWWWWmmhhhdddddhmmmk.kmmk.',
    '..kkk..kWWWWWWmmhhdddddmmmk..kdk..',
    '........kWWWWWmmmddddddmmkkkmdk...',
    '.........kkWWWmmmmmmmmmmmmmddk....',
    '..........kWWmmkkkkkkkkkkdddk.....',
    '..........kWWmk........kmmmk......',
    '...........kkk.........kWWmk......',
    '........................kkk.......',
]

# Michi Crema acurrucado durmiendo (28 x 17 bloques -> 56 x 34 px)
SPR_CREAM_SLEEP = [
    '.....k......k...............',
    '....kmk....kmk..............',
    '....kmpkkkkpmk..............',
    '...kmhhhhhhhhmk.............',
    '...kmhhhhhhhhhmk............',
    '..kmhkkhhhhkkhmhkkk.........',
    '..kmhWWppppWWhmhhhhkkk......',
    '...kkWWWWWWWWmhhhhhhhhmmk...',
    '..kmhhWWWWWWmhhhhhhhhhhmmk..',
    '.kmhhhWWWWWWmmhhhhhhhhhhdmk.',
    '.kmhhhWWWWWWmmmhhhhdddhhdmk.',
    '.kmhhhWWWWWmmmmmmdddddddmmk.',
    '..kmhhWWWWmmmmmmmmddddddmk..',
    '...kmmWWWWmmmmmddddddmmmk...',
    '....kkkmmmmmmmddddddmmkk....',
    '.......kkkkkkkkkkkkkkk......',
]

# Michi Gris acurrucado durmiendo (28 x 17 bloques -> 56 x 34 px)
SPR_GRAY_SLEEP = [
    '...............K......K.....',
    '..............KgK....KgK....',
    '..............KpgKKKKgpK....',
    '.............KgllllllllgK...',
    '............KgllllllllllgK..',
    '.........KKKglKKllllKKlgK...',
    '......KKKggggllWWppWWllgK...',
    '...KKglllllllgWWWWWWWWKK....',
    '..KgllGGGGllllgWWWWggggllgK.',
    '.KglGGllllGGgllWWWWggggllgK.',
    '.KgGllllllllggllWWgggggllgK.',
    '.KgGllllGGGGgllWWggggggllgK.',
    '..KggllllllggglWWggggggK....',
    '...KKgggggggggWWWggggKK.....',
    '.....KKKKKKKKKKKKKKKK.......',
]
