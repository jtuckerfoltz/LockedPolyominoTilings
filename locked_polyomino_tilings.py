import itertools
import random
from tqdm import tqdm
import pickle
import os.path
from matplotlib import pyplot as plt
import time
import os
from sys import argv


next_time = 0


def choose_arbitrarily(s):
    for x in s:
        return x


def neighbors(cell, triangular=False):
    x, y = cell
    yield x + 1, y
    yield x, y - 1
    yield x - 1, y
    yield x, y + 1
    if triangular:
        yield x + 1, y - 1
        yield x - 1, y + 1


def get_all_tetris_pieces(n, root, allowable_locations, all_cells=None, triangular=False):
    if type(n) != int:
        to_return = set()
        for nn in n:
            pieces = get_all_tetris_pieces(nn, root, allowable_locations, all_cells=all_cells, triangular=triangular)
            for piece in pieces:
                to_return.add(piece)
        return to_return
    elif not (allowable_locations is None) and root not in allowable_locations:
        raise Exception(f"Root {root} not in allowable locations {allowable_locations}")
    elif all_cells is None:
        return get_all_tetris_pieces(n, root, allowable_locations, {root}, triangular=triangular)
    elif len(all_cells) == n:
        return {tuple(sorted(all_cells))}
    else:
        to_return = set()
        for cell in all_cells:
            for neighbor in neighbors(cell, triangular=triangular):
                if (allowable_locations is None or neighbor in allowable_locations) \
                        and neighbor not in all_cells:
                    for piece in get_all_tetris_pieces(n, root, allowable_locations,
                                                       all_cells.union({neighbor}),
                                                       triangular=triangular):
                        to_return.add(piece)
        return to_return


def is_parent(parent, child, side_length, box):
    for row in range(side_length):
        for col in range(box if box else (side_length - row)):
            if not child[row][col].issubset(parent[row][col]):
                return False
    return True


def generate_types(n, triangular=False):
    types = get_all_tetris_pieces(n, (0, 0), None, triangular=triangular)
    return sorted(list(types))


def pf_mult_1(side_length, grid, finalized, box=None):
    best_row = -1
    best_col = -1
    best_obj_value = 999999999999
    for row in range(side_length):
        for col in range(box if box else (side_length - row)):
            num_possibilities = len(grid[row][col])
            if num_possibilities == 0:
                return -2, -2
            elif finalized[row][col]:
                continue
            else:
                obj_value = num_possibilities * (row + col + 5)
                if obj_value < best_obj_value:
                    best_row = row
                    best_col = col
                    best_obj_value = obj_value
    return best_row, best_col


def explore(n, types, side_length, priority_function, disallowable_pairs, grid, finalized,
            box=None, scout=0, rot_sym=None, stop_when_found=False, first_tile=None):
    this_time = time.time()
    global next_time
    if this_time > next_time:
        next_time = this_time + 60
        # Uncomment next line to print current status of search every minute.
        #print_nicely(n, grid)
    row_root, col_root = priority_function(side_length, grid, finalized, box)
    if row_root == -1:  # Exactly one choice for each cell, i.e., complete tiling.
        if type(n) == int:
            global test_num
            filename = f"Outputs/T{test_num}.txt"
            if os.path.exists(filename):
                with open(filename, "a") as f:
                    f.write(str(grid) + "\n")
            return 1, grid
        else:
            sizes = set()
            for row in grid:
                for cell in row:
                    t = choose_arbitrarily(cell)
                    if t != -1:
                        sizes.add(len(types[t]))
            if len(sizes) == len(n):
                return 1, grid
            else:
                return 0, None
        return 1, grid
    elif row_root == -2:  # No valid tilings.
        return 0, None
    else:  # Need to expand search on all possibilities for cell chosen by priority function.
        possible_types = grid[row_root][col_root]
        tilings = []
        total_num_tilings = 0
        if first_tile:
            possible_types = [first_tile]
        for t in possible_types:
            new_grid, new_finalized = place(disallowable_pairs, side_length, box, grid,
                             row_root, col_root, t, types, finalized)
            if rot_sym:
                r, r_fold = rot_sym
                if r_fold == 2:
                    new_grid, new_finalized = place(disallowable_pairs, side_length, box,
                                     new_grid, side_length - 1 - row_root,
                                     box - 1 - col_root, r[r[t]], types, new_finalized)
                elif r_fold == 4:
                    new_grid, new_finalized = place(disallowable_pairs, side_length, box,
                                     new_grid, side_length - 1 - col_root,
                                     row_root, r[r[r[t]]], types, new_finalized)
                    new_grid, new_finalized = place(disallowable_pairs, side_length, box,
                                     new_grid, side_length - 1 - row_root,
                                     box - 1 - col_root, r[r[t]], types, new_finalized)
                    new_grid, new_finalized = place(disallowable_pairs, side_length, box,
                                     new_grid, col_root,
                                     box - 1 - row_root, r[t], types, new_finalized)
                else:
                    raise Exception("Parameter rot_sym must be 2 or 4.")
            num_tilings, sample_tiling = explore(n, types, side_length, priority_function,
                                                 disallowable_pairs, new_grid, new_finalized,
                                                 box=box, scout=scout, rot_sym=rot_sym,
                                                 stop_when_found=stop_when_found)
            if num_tilings == "STOP":
                print(side_length, grid, finalized, box)
                print_nicely(n, grid)
                print(priority_function(side_length, grid, finalized, box))
                raise Exception("STOPPING")
            if num_tilings > 0:
                total_num_tilings += num_tilings
                tilings.append(sample_tiling)
                if stop_when_found:
                    break
        if total_num_tilings == 0:
            return 0, None
        else:
            return total_num_tilings, random.choice(tilings)


