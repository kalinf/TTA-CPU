import json
from pathlib import Path
from amaranth import *
from amaranth.build import Resource, Attrs, Pins


def create_resources(directory: Path):
    target_dir = directory.resolve()
    config_path = target_dir / "config_detail.json"
    with config_path.open() as f:
        configuration = json.load(f)
    resources = []
    if "resources" in configuration:
        for resource in configuration["resources"]:
            attrs = Attrs(**resource["attrs"])
            pins = Pins(
                resource["pins"]["pins"], dir=resource["pins"]["dir"], invert=resource["pins"].get("invert", False)
            )
            resources += [Resource(resource["name"], resource["number"], pins, attrs)]
    return resources


def add_resources(platform, resources):
    platform.add_resources(resources)


def get_requested_resources_names(directory: Path):
    target_dir = directory.resolve()
    config_path = target_dir / "config_detail.json"
    with config_path.open() as f:
        configuration = json.load(f)
    resources = []
    for f_unit in configuration["functional_units"]:
        if "resources" in f_unit:
            for resource in f_unit["resources"]:
                if resource not in resources:
                    resources += [resource]
    return resources
