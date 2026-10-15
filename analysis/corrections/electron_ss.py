import correctionlib
import numpy as np
import awkward as ak
from analysis.corrections.met import corrected_polar_met


# Official CVMFS repository mapping per year/campaign
REPO_DICT = {
    "2026": "Run3-26Prompt-Summer24-NanoAODv15",
    "2025": "Run3-25Prompt-Summer24-NanoAODv15",
    "2024": "Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15",
    "2023": "Run3-23CSep23-Summer23-NanoAODv12",
    "2023preBPix": "Run3-23CSep23-Summer23-NanoAODv12",
    "2023postBPix": "Run3-23DSep23-Summer23BPix-NanoAODv12",
    "2022": "Run3-22CDSep23-Summer22-NanoAODv12",
    "2022preEE": "Run3-22CDSep23-Summer22-NanoAODv12",
    "2022postEE": "Run3-22EFGSep23-Summer22EE-NanoAODv12",
    "2018": "Run2-2018-UL-NanoAODv15",
    "2017": "Run2-2017-UL-NanoAODv15",
    "2016postVFP": "Run2-2016postVFP-UL-NanoAODv15",
    "2016preVFP": "Run2-2016preVFP-UL-NanoAODv15",
}


def filter_boundaries(pt_corr, pt):
    """
    Filters out-of-bounds ([10, 500] GeV) or NaN values produced by the corrector,
    replacing them with the uncorrected (raw) pT.
    """
    outside_bounds = (pt < 10) | (pt > 500)
    pt_corr = ak.where(outside_bounds, pt, pt_corr)
    pt_corr = ak.where(np.isnan(pt_corr), pt, pt_corr)
    return pt_corr


def apply_electron_ss_corrections(
    events: ak.Array,
    year: str,
    seed: int = 42,
    obj_type: str = "Ele",
):
    if year not in REPO_DICT:
        raise KeyError(
            f"Year '{year}' is not mapped in REPO_DICT for CVMFS. "
            f"Available options: {list(REPO_DICT.keys())}"
        )

    # 1. Build CVMFS path following EGM POG standard conventions
    subfolder = "electron" if obj_type == "Ele" else "photon"
    json_path = f"/cvmfs/cms-griddata.cern.ch/cat/metadata/EGM/{REPO_DICT[year]}/latest/{subfolder}SS_EtDependent.json.gz"

    cset = correctionlib.CorrectionSet.from_file(json_path)

    # Standard evaluators in official CVMFS JSONs
    scale_evaluator = cset.compound["Scale"]
    smear_evaluator = cset["SmearAndSyst"]

    # 2. Store raw variables
    events["Electron", "pt_raw"] = events.Electron.pt
    events["PuppiMET", "pt_raw"] = events.PuppiMET.pt
    events["PuppiMET", "phi_raw"] = events.PuppiMET.phi

    # 3. Prepare electron variables
    electrons = events.Electron
    counts = ak.num(electrons)

    # Flatten collections for clean vectorized calls with correctionlib
    flat_pt = ak.flatten(electrons.pt_raw)
    flat_r9 = ak.flatten(electrons.r9)
    # Supercluster Eta = eta + deltaEtaSC
    flat_sc_eta = ak.flatten(electrons.eta + electrons.deltaEtaSC)
    flat_gain = ak.flatten(electrons.seedGain)
    flat_run = ak.flatten(ak.broadcast_arrays(events.run, electrons.pt_raw)[0])

    is_mc = hasattr(events, "genWeight")

    if is_mc:
        # --- MC: SMEARING AND SYSTEMATICS ---
        # Smearing width evaluator: ("smear", pt, r9, ScEta)
        smear_width = smear_evaluator.evaluate(
            "smear",
            ak.to_numpy(flat_pt),
            ak.to_numpy(flat_r9),
            ak.to_numpy(flat_sc_eta),
        )

        # Stochastic Gaussian random number generator N(0,1)
        rng = np.random.default_rng(seed=seed)
        random_numbers = rng.normal(loc=0.0, scale=1.0, size=len(flat_pt))

        # Nominal smearing
        smearing_factor = 1.0 + smear_width * random_numbers
        flat_pt_corrected = flat_pt * smearing_factor

        # Smearing uncertainties (Up / Down)
        smear_up = smear_evaluator.evaluate(
            "smear_up",
            ak.to_numpy(flat_pt),
            ak.to_numpy(flat_r9),
            ak.to_numpy(flat_sc_eta),
        )
        smear_down = smear_evaluator.evaluate(
            "smear_down",
            ak.to_numpy(flat_pt),
            ak.to_numpy(flat_r9),
            ak.to_numpy(flat_sc_eta),
        )

        # Prevent unphysical negative smearing widths
        smear_down = np.maximum(smear_down, 0.0)

        smearing_up = 1.0 + smear_up * random_numbers
        smearing_down = 1.0 + smear_down * random_numbers

        # Scale uncertainties (Up / Down in MC applied on top of smeared pT)
        scale_up = smear_evaluator.evaluate(
            "scale_up",
            ak.to_numpy(flat_pt),
            ak.to_numpy(flat_r9),
            ak.to_numpy(flat_sc_eta),
        )
        scale_down = smear_evaluator.evaluate(
            "scale_down",
            ak.to_numpy(flat_pt),
            ak.to_numpy(flat_r9),
            ak.to_numpy(flat_sc_eta),
        )

        # Unflatten back to nested Awkward array structures
        pt_corr = ak.unflatten(flat_pt_corrected, counts)
        pt_smear_up = ak.unflatten(flat_pt * smearing_up, counts)
        pt_smear_dn = ak.unflatten(flat_pt * smearing_down, counts)
        pt_scale_up = ak.unflatten(scale_up * flat_pt_corrected, counts)
        pt_scale_dn = ak.unflatten(scale_down * flat_pt_corrected, counts)

        # Apply boundary checks and store variations in events
        events["Electron", "pt"] = filter_boundaries(pt_corr, events.Electron.pt_raw)
        events["Electron", "pt_smear_up"] = filter_boundaries(pt_smear_up, events.Electron.pt_raw)
        events["Electron", "pt_smear_down"] = filter_boundaries(pt_smear_dn, events.Electron.pt_raw)
        events["Electron", "pt_scale_up"] = filter_boundaries(pt_scale_up, events.Electron.pt_raw)
        events["Electron", "pt_scale_down"] = filter_boundaries(pt_scale_dn, events.Electron.pt_raw)

    else:
        # --- DATA: SCALE CORRECTION ---
        # Scale evaluator: ("scale", run, ScEta, r9, pt, seedGain)
        scale_factor = scale_evaluator.evaluate(
            "scale",
            ak.to_numpy(flat_run),
            ak.to_numpy(flat_sc_eta),
            ak.to_numpy(flat_r9),
            ak.to_numpy(flat_pt),
            ak.to_numpy(flat_gain),
        )

        flat_pt_corrected = scale_factor * flat_pt
        pt_corr = ak.unflatten(flat_pt_corrected, counts)

        events["Electron", "pt"] = filter_boundaries(pt_corr, events.Electron.pt_raw)

    # 4. Propagate corrections to PuppiMET (nominal)
    met_pt, met_phi = corrected_polar_met(
        met_pt=events.PuppiMET.pt_raw,
        met_phi=events.PuppiMET.phi_raw,
        other_phi=events.Electron.phi,
        other_pt_old=events.Electron.pt_raw,
        other_pt_new=events.Electron.pt,
    )
    events["PuppiMET", "pt"] = met_pt
    events["PuppiMET", "phi"] = met_phi