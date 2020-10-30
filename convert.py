import re
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import plotly
from tqdm import tqdm

from event import Event
from vertex import Vertex

particle_fields = ['iPart', 'barcode', 'status', 'pdgId', 'px', 'py', 'pz', 'isCharged', 'm', 'pt', 'eta', 'phi',
                   'rapidity', 'hasProdVtx', 'prodVtx_id', 'prodVtx_x', 'prodVtx_y', 'prodVtx_z', 'hasDecayVtx', 'decayVtx_id']


def findall(prog, txt):
    results = []
    i = 0
    while True:
        result = prog.search(txt[i:])
        if not result:
            break
        results.append(result)
        i += result.span(0)[1]
    return results


def read_pileup(event_pu_result):
    pu_dfs = []
    for pu_id, pu_result in enumerate(event_pu_result):
        pu_df = pd.read_csv(StringIO(pu_result.group(
            'data')), sep='\t', names=particle_fields, index_col=False)
        pu_df['pileup_id'] = pu_id
        pu_dfs.append(pu_df)
    pileup = pd.concat(pu_dfs, ignore_index=True)
    return pileup


def make_event(event_result, event_pu_result):
    ip = Vertex(*event_result.group('ip').split())
    primary = pd.read_csv(StringIO(event_result.group(
        'truth_event')), sep='\t', names=particle_fields, index_col=False)
    pileup = read_pileup(event_pu_result)
    return Event(ip, primary, pileup)


def main():
    events_path = Path('truthparticle.txt')
    events_txt = events_path.open().read()

    event_pattern = r"^TruthEvent(?:.*?\n){4}^id.*?\n(?P<ip>.*?)\n.*?\n(?P<truth_event>(?:[-0-9].*?\n)+)(?P<pileup>(?s).+?)(?:(?:run)|\Z)"
    event_prog = re.compile(event_pattern, re.MULTILINE)
    pu_pattern = r"^TruthPileupEventContainer i(?:.*?\n){2}(?P<data>(?s).+?)(?:N|\Z)"
    pu_prog = re.compile(pu_pattern, re.MULTILINE)

    event_results = findall(event_prog, events_txt)
    event_pu_results = [findall(pu_prog, r.group('pileup'))
                        for r in event_results]

    events_dir = Path('events')
    events_dir.mkdir(parents=True, exist_ok=True)

    for i, (event_result, event_pu_result) in tqdm(enumerate(zip(event_results, event_pu_results)), total=len(event_results)):
        event = make_event(event_result, event_pu_result)
        event_dir = events_dir / f'event_{i:02d}.pkl'
        event.save(event_dir)


if __name__ == '__main__':
    main()