def place(disallowable_pairs, side_length, box, grid, row_root, col_root, t, types, finalized):
    new_grid = []
    for row_other in range(side_length):
        new_grid_row = []
        for col_other in range(box if box else (side_length - row_other)):
            d_row = row_other - row_root
            d_col = col_other - col_root
            if (d_row, d_col) in disallowable_pairs:
                new_grid_row.append(grid[row_other][col_other].difference(
                                    disallowable_pairs[(d_row, d_col)][t]))
            else:
                new_grid_row.append(grid[row_other][col_other].copy())
        new_grid.append(new_grid_row)
    new_finalized = [[finalized[i][j] for j in range(box if box else (side_length - i))] \
            for i in range(side_length)]
    new_finalized[row_root][col_root] = True
    return new_grid, new_finalized


def tile_grid(n, side_length, priority_function=pf_mult_1, disallowable_pairs=None, box=None,
              scout=0, triangle_box=False, rot_sym=None, stop_when_found=False,
              missing_cells=set(), first_tile=None, output_tilings=False):
    if output_tilings:
        if not os.path.exists("Outputs"):
            os.makedirs("Outputs")
        open(f"Outputs/T{test_num}.txt", "w").close()
    if type(n) == int and box and ((side_length * box - len(missing_cells)) % n != 0):
        return 0, None
    types = generate_types(n)
    if disallowable_pairs is None:
        disallowable_pairs = generate_disallowable_pairs(n)
    grid = [[set() for _ in range(box if box else (side_length - row))] \
            for row in range(side_length)]
    finalized = [[False for _ in range(box if box else (side_length - row))] \
            for row in range(side_length)]
    for i, j in missing_cells:
        grid[i][j].add(-1)
        finalized[i][j] = True
    for row_root in range(side_length):
        for col_root in range(box if box else (side_length - row_root)):
            if (row_root, col_root) in missing_cells:
                continue
            for t in range(len(types)):
                ok = True
                for d_row, d_col in types[t]:
                    row_other = row_root + d_row
                    if row_other < 0 or (box and row_other >= side_length) \
                                     or (triangle_box and row_other >= side_length):
                        ok = False
                        break
                    col_other = col_root + d_col
                    if col_other < 0 or (box and col_other >= box) \
                                     or (triangle_box and col_other >= side_length):
                        ok = False
                        break
                    if (row_other, col_other) in missing_cells:
                        ok = False
                        break
                if ok:
                    grid[row_root][col_root].add(t)
    if rot_sym:
        rot_sym = rotation_map(n), rot_sym
    return explore(n, types, side_length, priority_function, disallowable_pairs,
                   grid, finalized, box=box, rot_sym=rot_sym,
                   stop_when_found=stop_when_found, first_tile=first_tile)
    


