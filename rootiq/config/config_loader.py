from pathlib import Path
import yaml


class RootIQConfig:

    def __init__(self):

        config_path = (
            Path(__file__).parent / "rootiq.yaml"
        )

        with open(config_path, "r") as f:
            self.data = yaml.safe_load(f)

    @property
    def scan(self):
        return self.data.get("scan", {})