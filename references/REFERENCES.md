# 📚 SkyGuard AI - Scientific References & Authoritative Citations

This document provides peer-reviewed literature, meteorological standard manuals, and algorithmic citations underlying the SkyGuard AI architecture for Automatic Weather Stations (AWS).

---

## 1. Meteorological Standards & Quality Control
1. **World Meteorological Organization (WMO) (2018)**  
   *Guide to Meteorological Instruments and Methods of Observation (WMO-No. 8)*, Volume I – Measurement of Meteorological Variables. Geneva, Switzerland.  
   *Relevance:* Operational sensor range limits, response times, and standard instrument siting criteria.

2. **India Meteorological Department (IMD) (2021)**  
   *Quality Control and Validation Procedures for Automatic Weather Station (AWS) Networks*. Ministry of Earth Sciences, New Delhi.  
   *Relevance:* Step-by-step QC hierarchy: Plausibility bounds, rate-of-change thresholds, and neighbor check distances for India.

3. **Zahumenský, I. (2004)**  
   *Guidelines on Quality Control Procedures for Data from Automatic Weather Stations*. WMO TD-No. 1218, World Meteorological Organization.  
   *Relevance:* Real-time automated QC flags, persistence/stuck value tests, and spatial consensus methods.

---

## 2. Atmospheric Thermodynamics & Derived Formulations
4. **Bolton, D. (1980)**  
   "The computation of equivalent potential temperature." *Monthly Weather Review*, 108(7), 1046–1053.  
   *Relevance:* High-precision formulas for saturation vapor pressure $e_s(T)$ and potential temperature $\theta$.

5. **Alduchov, O. A., & Eskridge, R. E. (1996)**  
   "Improved Magnus form approximation of saturation vapor pressure." *Journal of Applied Meteorology and Climatology*, 35(4), 601–609.  
   *Relevance:* Optimized Magnus-Tetens coefficients: $a = 6.112\text{ hPa}, b = 17.67, c = 243.5^\circ\text{C}$ with $<0.05\%$ error in $-40^\circ\text{C} \le T \le 50^\circ\text{C}$.

6. **Monteith, J. L., & Unsworth, M. H. (2013)**  
   *Principles of Environmental Physics: Plants, Animals, and the Atmosphere*. Academic Press.  
   *Relevance:* Vapor Pressure Deficit (VPD) formulation and boundary layer thermodynamics.

---

## 3. Machine Learning, TreeSHAP & Anomaly Detection
7. **Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., ... & Liu, T. Y. (2017)**  
   "LightGBM: A highly efficient gradient boosting decision tree." *Advances in Neural Information Processing Systems (NeurIPS)*, 30, 3146–3154.  
   *Relevance:* High-speed multiclass tabular fault classification with histogram-based binning and leaf-wise tree growth.

8. **Lundberg, S. M., Erion, G., Chen, H., DeGrave, A., Prutkin, J. M., ... & Lee, S. I. (2020)**  
   "From local explanations to global understanding with explainable AI for trees." *Nature Machine Intelligence*, 2(1), 56–67.  
   *Relevance:* Exact polynomial-time TreeSHAP local feature attributions for real-time AWS anomaly explanations.

9. **Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008)**  
   "Isolation forest." In *2008 Eighth IEEE International Conference on Data Mining* (pp. 413-422). IEEE.  
   *Relevance:* Unsupervised baseline isolation tree benchmark.

---

## 4. State-Space Estimation & Self-Healing Imputation
10. **Kalman, R. E. (1960)**  
    "A new approach to linear filtering and prediction problems." *Journal of Basic Engineering*, 82(1), 35–45.  
    *Relevance:* Optimal recursive Bayesian state-space estimation for real-time sensor recovery and smooth imputation.

11. **Gelman, A., Hwang, J., & Vehtari, A. (2014)**  
    "Understanding predictive information criteria for Bayesian models." *Statistics and Computing*, 24(6), 997–1016.  
    *Relevance:* Confidence calibration and state variance quantification.
