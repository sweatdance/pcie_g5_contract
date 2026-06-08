#!/usr/bin/env python3
"""Advisory validator for PCIe Configuration Space JSON evidence."""

from governance_tools.validator_interface import DomainValidator, ValidatorResult


class PcieCfgspaceJsonValidator(DomainValidator):
    SUPPORTED_SCHEMA_VERSION = "1.0"
    REQUIRED_KEYS = {
        "vidpid_read_observed",
        "enumeration_sequence_complete",
        "bar_sizing_observed",
    }

    @property
    def rule_ids(self) -> list[str]:
        return [
            "pcie-cfgspace",
            "PCIE5-CFG-001", "PCIE5-CFG-002", "PCIE5-CFG-003",
            "PCIE5-CFG-004", "PCIE5-CFG-005", "PCIE5-CFG-006",
            "PCIE5-CFG-007", "PCIE5-CFG-008", "PCIE5-CFG-009",
            "PCIE5-CFG-010", "PCIE5-CFG-011", "PCIE5-CFG-012",
            "PCIE5-CFG-013", "PCIE5-CFG-014", "PCIE5-CFG-015",
            "PCIE5-CFG-016", "PCIE5-CFG-017", "PCIE5-CFG-018",
            "PCIE5-CFG-019", "PCIE5-CFG-020", "PCIE5-CFG-021",
            "PCIE5-CFG-022", "PCIE5-CFG-023", "PCIE5-CFG-024",
            "PCIE5-CFG-025", "PCIE5-CFG-026",
        ]

    def validate(self, payload: dict) -> ValidatorResult:
        checks = payload.get("checks") or {}
        report = checks.get("pcie_cfgspace_report") or {}

        if not report:
            return ValidatorResult(
                ok=True,
                rule_ids=self.rule_ids,
                warnings=["PCIe Config Space JSON report not provided; validator ran in advisory no-evidence mode"],
                evidence_summary="No pcie_cfgspace_report object found in checks",
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

        vidpid_read = report.get("vidpid_read_observed")
        enum_complete = report.get("enumeration_sequence_complete")
        bar_sizing = report.get("bar_sizing_observed")
        bus_master = report.get("bus_master_enabled")
        memory_space = report.get("memory_space_enabled")
        intx_disable = report.get("intx_disable")
        msi_enabled = report.get("msi_or_msix_enabled")
        msi_type = report.get("msi_type")
        msi_addr_valid = report.get("msi_address_valid")
        capability_traversed = report.get("capability_chain_traversed")
        link_ctrl_rmw = report.get("link_control_read_before_write")
        class_code = report.get("class_code_value")
        subsystem_read = report.get("subsystem_vidpid_read")
        ltr_enabled = report.get("ltr_enabled")
        ltr_msg_sent = report.get("ltr_message_sent")
        l1pm_configured = report.get("l1pm_substates_configured")
        command_value = report.get("command_register_value")
        notes = report.get("notes")

        for key, value in [
            ("vidpid_read_observed", vidpid_read),
            ("enumeration_sequence_complete", enum_complete),
            ("bar_sizing_observed", bar_sizing),
            ("bus_master_enabled", bus_master),
            ("memory_space_enabled", memory_space),
            ("msi_or_msix_enabled", msi_enabled),
        ]:
            if value is not None and not isinstance(value, bool):
                violations.append(f"{key} must be a boolean")

        # PCIE5-CFG-001: VID/DID read must be present when enumeration claimed
        if enum_complete is True and vidpid_read is False:
            violations.append(
                "PCIE5-CFG-001: enumeration_sequence_complete=true but vidpid_read_observed=false. "
                "VID/DID CfgRd 0x000 is mandatory before claiming enumeration complete."
            )

        # PCIE5-CFG-006: Memory Space Enable before BAR access
        if memory_space is False and enum_complete is True:
            violations.append(
                "PCIE5-CFG-006: memory_space_enabled=false but enumeration_sequence_complete=true. "
                "Memory Space Enable (Command bit1) must be set before MRd/MWr to BAR space."
            )

        # PCIE5-CFG-013: Class code present and non-zero
        if class_code is not None and isinstance(class_code, str):
            if class_code.lstrip("0x").lstrip("0") == "" or class_code.upper() in ("FFFFFF", "0XFFFFFF"):
                violations.append(
                    "PCIE5-CFG-013: class_code_value is all-zeros or all-F; device class cannot be determined. "
                    "Verify CfgRd 0x008 returned a valid class code."
                )
        elif enum_complete is True and class_code is None:
            warnings.append("PCIE5-CFG-013: class_code_value not provided; cannot confirm device class.")

        # PCIE5-CFG-002: BAR sizing evidence missing
        if bar_sizing is False and enum_complete is True:
            warnings.append(
                "PCIE5-CFG-002: bar_sizing_observed=false but enumeration_sequence_complete=true. "
                "BAR sizing probe (CfgWr FFFFFFFF → CfgRd → CfgWr address) evidence is missing."
            )

        # PCIE5-CFG-003: Capability chain not traversed before extended caps
        if capability_traversed is False and enum_complete is True:
            warnings.append(
                "PCIE5-CFG-003: capability_chain_traversed=false; PCIe Extended Capability pointer "
                "should be read before any extended capability (offset >= 0x100) is accessed."
            )

        # PCIE5-CFG-004: Link Control RMW
        if link_ctrl_rmw is False:
            warnings.append(
                "PCIE5-CFG-004: link_control_read_before_write=false; Link Control (0x090) write "
                "was not preceded by a read. Bare write risks overwriting ASPM, speed, or width bits."
            )

        # PCIE5-CFG-005: Bus Master Enable
        if bus_master is False and enum_complete is True:
            warnings.append(
                "PCIE5-CFG-005: bus_master_enabled=false; Bus Master Enable (Command bit2) must be "
                "set before any DMA (device-initiated MRd/MWr) is expected."
            )

        # PCIE5-CFG-007: MSI/MSI-X enable check
        if msi_enabled is True:
            if intx_disable is False:
                warnings.append(
                    "PCIE5-CFG-016: msi_or_msix_enabled=true but intx_disable=false; "
                    "INTx Disable (Command bit10) must be set when MSI or MSI-X is active."
                )
            if msi_addr_valid is False:
                warnings.append(
                    "PCIE5-CFG-019: msi_address_valid=false; MSI Message Address is invalid (zero or all-F). "
                    "MSI interrupts cannot be delivered to an invalid APIC address."
                )

        # PCIE5-CFG-012: Subsystem VID/ID
        if subsystem_read is False and enum_complete is True:
            warnings.append(
                "PCIE5-CFG-012: subsystem_vidpid_read=false; Subsystem VID/ID (CfgRd 0x02C) was not "
                "observed during enumeration. Platform-level device identity is unconfirmed."
            )

        # PCIE5-CFG-010: LTR Enable without LTR message
        if ltr_enabled is True and ltr_msg_sent is False:
            warnings.append(
                "PCIE5-CFG-010: ltr_enabled=true but ltr_message_sent=false; LTR Enable (Device "
                "Control 2 bit10) must only be set after the device has sent an LTR message."
            )

        # PCIE5-CFG-011: L1 PM Substates not configured for L1.1/L1.2 scenarios
        if l1pm_configured is False and report.get("l1pm_control1_value") is not None:
            warnings.append(
                "PCIE5-CFG-011: l1pm_control1_value is provided but l1pm_substates_configured=false; "
                "L1 PM Substates Control registers must be fully programmed before L1.1/L1.2 entry."
            )

        if notes is not None and not (isinstance(notes, list) and all(isinstance(n, str) for n in notes)):
            violations.append("notes must be a list of strings when provided")

        return ValidatorResult(
            ok=len(violations) == 0,
            rule_ids=self.rule_ids,
            violations=violations,
            warnings=warnings,
            evidence_summary="Validated PCIe Configuration Space JSON evidence",
            metadata={
                "mode": "enforcing",
                "report_present": True,
                "vidpid_read_observed": vidpid_read,
                "vidpid_value": report.get("vidpid_value"),
                "class_code_value": class_code,
                "enumeration_sequence_complete": enum_complete,
                "memory_space_enabled": memory_space,
                "bus_master_enabled": bus_master,
                "msi_or_msix_enabled": msi_enabled,
                "msi_type": msi_type,
                "ltr_enabled": ltr_enabled,
                "l1pm_substates_configured": l1pm_configured,
            },
        )
