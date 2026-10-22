import LockedHeptomino.Witness
import LockedHeptomino.CSPTable
namespace LockedHeptomino.Tests
set_option maxRecDepth 10000
set_option maxHeartbeats 0
def exampleWitness : SplitWitness := ⟨[(6,0),(5,0),(4,0),(3,0),(2,0),(1,0),(0,0)],[(6,1),(5,1),(4,1),(3,1),(2,1),(1,1),(0,1)],[(3,0),(2,1),(2,0),(1,1),(1,0),(0,1),(0,0)],[(6,1),(6,0),(5,1),(5,0),(4,0),(4,1),(3,1)]⟩

example : exampleWitness.check = true := by decide +kernel
example : ({ exampleWitness with firstLeft := [(0,0)] } : SplitWitness).check = false := by decide +kernel
example : ({ exampleWitness with
    secondLeft := exampleWitness.firstLeft
    secondRight := exampleWitness.firstRight } : SplitWitness).check = false := by decide +kernel
example : connectedOrder [(0,0),(2,0)] = false := by decide +kernel

open CSP

def permissive : RelationTable Nat := fun _ _ _ => 3
def initial : Domains Nat := fun _ => 3
example : check (treeExcludes permissive 1) (.empty 0) initial = false := by decide +kernel
example : check (treeExcludes permissive 1)
    (.revise 0 1 0 (.empty 0)) initial = false := by decide +kernel
example : check (treeExcludes permissive 1)
    (.split 0 (.cons 0 (.empty 0) .nil)) initial = false := by decide +kernel

end LockedHeptomino.Tests
