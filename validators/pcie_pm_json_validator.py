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
        return ["pcie-pm", "PCIE5-PM-001", "PCIE5-PM-002", "PCIE5-PM-003"]

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
            },
        )
