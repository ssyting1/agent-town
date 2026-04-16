"""Generate a Tiled-compatible JSON map for 49 NOWIS agents across 8 departments."""
import json
import copy

TILE = 48
MAP_W, MAP_H = 56, 34
FLOOR_TILE = 108
WALL_TOP = 13
WALL_LEFT = 40
WALL_RIGHT = 42
WALL_BOTTOM = 56

DEPTS = [
    {"name": "marketing", "count": 10},
    {"name": "engineering", "count": 8},
    {"name": "testing", "count": 8},
    {"name": "studio-operations", "count": 6},
    {"name": "design", "count": 5},
    {"name": "product", "count": 5},
    {"name": "specialized", "count": 4},
    {"name": "project-management", "count": 3},
]

with open("public/maps/office2.json") as f:
    base = json.load(f)

tilesets = copy.deepcopy(base["tilesets"])

def make_tile_layer(name, layer_id, fill=0):
    data = [fill] * (MAP_W * MAP_H)
    return {
        "data": data, "height": MAP_H, "id": layer_id, "name": name,
        "opacity": 1, "type": "tilelayer", "visible": True, "width": MAP_W, "x": 0, "y": 0,
    }

def set_tile(layer, x, y, tile_id):
    if 0 <= x < MAP_W and 0 <= y < MAP_H:
        layer["data"][y * MAP_W + x] = tile_id

floor = make_tile_layer("floor", 1, FLOOR_TILE)
walls = make_tile_layer("walls", 2, 0)
furniture = make_tile_layer("furniture", 3, 0)

for x in range(MAP_W):
    set_tile(walls, x, 1, WALL_TOP)
    set_tile(walls, x, MAP_H - 2, WALL_BOTTOM)
for y in range(1, MAP_H - 1):
    set_tile(walls, 1, y, WALL_LEFT)
    set_tile(walls, MAP_W - 2, y, WALL_RIGHT)

DESK_TILE = 356
CHAIR_TILE = 372

spawns = []
obj_id = 1

grid = [
    DEPTS[0:4],
    DEPTS[4:8],
]

section_w = 12
section_h = 10
start_x = 3
gap = 1

for row_idx, dept_row in enumerate(grid):
    base_y = 4 + row_idx * (section_h + 4)
    for col_idx, dept in enumerate(dept_row):
        base_x = start_x + col_idx * (section_w + gap)
        cols_per_row = min(dept["count"], 5)
        rows_needed = (dept["count"] + cols_per_row - 1) // cols_per_row

        agent_idx = 0
        for r in range(rows_needed):
            for c in range(cols_per_row):
                if agent_idx >= dept["count"]:
                    break
                sx = base_x + c * 2
                sy = base_y + r * 3
                facing = "down" if r % 2 == 0 else "up"
                set_tile(furniture, sx, sy, DESK_TILE)
                set_tile(furniture, sx, sy + 1, CHAIR_TILE)
                spawn = {
                    "id": obj_id,
                    "name": "",
                    "type": "",
                    "x": sx * TILE,
                    "y": (sy + 1) * TILE,
                    "width": 0, "height": 0,
                    "rotation": 0, "visible": True,
                    "properties": [{"name": "facing", "type": "string", "value": facing}],
                }
                spawns.append(spawn)
                obj_id += 1
                agent_idx += 1

boss_spawn = {
    "id": obj_id,
    "name": "boss",
    "type": "", "x": (MAP_W // 2) * TILE, "y": (MAP_H - 4) * TILE,
    "width": 0, "height": 0, "rotation": 0, "visible": True,
    "properties": [{"name": "facing", "type": "string", "value": "up"}],
}
spawns.append(boss_spawn)

collisions = []
coll_id = obj_id + 1
for x in range(MAP_W):
    for yy in [0, 1, MAP_H - 2, MAP_H - 1]:
        collisions.append({
            "id": coll_id, "name": "", "type": "", "x": x * TILE, "y": yy * TILE,
            "width": TILE, "height": TILE, "rotation": 0, "visible": True,
        })
        coll_id += 1
for y in range(MAP_H):
    for xx in [0, 1, MAP_W - 2, MAP_W - 1]:
        collisions.append({
            "id": coll_id, "name": "", "type": "", "x": xx * TILE, "y": y * TILE,
            "width": TILE, "height": TILE, "rotation": 0, "visible": True,
        })
        coll_id += 1

out = {
    "compressionlevel": -1,
    "height": MAP_H,
    "width": MAP_W,
    "infinite": False,
    "tilewidth": TILE,
    "tileheight": TILE,
    "orientation": "orthogonal",
    "renderorder": "right-down",
    "tiledversion": "1.11.0",
    "type": "map",
    "version": "1.10",
    "nextlayerid": 20,
    "nextobjectid": coll_id + 1,
    "tilesets": tilesets,
    "layers": [
        floor,
        walls,
        furniture,
        make_tile_layer("ground", 4, 0),
        make_tile_layer("objects", 5, 0),
        {"draworder": "topdown", "id": 6, "name": "props", "objects": [], "opacity": 1, "type": "objectgroup", "visible": True, "x": 0, "y": 0},
        {"draworder": "topdown", "id": 7, "name": "props-over", "objects": [], "opacity": 1, "type": "objectgroup", "visible": True, "x": 0, "y": 0},
        make_tile_layer("overhead", 8, 0),
        {"draworder": "topdown", "id": 9, "name": "collisions", "objects": collisions, "opacity": 1, "type": "objectgroup", "visible": True, "x": 0, "y": 0},
        {"draworder": "topdown", "id": 10, "name": "pois", "objects": [], "opacity": 1, "type": "objectgroup", "visible": True, "x": 0, "y": 0},
        {"draworder": "topdown", "id": 11, "name": "spawns", "objects": spawns, "opacity": 1, "type": "objectgroup", "visible": True, "x": 0, "y": 0},
    ],
}

with open("public/maps/nowis-hq.json", "w") as f:
    json.dump(out, f)

print(f"Generated nowis-hq.json: {MAP_W}x{MAP_H} tiles, {len(spawns)} spawns ({len(spawns)-1} workers + 1 boss)")
print(f"Departments: {', '.join(d['name'] + '(' + str(d['count']) + ')' for d in DEPTS)}")
