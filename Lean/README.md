Notes: The entire Lean directory, including the directions below, are AI-generated. You will need to unzip the large LockedHeptomino.zip directory after downloading.

# Heptomino rectangle proof

Open `Main.lean` to inspect the mathematical statements and all of their problem-specific definitions. `Tiling size height width` is a partition into connected tiles of the specified size. `Locked` means that no pair of tiles can be repartitioned into a different pair of connected tiles of that same size. `Nondegenerate` means another unlabelled tiling of the same size and rectangle exists. There are no symmetry assumptions.

The two theorems use these same definitions:

- No nondegenerate locked tiling of size **7** exists on any rectangle.
- A nondegenerate locked tiling of size **3** exists on the **6 × 6** rectangle: the explicit tiling in Figure 2 of “Locked Polyomino Tilings”.

The Figure 2 construction is in `LockedHeptomino/TriominoExample.lean`. It lists the twelve tiles, checks their coverage and connectivity, and verifies that every pair has only its original connected repartition. `TriominoChecks.lean` proves that the finite check covers all possible repartitions. A second, straight-triomino tiling witnesses nondegeneracy. `Main.lean` only assembles these checked facts into its public `Tiling` structure.

The axiom checks in `Main.lean` reject any dependencies beyond the displayed standard axioms. The sanity tests also exhibit two straight triominoes that can be repartitioned into two Ls, ensuring that size-3 rigidity is not vacuous.

## Verify

With Lean installed through elan, Git, and curl available, open a terminal in this directory. On a new installation, first download the pinned libraries and their official compiled cache:

```sh
lake exe cache get Mathlib.Algebra.BigOperators.Group.Finset.Basic Mathlib.Algebra.BigOperators.Ring.List Mathlib.Data.Finset.Powerset Mathlib.Data.Nat.Prime.Defs Mathlib.Tactic.IntervalCases Mathlib.Tactic.Ring
```

Then verify the proof with:

```sh
lake run
```

The entire `lake run` script starts `lake build Main Tests`, sets `LEAN_NUM_THREADS=1`, and returns the build's exit status. It has no download logic or custom verification logic. `Main` imports the proof implementations, so Lake builds those dependencies before checking both public theorems and their axiom guards. `Tests` adds the sanity tests.

To invoke the standard build directly instead of the script, use this equivalent command:

```sh
LEAN_NUM_THREADS=1 lake build Main Tests
```

The `lean-toolchain` file selects Lean 4.19.0. Initial library setup needs internet access; with dependencies installed, verification can run offline. The initial proof build may take hours. Later runs reuse outputs that Lake determines are up to date. A successful run ends with `Build completed successfully.` Messages about `exponentiation.threshold` are nonfatal simplifier warnings; they do not skip kernel verification.

Extract the complete source archive into a new directory on each computer. The archive contains no compiler, dependencies, symbolic links, or compiled proof files. Do not overlay it on an older project. Lake creates a local `.lake` directory for downloads and build outputs; do not transfer that directory between computers.

## Files

- `Main.lean`: size-parameterized definitions, both public theorems, and exact axiom checks.
- `LockedHeptomino/TriominoExample.lean`: Figure 2 construction and proof.
- `LockedHeptomino/TriominoChecks.lean`: soundness of the finite triomino checks.
- `LockedHeptomino/`: proof implementation and generated certificate data, all in Lean source form. The certificates are checked by the Lean kernel during the build.
- `Tests.lean` and `Tests/`: concrete model examples and checks that invalid certificates are rejected.
- `lakefile.lean`: library build and the short `lake run` entry point.
- `lean-toolchain` and `lake-manifest.json`: exact compiler and library versions.

No Python scripts, shell scripts, search programs, or certificate generators are needed to verify this proof.
