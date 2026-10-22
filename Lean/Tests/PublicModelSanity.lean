import Main
import LockedHeptomino.Witness

/-!
Concrete checks of the definitions displayed in `Main.lean`.

Diagonal contact is not adjacency, a two-edge path is admitted, and two explicit
different tilings of a 7 × 2 rectangle witness that `Nondegenerate` is possible.
The order checker proves the connectivity and cardinality of the four listed
tiles; the tested tilings use the public structure.
-/

namespace HeptominoProof.Tests

example : ¬ Adjacent (0, 0) (1, 1) := by
  unfold Adjacent
  decide

example : Relation.ReflTransGen
    (StepIn {(0, 0), (1, 0), (1, 1)}) (0, 0) (1, 1) :=
  .tail (b := (1, 0))
    (.tail .refl (by unfold StepIn Adjacent; decide))
    (by unfold StepIn Adjacent; decide)

example : ¬ Connected ∅ := by
  intro h
  exact Finset.not_nonempty_empty h.1

private def twoTileTiling (a b : List Cell)
    (ha : LockedHeptomino.tileOrderCheck a = true)
    (hb : LockedHeptomino.tileOrderCheck b = true)
    (hd : Disjoint a.toFinset b.toFinset)
    (hu : a.toFinset ∪ b.toFinset = rectangle 7 2) : Tiling 7 7 2 where
  tiles := {a.toFinset, b.toFinset}
  connected := by
    intro s hs
    simp only [Finset.mem_insert, Finset.mem_singleton] at hs
    rcases hs with rfl | rfl
    · exact (LockedHeptomino.tileOrderCheck_sound a ha).1
    · exact (LockedHeptomino.tileOrderCheck_sound b hb).1
  card := by
    intro s hs
    simp only [Finset.mem_insert, Finset.mem_singleton] at hs
    rcases hs with rfl | rfl
    · exact (LockedHeptomino.tileOrderCheck_sound a ha).2
    · exact (LockedHeptomino.tileOrderCheck_sound b hb).2
  disjoint := by
    intro s hs t ht hst
    simp only [Finset.mem_insert, Finset.mem_singleton] at hs ht
    rcases hs with rfl | rfl <;> rcases ht with rfl | rfl
    · exact False.elim (hst rfl)
    · exact hd
    · exact hd.symm
    · exact False.elim (hst rfl)
  covers := by simpa using hu

/-- Two straight, seven-cell columns. -/
def straightTiling : Tiling 7 7 2 := twoTileTiling
  [(6,0), (5,0), (4,0), (3,0), (2,0), (1,0), (0,0)]
  [(6,1), (5,1), (4,1), (3,1), (2,1), (1,1), (0,1)]
  (by decide) (by decide) (by decide) (by decide)

/-- Two bent tiles filling the same rectangle. -/
def bentTiling : Tiling 7 7 2 := twoTileTiling
  [(3,0), (2,1), (2,0), (1,1), (1,0), (0,1), (0,0)]
  [(6,1), (6,0), (5,1), (5,0), (4,0), (4,1), (3,1)]
  (by decide) (by decide) (by decide) (by decide)

example : bentTiling.tiles ≠ straightTiling.tiles := by decide

example : Nondegenerate straightTiling :=
  ⟨bentTiling, by decide⟩

example : Nondegenerate bentTiling :=
  ⟨straightTiling, by decide⟩

/-- Two straight triominoes in a 2 × 3 rectangle can be replaced by two Ls.
This would fail if rigidity still tested seven-cell replacements. -/
example : ¬ RigidPair 3
    {(0,0), (0,1), (0,2)} {(1,0), (1,1), (1,2)} := by
  let c : Finset Cell := {(0,0), (0,1), (1,0)}
  let d : Finset Cell := {(0,2), (1,1), (1,2)}
  have hc : Connected c := by
    have hs : ([(0,1), (1,0), (0,0)] : List Cell).toFinset = c := by decide
    rw [← hs]
    exact LockedHeptomino.connectedOrder_sound _ (by decide)
  have hd : Connected d := by
    have h := LockedHeptomino.connectedOrder_sound
      [(0,2), (1,1), (1,2)] (by decide)
    exact h
  intro h
  have split := h c d hc hd (by decide) (by decide) (by decide) (by decide)
  have different : c ≠ ({(0,0), (0,1), (0,2)} : Finset Cell) ∧
      c ≠ ({(1,0), (1,1), (1,2)} : Finset Cell) := by decide
  exact split.elim (fun h => different.1 h.1) (fun h => different.2 h.1)

end HeptominoProof.Tests
