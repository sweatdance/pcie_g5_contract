---
title: Consumer Integration Contract
description: Downstream integration contract and boundary rules
---

# Consumer Integration Contract

## Status

- Type: artifact index
- Source completeness: source-linked page

## Scope

- Defines how downstream RTL consumers should interpret required vs advisory slices.
- Describes expected claim discipline for CI, review, and triage contexts.

## Canonical source

- [`CONSUMER_INTEGRATION_CONTRACT.md`](../../../CONSUMER_INTEGRATION_CONTRACT.md)

## Decision matrix

- Required gate consumers: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`
- Advisory consumers: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`
- Required assertions must be backed by required fixture and regression suites.

## Open scope

- Link examples for each downstream repo profile (strict/safe/observability).
