# Quantifying CO2 and Cost Savings from Solar Wallbox Charging

Reproducible analysis and Hardware-in-the-Loop (HIL) validation for comparing solar (PV-first) and grid charging of an electric vehicle. Includes Python tools, HIL replay scripts, and a summary report with recommendations for PV sizing, storage options, and charging strategies.

## Project Overview

This project evaluates:
- PV-first (solar) charging
- Grid-only charging

The goal is to quantify CO2 emissions avoided and monetary savings. The project uses simulation data, reproducible Python notebooks, and HIL testing.

## Objectives

- Calculate per-session and annual CO2 savings.
- Compute cost savings between PV and grid charging.
- Compare PV-first and grid charging through HIL and offline replay.
- Run sensitivity studies for PV size, battery storage, and payback period.
- Provide a reusable toolkit and report.

## Motivation

Quantifying CO2 and cost benefits supports:
- Optimized EV charging strategies.
- Evidence-based PV and storage investment decisions.
- Standardized metrics for demonstrations and acceptance testing.

## System Configuration

### Consumer Profile
- Location: Freiburg, Germany
- Single-family house (125 m2)
- Two occupants
- Work pattern: 3 office days, 2 home-office days
- Weekly driving: 50 km office days, 50 km weekend shopping
- Car connected to wallbox on non-driving days

### PV System
- 10 kWp rooftop PV
- Orientation: True South
- Tilt: 48 degrees
- Simulated using Fraunhofer SynPro (1-minute resolution)

### EV Load
- Vehicle: VW ID.3 Pro (58 kWh battery, 320 km range)
- Weekly driving: 200 km
- Weekly recharge energy: (200/320) * 58 = 36.25 kWh
- Wallbox connection: Thursday, Friday, Sunday

### Tariffs and CO2 Emissions
- Electricity tariff: 0.48 EUR/kWh (flat rate)
- CO2 factors: hourly, from Electricity Maps / ENTSO-E

### Wallbox
- Amperfied Connect Solar Wallbox (11 kW)
