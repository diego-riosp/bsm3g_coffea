import copy
import numpy as np
import awkward as ak
import warnings
from coffea import processor
from coffea.analysis_tools import PackedSelection, Weights
from analysis.workflows.config import WorkflowConfigBuilder
from analysis.histograms import HistBuilder, fill_histograms
from analysis.corrections.jetvetomaps import apply_jetvetomaps
from analysis.corrections import (
    object_corrector_manager,
    weight_manager,
)
from analysis.selections import (
    ObjectSelector,
    get_lumi_mask,
    get_trigger_mask,
    get_trigger_match_mask,
    get_metfilters_mask,
    get_stitching_mask,
    get_hemcleaning_mask,
)
from analysis.corrections import apply_jerc_corrections


def update(events, collections):
    """Return a shallow copy of events array with some collections swapped out"""
    out = events
    for name, value in collections.items():
        out = ak.with_field(out, value, name)
    return out


class BaseProcessor(processor.ProcessorABC):
    def __init__(
        self,
        workflow: str,
        year: str = "2017",
        mode="virtual"
    ):
        assert mode in ["eager", "virtual", "dask"]
        self._mode = mode
        self.year = year
        self.workflow = workflow
        self.year_key = year[:4]
        self.run = "2" if year.startswith("201") else "3"

        config_builder = WorkflowConfigBuilder(workflow=workflow)
        self.workflow_config = config_builder.build_workflow_config()
        self.histogram_config = self.workflow_config.histogram_config
        self.histograms = HistBuilder(self.workflow_config).build_histogram()

    def add_cutflow(
        self, events, output, objects, selection_manager, weight_manager, dataset
    ):
        for category, category_cuts in self.workflow_config.event_selection[
            "categories"
        ].items():
            output["metadata"].update({category: {"cutflow": {"initial": self.sumw}}})
            selections = []
            for cut_name in category_cuts:
                selections.append(cut_name)
                current_selection = selection_manager.all(*selections)
                if ak.sum(current_selection) != 0:
                    sumw_cutflow = (
                        ak.sum(self.genweight[current_selection])
                        if self.is_mc
                        else len(events[current_selection])
                    )
                    output["metadata"][category]["cutflow"][cut_name] = sumw_cutflow
                    
                else:
                    output["metadata"][category]["cutflow"][cut_name] = 0

    def process(self, events):
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        np.seterr(divide="ignore", invalid="ignore")

        self.is_mc = hasattr(events, "genWeight")
        self.sumw = ak.sum(events.genWeight) if self.is_mc else len(events)
        if self.is_mc:
            self.genweight = events.genWeight

        object_corrector_manager(
            events=events,
            year=self.year,
            run=self.run,
            workflow_config=self.workflow_config,
            dataset=events.metadata["dataset"],
        )

        if "jets_veto" in self.workflow_config.corrections_config["objects"]:
            events = apply_jetvetomaps(events, self.year)
            
        if not self.is_mc:
            # add genPartFlav fields to leptons
            events["Muon", "genPartFlav"] = ak.zeros_like(events.Muon.pt)
            events["Electron", "genPartFlav"] = ak.zeros_like(events.Electron.pt)
            return self.process_shift(events, shift_name="nominal")

        met_key = "MET" if self.run == "2" else "PuppiMET"
        met = getattr(events, met_key)

        base_shifts = []

        if "jets" in self.workflow_config.corrections_config["objects"]:
            base_shifts = apply_jerc_corrections(
                events=events,
                year=self.year,
                shifts=base_shifts,
                corrections_config=self.workflow_config.corrections_config
            )



        if self.workflow_config.corrections_config["apply_obj_syst"]:
            shifts = []
            for jme_collections, shift_name in base_shifts:
                name = "nominal" if shift_name is None else shift_name

                collections = {
                    "Jet": jme_collections["Jet"],
                    met_key: jme_collections["MET"],
                    "Muon": events.Muon, 
                    "Tau": events.Tau
                }
                shifts.append((collections, name))
            base_jet = shifts[0][0]["Jet"]
            base_met = shifts[0][0][met_key]
            
            if self.run == "2":
                shifts.extend([
                    ({"Jet": base_jet, met_key: base_met, "Muon": events.Muon.rochester.up, "Tau": events.Tau}, f"CMS_rochester_{self.year_key}Up"),
                    ({"Jet": base_jet, met_key: base_met, "Muon": events.Muon.rochester.down, "Tau": events.Tau}, f"CMS_rochester_{self.year_key}Down"),
                    ({"Jet": base_jet, met_key: met.tau_energy.up, "Muon": events.Muon, "Tau": events.Tau.tau_energy.up}, f"CMS_t_energy_{self.year_key}Up"),
                    ({"Jet": base_jet, met_key: met.tau_energy.down, "Muon": events.Muon, "Tau": events.Tau.tau_energy.down}, f"CMS_t_energy_{self.year_key}Down"),
                ])
            else:
                run3_shifts = [
                    ({"Jet": base_jet, met_key: base_met, "Muon": events.Muon.ptscalecorr.up, "Tau": events.Tau}, f"CMS_scale_mu_{self.year_key}Up"),
                    ({"Jet": base_jet, met_key: base_met, "Muon": events.Muon.ptscalecorr.down, "Tau": events.Tau}, f"CMS_scale_mu_{self.year_key}Down"),
                    ({"Jet": base_jet, met_key: base_met, "Muon": events.Muon.ptresolcorr.up, "Tau": events.Tau}, f"CMS_res_mu_{self.year_key}Up"),
                    ({"Jet": base_jet, met_key: base_met, "Muon": events.Muon.ptresolcorr.down, "Tau": events.Tau}, f"CMS_res_mu_{self.year_key}Down"),
                    ({"Jet": base_jet, met_key: met.tau_energy.up, "Muon": events.Muon, "Tau": events.Tau.tau_energy.up}, f"CMS_t_energy_{self.year_key}Up"),
                    ({"Jet": base_jet, met_key: met.tau_energy.down, "Muon": events.Muon, "Tau": events.Tau.tau_energy.down}, f"CMS_t_energy_{self.year_key}Down"),
                ]

                if self.year != "2024":
                    run3_shifts.extend([
                        ({"Jet": base_jet, met_key: base_met.xycorr.up, "Muon": events.Muon, "Tau": events.Tau}, f"CMS_met_xy_{self.year_key}Up"),
                        ({"Jet": base_jet, met_key: base_met.xycorr.down, "Muon": events.Muon, "Tau": events.Tau}, f"CMS_met_xy_{self.year_key}Down"),
                    ])

                shifts.extend(run3_shifts)

        return processor.accumulate(
            self.process_shift(update(events, collections), name)
            for collections, name in shifts
        )


    def process_shift(self, events, shift_name):
        year = self.year
        is_mc = self.is_mc
        dataset = events.metadata["dataset"]

        output = {}
        output["metadata"] = {}
        if shift_name == "nominal":
            output["metadata"].update({"sumw": self.sumw})

            for category in self.workflow_config.event_selection["categories"]:
                output["metadata"].update({category: {"cutflow": {"initial": self.sumw}}})

        # ----------------------------------------------------------------------------------
        # object selection
        # ----------------------------------------------------------------------------------
        object_selector = ObjectSelector(
            self.workflow_config.object_selection, year, self.run
        )
        objects = object_selector.select_objects(events)

        # ----------------------------------------------------------------------------------
        # event selection
        # ----------------------------------------------------------------------------------
        selection_manager = PackedSelection()
        event_selection = self.workflow_config.event_selection
        if "hlt_paths" in event_selection:
            hlt_paths = event_selection["hlt_paths"]

        for selection, mask in event_selection["selections"].items():
            selection_manager.add(selection, eval(mask))

        self.add_cutflow(
            events, output, objects, selection_manager, weight_manager, dataset
        )

        # -----------------------------------------------------------------------------------
        # Histogram filling
        # -----------------------------------------------------------------------------------
        histograms = copy.deepcopy(self.histograms)
        for category, category_cuts in event_selection["categories"].items():
            category_mask = selection_manager.all(*category_cuts)
            nevents_after = ak.sum(category_mask)
            if nevents_after > 0:
                pruned_ev = events[category_mask]
                for obj in objects:
                    pruned_ev[f"selected_{obj}"] = objects[obj][category_mask]
                weights_container = weight_manager(
                    pruned_ev=pruned_ev,
                    year=year,
                    workflow=self.workflow,
                    category=category,
                    run=self.run,
                    workflow_config=self.workflow_config,
                    variation=shift_name,
                    dataset=dataset,
                )
                if shift_name == "nominal":
                    weighted_final_nevents = ak.sum(weights_container.weight())
                    output["metadata"][category].update(
                        {"weighted_final_nevents": weighted_final_nevents}
                    )
                variables_map = {}
                for variable, axis in self.histogram_config.axes.items():
                    variables_map[variable] = eval(axis.expression)[category_mask]
                fill_histograms(
                    histogram_config=self.histogram_config,
                    weights_container=weights_container,
                    variables_map=variables_map,
                    histograms=histograms,
                    shift_name=shift_name,
                    category=category,
                    is_mc=is_mc,
                    flow=self.histogram_config.flow,
                )
        output["histograms"] = histograms
        return output

    def postprocess(self, accumulator):
        return accumulator