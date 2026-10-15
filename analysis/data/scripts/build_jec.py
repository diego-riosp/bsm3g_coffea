import sys
import gzip
import cloudpickle
from pathlib import Path
from coffea.lookup_tools import extractor
from coffea.jetmet_tools import JECStack, CorrectedJetsFactory, CorrectedMETFactory

# CLI arguments
datatype = str(sys.argv[1])  # "mc" or "data"
run = str(sys.argv[2])       # "run2" or "run3"
output_name = str(sys.argv[3]) if len(sys.argv) > 3 else datatype

# variables map for JEC/JER
jec_name_map = {
    "JetPt": "pt",
    "JetMass": "mass",
    "JetEta": "eta",
    "JetA": "area",
    "ptGenJet": "pt_gen",
    "ptRaw": "pt_raw",
    "massRaw": "mass_raw",
    "Rho": "event_rho",
    "METpt": "pt" if run == "run2" else None,
    "METphi": "phi" if run == "run2" else None,
    "JetPhi": "phi",
    "UnClusteredEnergyDeltaX": "MetUnclustEnUpDeltaX" if run == "run2" else None,
    "UnClusteredEnergyDeltaY": "MetUnclustEnUpDeltaY" if run == "run2" else None,
}

data_path = Path(Path.home(), "bsm3g_coffea/analysis/data")

def jet_factory_factory(files):
    ext = extractor()
    ext.add_weight_sets([f"* * {Path(data_path, file)}" for file in files])
    ext.finalize()
    jec_stack = JECStack(ext.make_evaluator())
    return CorrectedJetsFactory(jec_name_map, jec_stack)


def get_factories(datatype, run):
    if datatype == "mc":
        return get_mc_factories(run)
    elif datatype == "data":
        return get_data_factories(run)
    else:
        raise ValueError("datatype debe ser 'mc' o 'data'")


def get_mc_factories(run):
    if run == "run2":
        jet_factory = {
            "2016preVFP": jet_factory_factory([
                "JEC/Summer19UL16APV_V7_MC_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_V7_MC_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_V7_MC_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_V7_MC_UncertaintySources_AK4PFchs.junc.txt",
                "JEC/Summer19UL16APV_V7_MC_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer20UL16APV_JRV3_MC_PtResolution_AK4PFchs.jr.txt",
                "JEC/Summer20UL16APV_JRV3_MC_SF_AK4PFchs.jersf.txt",
            ]),
            "2016postVFP": jet_factory_factory([
                "JEC/Summer19UL16_V7_MC_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL16_V7_MC_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL16_V7_MC_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL16_V7_MC_UncertaintySources_AK4PFchs.junc.txt",
                "JEC/Summer19UL16_V7_MC_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer20UL16_JRV3_MC_PtResolution_AK4PFchs.jr.txt",
                "JEC/Summer20UL16_JRV3_MC_SF_AK4PFchs.jersf.txt",
            ]),
            "2017": jet_factory_factory([
                "JEC/Summer19UL17_V5_MC_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_V5_MC_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_V5_MC_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_V5_MC_UncertaintySources_AK4PFchs.junc.txt",
                "JEC/Summer19UL17_V5_MC_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL17_JRV3_MC_PtResolution_AK4PFchs.jr.txt",
                "JEC/Summer19UL17_JRV3_MC_SF_AK4PFchs.jersf.txt",
            ]),
            "2018": jet_factory_factory([
                "JEC/Summer19UL18_V5_MC_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_V5_MC_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_V5_MC_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_V5_MC_UncertaintySources_AK4PFchs.junc.txt",
                "JEC/Summer19UL18_V5_MC_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL18_JRV2_MC_PtResolution_AK4PFchs.jr.txt",
                "JEC/Summer19UL18_JRV2_MC_SF_AK4PFchs.jersf.txt",
            ]),
        }
        met_factory = CorrectedMETFactory(jec_name_map)
        return jet_factory, met_factory
    else:
        jet_factory = {
            "2022preEE": jet_factory_factory([
                "JEC/Summer2222Sep2023_V2_MC_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer2222Sep2023_V2_MC_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer2222Sep2023_V2_MC_UncertaintySources_AK4PFPuppi.junc.txt",
                "JEC/Summer2222Sep2023_V2_MC_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer2222Sep2023_JRV1_MC_PtResolution_AK4PFPuppi.jr.txt",
                "JEC/Summer2222Sep2023_JRV1_MC_SF_AK4PFPuppi.jersf.txt",
            ]),
            "2022postEE": jet_factory_factory([
                "JEC/Summer22EE22Sep2023_V2_MC_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_V2_MC_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_V2_MC_UncertaintySources_AK4PFPuppi.junc.txt",
                "JEC/Summer22EE22Sep2023_V2_MC_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer22EE22Sep2023_JRV1_MC_PtResolution_AK4PFPuppi.jr.txt",
                "JEC/Summer22EE22Sep2023_JRV1_MC_SF_AK4PFPuppi.jersf.txt",
            ]),
            "2023preBPix": jet_factory_factory([
                "JEC/Summer23Prompt23_V1_MC_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_V1_MC_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_V1_MC_UncertaintySources_AK4PFPuppi.junc.txt",
                "JEC/Summer23Prompt23_V1_MC_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer23Prompt23RunCv1234_JRV1_MC_PtResolution_AK4PFPuppi.jr.txt",
                "JEC/Summer23Prompt23RunCv1234_JRV1_MC_SF_AK4PFPuppi.jersf.txt",
            ]),
            "2023postBPix": jet_factory_factory([
                "JEC/Summer23BPixPrompt23_V1_MC_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer23BPixPrompt23_V1_MC_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer23BPixPrompt23_V1_MC_UncertaintySources_AK4PFPuppi.junc.txt",
                "JEC/Summer23BPixPrompt23_V1_MC_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer23BPixPrompt23RunD_JRV1_MC_PtResolution_AK4PFPuppi.jr.txt",
                "JEC/Summer23BPixPrompt23RunD_JRV1_MC_SF_AK4PFPuppi.jersf.txt",
            ]),
            "2024": jet_factory_factory([
                "JEC/Summer24Prompt24_V5_MC_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_V5_MC_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_V5_MC_UncertaintySources_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_V5_MC_Uncertainty_AK4PFPuppi.junc.txt",
                #"JEC/Summer24Prompt24_JRV2_MC_PtResolution_AK4PFPuppi.jr.txt",
                #"JEC/Summer24Prompt24_JRV2_MC_SF_AK4PFPuppi.jersf.txt",
            ]),
        }
        return jet_factory, None


