# Healthcare HMIS Operational KPIs & Analytics Definitions

## 1. Executive Overview
The Healthcare HMIS module ingests public health data (from Data.gov.in / OGD API and synthetic facility streams) to compute operational indicators across maternal health, child immunization, and facility capacity.

## 2. Key Healthcare Operational Metrics (Gold Mart)
- **Bed Occupancy Rate (BOR)**: Ratio of occupied beds to total available beds across hospital facilities. Target range: 75% - 85%.
- **Average Length of Stay (ALOS)**: Mean number of days patients remain admitted per episode. Target: < 4.5 days for general acute care.
- **ANC 4th Checkup Coverage**: Percentage of pregnant women receiving at least 4 antenatal care checkups.
- **Full Immunization Rate**: Proportion of infants receiving BCG, OPV, DPT/Pentavalent, and Measles vaccines before age 1.
- **Facility Outbreak Risk Index**: Statistical anomaly score indicating localized spikes in disease notifications.

## 3. Data Quality & Quarantine Criteria
Healthcare data from public APIs (Data.gov.in) must pass strict validation checks:
- Mandatory non-null district and state codes.
- Facility reporting counts must be non-negative.
- Invalid or missing parameters trigger quarantine logging to `healthcare_quarantine`.
