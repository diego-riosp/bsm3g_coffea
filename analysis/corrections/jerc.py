# tools to apply JEC/JER and compute their uncertainties (https://cms-jerc.web.cern.ch/Recommendations/)
import gzip
import pickle
import yaml
import numpy as np
import awkward as ak
import importlib.resources
from pathlib import Path
from analysis.filesets.utils import get_dataset_era

with importlib.resources.open_text(
    "analysis.corrections", "jerc_params.yaml"
) as file:
    JEC_PARAMS = yaml.safe_load(file)


def load_factory_pkl(datatype, run_key):
    """
    Load the pkl.gz file containing the factories
    (jec_factories / met_factories) that were compiled prior to execution.
    """
    filename = f"{datatype}_{run_key.lower()}_jec_compiled.pkl.gz"
    path = Path(__file__).parent.parent / "data" / filename

    with gzip.open(path, "rb") as f:
        factories = pickle.load(f)
    return factories

def apply_jerc_corrections(
    events,
    year,
    dataset,
    apply_jec=True,
    apply_jer=True,
    apply_junc=True,
):
    era = get_dataset_era(dataset, year)
    run_key = "Run3" if year.startswith("202") else "Run2"
    datatype = "mc" if era == "MC" else "data"

    if not apply_jec:
        if era != "MC" and not hasattr(events.Jet, "JES_jes"):
            jes_dummy = ak.zip(
                {
                    "up": events.Jet,
                    "down": events.Jet,
                },
                depth_limit=1,
                with_name="JetSystematic",
            )
            events["Jet", "JES_jes"] = jes_dummy
        return events

    factories = load_factory_pkl(datatype, run_key)
    
    met_factories_dict = factories.get("met_factory")
    jet_factories_dict = factories.get("jet_factory") or {}

    # Helper function to extract factory if stored as dict or direct object
    def get_factory(factory_obj, key):
        if isinstance(factory_obj, dict):
            return factory_obj.get(key)
        return factory_obj  # Already the factory instance

    if datatype == "mc":
        jet_factory = get_factory(jet_factories_dict, year)
        met_factory = get_factory(met_factories_dict, year)
    else:
        jet_factory = None
        
        if era and era != "None":
            jet_factory = (
                jet_factories_dict.get(f"{year}_Run{era}")
                or jet_factories_dict.get(era)
                or jet_factories_dict.get((year, era))
            )
            if jet_factory is None:
                for key, val in jet_factories_dict.items():
                    if key.startswith(f"{year}_Run") and era in key:
                        jet_factory = val
                        break

        if jet_factory is None:
            year_matches = [
                val for key, val in jet_factories_dict.items() 
                if isinstance(key, str) and key.startswith(f"{year}_")
            ]
            if year_matches:
                jet_factory = year_matches[0]

        if jet_factory is None and len(jet_factories_dict) == 1:
            jet_factory = list(jet_factories_dict.values())[0]

        met_factory = get_factory(met_factories_dict, year)

    if jet_factory is None:
        raise KeyError(
            f"'jet_factory' not found for year='{year}', era='{era}' in the pkl {datatype}.\n"
            f"Available keys: {list(jet_factories_dict.keys()) if isinstance(jet_factories_dict, dict) else jet_factories_dict}"
        )

    jets = events.Jet
    events["Jet", "pt_raw"] = (1 - jets.rawFactor) * jets.pt
    events["Jet", "mass_raw"] = (1 - jets.rawFactor) * jets.mass

    if apply_jer and era == "MC":
        events["Jet", "pt_gen"] = ak.values_astype(
            ak.fill_none(jets.matched_gen.pt, 0), np.float32
        )
        
    if run_key == "Run3":
        events["Jet", "event_rho"] = (
            ak.ones_like(jets.pt) * events.Rho.fixedGridRhoFastjetAll
        )
    elif run_key == "Run2":
        events["Jet", "event_rho"] = ak.broadcast_arrays(
            events.fixedGridRhoFastjetAll, jets.pt
        )[0]

    corrected_jets = jet_factory.build(events.Jet)
    events["Jet"] = corrected_jets

    if run_key == "Run2" and met_factory is not None:
        events["MET"] = met_factory.build(events.MET, events.Jet)

    if era != "MC" and not hasattr(events.Jet, "JES_jes"):
        jes_dummy = ak.zip(
            {
                "up": events.Jet,
                "down": events.Jet,
            },
            depth_limit=1,
            with_name="JetSystematic",
        )
        events["Jet", "JES_jes"] = jes_dummy

    return events