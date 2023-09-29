# Locked Polyomino Tilings



Searches for locked polyomino tilings, as described in Section 4 of this paper:

https://arxiv.org/abs/2307.15996

SVG images of all known 4-fold symmetric, locked 5-omino tilings are in the ``Images`` directory.

## Running the code.

The code for enumerating locked polyomino tilings is contained in ``locked_polyomino_tilings.py``. The code is only very lightly documented, containing examples of how to use the core functions at the bottom of the file in 10 numbered code blocks. Not all functionality has corresponding tests that use it; for example, there is an old plotting function that uses matplotlib to visualize tilings, which has now been replaced by a far-superior SVG visualization tool. Such relics are left in the code and mostly still work, but are not essential.

It is instructive to go through an example of how to generate all of the 30 X 30 tilings in the file ``All5OminoTilings.txt`` and then use this file to produce all of the images in the ``Images`` directory. First, run
``python3 locked_polyomino_tilings.py 6``
``python3 locked_polyomino_tilings.py 7``
``python3 locked_polyomino_tilings.py 8``
These may each take several hours to finish. Note: if you do not download the .p files, they will be generated the first time the code is run for each polyomino size, which may take several seconds for $n = 3$, minutes for $n = 4$, and days for $n = 5$.