def generate_disallowable_pairs(n, triangular=False, refine=True):
    if type(n) == tuple:
        s = "-".join(map(str, n))
        filename = f"disallowable_pairs_{'T_' if triangular else ''}{s}.p"
        max_n = max(n)
    else:
        filename = f"disallowable_pairs_{'T_' if triangular else ''}{n}.p"
        max_n = n
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            return(pickle.load(f))
    types = generate_types(n)
    num_types = len(types)
    board_radius = 3*max_n if refine else 2*max_n - 2
    disallowable_pairs = {}
    root = (0, 0)
    for x in tqdm(range(-board_radius, board_radius + 1)):
        if False:
            with open(filename, 'rb') as f:
                disallowed_pairs = pickle.load(f)
                break
        height_aux = abs(abs(x) - board_radius)
        height = board_radius if triangular else height_aux
        for y in range(-height, height + 1):
            if triangular and ((x < 0 and y < -height_aux) or (x > 0 and y > height_aux)):
                continue
            other = (x, y)
            disallowable_pairs_for_other = {}
            for t_root in range(num_types):
                disallowable_types = set()
                for t_other in range(num_types):
                    s1 = set(types[t_root])
                    s2 = set((x + xx, y + yy) for xx, yy in types[t_other])
                    allowable_locations = s1.union(s2)
                    if s1 != s2 and len(allowable_locations) != len(s1) + len(s2):
                        disallowable_types.add(t_other)
                        continue
                    pieces = get_all_tetris_pieces(n, other, allowable_locations,
                                                   triangular=triangular)
                    found_unique_decomposition = False
                    for piece in pieces:
                        remaining_allowable_locations = allowable_locations.difference(piece)
                        if len(remaining_allowable_locations) == 0:
                            found_unique_decomposition = True
                            break
                        else:
                            new_root = choose_arbitrarily(remaining_allowable_locations)
                            remaining_pieces = get_all_tetris_pieces(n, new_root,
                                               remaining_allowable_locations,
                                               triangular=triangular)
                            if len(remaining_allowable_locations) in \
                                    [len(piece) for piece in remaining_pieces]:
                                if found_unique_decomposition:
                                    found_unique_decomposition = False
                                    break
                                else:
                                    found_unique_decomposition = True
                    if not found_unique_decomposition:
                        disallowable_types.add(t_other)
                disallowable_pairs_for_other[t_root] = disallowable_types
            disallowable_pairs[other] = disallowable_pairs_for_other
    if refine:
        found_new = True
        num_rounds_new_added = -1
        num_new_pairs_found = 0
        while found_new:
            print("Refining...")
            found_new = False
            for x in tqdm(range(-board_radius, board_radius + 1)):
                height = abs(abs(x) - board_radius)
                for y in range(-height, height + 1):
                    other = (x, y)
                    for t_root in range(num_types):
                        for t_other in set(range(num_types)).difference(
                                       disallowable_pairs[other][t_root]):
                            for x2 in range(-board_radius, board_radius + 1):
                                height2 = abs(abs(x2) - board_radius)
                                for y2 in range(-height2, height2 + 1):
                                    other2 = (x2, y2)
                                    other2_from_other = (x2 - x, y2 - y)
                                    if other2_from_other in disallowable_pairs and \
                                            len(disallowable_pairs[other2][t_root].union(
                                            disallowable_pairs[other2_from_other][t_other])) \
                                            == num_types:
                                        tiling = [[set() for col in range(2*board_radius + 1)] \
                                                   for row in range(2*board_radius + 1)]
                                        tiling[board_radius][board_radius] = {t_root}
                                        tiling[board_radius + x][board_radius + y] = {t_other}
                                        found_new = True
                                        num_new_pairs_found += 1
                                        disallowable_pairs[other][t_root].add(t_other)
            num_rounds_new_added += 1
        print(f"Num rounds refined: {num_rounds_new_added}\nNum new pairs: {num_new_pairs_found}")
    with open(filename, 'wb') as f:
        pickle.dump(disallowable_pairs, f)
    return disallowable_pairs