def get_data_factories(run):
    if run == "run2":
        jet_factory = {
            # 2016 APV
            "2016preVFP_RunBCD": jet_factory_factory([
                "JEC/Summer19UL16APV_RunBCD_V7_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_RunBCD_V7_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_RunBCD_V7_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_RunBCD_V7_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_RunBCD_V7_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL16APV_RunBCD_V7_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            "2016preVFP_RunEF": jet_factory_factory([
                "JEC/Summer19UL16APV_RunEF_V7_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_RunEF_V7_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_RunEF_V7_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_RunEF_V7_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL16APV_RunEF_V7_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL16APV_RunEF_V7_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            # 2016 PostVFP
            "2016postVFP_RunFGH": jet_factory_factory([
                "JEC/Summer19UL16_RunFGH_V7_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL16_RunFGH_V7_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL16_RunFGH_V7_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL16_RunFGH_V7_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL16_RunFGH_V7_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL16_RunFGH_V7_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            # 2017
            "2017_RunB": jet_factory_factory([
                "JEC/Summer19UL17_RunB_V5_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunB_V5_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunB_V5_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunB_V5_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunB_V5_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL17_RunB_V5_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            "2017_RunC": jet_factory_factory([
                "JEC/Summer19UL17_RunC_V5_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunC_V5_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunC_V5_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunC_V5_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunC_V5_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL17_RunC_V5_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            "2017_RunD": jet_factory_factory([
                "JEC/Summer19UL17_RunD_V5_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunD_V5_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunD_V5_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunD_V5_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunD_V5_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL17_RunD_V5_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            "2017_RunE": jet_factory_factory([
                "JEC/Summer19UL17_RunE_V5_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunE_V5_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunE_V5_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunE_V5_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunE_V5_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL17_RunE_V5_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            "2017_RunF": jet_factory_factory([
                "JEC/Summer19UL17_RunF_V5_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunF_V5_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunF_V5_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunF_V5_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL17_RunF_V5_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL17_RunF_V5_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            # 2018
            "2018_RunA": jet_factory_factory([
                "JEC/Summer19UL18_RunA_V5_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunA_V5_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunA_V5_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunA_V5_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunA_V5_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL18_RunA_V5_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            "2018_RunB": jet_factory_factory([
                "JEC/Summer19UL18_RunB_V5_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunB_V5_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunB_V5_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunB_V5_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunB_V5_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL18_RunB_V5_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            "2018_RunC": jet_factory_factory([
                "JEC/Summer19UL18_RunC_V5_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunC_V5_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunC_V5_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunC_V5_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunC_V5_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL18_RunC_V5_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
            "2018_RunD": jet_factory_factory([
                "JEC/Summer19UL18_RunD_V5_DATA_L1FastJet_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunD_V5_DATA_L2Relative_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunD_V5_DATA_L3Absolute_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunD_V5_DATA_L2L3Residual_AK4PFchs.jec.txt",
                "JEC/Summer19UL18_RunD_V5_DATA_Uncertainty_AK4PFchs.junc.txt",
                "JEC/Summer19UL18_RunD_V5_DATA_UncertaintySources_AK4PFchs.junc.txt",
            ]),
        }
        met_factory = CorrectedMETFactory(jec_name_map)
        return jet_factory, met_factory
    else:
        jet_factory = {
            # 2022
            "2022preEE_RunCD": jet_factory_factory([
                "JEC/Summer2222Sep2023_RunCD_V2_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer2222Sep2023_RunCD_V2_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer2222Sep2023_RunCD_V2_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer2222Sep2023_RunCD_V2_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer2222Sep2023_RunCD_V2_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer2222Sep2023_RunCD_V2_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2022postEE_RunE": jet_factory_factory([
                "JEC/Summer22EE22Sep2023_RunE_V2_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunE_V2_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunE_V2_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunE_V2_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunE_V2_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer22EE22Sep2023_RunE_V2_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2022postEE_RunF": jet_factory_factory([
                "JEC/Summer22EE22Sep2023_RunF_V2_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunF_V2_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunF_V2_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunF_V2_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunF_V2_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer22EE22Sep2023_RunF_V2_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2022postEE_RunG": jet_factory_factory([
                "JEC/Summer22EE22Sep2023_RunG_V2_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunG_V2_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunG_V2_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunG_V2_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer22EE22Sep2023_RunG_V2_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer22EE22Sep2023_RunG_V2_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            # 2023
            "2023preBPix_RunCv123": jet_factory_factory([
                "JEC/Summer23Prompt23_RunCv123_V1_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_RunCv123_V1_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_RunCv123_V1_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_RunCv123_V1_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_RunCv123_V1_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer23Prompt23_RunCv123_V1_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2023preBPix_RunCv4": jet_factory_factory([
                "JEC/Summer23Prompt23_RunCv4_V1_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_RunCv4_V1_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_RunCv4_V1_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_RunCv4_V1_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer23Prompt23_RunCv4_V1_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer23Prompt23_RunCv4_V1_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2023postBPix_RunD": jet_factory_factory([
                "JEC/Summer23BPixPrompt23_RunD_V1_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer23BPixPrompt23_RunD_V1_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer23BPixPrompt23_RunD_V1_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer23BPixPrompt23_RunD_V1_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer23BPixPrompt23_RunD_V1_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer23BPixPrompt23_RunD_V1_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            # 2024
            "2024_RunCnib1": jet_factory_factory([
                "JEC/Summer24Prompt24_RunCnib1_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunCnib1_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunCnib1_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunCnib1_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunCnib1_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunCnib1_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2024_RunDnib1": jet_factory_factory([
                "JEC/Summer24Prompt24_RunDnib1_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunDnib1_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunDnib1_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunDnib1_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunDnib1_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunDnib1_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2024_RunEnib1": jet_factory_factory([
                "JEC/Summer24Prompt24_RunEnib1_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunEnib1_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunEnib1_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunEnib1_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunEnib1_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunEnib1_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2024_RunFnib1": jet_factory_factory([
                "JEC/Summer24Prompt24_RunFnib1_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib1_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib1_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib1_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib1_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunFnib1_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2024_RunFnib2": jet_factory_factory([
                "JEC/Summer24Prompt24_RunFnib2_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib2_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib2_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib2_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib2_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunFnib2_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2024_RunFnib3": jet_factory_factory([
                "JEC/Summer24Prompt24_RunFnib3_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib3_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib3_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib3_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunFnib3_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunFnib3_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2024_RunGnib1": jet_factory_factory([
                "JEC/Summer24Prompt24_RunGnib1_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunGnib1_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunGnib1_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunGnib1_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunGnib1_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunGnib1_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2024_RunGnib2": jet_factory_factory([
                "JEC/Summer24Prompt24_RunGnib2_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunGnib2_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunGnib2_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunGnib2_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunGnib2_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunGnib2_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2024_RunHnib1": jet_factory_factory([
                "JEC/Summer24Prompt24_RunHnib1_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunHnib1_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunHnib1_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunHnib1_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunHnib1_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunHnib1_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
            "2024_RunInib1": jet_factory_factory([
                "JEC/Summer24Prompt24_RunInib1_V5_DATA_L1FastJet_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunInib1_V5_DATA_L2Relative_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunInib1_V5_DATA_L3Absolute_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunInib1_V5_DATA_L2L3Residual_AK4PFPuppi.jec.txt",
                "JEC/Summer24Prompt24_RunInib1_V5_DATA_Uncertainty_AK4PFPuppi.junc.txt",
                "JEC/Summer24Prompt24_RunInib1_V5_DATA_UncertaintySources_AK4PFPuppi.junc.txt",
            ]),
        }
        return jet_factory, None


def save_factory(jet_factory, met_factory, name, run):
    with gzip.open(f"{data_path}/{name}_{run}_jec_compiled.pkl.gz", "wb") as fout:
        cloudpickle.dump(
            {
                "jet_factory": jet_factory,
                "met_factory": met_factory,
            },
            fout,
        )

if __name__ == "__main__":
    jet_fact, met_fact = get_factories(datatype, run)
    save_factory(jet_fact, met_fact, output_name, run)