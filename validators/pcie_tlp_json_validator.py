#!/usr/bin/env python3
"""Advisory validator for PCIe Transaction Layer JSON evidence."""

from governance_tools.validator_interface import DomainValidator, ValidatorResult


class PcieTlpJsonValidator(DomainValidator):
    SUPPORTED_SCHEMA_VERSION = "1.0"
    REQUIRED_KEYS = {
        "non_sc_completion_observed",
        "poisoned_tlp_observed",
        "cfgrd_without_cpld_observed",
        "memory_access_to_unassigned_bar",
        "total_tlp_count",
    }

    @property
    def rule_ids(self) -> list[str]:
        return [
            "pcie-tlp",
            "PCIE5-TLP-001", "PCIE5-TLP-002", "PCIE5-TLP-003",
            "PCIE5-TLP-004", "PCIE5-TLP-005", "PCIE5-TLP-006",
            "PCIE5-TLP-007", "PCIE5-TLP-008", "PCIE5-TLP-009",
            "PCIE5-TLP-010", "PCIE5-TLP-011", "PCIE5-TLP-012", "PCIE5-TLP-013",
        ]

    def validate(self, payload: dict) -> ValidatorResult:
        checks = payload.get("checks") or {}
        report = checks.get("pcie_tlp_report") or {}

        if not report:
            return ValidatorResult(
                ok=True,
                rule_ids=self.rule_ids,
                warnings=["PCIe TLP JSON report not provided; validator ran in advisory no-evidence mode"],
                evidence_summary="No pcie_tlp_report object found in checks",
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

        non_sc = report.get("non_sc_completion_observed")
        poisoned = report.get("poisoned_tlp_observed")
        cfgrd_timeout = report.get("cfgrd_without_cpld_observed")
        bar_violation = report.get("memory_access_to_unassigned_bar")
        total_tlp = report.get("total_tlp_count")
        non_sc_types = report.get("non_sc_completion_types", [])
        non_sc_expl = report.get("non_sc_completion_explanation")
        poisoned_aer = report.get("poisoned_tlp_aer_logged")
        tag_reuse = report.get("tag_reuse_observed")
        invalid_be = report.get("invalid_last_dw_be_observed")
        tc_out_of_vc = report.get("tc_out_of_vc_range_observed")
        ext_tag_enabled = report.get("extended_tag_enabled")
        max_tag = report.get("max_tag_value_seen")
        length_mismatch = report.get("tlp_length_mismatch_observed")
        notes = report.get("notes")

        for key, value in [
            ("non_sc_completion_observed", non_sc),
            ("poisoned_tlp_observed", poisoned),
            ("cfgrd_without_cpld_observed", cfgrd_timeout),
            ("memory_access_to_unassigned_bar", bar_violation),
        ]:
            if value is not None and not isinstance(value, bool):
                violations.append(f"{key} must be a boolean")

        # PCIE5-TLP-001: Non-SC Completion without explanation
        if non_sc is True:
            expl_text = non_sc_expl if isinstance(non_sc_expl, str) else ""
            if not expl_text.strip():
                violations.append(
                    "PCIE5-TLP-001: non_sc_completion_observed=true but non_sc_completion_explanation "
                    "is absent or empty. Every non-SC Completion (UR/CA/CRS) requires a traceable cause."
                )

        # PCIE5-TLP-002: Poisoned TLP without AER
        if poisoned is True and poisoned_aer is False:
            violations.append(
                "PCIE5-TLP-002: poisoned_tlp_observed=true but poisoned_tlp_aer_logged=false. "
                "Poisoned TLP (EP=1) must produce AER Uncorrectable Error (bit12 of Reg=0x104)."
            )
        elif poisoned is True and poisoned_aer is None:
            warnings.append(
                "PCIE5-TLP-002: poisoned_tlp_observed=true but poisoned_tlp_aer_logged not provided. "
                "Verify AER Uncorrectable Error bit12 was set and logged."
            )

        # PCIE5-TLP-003: Memory access to unassigned BAR
        if bar_violation is True:
            violations.append(
                "PCIE5-TLP-003: memory_access_to_unassigned_bar=true. "
                "Memory or I/O request to an address not assigned via BAR sizing is a hard stop."
            )

        # PCIE5-TLP-008: Tag reuse
        if tag_reuse is True:
            violations.append(
                "PCIE5-TLP-008: tag_reuse_observed=true. "
                "Tag reuse before Completion is returned causes routing ambiguity at the completer. "
                "This is a hard stop requiring requester driver investigation."
            )

        # PCIE5-TLP-013: TLP Length mismatch (Malformed TLP)
        if length_mismatch is True:
            violations.append(
                "PCIE5-TLP-013: tlp_length_mismatch_observed=true. "
                "TLP Length field does not match actual payload DWORDs (CATC Malformed TLP decode). "
                "This is always a hard stop; cross-reference AER Uncorrectable bit18 (Malformed TLP)."
            )

        # PCIE5-TLP-004: CfgRd without CplD
        if cfgrd_timeout is True:
            warnings.append(
                "PCIE5-TLP-004: cfgrd_without_cpld_observed=true. "
                "CfgRd without matching CplD suggests Completion Timeout. "
                "Check AER Uncorrectable bit14 (CTO) and Windows BSOD code (0x9F / 0xA0)."
            )

        # PCIE5-TLP-005: CRS repeated
        if isinstance(non_sc_types, list) and non_sc_types.count("CRS") > 1:
            warnings.append(
                f"PCIE5-TLP-005: CRS appears {non_sc_types.count('CRS')} times in non_sc_completion_types. "
                "Device not completing initialization on schedule; verify readiness timing."
            )

        # PCIE5-TLP-007: Invalid Last DW BE
        if invalid_be is True:
            warnings.append(
                "PCIE5-TLP-007: invalid_last_dw_be_observed=true. "
                "Last DW BE=0x0 for a multi-DWORD request is an invalid Byte Enable combination "
                "that causes Malformed TLP at the completer."
            )

        # PCIE5-TLP-010: TC out of VC range
        if tc_out_of_vc is True:
            warnings.append(
                "PCIE5-TLP-010: tc_out_of_vc_range_observed=true. "
                "Traffic Class field maps to an unestablished Virtual Channel. "
                "Switches silently drop TLPs with unmapped TC; verify VC Extended Capability."
            )

        # PCIE5-TLP-012: Extended Tag used without Enable
        if isinstance(max_tag, int) and max_tag > 31:
            if ext_tag_enabled is False:
                warnings.append(
                    f"PCIE5-TLP-012: max_tag_value_seen={max_tag} > 31 (8-bit tag range) "
                    "but extended_tag_enabled=false. Extended Tag used without Device Control bit8=1 "
                    "may cause completions to be silently dropped by non-compliant targets."
                )
            elif ext_tag_enabled is None:
                warnings.append(
                    f"PCIE5-TLP-012: max_tag_value_seen={max_tag} > 31 but extended_tag_enabled "
                    "is not provided. Confirm Extended Tag Field Enable (Device Control bit8) is set."
                )

        if notes is not None and not (isinstance(notes, list) and all(isinstance(n, str) for n in notes)):
            violations.append("notes must be a list of strings when provided")

        return ValidatorResult(
            ok=len(violations) == 0,
            rule_ids=self.rule_ids,
            violations=violations,
            warnings=warnings,
            evidence_summary="Validated PCIe Transaction Layer JSON evidence",
            metadata={
                "mode": "enforcing",
                "report_present": True,
                "non_sc_completion_observed": non_sc,
                "non_sc_completion_types": non_sc_types,
                "poisoned_tlp_observed": poisoned,
                "cfgrd_without_cpld_observed": cfgrd_timeout,
                "memory_access_to_unassigned_bar": bar_violation,
                "total_tlp_count": total_tlp,
                "tag_reuse_observed": tag_reuse,
                "tc_out_of_vc_range_observed": tc_out_of_vc,
            },
        )
