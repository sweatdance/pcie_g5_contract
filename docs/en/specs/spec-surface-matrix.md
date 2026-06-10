---
title: Spec Surface Matrix
description: Consolidated PCIe 5 governance surface map for navigation and smoke readiness
---

# Spec Surface Matrix

## Scope

This matrix is the compact index for all contract-defined PCIe 5 spec slices in this repo.

| Surface | Claim Level | Contract Surface | Key Evidence | Rule IDs | Smoke Suite | Primary source |
|---|---|---|---|---|---|---|
| LTSSM State Transitions | `required_gate_ready` | `pcie-ltssm` | `state_transition_ok`, `illegal_transition_count` | `PCIE5-LTSSM-001` … | `pcie-ltssm` | `PCIE5_LTSSM_STATE_TRANSITIONS.md` |
| LTSSM Checklist | `required_gate_ready` | `pcie-ltssm` | `ltssm_init_complete`, `recovery_paths_observed` | `PCIE5-LTSSM-CHK-...` | `pcie-ltssm` | `PCIE5_LTSSM_CHECKLIST.md` |
| Link Equalization | `required_gate_ready` | `pcie-eq` | `eq_phase_count`, `eq_start_stop_balance` | `PCIE5-EQ-001` … | `pcie-eq` | `PCIE5_LINK_EQUALIZATION_RULES.md` |
| Speed & Width Negotiation | `required_gate_ready` | `pcie-link-negotiation` | `negotiated_width`, `link_width_request_ok` | `PCIE5-LINK-...` | `pcie-link-negotiation` | `PCIE5_SPEED_WIDTH_NEGOTIATION.md` |
| Recovery and Fallback | `required_gate_ready` | `pcie-ltssm` | `downtrained`, `recovery_reason`, `fallback_reason` | `PCIE5-RECOVERY-...` | `pcie-ltssm` | `PCIE5_RECOVERY_AND_FALLBACK.md` |
| Power Management | `advisory_expansion` | `pcie-pm` | `pm_req_ack`, `l1_substate_mode` | `PCIE5-PM-001` … | `pcie-pm` | `PCIE5_POWER_MANAGEMENT.md` |
| AER Rules | `advisory_expansion` | `pcie-aer` | `surprise_handled`, `aer_payload_logged` | `PCIE5-AER-001` … | `pcie-aer` | `PCIE5_AER_RULES.md` |
| DLL Rules | `advisory_expansion` | `pcie-dll` | `dll_state_stability`, `dll_recovery_path` | `PCIE5-DLL-001` … | `pcie-dll` | `PCIE5_DLL_RULES.md` |
| TLP Rules | `advisory_expansion` | `pcie-tlp` | `tlp_ordering`, `completion_behavior` | `PCIE5-TLP-001` … | `pcie-tlp` | `PCIE5_TLP_RULES.md` |
| Hot-Plug Rules | `advisory_expansion` | `pcie-hotplug` | `hotplug_entry_guard`, `fast_link_trainer` | `PCIE5-HOTPLUG-001` … | `pcie-hotplug` | `PCIE5_HOTPLUG_RULES.md` |
| Config Space | `advisory_expansion` | `pcie-cfgspace` | `vendor_id_present`, `did_vid_mandatory` | `PCIE5-CFG-001` … | `pcie-cfgspace` | `PCIE5_CONFIG_SPACE.md` |

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

