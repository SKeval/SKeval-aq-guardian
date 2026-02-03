# PHASE 0: Project Setup & Environment
## AQ-Guardian - Germany-Wide Air Quality System

## ✅ DECISION SUMMARY

**Target Region**: Germany-wide (all major cities)  
**GitHub Repo**: https://github.com/SKeval/aq-guardian  
**Time**: 2–3 hours per day, Berlin time, daily check-ins.

## DATA SOURCES

### Air Quality: Umweltbundesamt (UBA)
- API docs: https://luftqualitaet.api.bund.dev [web:66]
- 400+ stations across Germany, hourly data, pollutants: PM10, PM2.5, NO2, O3, CO, SO2.[web:57][web:60]
- Free, official open data.[web:57][web:60]

### Weather: Open-Meteo (DWD-based)
- API docs: https://open-meteo.com/en/docs/dwd-api [web:72]
- Hourly weather (temperature, humidity, wind, pressure), Germany-focused, free.[web:72][web:75]

---

## TASK 1: Project Structure

From repo root:

```bash
mkdir -p data/{raw,processed,external} \
         notebooks \
         src/{data,features,models,api,dashboard} \
         models logs tests docs

touch src/__init__.py \
      src/data/__init__.py \
      src/features/__init__.py \
      src/models/__init__.py \
      src/api/__init__.py \
      src/dashboard/__init__.py
