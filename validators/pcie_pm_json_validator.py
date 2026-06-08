#!/usr/bin/env python3
"""Advisory validator for PCIe Power Management JSON evidence."""

from governance_tools.validator_interface import DomainValidator, ValidatorResult


class PciePmJsonValidator(DomainValidator):
    SUPPORTED_SCHEMA_VERSION = "1.0"
    REQUIRED_KEYS = {
        "enumeration_complete",
        "pm_l1_observed",
        "aspm_enabled_by_cfgwr",
        "link_control_aspm_value",
        "pm_request_ack_in_enum_window",
    }

    @property
    def rule_ids(self) -> list[str]:
        return [
            "pcie-pm",
            "PCIE5-PM-001", "PCIE5-PM-002", "PCIE5-PM-003",
            "PCIE5-PM-004", "PCIE5-PM-005", "PCIE5-PM-006",
            "PCIE5-PM-007", "PCIE5-PM-008", "PCIE5-PM-009",
            "PCIE5-PM-010", "PCIE5-PM-011", "PCIE5-PM-012",
            "PCIE5-PM-013", "PCIE5-PM-014", "PCIE5-PM-015",
            "PCIE5-PM-016", "PCIE5-PM-017",
        ]

    def validate(self, payload: dict) -> ValidatorResult:
        checks = payload.get("checks") or {}
        report = checks.get("pcie_pm_report") or {}

        if not report:
            return ValidatorResult(
                ok=True,
                rule_ids=self.rule_ids,
                warnings=["PCIe PM JSON report not provided; validator ran in advisory no-evidence mode"],
                evidence_summary="No pcie_pm_report object found in checks",
                metadata={"mode": "advisory", "report_present": False},
            )

        missing = sorted(self.REQUIRED_KEYS - set(report))
        warnings: list[str] = []
        violations: list[str] = []

        if missing:
            violations.append(f"Missing required report keys: {', '.join(missing)}")

        schema_version = report.get("schema_version")
        if schema_version is not None:
            if not isinstance(schema_version, str) or schema_version.strip() != self.SUPPORTED_SCHEMA_VERSION:
                violations.append(
                    f"Unsupported schema_version: {schema_version!r}; expected {self.SUPPORTED_SCHEMA_VERSION!r}"
                )

        enumeration_complete = report.get("enumeration_complete")
        pm_l1_observed = report.get("pm_l1_observed")
        aspm_enabled_by_cfgwr = report.get("aspm_enabled_by_cfgwr")
        pm_request_ack_in_enum_window = report.get("pm_request_ack_in_enum_window")
        link_control_aspm_value = report.get("link_control_aspm_value")
        l1_cycle_count = report.get("l1_cycle_count")
        notes = report.get("notes")

        for key, value in [
            ("enumeration_complete", enumeration_complete),
            ("pm_l1_observed", pm_l1_observed),
            ("aspm_enabled_by_cfgwr", aspm_enabled_by_cfgwr),
            ("pm_request_ack_in_enum_window", pm_request_ack_in_enum_window),
        ]:
            if value is not None and not isinstance(value, bool):
                violations.append(f"{key} must be a boolean")

        if link_control_aspm_value is not None and (
            not isinstance(link_control_aspm_value, str) or not link_control_aspm_value.strip()
        ):
            violations.append("link_control_aspm_value must be a non-empty string when provided")

        # PCIE5-PM-001: PM L1 must not occur before enumeration completes
        if pm_l1_observed is True and enumeration_complete is False:
            violations.append(
                "PCIE5-PM-001: PM_Active_State_Request_L1 observed before enumeration was complete "
                "(no VID/DID CfgRd 0x000 confirmed). PM L1 must not interrupt enumeration."
            )

        # PCIE5-PM-002: PM L1 without ASPM enable via CfgWr is an unexpected trigger path
        if pm_l1_observed is True and aspm_enabled_by_cfgwr is False:
            violations.append(
                "PCIE5-PM-002: PM_Active_State_Request_L1 observed but no CfgWr to Link Control "
                "(Reg=0x090) enabling ASPM was found. Unexpected PM L1 trigger path must be identified."
            )

        # PCIE5-PM-003: Host ACK during enumeration window
        if pm_request_ack_in_enum_window is True:
            violations.append(
                "PCIE5-PM-003: PM_Request_Ack sent by host downstream port while new device "
                "enumeration was not yet complete. Host ACKed L1 during the critical enumeration window."
            )

        # Conditional field checks
        if pm_l1_observed is True:
            if not report.get("pm_l1_timestamp"):
                warnings.append("pm_l1_timestamp should be provided when pm_l1_observed = true")
        if aspm_enabled_by_cfgwr is True:
            if not report.get("aspm_enable_timestamp"):
                warnings.append("aspm_enable_timestamp should be provided when aspm_enabled_by_cfgwr = true")
        if enumeration_complete is True:
            if not report.get("vidpid_read_timestamp"):
                warnings.append("vidpid_read_timestamp should be provided when enumeration_complete = true")

        # PCIE5-PM-005: warn if L1 cycle count is high
        if isinstance(l1_cycle_count, int) and l1_cycle_count > 3:
            warnings.append(
                f"PCIE5-PM-005: l1_cycle_count={l1_cycle_count} > 3 after enumeration; "
                "excessive idle timer sensitivity may warrant review."
            )

        # ---- D-state rules ----
        d_state_observed = report.get("d_state_transition_observed")
        d_state_to = report.get("d_state_to")
        transactions_pending_zero = report.get("transactions_pending_zero")
        pmcsr_written = report.get("pmcsr_written")
        pme_en_set = report.get("pme_en_set")
        pme_status_cleared = report.get("pme_status_cleared")
        d3hot_to_d0_trst = report.get("d3hot_to_d0_trst_observed")

        # PCIE5-PM-007: Writing PMCSR to unsupported D1/D2 (check via pmcsr_value)
        pmcsr_value = report.get("pmcsr_value")
        if pmcsr_written is True and pmcsr_value is not None and isinstance(pmcsr_value, str):
            try:
                pmcsr_int = int(pmcsr_value, 16)
                power_state = pmcsr_int & 0x3
                if power_state in (1, 2):  # D1 or D2
                    warnings.append(
                        f"PCIE5-PM-007: PMCSR written with PowerState={power_state} (D{power_state}); "
                        "verify PM Capabilities D1_Support/D2_Support bits confirm this state is supported."
                    )
            except ValueError:
                pass

        # PCIE5-PM-008: D3hot write with Transactions Pending
        if d_state_observed is True and d_state_to == "D3hot":
            if transactions_pending_zero is False:
                violations.append(
                    "PCIE5-PM-008: PMCSR written to D3hot while Transactions Pending (Device Status bit5) "
                    "was reported non-zero. All outstanding completions must drain before D3hot entry."
                )
            if transactions_pending_zero is None:
                warnings.append(
                    "PCIE5-PM-008: D3hot transition observed but transactions_pending_zero is not reported; "
                    "confirm Device Status bit5=0 before D3hot."
                )

        # PCIE5-PM-010: D3hot→D0 without Trst delay
        if d_state_observed is True and d_state_to == "D0" and report.get("d_state_from") == "D3hot":
            if d3hot_to_d0_trst is False:
                warnings.append(
                    "PCIE5-PM-010: D3hot→D0 transition observed but d3hot_to_d0_trst_observed=false; "
                    "Trst (≥1ms, typically 10–100ms) must elapse before device is accessed."
                )

        # PCIE5-PM-011: PME_Status not cleared
        if pme_en_set is True and pme_status_cleared is False:
            warnings.append(
                "PCIE5-PM-011: PME_En is set but pme_status_cleared=false; "
                "stale PME_Status in PMCSR blocks subsequent PME delivery. Clear with write-1-to-clear."
            )

        # ---- L1 PM Substates rules ----
        l1pm_configured = report.get("l1pm_substates_configured")
        ltr_threshold_nonzero = report.get("ltr_l1_2_threshold_nonzero")
        t_power_on_ok = report.get("t_power_on_programmed_correctly")
        cm_restore_ok = report.get("common_mode_restore_time_sufficient")
        l1_substate_mode = report.get("l1_substate_mode")

        # PCIE5-PM-013: L1.2 enabled without capability confirmation
        if l1_substate_mode in ("L1.2", "L1.1_and_L1.2") and l1pm_configured is False:
            warnings.append(
                "PCIE5-PM-013: L1.2 mode indicated but l1pm_substates_configured=false; "
                "L1 PM Substates Control registers must be written before L1.2 entry."
            )

        # PCIE5-PM-014: T_POWER_ON under-programmed
        if l1pm_configured is True and t_power_on_ok is False:
            warnings.append(
                "PCIE5-PM-014: t_power_on_programmed_correctly=false; T_POWER_ON in L1 PM Substates "
                "Control 2 is less than Port T_POWER_ON from Capabilities. L1.2 exit may fail."
            )

        # PCIE5-PM-015: LTR_L1.2_Threshold=0 (unconditional L1.2)
        if l1pm_configured is True and ltr_threshold_nonzero is False:
            warnings.append(
                "PCIE5-PM-015: ltr_l1_2_threshold_nonzero=false; LTR_L1.2_Threshold=0 means L1.2 "
                "entry is never gated by LTR requirements. Confirm this is intentional."
            )

        # PCIE5-PM-016: Common Mode Restore Time insufficient
        if l1pm_configured is True and cm_restore_ok is False:
            warnings.append(
                "PCIE5-PM-016: common_mode_restore_time_sufficient=false; Common_Mode_Restore_Time "
                "in L1 PM Substates Control 1 is less than Port Common Mode Restore Time from "
                "Capabilities. L1.1 exit may fail."
            )

        if notes is not None and not (isinstance(notes, list) and all(isinstance(n, str) for n in notes)):
            violations.append("notes must be a list of strings when provided")

        return ValidatorResult(
            ok=len(violations) == 0,
            rule_ids=self.rule_ids,
            violations=violations,
            warnings=warnings,
            evidence_summary="Validated PCIe Power Management JSON evidence",
            metadata={
                "mode": "enforcing",
                "report_present": True,
                "enumeration_complete": enumeration_complete,
                "pm_l1_observed": pm_l1_observed,
                "aspm_enabled_by_cfgwr": aspm_enabled_by_cfgwr,
                "pm_request_ack_in_enum_window": pm_request_ack_in_enum_window,
                "link_control_aspm_value": link_control_aspm_value,
                "l1_cycle_count": l1_cycle_count,
                "d_state_transition_observed": d_state_observed,
                "l1_substate_mode": l1_substate_mode,
                "l1pm_substates_configured": l1pm_configured,
            },
        )
