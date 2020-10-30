from dataclasses import dataclass
import pandas as pd 
from vertex import Vertex

import pickle

@dataclass
class Event():
    ip: Vertex
    primary: pd.DataFrame 
    pileup: pd.DataFrame

    def save(self, path):
        with path.open('wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with path.open('rb') as f:
            event = pickle.load(f)
        return event