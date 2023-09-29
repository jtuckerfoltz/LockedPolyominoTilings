from sys import argv
import os


# Example usage: 'python3 print_to_svg.py 5OminoTilinings'
USAGE = "Usage: 'python3 print_to_svg.py tiling_file color_file output_directory'"

def preamble(num_rows, num_columns):
    num_rows_p = 80*num_rows
    num_columns_p = 80*num_columns
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<svg xmlns="http://www.w3.org/2000/svg" style="background-color: rgb(255, 255, 255);" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="{num_columns_p}px" height="{num_rows_p}px" viewBox="0 0 {num_columns_p} {num_rows_p}"><defs/><g>'

POSTAMBLE = '</g></svg>\n'


def choose_arbitrarily(s):
    for x in s:
        return x


def flip(coordinates):
    return tuple((coordinate[0], -coordinate[1]) for coordinate in coordinates)


def rotate(coordinates):
    return tuple((coordinate[1], -coordinate[0]) for coordinate in coordinates)


def read_array(str_grid):
    num_rows = len(str_grid)
    num_columns = max(len(row) for row in str_grid)
    grid = []
    for s in str_grid:
        row = list(s)
        for _ in range(num_columns - len(row)):
            row.append(" ")
        grid.append(row)
    return grid, num_rows, num_columns


def canonize(coordinates):
    min_i = min(coordinate[0] for coordinate in coordinates)
    min_j = min(coordinate[1] for coordinate in coordinates)
    canonical_form = tuple(sorted((coordinate[0] - min_i, coordinate[1] - min_j)
        for coordinate in coordinates))
    return canonical_form


def horizontal_edge_coordinates(i, j):
    return (80*i + 40, 10 + 80*j, 80*i + 40, 150 + 80*j)


def vertical_edge_coordinates(i, j):
    return (80*i + 10, 40 + 80*j, 80*i + 150, 40 + 80*j)


def get_edges_in_piece(grid, num_rows, num_columns, i, j):
    edges = []
    c = grid[i][j]
    processed = set()
    queue = {(i, j)}
    while len(queue) > 0:
        cell = choose_arbitrarily(queue)
        i, j = cell
        if i > 0 and grid[i - 1][j] == c:
            new_i = i - 1
            new_j = j
            new_cell = (new_i, new_j)
            edges.append(vertical_edge_coordinates(i - 1, j))
            if new_cell not in processed:
                queue.add(new_cell)
        if i < num_rows - 1 and grid[i + 1][j] == c:
            new_i = i + 1
            new_j = j
            new_cell = (new_i, new_j)
            edges.append(vertical_edge_coordinates(i, j))
            if new_cell not in processed:
                queue.add(new_cell)
        if j > 0 and grid[i][j - 1] == c:
            new_i = i
            new_j = j - 1
            new_cell = (new_i, new_j)
            edges.append(horizontal_edge_coordinates(i, j - 1))
            if new_cell not in processed:
                queue.add(new_cell)
        if j < num_columns - 1 and grid[i][j + 1] == c:
            new_i = i
            new_j = j + 1
            new_cell = (new_i, new_j)
            edges.append(horizontal_edge_coordinates(i, j))
            if new_cell not in processed:
                queue.add(new_cell)
        queue.remove(cell)
        processed.add(cell)
    canonical_form = canonize(processed)
    return edges, canonical_form


def get_equivalences(str_grid):
    equivalences = set()
    grid, num_rows, num_columns = read_array(str_grid)
    for i in range(num_rows):
        for j in range(num_columns):
            c = grid[i][j]
            if c != " ":
                edges_list, coordinates = get_edges_in_piece(grid, num_rows, num_columns, i, j)
                for f_num in range(2):
                    for r_num in range(4):
                        equivalences.add(canonize(coordinates))
                        coordinates = rotate(coordinates)
                    coordinates = flip(coordinates)
    return equivalences


def get_edges(str_grid, color_map):
    edges = {}
    grid, num_rows, num_columns = read_array(str_grid)
    for i in range(num_rows):
        for j in range(num_columns):
            c = grid[i][j]
            if c != " ":
                edges_list, canonical_form = get_edges_in_piece(grid, num_rows, num_columns, i, j)
                color = color_map[canonical_form]
                for edge in edges_list:
                    edges[edge] = color
    return edges, num_rows, num_columns


def make_xml_cell(edge, color, id_num):
    return f'<path d="M {edge[0]} {edge[1]} L {edge[2]} {edge[3]}" fill="none" stroke="{color}" stroke-width="60" stroke-miterlimit="10" pointer-events="stroke"/>'


if __name__ == "__main__":
    try:
        tiling_filename = argv[1]
        color_filename = argv[2]
        output_directory = argv[3]
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
    except:
        print(USAGE)
        exit()


    color_map = {}
    with open(color_filename, "r") as f_read:
        next_is_color = True
        for line in f_read:
            s = line.rstrip()
            if next_is_color:
                if "#" in s:
                    color = s
                    grid = []
                    next_is_color = False
            else:
                if len(s) > 0:
                    grid.append(s)
                elif len(grid) > 0:
                    equivalences = get_equivalences(grid)
                    for e in equivalences:
                        color_map[e] = color
                    next_is_color = True

    with open(tiling_filename, "r") as f_read:
        next_is_name = True
        for line in f_read:
            s = line.rstrip()
            if "{" in s or "..." in s:
                continue
            if next_is_name:
                if len(s) > 0:
                    name = s
                    grid = []
                    next_is_name = False
            else:
                if len(s) > 0:
                    grid.append(s)
                elif len(grid) > 0:
                    edges, num_rows, num_columns = get_edges(grid, color_map)
                    xml_cells = []
                    id_num = 0
                    for edge, color in edges.items():
                        id_num += 1
                        xml_cells.append(make_xml_cell(edge, color, id_num))
                    with open(f"{output_directory}/{name}.svg", "w") as f_write:
                        f_write.write(preamble(num_rows, num_columns) + "".join(xml_cells) + POSTAMBLE)
                    next_is_name = True

