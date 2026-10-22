import LockedHeptomino.RelationCertificates

namespace LockedHeptomino.RelationNegativeControls

open Generated Encoding

set_option maxRecDepth 16384
set_option exponentiation.threshold 16384

-- The arithmetic certificate accepts this actual pair.
example : packedFlexibleCheck typeInfo witnessCode 0 65 213719302144 = true := by decide

-- Changing the target shape, witness code, or translation breaks the certificate.
example : packedFlexibleCheck typeInfo witnessCode 0 65 213719302145 = false := by decide
example : packedFlexibleCheck typeInfo (fun i => witnessCode i + 1)
    0 65 213719302144 = false := by decide
example : packedFlexibleCheck typeInfo witnessCode 0 65
    (213719302144 + 34359738368) = false := by decide

-- Coverage cannot silently omit the pair witnesses required by this row.
example : localRowCheck 0 65 [] = false := by decide

-- Two references to the same tile must remain compatible.
example : typeShape 17 = translate (direction 0) (typeShape 6) := by decide
example : (overlapForbidden incidence sameIndex 0 17 (typeCells 17)).testBit 6 = false := by
  decide

end LockedHeptomino.RelationNegativeControls
