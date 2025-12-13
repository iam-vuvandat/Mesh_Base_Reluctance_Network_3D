from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Output:
    flux_direct : Any

def find_flux_direct(element):
    flux_direct = np.zeros((2,3))
    


    return Output(flux_direct= flux_direct)