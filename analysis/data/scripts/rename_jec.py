#!/bin/bash

echo "=== Renaming files Summer24Prompt24_* ==="

rename_suffix() {
  local old_pat="$1"
  local ext="$2"
  
  find Summer24Prompt24_*/ -type f -name "*${old_pat}.txt" | while read -r file; do
    new_file="${file%.txt}.${ext}.txt"
    echo "Renombrando: $(basename "$file") -> $(basename "$new_file")"
    mv "$file" "$new_file"
  done
}

rename_suffix "_Uncertainty_AK4PFPuppi" "junc"
rename_suffix "_UncertaintySources_AK4PFPuppi" "junc"
rename_suffix "_L3Absolute_AK4PFPuppi" "jec"
rename_suffix "_L2Residual_AK4PFPuppi" "jec"
rename_suffix "_L2Relative_AK4PFPuppi" "jec"
rename_suffix "_L2L3Residual_AK4PFPuppi" "jec"
rename_suffix "_L1FastJet_AK4PFPuppi" "jec"
rename_suffix "_PtResolution_AK4PFPuppi" "jr"

echo "=== Proceso finalizado ==="