import re
import correctionlib
import numpy as np
import awkward as ak
from typing import Tuple
from analysis.corrections.utils import get_pog_json


def apply_met_phi_corrections(
    events: ak.Array,
    year: str,
) -> Tuple[ak.Array, ak.Array]:
    """
    Apply MET phi modulation corrections (only for Run2)

    Parameters:
    -----------
        events:
            Events array
        year:
            Year of the dataset  {2016preVFP, 2016postVFP, 2017, 2018, 2022preEE, 2022postEE, 2023preBPix, 2023postBPix}

    Returns:
    --------
        corrected MET pt and phi
    """
    # use correct run ranges when working with data, otherwise use uniform run numbers in an arbitrary large window
    run_ranges = {
        "2016preVFP": [272007, 278771],
        "2016postVFP": [278769, 284045],
        "2017": [297020, 306463],
        "2018": [315252, 325274],
#        "2022preEE": [355094, 359017],
#        "2022postEE": [359045, 362760],
        "2024": [378971,387121]
    }
    run_key = (
        "run3" if year.startswith("202") else "run2"
    )
    met_key = "MET" if run_key == "run2" else "PuppiMET"
    cset_file = (
        get_pog_json(json_name="met", year=year)
        if year != "2024"
        else "analysis/data/run3_met_xy_corrections.json"
    )
    cset = correctionlib.CorrectionSet.from_file(cset_file)

    events[met_key, "pt_raw"] = (
        ak.ones_like(events[met_key].pt) * events[met_key].pt
    )
    events[met_key, "phi_raw"] = (
        ak.ones_like(events[met_key].phi) * events[met_key].phi
    )

    # make sure to not cross the maximum allowed value for uncorrected met
    met_pt = events[met_key].pt_raw
    met_pt = np.clip(met_pt, 0.0, 6499.0)
    met_phi = events[met_key].phi_raw
    met_phi = np.clip(met_phi, -3.5, 3.5)

    data_kind = "mc" if hasattr(events, "genWeight") else "data"


    if run_key == "run3" and year != "2024":
        # prepare common evaluation arguments (excluding pt_phi and variation)
        epoch_str = f"{year[:4] + re.search(r'post(.*)', year).group(1) if 'post' in year else year[:4]}"
        dtmc_str = "MC" if data_kind == "mc" else "DATA"

        # schema: (met_type, epoch, dtmc, variation, met_pt, met_phi, npvGood)
        eval_inputs = lambda var_name, pu_var="nom": (
            var_name,
            "PuppiMET",
            epoch_str,
            dtmc_str,
            pu_var,
            met_pt.to_numpy(),
            met_phi.to_numpy(),
            events.PV.npvsGood.to_numpy(),
        )

        # evaluate nominal corrections
        pt_nom = cset["met_xy_corrections"].evaluate(*eval_inputs("pt"))
        phi_nom = cset["met_xy_corrections"].evaluate(*eval_inputs("phi"))

        # evaluate individual statistical x/y variations
        pt_stat_xup = cset["met_xy_corrections"].evaluate(*eval_inputs("pt_stat_xup"))
        pt_stat_xdn = cset["met_xy_corrections"].evaluate(*eval_inputs("pt_stat_xdn"))
        pt_stat_yup = cset["met_xy_corrections"].evaluate(*eval_inputs("pt_stat_yup"))
        pt_stat_ydn = cset["met_xy_corrections"].evaluate(*eval_inputs("pt_stat_ydn"))

        phi_stat_xup = cset["met_xy_corrections"].evaluate(*eval_inputs("phi_stat_xup"))
        phi_stat_xdn = cset["met_xy_corrections"].evaluate(*eval_inputs("phi_stat_xdn"))
        phi_stat_yup = cset["met_xy_corrections"].evaluate(*eval_inputs("phi_stat_yup"))
        phi_stat_ydn = cset["met_xy_corrections"].evaluate(*eval_inputs("phi_stat_ydn"))

        # assign nominal values to PuppiMET
        events[met_key, "pt"] = pt_nom
        events[met_key, "phi"] = phi_nom

        # combine uncorrelated x/y variations in quadrature (up and down)
        delta_pt_up = np.sqrt((pt_stat_xup - pt_nom) ** 2 + (pt_stat_yup - pt_nom) ** 2)
        delta_pt_dn = np.sqrt((pt_stat_xdn - pt_nom) ** 2 + (pt_stat_ydn - pt_nom) ** 2)

        delta_phi_up = np.sqrt((phi_stat_xup - phi_nom) ** 2 + (phi_stat_yup - phi_nom) ** 2)
        delta_phi_dn = np.sqrt((phi_stat_xdn - phi_nom) ** 2 + (phi_stat_ydn - phi_nom) ** 2)

        # retrieve behavior and parameters from existing PuppiMET object
        met_obj = events[met_key]
        met_params = met_obj._layout.parameters if hasattr(met_obj, "_layout") else None
        met_behavior = met_obj.behavior

        # build up and down records with proper vector behavior
        puppimet_up = ak.zip(
            {"pt": pt_nom + delta_pt_up, "phi": phi_nom + delta_phi_up},
            depth_limit=1,
            with_name="MissingET",
            behavior=met_behavior,
        )
        puppimet_down = ak.zip(
            {"pt": pt_nom - delta_pt_dn, "phi": phi_nom - delta_phi_dn},
            depth_limit=1,
            with_name="MissingET",
            behavior=met_behavior,
        )

        # package systematic variations using METSystematic structure
        xy_corr_systematics = ak.zip(
            {"up": puppimet_up, "down": puppimet_down},
            depth_limit=1,
            with_name="METSystematic",
            behavior=met_behavior,
        )

        # attach xy_corr field to events.PuppiMET (or met_key)
        events[met_key, "xycorr"] = xy_corr_systematics
    else:
        if data_kind == "mc" and year in run_ranges.keys():
            run = np.random.randint(
                run_ranges[year][0], run_ranges[year][1], size=len(met_pt)
            )
        else:
            run = events.run
        # evaluate nominal corrections for Run 2 and 2024
        pt_corr_file = (
            f"pt_metphicorr_pfmet_{data_kind}"
            if run_key == "run2"
            else f"pt_metphicorr_puppimet_{data_kind}"
        )
        events[met_key, "pt"] = cset[pt_corr_file].evaluate(
            met_pt.to_numpy(),
            met_phi.to_numpy(),
            events.PV.npvsGood.to_numpy(),
            run,
        )

        phi_corr_file = (
            f"phi_metphicorr_pfmet_{data_kind}"
            if run_key == "run2"
            else f"phi_metphicorr_puppimet_{data_kind}"
        )
        events[met_key, "phi"] = cset[phi_corr_file].evaluate(
            met_pt.to_numpy(),
            met_phi.to_numpy(),
            events.PV.npvsGood.to_numpy(),
            run,
        )

def corrected_polar_met(
    met_pt,
    met_phi,
    other_phi,
    other_pt_old,
    other_pt_new,
    positive=None,
    dx=None,
    dy=None,
) -> tuple:
    """
    helper function to compute new MET polar components after some other object pT correction.

    https://github.com/CoffeaTeam/coffea/blob/master/src/coffea/jetmet_tools/CorrectedMETFactory.py#L6
    """
    sin, cos = np.sin(other_phi), np.cos(other_phi)
    met_px = met_pt * np.cos(met_phi) - ak.sum(
        (other_pt_new - other_pt_old) * cos, axis=1
    )
    met_py = met_pt * np.sin(met_phi) - ak.sum(
        (other_pt_new - other_pt_old) * sin, axis=1
    )
    if positive is not None and dx is not None and dy is not None:
        met_px = met_px + dx if positive else x - dx
        met_py = met_py + dy if positive else y - dy

    corrected_met_pt = np.hypot(met_px, met_py)
    corrected_met_phi = np.arctan2(met_py, met_px)
    return corrected_met_pt, corrected_met_phi
