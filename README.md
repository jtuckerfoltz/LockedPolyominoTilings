# Locked Polyomino Tilings

Searches for locked polyomino tilings, as described in Section 4 of this paper:

https://arxiv.org/abs/2307.15996

SVG images of all known 4-fold symmetric, locked 5-omino tilings are in the Images directory.

## Running the code.

The code for enumerating locked polyomino tilings is contained in ``locked_polyomino_tilings.py``. The code is only very lightly documented, containing examples of how to use the core functions at the bottom of the file in 10 numbered code blocks. Not all functionality has corresponding tests that use it; for example, there is an old plotting function that uses matplotlib to visualize tilings, which has now been replaced by a far-superior SVG visualization tool. Such relics are left in the code and they mostly still work, but are not essential.

Note: If you do not download the .p files, they will be generated the first time the code is run for each polyomino size, which may take several seconds for $n = 3$, minutes for $n = 4$, and days for $n = 5$.
