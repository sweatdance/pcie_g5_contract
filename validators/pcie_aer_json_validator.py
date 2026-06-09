#!/usr/bin/env python3
"""Advisory validator for PCIe AER / Error Handling JSON evidence."""

from governance_tools.validator_interface import DomainValidator, ValidatorResult


class PcieAerJsonValidator(DomainValidator):
    SUPPORTED_SCHEMA_VERSION = "1.0"
    REQUIRED_KEYS = {
        "surprise_down_observed",
        "aer_surprise_down_logged",
        "aer_registers_cleared",
        "malformed_tlp_observed",
        "unexpected_completion_observed",
        "correctable_error_count",
        "completion_timeout_observed",
    }
    CORRECTABLE_ERROR_WARN_THRESHOLD = 10
    CORRECTABLE_ERROR_BURST_THRESHOLD = 5

    @property
    def rule_ids(self) -> list[str]:
        return [
            "pcie-aer",
            "PCIE5-AER-001", "PCIE5-AER-002", "PCIE5-AER-003",
            "PCIE5-AER-004", "PCIE5-AER-005", "PCIE5-AER-006",
            "PCIE5-AER-007", "PCIE5-AER-008", "PCIE5-AER-009",
            "PCIE5-AER-010", "PCIE5-AER-011", "PCIE5-AER-012", "PCIE5-AER-013",
        ]

    def validate(self, payload: dict) -> ValidatorResult:
        checks = payload.get("checks") or {}
        report = checks.get("pcie_aer_report") or {}

        if not report:
            return ValidatorResult(
                ok=True,
                rule_ids=self.rule_ids,
                warnings=["PCIe AER JSON report not provided; validator ran in advisory no-evidence mode"],
                evidence_summary="No pcie_aer_report object found in checks",
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

        surprise_down = report.get("surprise_down_observed")
        aer_logged = report.get("aer_surprise_down_logged")
        aer_cleared = report.get("aer_registers_cleared")
        malformed_tlp = report.get("malformed_tlp_observed")
        unexpected_cpl = report.get("unexpected_completion_observed")
        correctable_count = report.get("correctable_error_count")
        cto_observed = report.get("completion_timeout_observed")
        aer_uncorr_value = report.get("aer_uncorrectable_error_value")
        aer_mask_value = report.get("aer_uncorrectable_mask_value")
        first_error_ptr = report.get("first_error_pointer")
        ecrc_gen = report.get("ecrc_generation_enable")
        ecrc_chk = report.get("ecrc_check_enable")
        root_err_status = report.get("root_error_status_value")
        aer_source_id = report.get("aer_source_id")
        notes = report.get("notes")

        # Type validation for booleans
        for key, value in [
            ("surprise_down_observed", surprise_down),
            ("aer_surprise_down_logged", aer_logged),
            ("aer_registers_cleared", aer_cleared),
            ("malformed_tlp_observed", malformed_tlp),
            ("unexpected_completion_observed", unexpected_cpl),
            ("completion_timeout_observed", cto_observed),
        ]:
            if value is not None and not isinstance(value, bool):
                violations.append(f"{key} must be a boolean")

        # PCIE5-AER-001: Malformed TLP must have AER record
        if malformed_tlp is True and aer_logged is False:
            violations.append(
                "PCIE5-AER-001: malformed_tlp_observed=true but aer_surprise_down_logged=false. "
                "Malformed TLP (AER Uncorrectable bit18) must produce an AER Uncorrectable Error record."
            )

        # PCIE5-AER-002: Unexpected Completion must be explained
        if unexpected_cpl is True:
            expl = (report.get("notes") or [])
            expl_text = " ".join(expl) if isinstance(expl, list) else str(expl or "")
            if not expl_text.strip():
                violations.append(
                    "PCIE5-AER-002: unexpected_completion_observed=true but no explanation in notes. "
                    "Every Unexpected Completion (AER bit16) requires a traceable cause."
                )

        # PCIE5-AER-003: Surprise Down must be AER-logged
        if surprise_down is True and aer_logged is False:
            violations.append(
                "PCIE5-AER-003: surprise_down_observed=true but aer_surprise_down_logged=false. "
                "Surprise Down Error (AER Uncorrectable bit5) must be logged to be diagnosable."
            )

        # PCIE5-AER-008: Flow Control Protocol Error is always fatal
        if isinstance(aer_uncorr_value, str):
            try:
                aer_int = int(aer_uncorr_value.replace("0x", "").replace("0X", ""), 16)
                if aer_int & (1 << 13):  # bit13 = Flow Control Protocol Error
                    violations.append(
                        "PCIE5-AER-008: Flow Control Protocol Error (AER Uncorrectable bit13) is set. "
                        "This error is always fatal and requires immediate link health investigation."
                    )
                # Check First Error Pointer consistency
                if first_error_ptr is not None and isinstance(first_error_ptr, int):
                    # Find lowest set bit in aer_int
                    if aer_int > 0:
                        lowest_bit = (aer_int & -aer_int).bit_length() - 1
                        if first_error_ptr != lowest_bit:
                            violations.append(
                                f"PCIE5-AER-011: First Error Pointer={first_error_ptr} does not match "
                                f"lowest set bit in Uncorrectable Error Status ({lowest_bit}). "
                                "AER state is inconsistent; root-cause analysis is unreliable."
                            )
            except ValueError:
                warnings.append(f"aer_uncorrectable_error_value {aer_uncorr_value!r} is not valid hex")

        # PCIE5-AER-004: Correctable error count threshold
        if isinstance(correctable_count, int) and correctable_count > self.CORRECTABLE_ERROR_WARN_THRESHOLD:
            warnings.append(
                f"PCIE5-AER-004: correctable_error_count={correctable_count} > "
                f"{self.CORRECTABLE_ERROR_WARN_THRESHOLD}. "
                "Signal integrity review warranted (LCRC, REPLAY_NUM rollover, Receiver Error)."
            )

        # PCIE5-AER-005: AER not cleared after Surprise Down
        if surprise_down is True and aer_cleared is False:
            warnings.append(
                "PCIE5-AER-005: surprise_down_observed=true but aer_registers_cleared=false. "
                "Stale AER status bits (Reg=0x104, 0x110) will affect next enumeration session."
            )

        # PCIE5-AER-006: Completion Timeout without AER log
        if cto_observed is True and aer_logged is False:
            warnings.append(
                "PCIE5-AER-006: completion_timeout_observed=true but no AER log evidence. "
                "Check AER Uncorrectable bit14 (Completion Timeout) in device AER registers."
            )

        # PCIE5-AER-007: Asymmetric ECRC configuration
        if ecrc_gen is not None and ecrc_chk is not None:
            if isinstance(ecrc_gen, bool) and isinstance(ecrc_chk, bool):
                if ecrc_gen != ecrc_chk:
                    warnings.append(
                        f"PCIE5-AER-007: ECRC Generation Enable={ecrc_gen} != Check Enable={ecrc_chk}. "
                        "Asymmetric ECRC configuration means ECRC protection is non-functional."
                    )

        # PCIE5-AER-009: Non-default AER mask
        if isinstance(aer_mask_value, str) and aer_mask_value not in ("0x00000000", "0x0", "0"):
            warnings.append(
                f"PCIE5-AER-009: aer_uncorrectable_mask_value={aer_mask_value!r} is non-zero. "
                "Masked AER bits suppress error reporting. Document the reason for each masked bit."
            )

        # PCIE5-AER-012: Root Error Status without Source ID
        if isinstance(root_err_status, str) and root_err_status not in ("0x00000000", "0x0", "0"):
            try:
                rss_int = int(root_err_status.replace("0x", "").replace("0X", ""), 16)
                # bits[2:6] indicate received errors
                if rss_int & 0x7C:  # ERR bits
                    if not aer_source_id:
                        warnings.append(
                            "PCIE5-AER-012: Root Error Status shows received errors but aer_source_id "
                            "is not provided. Error source cannot be identified for forensic analysis."
                        )
            except ValueError:
                pass

        if notes is not None and not (isinstance(notes, list) and all(isinstance(n, str) for n in notes)):
            violations.append("notes must be a list of strings when provided")

        return ValidatorResult(
            ok=len(violations) == 0,
            rule_ids=self.rule_ids,
            violations=violations,
            warnings=warnings,
            evidence_summary="Validated PCIe AER / Error Handling JSON evidence",
            metadata={
                "mode": "enforcing",
                "report_present": True,
                "surprise_down_observed": surprise_down,
                "aer_surprise_down_logged": aer_logged,
                "aer_registers_cleared": aer_cleared,
                "malformed_tlp_observed": malformed_tlp,
                "unexpected_completion_observed": unexpected_cpl,
                "correctable_error_count": correctable_count,
                "completion_timeout_observed": cto_observed,
                "aer_uncorrectable_error_value": aer_uncorr_value,
            },
        )
