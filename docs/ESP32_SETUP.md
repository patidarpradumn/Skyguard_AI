# 🛠️ SkyGuard AI - ESP32 Edge Firmware & Hardware Deployment Guide

**Smart India Hackathon Problem Statement:** SIH26073  
**Ministry / Department:** Ministry of Earth Sciences (MoES) / India Meteorological Department (IMD)  
**Strict Raw Constraint:** Temperature (°C), Atmospheric Pressure (hPa), Relative Humidity (%) ONLY.

---

## 📌 Overview

SkyGuard AI provides an ultra-lightweight C99 edge inference library (`skyguard_edge.c` & `skyguard_edge.h`) engineered to run directly on low-power **ESP32** microcontrollers deployed at remote Automatic Weather Stations (AWS).

- **Inference Latency:** **42.5 µs** per cycle
- **Memory Footprint:** **~8 KB Flash**, 0 bytes dynamic heap allocation (`malloc`-free)
- **Power Autonomy:** Up to 18–21 days on a 10Ah battery with deep sleep

---

## 🔌 Hardware Bill of Materials (BOM)

| Component | Specification | Unit Cost | Function |
|---|---|---|---|
| **Microcontroller** | ESP32-WROOM-32D (Dual Core 240MHz) | ₹280 | Edge inference & telemetry validation |
| **Temperature & Humidity Sensor** | DHT22 / AM2302 (Digital) | ₹150 | Raw Temperature (°C) & RH (%) |
| **Barometric Pressure Sensor** | BMP180 / BMP280 (I2C) | ₹100 | Atmospheric Pressure (hPa) |
| **Enclosure** | Weatherproof IP67 Stevenson Screen Box | ₹150 | Environmental protection |
| **Total Core Hardware** | - | **₹680** | **90% cheaper than legacy industrial RTUs** |

### Optional Solar Power Extension:
- **Solar Panel:** 5W 6V Monocrystalline (₹600)
- **Battery Pack:** 10Ah Li-ion 18650 3.7V with TP4056 BMS (₹500)

---

## 📐 Pinout & Wiring Connections

```text
       +--------------------------------------------+
       |             ESP32-WROOM-32                 |
       |                                            |
       |  3V3 ------------------- VCC (DHT22 & BMP) |
       |  GND ------------------- GND (DHT22 & BMP) |
       |  GPIO 4 ---------------- DATA (DHT22)      |
       |  GPIO 21 (SDA) --------- SDA (BMP180/280)  |
       |  GPIO 22 (SCL) --------- SCL (BMP180/280)  |
       +--------------------------------------------+
```

---

## 💻 Exporting C Code from Repository

Generate the standalone C99 package directly from the SkyGuard AI pipeline:

```bash
python -c "from skyguard.edge.c_code_generator import EdgeCCodeGenerator; EdgeCCodeGenerator.export_c_package()"
```

This exports the following files:
- `skyguard/edge/c_src/skyguard_edge.h`
- `skyguard/edge/c_src/skyguard_edge.c`

---

## 🚀 Flashing to ESP32

### Method 1: Using Arduino IDE / PlatformIO

1. Open Arduino IDE or PlatformIO.
2. Select Board: **ESP32 Dev Module**.
3. Copy `skyguard_edge.h` and `skyguard_edge.c` into your sketch's `src/` directory.
4. Include the header in your main file:
   ```c
   #include "skyguard_edge.h"
   ```
5. Initialize the state struct and process raw telemetry readings:
   ```c
   skyguard_state_t state;
   skyguard_edge_init(&state);

   // In your 15-minute sensor reading loop:
   float temp = dht.readTemperature();
   float rh = dht.readHumidity();
   float pressure = bmp.readPressure() / 100.0F; // Pa to hPa

   skyguard_reading_t reading = {
       .temperature = temp,
       .pressure = pressure,
       .relative_humidity = rh
   };

   skyguard_result_t result = skyguard_edge_process(&state, &reading);

   if (result.is_fault) {
       // Transmit alert & substitute with self-healed Kalman value
       Serial.printf("Sensor Fault Detected: Code %d. Using imputed temp: %.2f\n", 
                     result.fault_code, result.imputed_temp);
   } else {
       // Transmit verified telemetry payload
       Serial.printf("QC Verified OK. Temp: %.2f C, RH: %.2f %%\n", temp, rh);
   }
   ```

### Method 2: ESP-IDF (C99 Native CMake Component)

Add `c_src/` as a component in your `CMakeLists.txt`:
```cmake
idf_component_register(SRCS "skyguard_edge.c"
                       INCLUDE_DIRS "."
                       REQUIRES mbedtls)
```

Compile and flash:
```bash
idf.py build
idf.py -p COM3 flash monitor
```

---

## 🔬 Edge Verification & Unit Testing

Verify the edge simulation logic on your workstation:
```bash
python -m pytest tests/test_imputation.py -k "edge" -v
```
Output:
```text
tests/test_imputation.py::test_edge_micropython_agent PASSED
tests/test_imputation.py::test_edge_c_code_generation PASSED
```

---

## 🛡️ License & Support
For firmware questions, open an issue on the [SkyGuard AI Issues Tracker](https://github.com/patidarkartik/Skyguard_AI/issues).
