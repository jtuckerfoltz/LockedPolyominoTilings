import LockedHeptomino.Proof
import LockedHeptomino.TriominoExample

namespace HeptominoProof

/-- Integer row and column coordinates of a grid cell. -/
abbrev Cell := Int × Int

/-- Sharing one edge of a unit square. -/
def Adjacent (p q : Cell) : Prop :=
  q ∈ ({(p.1 + 1, p.2), (p.1 - 1, p.2),
    (p.1, p.2 + 1), (p.1, p.2 - 1)} : Finset Cell)

/-- One edge step, with both endpoints inside the tile. -/
def StepIn (s : Finset Cell) (p q : Cell) : Prop :=
  p ∈ s ∧ q ∈ s ∧ Adjacent p q

/-- Nonempty, with a finite path of zero or more steps between any two cells.
`Relation.ReflTransGen r` is the standard reflexive transitive closure of `r`. -/
def Connected (s : Finset Cell) : Prop :=
  s.Nonempty ∧ ∀ p ∈ s, ∀ q ∈ s, Relation.ReflTransGen (StepIn s) p q

/-- Rows 0 through height-1 and columns 0 through width-1. -/
def rectangle (height width : Nat) : Finset Cell :=
  ((Finset.range height).product (Finset.range width)).image
    (fun p : Nat × Nat => ((p.1 : Int), (p.2 : Int)))

/-- A partition of the rectangle into connected tiles, each with `size` cells. -/
structure Tiling (size height width : Nat) where
  tiles : Finset (Finset Cell)
  connected : ∀ s ∈ tiles, Connected s
  card : ∀ s ∈ tiles, s.card = size
  disjoint : ∀ a ∈ tiles, ∀ b ∈ tiles, a ≠ b → Disjoint a b
  covers : tiles.biUnion id = rectangle height width

/-- Every connected repartition into two `size`-cell tiles is the same unordered pair. -/
def RigidPair (size : Nat) (a b : Finset Cell) : Prop :=
  ∀ c d : Finset Cell, Connected c → Connected d → c.card = size → d.card = size →
    Disjoint c d → c ∪ d = a ∪ b →
      (c = a ∧ d = b) ∨ (c = b ∧ d = a)

/-- No two distinct tiles can be replaced by a different pair. -/
def Locked {size height width : Nat} (t : Tiling size height width) : Prop :=
  ∀ a ∈ t.tiles, ∀ b ∈ t.tiles, a ≠ b → RigidPair size a b

/-- The same rectangle admits another unlabelled tiling. -/
def Nondegenerate {size height width : Nat} (t : Tiling size height width) : Prop :=
  ∃ u : Tiling size height width, u.tiles ≠ t.tiles

/-- No nondegenerate finite rectangle has a locked heptomino tiling. -/
theorem no_locked_nondegenerate_rectangle {height width : Nat}
    : ¬ ∃ t : Tiling 7 height width, Nondegenerate t ∧ Locked t := by
  rintro ⟨t, ⟨u, hu⟩, ht⟩
  let original {h w : Nat} (u : Tiling 7 h w) : LockedHeptomino.HeptominoTiling h w :=
    ⟨u.tiles, u.connected, u.card, u.disjoint, u.covers⟩
  exact LockedHeptomino.no_locked_nondegenerate_heptomino_rectangle
    (original t) ⟨original u, hu⟩ ht

-- Lean's three standard axioms; the exact dependency list is checked below.
#print propext
#print Classical.choice
#print Quot.sound

/-- info: 'HeptominoProof.no_locked_nondegenerate_rectangle' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms no_locked_nondegenerate_rectangle

open LockedHeptomino.TriominoExample in
/-- Figure 2 gives a nondegenerate locked tiling by three-cell tiles. -/
theorem exists_locked_triomino_rectangle
    : ∃ t : Tiling 3 6 6, Nondegenerate t ∧ Locked t := by
  let t : Tiling 3 6 6 :=
    ⟨tiles, tiles_connected, tiles_card, tiles_disjoint, tiles_covers⟩
  let u : Tiling 3 6 6 :=
    ⟨alternativeTiles, alternative_connected, alternative_card,
      alternative_disjoint, alternative_covers⟩
  exact ⟨t, ⟨u, alternative_different⟩, tiles_rigid⟩

/-- info: 'HeptominoProof.exists_locked_triomino_rectangle' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms exists_locked_triomino_rectangle

end HeptominoProof
