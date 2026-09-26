"""Atmospheric thermodynamics calculations based on peer-reviewed meteorological formulations.
Citations: Bolton (1980), Alduchov & Eskridge (1996), WMO-No. 8.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple


class AtmosphericThermodynamics:
    """Deterministic thermodynamic formulas using ONLY Temperature, Pressure, and Relative Humidity."""

    # Magnus-Tetens coefficients for water (Alduchov & Eskridge 1996)
    A_WATER: float = 6.112  # hPa
    B_WATER: float = 17.67  # dimensionless
    C_WATER: float = 243.5  # °C

    # Constants
    P0_HPA: float = 1000.0   # Reference pressure for potential temperature (hPa)
    KAPPA: float = 0.285714  # Poisson constant (R / cp = 287.058 / 1005.0)

    @classmethod
    def saturation_vapor_pressure(cls, temp_c: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
        """Calculates saturation vapor pressure e_s(T) in hPa using Magnus-Tetens formula.
        e_s(T) = A * exp( (B * T) / (C + T) )
        """
        return cls.A_WATER * np.exp((cls.B_WATER * temp_c) / (cls.C_WATER + temp_c))

    @classmethod
    def actual_vapor_pressure(
        cls,
        temp_c: Union[float, np.ndarray, pd.Series],
        rh_pct: Union[float, np.ndarray, pd.Series]
    ) -> Union[float, np.ndarray, pd.Series]:
        """Calculates actual vapor pressure e in hPa: e = (RH / 100) * e_s(T)."""
        rh_clamped = np.clip(rh_pct, 0.0, 100.0)
        es = cls.saturation_vapor_pressure(temp_c)
        return (rh_clamped / 100.0) * es

    @classmethod
    def dew_point(
        cls,
        temp_c: Union[float, np.ndarray, pd.Series],
        rh_pct: Union[float, np.ndarray, pd.Series]
    ) -> Union[float, np.ndarray, pd.Series]:
        """Calculates dew point temperature T_d in °C by inverting the Magnus formula.
        
        gamma(T, RH) = ln(RH / 100) + (B * T) / (C + T)
        T_d = (C * gamma) / (B - gamma)
        
        Guaranteed physical invariant: T_d <= T (when RH <= 100%).
        """
        rh_clamped = np.clip(rh_pct, 1e-4, 100.0)
        gamma = np.log(rh_clamped / 100.0) + (cls.B_WATER * temp_c) / (cls.C_WATER + temp_c)
        td = (cls.C_WATER * gamma) / (cls.B_WATER - gamma)
        return td

    @classmethod
    def vapor_pressure_deficit(
        cls,
        temp_c: Union[float, np.ndarray, pd.Series],
        rh_pct: Union[float, np.ndarray, pd.Series]
    ) -> Union[float, np.ndarray, pd.Series]:
        """Calculates Vapor Pressure Deficit (VPD) in hPa: VPD = e_s(T) - e.
        VPD is strictly >= 0 under physical conditions.
        """
        es = cls.saturation_vapor_pressure(temp_c)
        e = cls.actual_vapor_pressure(temp_c, rh_pct)
        return np.maximum(0.0, es - e)

    @classmethod
    def potential_temperature(
        cls,
        temp_c: Union[float, np.ndarray, pd.Series],
        pressure_hpa: Union[float, np.ndarray, pd.Series]
    ) -> Union[float, np.ndarray, pd.Series]:
        """Calculates Potential Temperature (theta) in Kelvin:
        theta = T_Kelvin * (P0 / P)^kappa
        """
        temp_k = temp_c + 273.15
        p_safe = np.maximum(100.0, pressure_hpa)
        theta = temp_k * np.power(cls.P0_HPA / p_safe, cls.KAPPA)
        return theta

    @classmethod
    def virtual_temperature(
        cls,
        temp_c: Union[float, np.ndarray, pd.Series],
        pressure_hpa: Union[float, np.ndarray, pd.Series],
        rh_pct: Union[float, np.ndarray, pd.Series]
    ) -> Union[float, np.ndarray, pd.Series]:
        """Calculates Virtual Temperature T_v in Kelvin:
        T_v = T_K * (1 + 0.61 * q) where q is specific humidity.
        """
        temp_k = temp_c + 273.15
        e = cls.actual_vapor_pressure(temp_c, rh_pct)
        p_safe = np.maximum(100.0, pressure_hpa)
        mixing_ratio = 0.622 * (e / (p_safe - e))
        q = mixing_ratio / (1.0 + mixing_ratio)
        tv = temp_k * (1.0 + 0.608 * q)
        return tv
