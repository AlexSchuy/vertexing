from pathlib import Path

import pandas as pd
import plotly
import plotly.express as px
from PyPDF2 import PdfFileMerger
from tqdm import tqdm

from event import Event


def write_images(merger, df, images_dir, log_y=False):
    for x in tqdm(df.columns):
        fig = px.histogram(df, x=x, log_y=log_y)
        image_path = images_dir / f'{x}.pdf'
        fig.write_image(str(image_path), width=1200, height=800)
        merger.append(str(image_path))


def main():
    events_dir = Path('events')
    events = [Event.load(p) for p in sorted(events_dir.glob('*.pkl'))]

    per_event_df = pd.DataFrame()
    per_event_df['ntracks_per_event'] = [
        e.primary.shape[0] + e.pileup.shape[0] for e in events]
    per_event_df['nprimary_tracks_per_event'] = [
        e.primary.shape[0] for e in events]
    per_event_df['npileup_tracks_per_event'] = [
        e.pileup.shape[0] for e in events]
    per_event_df['npileup_vertices_per_event'] = [
        e.pileup['pileup_id'].max()+1 for e in events]
    per_event_df['npileup_tracks_per_pileup_vertex_per_event'] = [
        e.pileup.shape[0]/(e.pileup['pileup_id'].max()+1) for e in events]

    per_pu_track_df = pd.DataFrame()
    per_pu_track_df['pileup_track_Vx'] = pd.concat(
        [e.pileup['prodVtx_x'] for e in events], ignore_index=True)
    per_pu_track_df['pileup_track_Vy'] = pd.concat(
        [e.pileup['prodVtx_y'] for e in events], ignore_index=True)
    per_pu_track_df['pileup_track_Vz'] = pd.concat(
        [e.pileup['prodVtx_z'] for e in events], ignore_index=True)

    per_hs_track_df = pd.DataFrame()
    per_hs_track_df['primary_track_Vx'] = pd.concat(
        [e.primary['prodVtx_x'] for e in events], ignore_index=True)
    per_hs_track_df['primary_track_Vy'] = pd.concat(
        [e.primary['prodVtx_y'] for e in events], ignore_index=True)
    per_hs_track_df['primary_track_Vz'] = pd.concat(
        [e.primary['prodVtx_z'] for e in events], ignore_index=True)

    per_track_df = pd.DataFrame()
    per_track_df['track_Vx'] = pd.concat(
        (per_pu_track_df['pileup_track_Vx'], per_hs_track_df['primary_track_Vx']), ignore_index=True)
    per_track_df['track_Vy'] = pd.concat(
        (per_pu_track_df['pileup_track_Vy'], per_hs_track_df['primary_track_Vy']), ignore_index=True)
    per_track_df['track_Vz'] = pd.concat(
        (per_pu_track_df['pileup_track_Vz'], per_hs_track_df['primary_track_Vz']), ignore_index=True)

    images_dir = Path('images')
    images_dir.mkdir(exist_ok=True, parents=True)

    merger = PdfFileMerger()
    write_images(merger, per_event_df, images_dir)
    write_images(merger, per_pu_track_df, images_dir, log_y=True)
    write_images(merger, per_hs_track_df, images_dir, log_y=True)
    write_images(merger, per_track_df, images_dir, log_y=True)
    merger.write(str(images_dir / 'images.pdf'))
    merger.close()


if __name__ == '__main__':
    main()
