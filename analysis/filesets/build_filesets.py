import os
import yaml
import json
import argparse
import subprocess
from pathlib import Path

def discover_with_das(das_query: str, redirector: str = "root://cms-xrd-global.cern.ch//") -> dict:
    """Queries dataset files using dasgoclient."""
    # Ensure the query has the required /PRIMARY/PROCESSED/TIER syntax
    formatted_query = f"/{das_query.strip('/')}"
    das_cmd = ["dasgoclient", f"-query=file dataset={formatted_query} status=*"]

    # Clean the environment to avoid Python/LCG errors on LXPLUS
    das_env = os.environ.copy()
    das_env.pop("PYTHONHOME", None)
    das_env.pop("PYTHONPATH", None)

    try:
        result = subprocess.run(
            das_cmd, capture_output=True, text=True, check=True, env=das_env
        )
        file_paths = result.stdout.strip().splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error running dasgoclient for {formatted_query}:\n{e.stderr}")
        return {}

    files_dict = {}
    redirector = redirector.rstrip("/") + "/"
    
    for path in file_paths:
        path = path.strip()
        if path:
            # Build the full XRootD URL
            clean_path = path if not path.startswith("/") else path[1:]
            full_path = f"{redirector}/{clean_path}"
            
            # Exact format expected by Coffea: { "url_to_file.root": "Events" }
            files_dict[full_path] = "Events"

    if not files_dict:
        print(f"Warning: 0 files queried for {formatted_query}")

    return files_dict


def discover_with_rucio(
    das_queries: dict, filesets_dir: Path, year: str
) -> dict:
    """Queries dataset files using Coffea's DataDiscoveryCLI (Rucio)."""
    from coffea.dataset_tools.dataset_query import DataDiscoveryCLI

    dataset_definition = {}
    for dataset_key, query in das_queries.items():
        dataset_definition[f"/{query}"] = {"short_name": dataset_key}

    ddc = DataDiscoveryCLI()
    sites_file = filesets_dir / f"{year}_sites.yaml"
    with open(sites_file, "r") as f:
        sites = yaml.safe_load(f)["white"]
    ddc.do_allowlist_sites(sites)

    ddc.load_dataset_definition(
        dataset_definition,
        query_results_strategy="all",
        replicas_strategy="round-robin",
    )

    tmp_json = f"dataset_discovery_{year}.json"
    ddc.do_save(tmp_json)

    with open(tmp_json, "r") as f:
        dataset_discovery = json.load(f)

    os.remove(tmp_json)
    return dataset_discovery


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fileset generator for CMS analysis"
    )
    parser.add_argument(
        "-y",
        "--year",
        dest="year",
        type=str,
        required=True,
        choices=[
            "2016preVFP",
            "2016postVFP",
            "2017",
            "2018",
            "2022preEE",
            "2022postEE",
            "2023preBPix",
            "2023postBPix",
            "2024",
        ],
    )
    parser.add_argument(
        "--samples",
        nargs="*",
        type=str,
        help="(Optional) List of samples to use. If omitted, all available samples will be used.",
    )

    # Mutually exclusive group for dataset discovery strategy
    discovery_group = parser.add_mutually_exclusive_group()
    discovery_group.add_argument(
        "--das",
        dest="discovery",
        action="store_const",
        const="das",
        help="Use dasgoclient for dataset discovery (Default).",
    )
    discovery_group.add_argument(
        "--rucio",
        dest="discovery",
        action="store_const",
        const="rucio",
        help="Use DataDiscoveryCLI (Rucio) for dataset discovery.",
    )
    parser.set_defaults(discovery="rucio")

    args = parser.parse_args()

    # Open dataset configs
    filesets_dir = Path.cwd() / "analysis" / "filesets"
    run_key = "Run3" if args.year.startswith("202") else "Run2"
    nano_version = (
        "nanov15"
        if args.year == "2024"
        else ("nanov9" if run_key == "Run2" else "nanov12")
    )
    datasets_file = filesets_dir / f"{args.year}_{nano_version}.yaml"

    with open(datasets_file, "r") as f:
        dataset_configs = yaml.safe_load(f)

    samples_to_use = args.samples if args.samples else list(dataset_configs.keys())
    das_queries = {sample: dataset_configs[sample]["query"] for sample in samples_to_use}

    new_dataset = {}

    # Run discovery based on selected flag
    if args.discovery == "das":
        print("--> Using DAS method (dasgoclient)")
        for sample in samples_to_use:
            query = das_queries[sample]
            print(f"Querying DAS for {sample}...")
            files = discover_with_das(query)
            new_dataset[sample] = {
                "files": files,
                "metadata": {"short_name": sample},
            }

    elif args.discovery == "rucio":
        print("--> Using Rucio method (DataDiscoveryCLI)")
        dataset_discovery = discover_with_rucio(das_queries, filesets_dir, args.year)

        for dataset_name, dataset_info in dataset_discovery.items():
            short_name = dataset_info["metadata"]["short_name"]
            new_dataset[short_name] = {
                "files": dataset_info["files"],
                "metadata": {"short_name": short_name},
            }

    # Save output to JSON
    fileset_file = filesets_dir / f"fileset_{args.year}_NANO_lxplus.json"
    fileset_file.parent.mkdir(parents=True, exist_ok=True)

    with open(fileset_file, "w") as json_file:
        json.dump(new_dataset, json_file, indent=4, sort_keys=True)

    print(f"Fileset successfully saved to: {fileset_file}")