/*
 * SkyGuard AI - Embedded Edge Anomaly Detection & Self-Healing Library
 * Designed for ESP32 / ARM Cortex-M Microcontrollers (SIH26073)
 * Standard: C99 / C++11 compatible. Zero external dependencies.
 */

#ifndef SKYGUARD_EDGE_H
#define SKYGUARD_EDGE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Anomaly & Weather Classifications */
typedef enum {
    EDGE_CLASS_NORMAL = 0,
    EDGE_CLASS_GENUINE_EXTREME_WEATHER = 1,
    EDGE_CLASS_SPIKE = 2,
    EDGE_CLASS_FROZEN = 3,
    EDGE_CLASS_DRIFT = 4,
    EDGE_CLASS_COMMUNICATION_ERROR = 5,
    EDGE_CLASS_CORRUPTED_DATA = 6,
    EDGE_CLASS_OTHER_SENSOR_FAULT = 7
} skyguard_class_t;

/* Edge Inference Output Structure */
typedef struct {
    skyguard_class_t classification;
    float anomaly_score;       /* 0.0 to 1.0 */
    float confidence;          /* 0.0 to 100.0% */
    bool is_fault;
    bool is_extreme_weather;
    
    /* Derived Edge Physics */
    float dew_point_c;
    float vpd_hpa;
    bool physics_violation;

    /* On-Device Self-Healed Imputed Values */
    float imputed_temperature_c;
    float imputed_pressure_hpa;
    float imputed_humidity_pct;
    
    /* Diagnostics */
    uint32_t inference_time_us;
} skyguard_edge_result_t;

/* State context for embedded Kalman filter and temporal tracking */
typedef struct {
    float prev_temp;
    float prev_press;
    float prev_rh;
    uint32_t stuck_count_temp;
    uint32_t stuck_count_press;
    uint32_t stuck_count_rh;
    
    /* Kalman states */
    float k_state_temp;
    float k_cov_temp;
    float k_state_press;
    float k_cov_press;
    float k_state_rh;
    float k_cov_rh;
    
    bool initialized;
} skyguard_edge_context_t;

/* API Functions */
void skyguard_edge_init(skyguard_edge_context_t *ctx, float init_t, float init_p, float init_rh);
void skyguard_edge_process(
    skyguard_edge_context_t *ctx,
    float raw_temp,
    float raw_press,
    float raw_rh,
    skyguard_edge_result_t *out_result
);

#ifdef __cplusplus
}
#endif

#endif /* SKYGUARD_EDGE_H */
