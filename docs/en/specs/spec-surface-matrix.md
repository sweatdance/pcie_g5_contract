---
title: Spec Surface Matrix
description: Consolidated PCIe 5 governance surface map for navigation and smoke readiness
---

# Spec Surface Matrix

## Scope

This matrix is the compact index for all contract-defined PCIe 5 spec slices in this repo.

| Surface | Claim Level | Contract Surface | Key Evidence | Rule IDs | Smoke Suite | Primary Source | Gate action |
|---|---|---|---|---|---|---|---|
| LTSSM State Transitions | `required_gate_ready` | `pcie-ltssm` | `state_transition_ok`, `illegal_transition_count` | `PCIE5-LTSSM-STATE-001` .. `PCIE5-LTSSM-STATE-002` | `pcie-ltssm` | `PCIE5_LTSSM_STATE_TRANSITIONS.md` | required |
| LTSSM Checklist | `required_gate_ready` | `pcie-ltssm` | `ltssm_init_complete`, `recovery_paths_observed` | `PCIE5-LTSSM-STATE-001` .. `PCIE5-LTSSM-STATE-002` | `pcie-ltssm` | `PCIE5_LTSSM_CHECKLIST.md` | required |
| Link Equalization | `required_gate_ready` | `pcie-eq` | `equalization_complete`, `equalization_phase_summary` | `PCIE5-EQ-001` .. `PCIE5-EQ-002` | `pcie-eq` | `PCIE5_LINK_EQUALIZATION_RULES.md` | required |
| Speed & Width Negotiation | `required_gate_ready` | `pcie-link-negotiation` | `negotiated_width`, `link_width_request_ok` | `PCIE5-LINK-NEG-001` .. `PCIE5-LINK-NEG-002` | `pcie-link-negotiation` | `PCIE5_SPEED_WIDTH_NEGOTIATION.md` | required |
| Recovery and Fallback | `required_gate_ready` | `pcie-ltssm` | `downtrained`, `recovery_reason`, `fallback_reason` | `PCIE5-RECOVERY-001` | `pcie-ltssm` | `PCIE5_RECOVERY_AND_FALLBACK.md` | required |
| Power Management | `advisory_expansion` | `pcie-pm` | `pm_req_ack`, `l1_substate_mode` | `PCIE5-PM-001` .. `PCIE5-PM-017` | `pcie-pm` | `PCIE5_POWER_MANAGEMENT.md` | advisory |
| AER Rules | `advisory_expansion` | `pcie-aer` | `surprise_handled`, `aer_payload_logged` | `PCIE5-AER-001` .. `PCIE5-AER-013` | `pcie-aer` | `PCIE5_AER_RULES.md` | advisory |
| DLL Rules | `advisory_expansion` | `pcie-dll` | `dll_state_stability`, `dll_recovery_path` | `PCIE5-DLL-001` .. `PCIE5-DLL-011` | `pcie-dll` | `PCIE5_DLL_RULES.md` | advisory |
| TLP Rules | `advisory_expansion` | `pcie-tlp` | `tlp_ordering`, `completion_behavior` | `PCIE5-TLP-001` .. `PCIE5-TLP-013` | `pcie-tlp` | `PCIE5_TLP_RULES.md` | advisory |
| Hot-Plug Rules | `advisory_expansion` | `pcie-hotplug` | `hotplug_entry_guard`, `fast_link_trainer` | `PCIE5-HP-001` .. `PCIE5-HP-016` | `pcie-hotplug` | `PCIE5_HOTPLUG_RULES.md` | advisory |
| Config Space | `advisory_expansion` | `pcie-cfgspace` | `vendor_id_present`, `did_vid_mandatory` | `PCIE5-CFG-001` .. `PCIE5-CFG-026` | `pcie-cfgspace` | `PCIE5_CONFIG_SPACE.md` | advisory |

## Consumption rule

- Only `required_gate_ready` surfaces may be treated as required for hard CI gate decisions.
- Advisory surfaces support investigation and evidence triage but cannot alone satisfy hard-stop readiness.

## Fast path

- Required hard-stop checks: `pcie-ltssm`, `pcie-eq`, `pcie-link-negotiation`.
- Advisory scan path: `pcie-pm`, `pcie-aer`, `pcie-dll`, `pcie-tlp`, `pcie-hotplug`, `pcie-cfgspace`.
- Regression baseline command:

```powershell
python scripts/run_regression_smoke.py --suite all --format json
```

- Fixture audit command:

```powershell
python scripts/run_fixture_smoke.py --suite all --format json
```
