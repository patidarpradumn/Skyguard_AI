"""Spatial neighborhood discovery and distance calculation using Haversine distance."""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class SpatialNeighborhood:
    """Manages geographic distances and neighborhood clusters between AWS stations."""

    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes great-circle distance between two GPS coordinates in kilometers."""
        r = 6371.0 # Earth radius in km
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        dphi = np.radians(lat2 - lat1)
        dlambda = np.radians(lon2 - lon1)

        a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
        c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
        return r * c

    @classmethod
    def get_station_neighbors(
        cls,
        station_df: pd.DataFrame,
        max_radius_km: float = 75.0,
        max_neighbors: int = 5
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Finds neighboring stations and their distances for each unique station."""
        stations = station_df[["station_id", "latitude", "longitude"]].drop_duplicates().to_dict("records")
        neighbors_map = {}

        for st1 in stations:
            sid1 = st1["station_id"]
            distances = []
            for st2 in stations:
                sid2 = st2["station_id"]
                if sid1 == sid2:
                    continue
                dist = cls.haversine_distance_km(st1["latitude"], st1["longitude"], st2["latitude"], st2["longitude"])
                if dist <= max_radius_km:
                    distances.append((sid2, dist))

            distances.sort(key=lambda x: x[1])
            neighbors_map[sid1] = distances[:max_neighbors]

        return neighbors_map
