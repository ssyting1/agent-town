"""Replicate the original office2 design 8 times (one per department) into a single NOWIS HQ map."""
import json
import copy

TILE = 48

with open("public/maps/office2.json") as f:
    original = json.load(f)

OW, OH = original["width"], original["height"]  # 27 x 20

COLS, ROWS = 4, 2
GAP_X, GAP_Y = 3, 3
MAP_W = COLS * OW + (COLS - 1) * GAP_X + 4
MAP_H = ROWS * OH + (ROWS - 1) * GAP_Y + 4
CORRIDOR_FLOOR = 108

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

TILE_LAYERS = ["floor", "walls", "ground", "furniture", "objects", "overhead"]

orig_layers = {}
for layer in original["layers"]:
    if layer["type"] == "tilelayer":
        orig_layers[layer["name"]] = layer["data"]

orig_spawns = []
orig_boss = None
for layer in original["layers"]:
    if layer.get("name") == "spawns" and layer["type"] == "objectgroup":
        for obj in layer["objects"]:
            if obj.get("name") == "boss":
                orig_boss = obj
            else:
                orig_spawns.append(obj)
        break

orig_collisions = []
for layer in original["layers"]:
    if layer.get("name") == "collisions" and layer["type"] == "objectgroup":
        orig_collisions = layer["objects"]
        break

orig_pois = []
for layer in original["layers"]:
    if layer.get("name") == "pois" and layer["type"] == "objectgroup":
        orig_pois = layer["objects"]
        break

def blit_layer(dest, src, ox, oy, dest_w):
    for y in range(OH):
        for x in range(OW):
            tile = src[y * OW + x]
            if tile != 0:
                dx, dy = ox + x, oy + y
                if 0 <= dx < dest_w and 0 <= dy < MAP_H:
                    dest[dy * dest_w + dx] = tile

def offset_objects(objects, ox_px, oy_px, id_start):
    result = []
    for i, obj in enumerate(objects):
        o = copy.deepcopy(obj)
        o["x"] = obj["x"] + ox_px
        o["y"] = obj["y"] + oy_px
        o["id"] = id_start + i
        result.append(o)
    return result

combined_layers = {}
for name in TILE_LAYERS:
    if name == "floor":
        combined_layers[name] = [CORRIDOR_FLOOR] * (MAP_W * MAP_H)
    else:
        combined_layers[name] = [0] * (MAP_W * MAP_H)

all_spawns = []
all_collisions = []
all_pois = []
obj_id = 1

for idx in range(8):
    row = idx // COLS
    col = idx % COLS
    ox = 2 + col * (OW + GAP_X)
    oy = 2 + row * (OH + GAP_Y)
    dept = DEPTS[idx]

    for name in TILE_LAYERS:
        if name in orig_layers:
            blit_layer(combined_layers[name], orig_layers[name], ox, oy, MAP_W)

    ox_px = ox * TILE
    oy_px = oy * TILE

    worker_spawns = offset_objects(orig_spawns, ox_px, oy_px, obj_id)
    obj_id += len(worker_spawns)
    for s in worker_spawns[:dept["count"]]:
        all_spawns.append(s)

    colls = offset_objects(orig_collisions, ox_px, oy_px, obj_id)
    obj_id += len(colls)
    all_collisions.extend(colls)

    pois = offset_objects(orig_pois, ox_px, oy_px, obj_id)
    obj_id += len(pois)
    all_pois.extend(pois)

boss = {
    "id": obj_id, "name": "boss", "type": "",
    "x": (MAP_W // 2) * TILE, "y": (2 + OH + GAP_Y // 2) * TILE,
    "width": 0, "height": 0, "rotation": 0, "visible": True,
    "properties": [{"name": "facing", "type": "string", "value": "up"}],
}
all_spawns.append(boss)
obj_id += 1

def make_tile_layer(name, layer_id, data):
    return {
        "data": data, "height": MAP_H, "id": layer_id, "name": name,
        "opacity": 1, "type": "tilelayer", "visible": True, "width": MAP_W, "x": 0, "y": 0,
    }

def make_obj_layer(name, layer_id, objects):
    return {
        "draworder": "topdown", "id": layer_id, "name": name,
        "objects": objects, "opacity": 1, "type": "objectgroup",
        "visible": True, "x": 0, "y": 0,
    }

out = {
    "compressionlevel": -1,
    "height": MAP_H, "width": MAP_W,
    "infinite": False,
    "tilewidth": TILE, "tileheight": TILE,
    "orientation": "orthogonal",
    "renderorder": "right-down",
    "tiledversion": "1.11.0", "type": "map", "version": "1.10",
    "nextlayerid": 20, "nextobjectid": obj_id + 1,
    "tilesets": copy.deepcopy(original["tilesets"]),
    "layers": [
        make_tile_layer("floor", 1, combined_layers.get("floor", [0] * MAP_W * MAP_H)),
        make_tile_layer("walls", 2, combined_layers.get("walls", [0] * MAP_W * MAP_H)),
        make_tile_layer("ground", 3, combined_layers.get("ground", [0] * MAP_W * MAP_H)),
        make_tile_layer("furniture", 4, combined_layers.get("furniture", [0] * MAP_W * MAP_H)),
        make_tile_layer("objects", 5, combined_layers.get("objects", [0] * MAP_W * MAP_H)),
        make_obj_layer("props", 6, []),
        make_obj_layer("props-over", 7, []),
        make_tile_layer("overhead", 8, combined_layers.get("overhead", [0] * MAP_W * MAP_H)),
        make_obj_layer("collisions", 9, all_collisions),
        make_obj_layer("pois", 10, all_pois),
        make_obj_layer("spawns", 11, all_spawns),
    ],
}

with open("public/maps/nowis-hq.json", "w") as f:
    json.dump(out, f)

total_workers = len(all_spawns) - 1
print(f"Generated nowis-hq.json: {MAP_W}x{MAP_H} tiles ({MAP_W*TILE}x{MAP_H*TILE}px)")
print(f"Spawns: {total_workers} workers + 1 boss = {len(all_spawns)} total")
for i, d in enumerate(DEPTS):
    assigned = min(d["count"], len(orig_spawns))
    print(f"  Office {i+1}: {d['name']} ({assigned}/{d['count']} seated)")
