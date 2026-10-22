import Lake
open Lake DSL

package lockedHeptomino where
  leanOptions := #[⟨`autoImplicit, false⟩, ⟨`Elab.async, false⟩]
  moreLeanArgs := #["-j1", "-s65536"]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @
  "c44e0c8ee63ca166450922a373c7409c5d26b00b"

@[default_target]
lean_lib Proof where
  roots := #[`Main, `Tests, `LockedHeptomino]

/-- Build Main and the sanity tests with one compiler process at a time. -/
@[default_script]
script verify (_args) do
  let child ← IO.Process.spawn {
    cmd := (← getLake).toString
    args := #["build", "Main", "Tests"]
    cwd := (← getRootPackage).dir
    env := #[("LEAN_NUM_THREADS", some "1")] }
  child.wait
