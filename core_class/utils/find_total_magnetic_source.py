import numpy as np 
from dataclasses import dataclass
from typing import Any

@dataclass
class Output:
    total_magnetic_source : Any

def find_total_magnetic_source(element):
    total_magnetic_source = element.magnet_source + element.winding_source

    return Output(total_magnetic_source= total_magnetic_source)