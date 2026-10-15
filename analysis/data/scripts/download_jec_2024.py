import urllib.request, os

def get_real_content(url, repo="JECDatabase"):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        content = response.read().decode("utf-8")
    
    if content.startswith("../"):
        target_path = content.strip().replace("../", "")
        real_url = f"https://raw.githubusercontent.com/cms-jet/{repo}/master/textFiles/{target_path}"
        return get_real_content(real_url, repo)
    return content

# ==========================================
# 1. JEC DATA (10 Eras)
# ==========================================
data_eras = [
    "Summer24Prompt24_RunCnib1_V5_DATA", "Summer24Prompt24_RunDnib1_V5_DATA",
    "Summer24Prompt24_RunEnib1_V5_DATA", "Summer24Prompt24_RunFnib1_V5_DATA",
    "Summer24Prompt24_RunFnib2_V5_DATA", "Summer24Prompt24_RunFnib3_V5_DATA",
    "Summer24Prompt24_RunGnib1_V5_DATA", "Summer24Prompt24_RunGnib2_V5_DATA",
    "Summer24Prompt24_RunHnib1_V5_DATA", "Summer24Prompt24_RunInib1_V5_DATA"
]

data_files = {
    "_Uncertainty_AK4PFPuppi.junc.txt": "_Uncertainty_AK4PFPuppi.txt",
    "_UncertaintySources_AK4PFPuppi.junc.txt": "_UncertaintySources_AK4PFPuppi.txt",
    "_L3Absolute_AK4PFPuppi.jec.txt": "_L3Absolute_AK4PFPuppi.txt",
    "_L2Residual_AK4PFPuppi.jec.txt": "_L2Residual_AK4PFPuppi.txt",
    "_L2Relative_AK4PFPuppi.jec.txt": "_L2Relative_AK4PFPuppi.txt",
    "_L2L3Residual_AK4PFPuppi.jec.txt": "_L2L3Residual_AK4PFPuppi.txt",
    "_L1FastJet_AK4PFPuppi.jec.txt": "_L1FastJet_AK4PFPuppi.txt"
}

base_jec = "https://raw.githubusercontent.com/cms-jet/JECDatabase/master/textFiles"

print("=== 1/4 DOWNLOADING JEC DATA ===")
for era in data_eras:
    os.makedirs(era, exist_ok=True)
    for out_ext, orig_ext in data_files.items():
        fname_orig = f"{era}{orig_ext}"
        fname_out = f"{era}{out_ext}"
        dest = os.path.join(era, fname_out)
        
        version_fallbacks = [era] + [
            era.replace("_V5_DATA", f"_V{v}_DATA") for v in range(4, 0, -1)
        ]
        
        downloaded = False
        for current_era in version_fallbacks:
            url = f"{base_jec}/{current_era}/{current_era}{orig_ext}"
            try:
                real_data = get_real_content(url, "JECDatabase")
                with open(dest, "w") as f:
                    f.write(real_data)
                print(f"OK JEC DATA: {dest} (from {current_era})")
                downloaded = True
                break
            except Exception:
                continue
                
        if not downloaded:
            print(f"WARNING: {fname_out} not found in any previous version.")

# ==========================================
# 2. JEC MC (Summer24Prompt24_V5_MC)
# ==========================================
jec_mc_era = "Summer24Prompt24_V5_MC"
jec_mc_files = {
    "_Uncertainty_AK4PFPuppi.junc.txt": "_Uncertainty_AK4PFPuppi.txt",
    "_UncertaintySources_AK4PFPuppi.junc.txt": "_UncertaintySources_AK4PFPuppi.txt",
    "_L3Absolute_AK4PFPuppi.jec.txt": "_L3Absolute_AK4PFPuppi.txt",
    "_L2Residual_AK4PFPuppi.jec.txt": "_L2Residual_AK4PFPuppi.txt",
    "_L2Relative_AK4PFPuppi.jec.txt": "_L2Relative_AK4PFPuppi.txt",
    "_L1FastJet_AK4PFPuppi.jec.txt": "_L1FastJet_AK4PFPuppi.txt"
}

