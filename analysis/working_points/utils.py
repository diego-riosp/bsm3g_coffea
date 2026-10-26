import correctionlib
from analysis.corrections.utils import get_pog_json


def get_btag_mask(jets, year, wp):
    """
    Parameters:
    -----------
      jets: Jet collection
      year: {2016preVFP, 2016postVFP, 2017, 2018, 2022preEE, 2022postEE, 2023preBPix, 2023postBPix, 2024}
      wp: {loose, medium, tight}
    """
    # https://cms-analysis-corrections.docs.cern.ch/corrections/BTV/
    
    # set working points mapping
    wp_map = {"loose": "L", "medium": "M", "tight": "T"}
    # select tagger according to run era
    tagger = "deepJet" if year.startswith("201") else ("particleNet" if year != "2024" else "UParTAK4")
    tagger_map = {
        "deepJet": "deepJet_wp_values",
        "particleNet": "particleNet_wp_values",
        "UParTAK4": "UParTAK4_wp_values",
    }
    # load correction set with working points
    cset = correctionlib.CorrectionSet.from_file(get_pog_json(json_name="btag", year=year))
    btag_wp = cset[tagger_map[tagger]].evaluate(wp_map[wp])

    if tagger == "deepJet":
        pass_btag_wp = jets.btagDeepFlavB > btag_wp
    elif tagger == "particleNet":
        pass_btag_wp = jets.btagPNetB > btag_wp
    elif tagger == "UParTAK4":
        pass_btag_wp = jets.btagUParTAK4B > btag_wp
    return pass_btag_wp
