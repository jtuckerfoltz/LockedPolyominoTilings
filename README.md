# Locked Polyomino Tilings



Searches for locked polyomino tilings, as described in Section 4 of this paper:

https://arxiv.org/abs/2307.15996

Also see the relevant OEIS sequence:

TODO (under submission)

SVG images of all known 4-fold symmetric, locked 5-omino tilings are in the ``Images`` directory.

## Running the code.

The code for enumerating locked polyomino tilings is contained in ``locked_polyomino_tilings.py``. The code is only very lightly documented, containing examples of how to use the core functions at the bottom of the file in 10 numbered code blocks. Not all functionality has corresponding tests that use it; for example, there is an old plotting function that uses matplotlib to visualize tilings, which has now been replaced by a far-superior SVG visualization tool. Such relics are left in the code and mostly still work, but are not essential.

It is instructive to go through an example of how to generate all of the 30 X 30 tilings in the file ``All5OminoTilings.txt`` and then use this file to produce all of the images in the ``Images`` directory. You should follow along by reading the comments in the Python files. First, run:

``python3 locked_polyomino_tilings.py 6``

``python3 locked_polyomino_tilings.py 7``

``python3 locked_polyomino_tilings.py 8``

These can be run in parallel, and may each take several hours to finish. Important note: If you do not download the .p files, they will be generated the first time the code is run for each polyomino size, which may take several seconds for $n = 3$, several minutes for $n = 4$, and several days for $n = 5$. Outputs will be stored in three separate files in an ``Outputs`` directory. Once they are done, run

``python3 locked_polyomino_tilings.py 9``

and cut/paste from the terminal (or redirect output) into a new file ``5OminoTilings.txt``. Make sure to include a line return at the very end of the file. The file ``All5OminoTilings.txt`` was created in this exact same way, except that it also included outputs from runs on the 20 X 20 and 35 X 35 grids (the latter of which took more than a week to run). Finally, to create the SVGs and store them in the ``Images`` directory, run:

``python3 print_to_svg.py All5OminoTilings.txt ColorCode5Ominoes.txt Images``

This uses the coloring defined in ``ColorCode5Ominoes.txt``, which you can edit first if you want to change the color scheme.
