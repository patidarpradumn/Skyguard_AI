"""Physical invariants and thermodynamic consistency checks for AWS observations."""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from skyguard.physics.thermodynamics import AtmosphericThermodynamics


class PhysicsInvariantChecker:
    """Verifies fundamental physical invariants derived from atmospheric thermodynamics."""

    @classmethod
    def check_invariants(
        cls,
        temp_c: float,
        pressure_hpa: float,
        rh_pct: float,
        tolerance_c: float = 0.05
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """Checks if an observation violates fundamental atmospheric invariants.
        
        Key Invariants:
        1. Dew Point <= Temperature: T_d cannot exceed T by more than measurement tolerance.
        2. VPD >= 0: Vapor pressure deficit must be non-negative.
        3. Potential Temperature bounds: 220 K <= theta <= 420 K for troposphere.
        4. RH Bounds: 0% <= RH <= 100%.
        
        Returns:
            (is_valid, violation_score, details_dict)
        """
        td = AtmosphericThermodynamics.dew_point(temp_c, rh_pct)
        vpd = AtmosphericThermodynamics.vapor_pressure_deficit(temp_c, rh_pct)
        theta = AtmosphericThermodynamics.potential_temperature(temp_c, pressure_hpa)

        violations = []
        violation_score = 0.0

        # Invariant 1: Td <= T
        td_excess = td - temp_c
        if td_excess > tolerance_c:
            violations.append(f"DEW_POINT_EXCEEDS_TEMP (Td={td:.2f}, T={temp_c:.2f}, excess={td_excess:.2f}°C)")
            violation_score += min(1.0, td_excess / 5.0)

        # Invariant 2: VPD >= 0
        if vpd < -1e-4:
            violations.append(f"NEGATIVE_VPD (VPD={vpd:.3f} hPa)")
            violation_score += 0.5

        # Invariant 3: Tropospheric Potential Temperature
        if theta < 220.0 or theta > 420.0:
            violations.append(f"UNREALISTIC_POTENTIAL_TEMP (theta={theta:.1f} K)")
            violation_score += 0.7

        # Invariant 4: RH bounds (0% to 100%)
        if rh_pct < 0.0 or rh_pct > 100.0:
            violations.append(f"SUPER_SATURATION_OR_NEGATIVE_RH (RH={rh_pct:.1f}%)")
            violation_score += 0.8

        is_valid = len(violations) == 0
        violation_score = float(np.clip(violation_score, 0.0, 1.0))

        details = {
            "dew_point_c": float(td),
            "dew_point_depression_c": float(temp_c - td),
            "vpd_hpa": float(vpd),
            "potential_temp_k": float(theta),
            "is_physically_valid": is_valid,
            "violations": violations,
            "physics_violation_score": violation_score
        }
        return is_valid, violation_score, details
