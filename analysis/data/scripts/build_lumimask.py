import pickle
from coffea.lumi_tools import LumiMask
from pathlib import Path


if __name__ == "__main__":

    data_path = Path.home() / "bsm3g_coffea/analysis/data"

    golden_json = {
        "2016preVFP": "Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
        "2016postVFP": "Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
        "2017": "Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt",
        "2018": "Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt",
        "2022preEE": "Cert_Collisions2022_355100_362760_Golden.txt",
        "2022postEE": "Cert_Collisions2022_355100_362760_Golden.txt",
        "2023preBPix": "Cert_Collisions2023_366442_370790_Golden.txt",
        "2023postBPix": "Cert_Collisions2023_366442_370790_Golden.txt",
        "2024": "Cert_Collisions2024_378981_386951_Golden.txt",
    }

    lumi_masks = {era: LumiMask(data_path / filename) for era, filename in golden_json.items()}
    with open(data_path /"lumi_masks.pkl", "wb") as handle:
        pickle.dump(lumi_masks, handle, protocol=pickle.HIGHEST_PROTOCOL)