def print_nicely(n, tiling, plot=False, recolor=False, just_return=False):
    if tiling is None:
        print("[NONE]\n\n")
        return
    side_length = len(tiling)
    box = len(tiling[0])
    if side_length == 1 or box != len(tiling[1]):
        box = False
    types = generate_types(n)
    last_id = 0
    if box:
        printable_grid = [[0 for __ in range(box)] for _ in range(side_length)]
    else:
        printable_grid = [[0 for _ in range(side_length + n - 1 - row)] \
                          for row in range(side_length + n - 1)]
    for row_root in range(side_length):
        for col_root in range(box if box else (side_length - row_root)):
            possible_types = tiling[row_root][col_root]
            if len(possible_types) == 1:
                the_type = choose_arbitrarily(possible_types)
                if the_type == -1:
                    continue
                current_id = printable_grid[row_root][col_root]
                if current_id == 0:
                    last_id += 1
                    if last_id == 27 and not recolor:
                        last_id = 33
                    elif last_id == 59 and not recolor:
                        last_id = 1
                    for d_row, d_col in types[the_type]:
                        row_other = row_root + d_row
                        col_other = col_root + d_col
                        if row_other >= 0 and col_other >= 0 and \
                            (not box and row_other + col_other < side_length + n - 1 or \
                            (box and row_other < side_length and col_other < box)):
                            printable_grid[row_other][col_other] = last_id
    if just_return:
        return printable_grid
    if plot:
        if recolor:
            recolor_map = [random.random() for _ in range(10000)]
            for i in range(side_length):
                for j in range(box):
                    printable_grid[i][j] = recolor_map[printable_grid[i][j]]
        global test_num
        im = plt.imshow(printable_grid, interpolation="nearest")
        plt.axis('off')
        im.set_data(printable_grid)
        plt.savefig("Plots/T%i.png" % test_num)
    else:
        print("\n".join(["".join(map(lambda x: chr(64 + x) if x > 0 else " ",
                     printable_grid[row])) for row in range(side_length if box else \
                                                            (side_length + n - 1))]))
        print("")


def rotation_map(n):
    type_to_blocks = generate_types(n)
    num_types = len(type_to_blocks)
    blocks_to_type = {}
    for t in range(num_types):
        blocks_to_type[type_to_blocks[t]] = t
    r = {}
    for t in range(num_types):
        original_blocks = type_to_blocks[t]
        rotated_blocks = tuple(sorted((y, -x) for x, y in original_blocks))
        r[t] = blocks_to_type[rotated_blocks]
    return r


def get_oeis_str(n, tiling):
    grid = print_nicely(n, tiling, just_return=True)
    num_rows = len(grid)
    num_columns = len(grid[0])
    s = "." + ("_" * (2*num_columns - 1)) + "."
    row_template = ["|"] + ["_" for _ in range(2*num_columns - 1)] + ["|"]
    for i in range(num_rows):
        row = row_template.copy()
        for j in range(num_columns):
            if i < num_rows - 1 and grid[i][j] == grid[i + 1][j]:
                row[2*j + 1] = " "
        for j in range(num_columns - 1):
            c = "|"
            if grid[i][j] == grid[i][j + 1]:
                v1 = 1 if row[2*j + 1] == "_" else 0
                v2 = 1 if row[2*j + 3] == "_" else 0
                v3 = v1 + v2
                if v3 == 0:
                    c = " "
                elif v3 == 1:
                    c = "."
                elif v3 == 2:
                    c = "_"
                else:
                    raise Exception("This can't happen.")
            row[2*j + 2] = c
        s += "\n" + "".join(row)
    return s


test_num = 0
if len(argv) > 1:
    test_num = int(argv[1])
    print(f"Running test {test_num}...\n")
else:
    print("Usage: 'python3 locked_polyomino_tilings test_num'")


if test_num == 1:  # Simplest grid where locked polyomino tilings exist: 6 X 4 into 3-ominoes
    n = 3
    num_tilings, sample_tiling = tile_grid(n, side_length=6, box=4)
    print(f"Num tilings: {num_tilings}\n")
    print_nicely(n, sample_tiling)
elif test_num == 2:  # Finds the only known locked 4-omino tiling, which is on a 10 X 10 grid
    n = 4
    num_tilings, sample_tiling = tile_grid(n, side_length=10, box=10)
    print(f"Num tilings: {num_tilings}\n")
    print_nicely(n, sample_tiling)
