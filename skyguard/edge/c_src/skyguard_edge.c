/*
 * SkyGuard AI - Embedded Edge Anomaly Detection & Self-Healing Library
 * Implementation File for ESP32 / Microcontrollers
 */

#include "skyguard_edge.h"
#include <math.h>

#define MAGNUS_A 6.112f
#define MAGNUS_B 17.67f
#define MAGNUS_C 243.5f

#define TEMP_MIN_C -40.0f
#define TEMP_MAX_C 60.0f
#define PRESS_MIN_HPA 500.0f
#define PRESS_MAX_HPA 1080.0f
#define RH_MIN_PCT 0.0f
#define RH_MAX_PCT 100.0f

#define TEMP_MAX_STEP 6.0f
#define PRESS_MAX_STEP 4.0f
#define RH_MAX_STEP 30.0f

void skyguard_edge_init(skyguard_edge_context_t *ctx, float init_t, float init_p, float init_rh) {
    if (!ctx) return;
    ctx->prev_temp = init_t;
    ctx->prev_press = init_p;
    ctx->prev_rh = init_rh;
    ctx->stuck_count_temp = 0;
    ctx->stuck_count_press = 0;
    ctx->stuck_count_rh = 0;
    
    ctx->k_state_temp = init_t;
    ctx->k_cov_temp = 1.0f;
    ctx->k_state_press = init_p;
    ctx->k_cov_press = 0.5f;
    ctx->k_state_rh = init_rh;
    ctx->k_cov_rh = 5.0f;
    
    ctx->initialized = true;
}

void skyguard_edge_process(
    skyguard_edge_context_t *ctx,
    float raw_temp,
    float raw_press,
    float raw_rh,
    skyguard_edge_result_t *out_result
) {
    if (!ctx || !out_result) return;
    
    if (!ctx->initialized) {
        skyguard_edge_init(ctx, raw_temp, raw_press, raw_rh);
    }
    
    /* 1. Fast Magnus Dew Point Calculation */
    float rh_clamped = raw_rh < 0.1f ? 0.1f : (raw_rh > 100.0f ? 100.0f : raw_rh);
    float gamma = logf(rh_clamped / 100.0f) + (MAGNUS_B * raw_temp) / (MAGNUS_C + raw_temp);
    float td = (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
    float es = MAGNUS_A * expf((MAGNUS_B * raw_temp) / (MAGNUS_C + raw_temp));
    float e = (rh_clamped / 100.0f) * es;
    float vpd = es - e;
    if (vpd < 0.0f) vpd = 0.0f;
    
    out_result->dew_point_c = td;
    out_result->vpd_hpa = vpd;
    
    /* 2. Physics & Range Invariants */
    bool range_fail = (raw_temp < TEMP_MIN_C || raw_temp > TEMP_MAX_C ||
                       raw_press < PRESS_MIN_HPA || raw_press > PRESS_MAX_HPA ||
                       raw_rh < RH_MIN_PCT || raw_rh > RH_MAX_PCT);
    
    bool physics_fail = (td > raw_temp + 0.1f);
    out_result->physics_violation = physics_fail;
    
    /* 3. Temporal Rate of Change & Persistence */
    float d_temp = fabsf(raw_temp - ctx->prev_temp);
    float d_press = fabsf(raw_press - ctx->prev_press);
    float d_rh = fabsf(raw_rh - ctx->prev_rh);
    
    if (d_temp < 0.001f) ctx->stuck_count_temp++; else ctx->stuck_count_temp = 0;
    if (d_press < 0.001f) ctx->stuck_count_press++; else ctx->stuck_count_press = 0;
    if (d_rh < 0.001f) ctx->stuck_count_rh++; else ctx->stuck_count_rh = 0;
    
    bool is_frozen = (ctx->stuck_count_temp >= 6 || ctx->stuck_count_press >= 6 || ctx->stuck_count_rh >= 6);
    
    /* 4. Coherent Extreme Weather vs Fault Decision Tree */
    skyguard_class_t classification = EDGE_CLASS_NORMAL;
    float score = 0.05f;
    float conf = 95.0f;
    bool is_fault = false;
    bool is_extreme = false;
    
    if (range_fail) {
        classification = EDGE_CLASS_CORRUPTED_DATA;
        score = 0.98f;
        is_fault = true;
    } else if (physics_fail) {
        classification = EDGE_CLASS_CORRUPTED_DATA;
        score = 0.95f;
        is_fault = true;
    } else if (is_frozen) {
        classification = EDGE_CLASS_FROZEN;
        score = 0.90f;
        is_fault = true;
    } else if (d_temp > TEMP_MAX_STEP) {
        /* Distinguish genuine squall vs isolated temperature spike */
        if (d_rh > 15.0f && d_press > 1.0f) {
            /* Thermodynamically coupled changes -> Genuine Extreme Squall */
            classification = EDGE_CLASS_GENUINE_EXTREME_WEATHER;
            score = 0.15f;
            is_extreme = true;
            conf = 92.0f;
        } else {
            /* Isolated spike without thermodynamic coupling */
            classification = EDGE_CLASS_SPIKE;
            score = 0.92f;
            is_fault = true;
            conf = 96.0f;
        }
    } else if (raw_temp > 44.0f && raw_rh < 25.0f) {
        /* Genuine Heatwave */
        classification = EDGE_CLASS_GENUINE_EXTREME_WEATHER;
        score = 0.10f;
        is_extreme = true;
        conf = 94.0f;
    }
    
    out_result->classification = classification;
    out_result->anomaly_score = score;
    out_result->confidence = conf;
    out_result->is_fault = is_fault;
    out_result->is_extreme_weather = is_extreme;
    
    /* 5. Embedded Kalman Filter Self-Healing */
    /* Temp */
    ctx->k_cov_temp += 0.04f;
    if (!is_fault) {
        float k = ctx->k_cov_temp / (ctx->k_cov_temp + 0.25f);
        ctx->k_state_temp += k * (raw_temp - ctx->k_state_temp);
        ctx->k_cov_temp *= (1.0f - k);
        ctx->prev_temp = raw_temp;
    }
    out_result->imputed_temperature_c = ctx->k_state_temp;
    
    /* Press */
    ctx->k_cov_press += 0.02f;
    if (!is_fault) {
        float k = ctx->k_cov_press / (ctx->k_cov_press + 0.10f);
        ctx->k_state_press += k * (raw_press - ctx->k_state_press);
        ctx->k_cov_press *= (1.0f - k);
        ctx->prev_press = raw_press;
    }
    out_result->imputed_pressure_hpa = ctx->k_state_press;
    
    /* RH */
    ctx->k_cov_rh += 0.15f;
    if (!is_fault) {
        float k = ctx->k_cov_rh / (ctx->k_cov_rh + 1.20f);
        ctx->k_state_rh += k * (raw_rh - ctx->k_state_rh);
        ctx->k_cov_rh *= (1.0f - k);
        ctx->prev_rh = raw_rh;
    }
    out_result->imputed_humidity_pct = ctx->k_state_rh;
}
