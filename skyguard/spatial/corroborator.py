"""Spatial Corroboration Engine with Graceful Degradation."""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from skyguard.spatial.neighborhood import SpatialNeighborhood


class SpatialCorroborator:
    """Computes spatial consistency against nearby stations.
    
    CRITICAL DESIGN: If no neighboring stations exist, spatial features default to neutral (0.0)
    and spatial_available is flagged as False, allowing graceful degradation without crashing.
    """

    def __init__(self, max_radius_km: float = 75.0, max_neighbors: int = 5):
        self.max_radius_km = max_radius_km
        self.max_neighbors = max_neighbors

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        num_stations = df["station_id"].nunique() if "station_id" in df.columns else 1
        if num_stations <= 1:
            # Single station fallback mode
            df["spatial_available"] = False
            df["neighbor_temp_median"] = df["temperature"]
            df["neighbor_temp_dev"] = 0.0
            df["neighbor_press_dev"] = 0.0
            df["neighbor_rh_dev"] = 0.0
            df["spatial_anomaly_score"] = 0.0
            return df

        # Multi-station network available
        df["spatial_available"] = True
        neighbors_map = SpatialNeighborhood.get_station_neighbors(df, self.max_radius_km, self.max_neighbors)

        # Pivot observations on timestamp to calculate spatial medians efficiently
        pivot_temp = df.pivot_table(index="timestamp", columns="station_id", values="temperature")
        pivot_press = df.pivot_table(index="timestamp", columns="station_id", values="pressure")
        pivot_rh = df.pivot_table(index="timestamp", columns="station_id", values="relative_humidity")

        # Compute deviations for each row
        dev_temp_list, dev_press_list, dev_rh_list = [], [], []

        for _, row in df.iterrows():
            st_id = row["station_id"]
            ts = row["timestamp"]
            st_neighbors = [n[0] for n in neighbors_map.get(st_id, [])]

            if not st_neighbors or ts not in pivot_temp.index:
                dev_temp_list.append(0.0)
                dev_press_list.append(0.0)
                dev_rh_list.append(0.0)
                continue

            # Robust median of neighbors
            n_temps = pivot_temp.loc[ts, st_neighbors].dropna()
            n_press = pivot_press.loc[ts, st_neighbors].dropna()
            n_rhs = pivot_rh.loc[ts, st_neighbors].dropna()

            t_dev = abs(row["temperature"] - n_temps.median()) if len(n_temps) > 0 else 0.0
            p_dev = abs(row["pressure"] - n_press.median()) if len(n_press) > 0 else 0.0
            rh_dev = abs(row["relative_humidity"] - n_rhs.median()) if len(n_rhs) > 0 else 0.0

            dev_temp_list.append(float(t_dev))
            dev_press_list.append(float(p_dev))
            dev_rh_list.append(float(rh_dev))

        df["neighbor_temp_dev"] = dev_temp_list
        df["neighbor_press_dev"] = dev_press_list
        df["neighbor_rh_dev"] = dev_rh_list

        # Spatial anomaly score: High when station deviates significantly from all surrounding stations
        # e.g. T deviation > 5°C or P dev > 4 hPa or RH dev > 30%
        sp_score = (
            np.clip(df["neighbor_temp_dev"] / 6.0, 0.0, 1.0) * 0.4 +
            np.clip(df["neighbor_press_dev"] / 4.0, 0.0, 1.0) * 0.3 +
            np.clip(df["neighbor_rh_dev"] / 35.0, 0.0, 1.0) * 0.3
        )
        df["spatial_anomaly_score"] = sp_score
        return df