elif test_num == 3:  # Search for ways to complete top-left corner of grid with locked 4-ominoes
    n = 4
    for side_length in range(2, 16):
        num_tilings, sample_tiling = tile_grid(n, side_length)
        print(f"Side length: {side_length}")
        print(f"Num tilings: {num_tilings}\n")
        print_nicely(n, sample_tiling)
        print("\n\n")
elif test_num == 4:  # Finds the smallest known locked-5-omino tiling, which is on a 20 X 20 grid
    n = 5
    # Setting rot_sym=4 only searches for 4-fold symmetric tilings. Saves a ton of time.
    num_tilings, sample_tiling = tile_grid(n, side_length=20, box=20, rot_sym=4)
    print(f"Num tilings: {num_tilings}\n")
    print_nicely(n, sample_tiling)
elif test_num == 5:  # Prove that top-left corner tile must be 269 (P), 274 (L), or 279 (Z)
    n = 5
    # We compute this once and pass in so it doesn't have load from disk each time
    disallowable_pairs = generate_disallowable_pairs(n)
    for side_length in range(1, 6):  # Only get the contradiction starting at side_length = 5
        print(f"\n**************** SIDE_LENGTH: {side_length} ****************\n")
        for tile in [256, 258, 259, 260, 261, 262, 263, 264, 269, 270, 271, 273, 274, 275, 276, \
                     277, 278, 279, 280, 281, 296, 297, 298, 299, 301, 302, 303, 304, 309, 310, \
                     311, 313, 314, 252, 253, 254, 255]:
            if tile in [269, 271, 274, 253, 279, 299]:  # 271, 253, and 299 are flips, redundant.
                continue
            num_tilings, sample_tiling = tile_grid(n, side_length, first_tile=tile,
                                                   disallowable_pairs=disallowable_pairs)
            print(f"Num tilings: {num_tilings}\n")
            print_nicely(n, sample_tiling)
elif test_num == 6:  # These next three tests find all symmetric 30 X 30 locked 5-omino tilings
    n = 5
    num_tilings, sample_tiling = tile_grid(n, side_length=30, box=30,\
            rot_sym=4, first_tile=269, output_tilings=True)
    print(f"Num tilings: {num_tilings}\n")
    print_nicely(n, sample_tiling)
elif test_num == 7:  # From test 5, we know we only have to check first tiles 269, 274, and 279
    n = 5
    num_tilings, sample_tiling = tile_grid(n, side_length=30, box=30,\
            rot_sym=4, first_tile=274, output_tilings=True)
    print(f"Num tilings: {num_tilings}\n")
    print_nicely(n, sample_tiling)
elif test_num == 8:  # Tilings from these three tests are written to the Outputs directory
    n = 5
    num_tilings, sample_tiling = tile_grid(n, side_length=30, box=30,\
            rot_sym=4, first_tile=279, output_tilings=True)
    print(f"Num tilings: {num_tilings}\n")
    print_nicely(n, sample_tiling)
elif test_num == 9:  # Output tilings from tests 6, 7, and 8 in format of AllSymmetricTilings.txt
    n = 5
    lines = []
    counters = {}
    for filenumber in [6, 7, 8]:
        with open(f"Outputs/T{filenumber}.txt", "r") as f:
            for line in f:
                if "{" in line:
                    tiling = eval(line)
                    first_char = {279: "Z", 274: "L", 269: "P"}[choose_arbitrarily(tiling[0][0])]
                    name = f"S{len(tiling)}-{first_char}"
                    if name in counters:
                        counters[name] += 1
                    else:
                        counters[name] = 1
                    print(f"{name}{counters[name]:02}\n")
                    print(tiling)
                    print("")
                    print_nicely(n, tiling)
                    print("\n")
elif test_num == 10:  # Output tilings from tests 6, 7, and 8 in OEIS format
    n = 5
    lines = []
    counters = {}
    for filenumber in [6, 7, 8]:
        with open(f"Outputs/T{filenumber}.txt", "r") as f:
            for line in f:
                if "{" in line:
                    tiling = eval(line)
                    first_char = {279: "Z", 274: "L", 269: "P"}[choose_arbitrarily(tiling[0][0])]
                    name = f"S{len(tiling)}-{first_char}"
                    if name in counters:
                        counters[name] += 1
                    else:
                        counters[name] = 1
                    print(f"{name}{counters[name]:02}\n")
                    print(get_oeis_str(n, tiling))
                    print("\n")

