from dataclasses import dataclass


@dataclass
class Evidence:

    field: str

    expected: str

    actual: str