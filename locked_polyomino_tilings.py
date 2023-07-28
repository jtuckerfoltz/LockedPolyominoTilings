import itertools
import random
from tqdm import tqdm
import pickle
import os.path
import networkx as nx
from matplotlib import pyplot as plt


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
    if not (allowable_locations is None) and root not in allowable_locations:
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
            if finalized[row][col]:
                continue
            num_possibilities = len(grid[row][col])
            if num_possibilities == 0:
                return -2, -2
            else:
                obj_value = num_possibilities * (row + col + 5)
                if obj_value < best_obj_value:
                    best_row = row
                    best_col = col
                    best_obj_value = obj_value
    return best_row, best_col


def pf_poss_lex_1(side_length, grid, box=None):
    best_row = -1
    best_col = -1
    best_obj_value = 999999999999
    for row in range(side_length):
        for col in range(box if box else (side_length - row)):
            num_possibilities = len(grid[row][col])
            if num_possibilities == 0:
                return -2, -2
            elif num_possibilities == 1:
                pass
            else:
                obj_value = num_possibilities
                if obj_value < best_obj_value:
                    best_row = row
                    best_col = col
                    best_obj_value = obj_value
    return best_row, best_col


def explore(n, types, side_length, priority_function, disallowable_pairs, grid, finalized,
            box=None, scout=0, rot_sym=None, stop_when_found=False):
    row_root, col_root = priority_function(side_length, grid, finalized, box)
    if row_root == -1:  # Exactly one choice for each cell, i.e., complete tiling.
        return 1, grid
    elif row_root == -2:  # No valid tilings.
        return 0, None
    else:  # Need to expand search on all possibilities for cell chosen by priority function.
        possible_types = grid[row_root][col_root]
        tilings = []
        total_num_tilings = 0
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


def tile_grid(n, side_length, priority_function, disallowable_pairs=None, box=None, scout=0,
              triangle_box=False, rot_sym=None, stop_when_found=False):
    if box and ((side_length * box) % n != 0):
        return 0, None
    types = generate_types(n)
    if disallowable_pairs is None:
        disallowable_pairs = generate_disallowable_pairs(n)
    grid = [[set() for _ in range(box if box else (side_length - row))] \
            for row in range(side_length)]
    finalized = [[False for _ in range(box if box else (side_length - row))] \
            for row in range(side_length)]
    for row_root in range(side_length):
        for col_root in range(box if box else (side_length - row_root)):
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
                if ok:
                    grid[row_root][col_root].add(t)
    if rot_sym:
        rot_sym = rotation_map(n), rot_sym
    return explore(n, types, side_length, priority_function, disallowable_pairs,
                   grid, finalized, box=box, rot_sym=rot_sym,
                   stop_when_found=stop_when_found)


def generate_disallowable_pairs(n, triangular=False, refine=True):
    filename = f"disallowable_pairs_{'T_' if triangular else ''}{n}.p"
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            return(pickle.load(f))
    types = generate_types(n)
    num_types = len(types)
    board_radius = 3*n if refine else 2*n - 2
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
                    allowable_locations = set(types[t_root]
                                        + tuple((x + xx, y + yy) for xx, yy in types[t_other]))
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
                            if len(remaining_pieces) == 0:
                                pass
                            elif len(remaining_pieces) == 1:
                                if found_unique_decomposition:
                                    found_unique_decomposition = False
                                    break
                                else:
                                    found_unique_decomposition = True
                            else:
                                raise Exception(f"Remaining pieces: {remaining_pieces}")
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
    if box != len(tiling[1]):
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
                current_id = printable_grid[row_root][col_root]
                if current_id == 0:
                    last_id += 1
                    if last_id == 27 and not recolor:
                        last_id = 1
                    for d_row, d_col in types[choose_arbitrarily(possible_types)]:
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


test_num = 1
print(f"Running test {test_num}...\n")


if test_num == 1:  # Search for locked 4-omino tilings.
    n = 4
    for graph_size in range(n, 401, n):
        print(f"**Graph size: {graph_size}**\n")
        for side_length in range(2, graph_size):
            box_frac = graph_size/side_length
            box = int(box_frac)
            if box_frac == box and box <= side_length and box > 1:
                num_tilings, sample_tiling = tile_grid(n, side_length, pf_mult_1, box=box)
                print(f"Grid dimensions: {side_length} X {box}")
                print(f"Num tilings: {num_tilings}\n")
                if not sample_tiling is None:
                    print_nicely(n, sample_tiling)
elif test_num == 2:  # Search for symmetric locked 4-omino tilings.
    n = 4
    disallowable_pairs = generate_disallowable_pairs(n)
    for side_length in range(2, 31):
        for box in [side_length]:
            num_tilings, sample_tiling = tile_grid(n, side_length, pf_mult_1, \
                                                   disallowable_pairs, box=box, rot_sym=4)
            print(f"Grid dimensions: {side_length} X {box}")
            print(f"Num tilings: {num_tilings}\n")
            if not sample_tiling is None:
                print_nicely(n, sample_tiling)
elif test_num == 3:  # Search for ways to complete top-left corner of grid with locked 4-ominoes.
    n = 4
    disallowable_pairs = generate_disallowable_pairs(n)
    for side_length in range(2, 20):
        num_tilings, sample_tiling = tile_grid(n, side_length, pf_mult_1, disallowable_pairs)
        print(f"Side length: {side_length}")
        print(f"Num tilings: {num_tilings}\n")
        print_nicely(n, sample_tiling)
        print("\n\n")
elif test_num == 4:  # Search for locked 5-omino tilings.
    n = 5
    disallowable_pairs = generate_disallowable_pairs(n)
    for side_length in range(2, 20):
        for box in range(1, side_length + 1):
            num_tilings, sample_tiling = tile_grid(n, side_length, pf_mult_1,
                                                   disallowable_pairs, box=box)
            print(f"Grid dimensions: {side_length} X {box}")
            print(f"Num tilings: {num_tilings}\n")
            if not sample_tiling is None:
                print_nicely(n, sample_tiling)
elif test_num == 5:  # Search for symmetric locked 5-omino tilings.
    n = 5
    disallowable_pairs = generate_disallowable_pairs(n)
    for side_length in range(2, 26):
        for box in range(side_length, side_length + 1):
            num_tilings, sample_tiling = tile_grid(n, side_length, pf_mult_1, disallowable_pairs, box=box, rot_sym=4)
            print(f"Grid dimensions: {side_length} X {box}")
            print(f"Num tilings: {num_tilings}\n")
            if not sample_tiling is None:
                print_nicely(n, sample_tiling)
elif test_num == 6:  # Search for ways to complete top-left corner of grid with locked 5-ominoes.
    n = 5
    disallowable_pairs = generate_disallowable_pairs(n)
    for side_length in range(2, 15):
        num_tilings, sample_tiling = tile_grid(n, side_length, pf_mult_1, disallowable_pairs)
        print(f"Side length: {side_length}")
        print(f"Num tilings: {num_tilings}\n")
        print_nicely(n, sample_tiling)
        print("\n\n")