print("\n=== 2/4 DOWNLOADING JEC MC (Summer24Prompt24_V5_MC) ===")
os.makedirs(jec_mc_era, exist_ok=True)

for out_ext, orig_ext in jec_mc_files.items():
    fname_orig = f"{jec_mc_era}{orig_ext}"
    fname_out = f"{jec_mc_era}{out_ext}"
    dest = os.path.join(jec_mc_era, fname_out)
    
    version_fallbacks = [jec_mc_era] + [
        f"Summer24Prompt24_V{v}_MC" for v in range(4, 0, -1)
    ]
    
    downloaded = False
    for current_era in version_fallbacks:
        url = f"{base_jec}/{current_era}/{current_era}{orig_ext}"
        try:
            real_data = get_real_content(url, "JECDatabase")
            with open(dest, "w") as f:
                f.write(real_data)
            print(f"OK JEC MC: {dest} (from {current_era})")
            downloaded = True
            break
        except Exception:
            continue
            
    if not downloaded:
        print(f"WARNING: {fname_out} not found in JEC MC.")

# ==========================================
# 3. JR MC (Summer24Prompt24_JRV2_MC)
# ==========================================
jr_mc_era = "Summer24Prompt24_JRV2_MC"
jr_mc_files = {
    "_PtResolution_AK4PFPuppi.jr.txt": "_PtResolution_AK4PFPuppi.txt",
    "_SF_AK4PFPuppi.jersf.txt": "_SF_AK4PFPuppi.txt"
}

base_jr = "https://raw.githubusercontent.com/cms-jet/JRDatabase/master/textFiles"

print("\n=== 3/4 DOWNLOADING JR MC (Summer24Prompt24_JRV2_MC) ===")
os.makedirs(jr_mc_era, exist_ok=True)

for out_ext, orig_ext in jr_mc_files.items():
    fname_orig = f"{jr_mc_era}{orig_ext}"
    fname_out = f"{jr_mc_era}{out_ext}"
    dest = os.path.join(jr_mc_era, fname_out)
    
    url = f"{base_jr}/{jr_mc_era}/{fname_orig}"
    try:
        real_data = get_real_content(url, "JRDatabase")
        with open(dest, "w") as f:
            f.write(real_data)
        print(f"OK JR MC: {dest}")
    except Exception as e:
        print(f"WARNING in JR MC {fname_out}: {e}")

# ==========================================
# 4. JR DATA (Summer24Prompt24_JRV2_DATA)
# ==========================================
jr_data_era = "Summer24Prompt24_JRV2_DATA"
jr_data_files = {
    "_PtResolution_AK4PFPuppi.jr.txt": "_PtResolution_AK4PFPuppi.txt",
    "_SF_AK4PFPuppi.jersf.txt": "_SF_AK4PFPuppi.txt"
}

print("\n=== 4/4 DOWNLOADING JR DATA (Summer24Prompt24_JRV2_DATA) ===")
os.makedirs(jr_data_era, exist_ok=True)

for out_ext, orig_ext in jr_data_files.items():
    fname_orig = f"{jr_data_era}{orig_ext}"
    fname_out = f"{jr_data_era}{out_ext}"
    dest = os.path.join(jr_data_era, fname_out)
    
    version_fallbacks = [jr_data_era] + [
        f"Summer24Prompt24_JRV{v}_DATA" for v in range(1, 0, -1)
    ]
    
    downloaded = False
    for current_era in version_fallbacks:
        url = f"{base_jr}/{current_era}/{current_era}{orig_ext}"
        try:
            real_data = get_real_content(url, "JRDatabase")
            with open(dest, "w") as f:
                f.write(real_data)
            print(f"OK JR DATA: {dest} (from {current_era})")
            downloaded = True
            break
        except Exception:
            continue
            
    if not downloaded:
        print(f"WARNING: {fname_out} not found in JR DATA.")

print("\n=== PROCESS COMPLETED SUCCESSFULLY ===")