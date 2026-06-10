---
title: JSON Report Schema
description: Validator report schema reference for contract tooling
---

# JSON Report Schema

## Status

- Type: artifact index
- Source completeness: source-linked page

## Purpose

- Keep downstream parsers aligned to the same field names that this repo's smoke scripts and docs expect.
- Prevent wrong assumptions across required/advisory scripts.

## Canonical source

- [`PCIE5_JSON_REPORT_SCHEMA.md`](../../../PCIE5_JSON_REPORT_SCHEMA.md)

## Relevant report groups

- Required suites: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`
- Advisory suites: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`

## Workflow references

- Smoke outputs: `scripts/run_fixture_smoke.py`
- Regression outputs: `scripts/run_regression_smoke.py`

## Open scope

- Add field-by-field quick-check table for required outputs first, then advisory.
