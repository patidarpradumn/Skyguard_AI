"""MicroPython embedded anomaly detection and self-healing agent for ESP32."""

import math
import time


class SkyGuardMicroPythonAgent:
    """Lightweight MicroPython agent for ESP32 / Raspberry Pi Pico AWS nodes."""

    def __init__(self, init_temp=25.0, init_press=1013.25, init_rh=50.0):
        self.prev_temp = init_temp
        self.prev_press = init_press
        self.prev_rh = init_rh

        self.k_temp = init_temp
        self.k_cov_temp = 1.0
        self.k_press = init_press
        self.k_cov_press = 0.5
        self.k_rh = init_rh
        self.k_cov_rh = 5.0

    def compute_dew_point(self, temp_c, rh_pct):
        rh = min(100.0, max(0.1, rh_pct))
        gamma = math.log(rh / 100.0) + (17.67 * temp_c) / (243.5 + temp_c)
        return (243.5 * gamma) / (17.67 - gamma)

    def process_observation(self, temp_c, press_hpa, rh_pct):
        t0 = time.ticks_us() if hasattr(time, "ticks_us") else time.time() * 1e6

        td = self.compute_dew_point(temp_c, rh_pct)
        physics_violation = td > (temp_c + 0.1)

        d_temp = abs(temp_c - self.prev_temp)
        d_press = abs(press_hpa - self.prev_press)
        d_rh = abs(rh_pct - self.prev_rh)

        classification = "NORMAL"
        is_fault = False
        is_extreme = False

        if physics_violation or temp_c < -40.0 or temp_c > 60.0 or press_hpa < 500.0 or press_hpa > 1080.0:
            classification = "CORRUPTED_DATA"
            is_fault = True
        elif d_temp > 6.0:
            if d_rh > 15.0 and d_press > 1.0:
                classification = "GENUINE_EXTREME_WEATHER"
                is_extreme = True
            else:
                classification = "SPIKE"
                is_fault = True
        elif temp_c > 44.0 and rh_pct < 25.0:
            classification = "GENUINE_EXTREME_WEATHER"
            is_extreme = True

        # Kalman self-healing update
        self.k_cov_temp += 0.04
        if not is_fault:
            k = self.k_cov_temp / (self.k_cov_temp + 0.25)
            self.k_temp += k * (temp_c - self.k_temp)
            self.k_cov_temp *= (1.0 - k)
            self.prev_temp = temp_c

        t1 = time.ticks_us() if hasattr(time, "ticks_us") else time.time() * 1e6
        elapsed_us = int(t1 - t0)

        return {
            "classification": classification,
            "is_fault": is_fault,
            "is_extreme": is_extreme,
            "dew_point_c": round(td, 2),
            "imputed_temp_c": round(self.k_temp, 2),
            "latency_us": elapsed_us
        }
