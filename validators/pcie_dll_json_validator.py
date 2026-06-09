#!/usr/bin/env python3
"""Advisory validator for PCIe Data Link Layer JSON evidence."""

from governance_tools.validator_interface import DomainValidator, ValidatorResult


class PcieDllJsonValidator(DomainValidator):
    SUPPORTED_SCHEMA_VERSION = "1.0"
    REQUIRED_KEYS = {
        "initfc_complete",
        "dl_up_confirmed",
        "nak_observed",
        "nak_followed_by_replay",
        "updatefc_observed",
        "capture_duration_ms",
    }
    UPDATEFC_ABSENT_THRESHOLD_MS = 200.0
    NAK_WARN_THRESHOLD = 5

    @property
    def rule_ids(self) -> list[str]:
        return [
            "pcie-dll",
            "PCIE5-DLL-001", "PCIE5-DLL-002", "PCIE5-DLL-003",
            "PCIE5-DLL-004", "PCIE5-DLL-005", "PCIE5-DLL-006",
            "PCIE5-DLL-007", "PCIE5-DLL-008", "PCIE5-DLL-009",
            "PCIE5-DLL-010", "PCIE5-DLL-011",
        ]

    @staticmethod
    def _is_number(value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def validate(self, payload: dict) -> ValidatorResult:
        checks = payload.get("checks") or {}
        report = checks.get("pcie_dll_report") or {}

        if not report:
            return ValidatorResult(
                ok=True,
                rule_ids=self.rule_ids,
                warnings=["PCIe DLL JSON report not provided; validator ran in advisory no-evidence mode"],
                evidence_summary="No pcie_dll_report object found in checks",
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

        initfc_complete = report.get("initfc_complete")
        dl_up_confirmed = report.get("dl_up_confirmed")
        nak_observed = report.get("nak_observed")
        nak_followed_by_replay = report.get("nak_followed_by_replay")
        updatefc_observed = report.get("updatefc_observed")
        capture_ms = report.get("capture_duration_ms")
        nak_count = report.get("nak_count", 0)
        repeated_initfc2 = report.get("repeated_initfc2_count", 0)
        replay_rollover = report.get("replay_num_rollover_observed")
        replay_rollover_recovery = report.get("replay_num_rollover_recovery_confirmed")
        seq_wrap = report.get("sequence_number_wrap_observed")
        ack_seq_ok = report.get("ack_seq_progression_consistent")
        pm_dllp_before_dl_up = report.get("pm_dllp_before_dl_up")
        dllp_crc_errors = report.get("dllp_crc_error_count", 0)
        fc_all_initialized = report.get("initfc_credit_type_all_initialized")
        notes = report.get("notes")

        for key, value in [
            ("initfc_complete", initfc_complete),
            ("dl_up_confirmed", dl_up_confirmed),
            ("nak_observed", nak_observed),
            ("nak_followed_by_replay", nak_followed_by_replay),
            ("updatefc_observed", updatefc_observed),
        ]:
            if value is not None and not isinstance(value, bool):
                violations.append(f"{key} must be a boolean")

        # PCIE5-DLL-001: TLPs before DL_Up
        if dl_up_confirmed is False:
            violations.append(
                "PCIE5-DLL-001: dl_up_confirmed=false but the report implies TLPs may be present. "
                "TLPs must not appear before InitFC1+InitFC2 exchange completes (DL_Active state)."
            )

        # PCIE5-DLL-002: NAK without replay
        if nak_observed is True and nak_followed_by_replay is False:
            violations.append(
                "PCIE5-DLL-002: nak_observed=true but nak_followed_by_replay=false. "
                "NAK DLLP must be followed by replay of the oldest unacknowledged TLP. "
                "Missing replay is a Data Link layer protocol violation."
            )

        # PCIE5-DLL-007: REPLAY_NUM rollover without Recovery
        if replay_rollover is True and replay_rollover_recovery is False:
            violations.append(
                "PCIE5-DLL-007: replay_num_rollover_observed=true but "
                "replay_num_rollover_recovery_confirmed=false. "
                "REPLAY_NUM overflow (4 consecutive replays) must trigger LTSSM Recovery state."
            )

        # PCIE5-DLL-003: UpdateFC absent in long capture
        if updatefc_observed is False and self._is_number(capture_ms) and capture_ms > self.UPDATEFC_ABSENT_THRESHOLD_MS:
            warnings.append(
                f"PCIE5-DLL-003: updatefc_observed=false in a capture of {capture_ms:.0f}ms "
                f"(>{self.UPDATEFC_ABSENT_THRESHOLD_MS}ms). Possible FC credit starvation or "
                "capture filtering; UpdateFC DLLPs may have been filtered out."
            )

        # PCIE5-DLL-004: Repeated InitFC2 (CATC artifact)
        if isinstance(repeated_initfc2, int) and repeated_initfc2 > 3:
            warnings.append(
                f"PCIE5-DLL-004: repeated_initfc2_count={repeated_initfc2} > 3. "
                "Repeated identical InitFC2 values are typically CATC frequency-lock artifacts "
                "at link build-up. Verify these are not real FC re-initialization events."
            )

        # PCIE5-DLL-005: NAK count threshold
        if isinstance(nak_count, int) and nak_count > self.NAK_WARN_THRESHOLD:
            warnings.append(
                f"PCIE5-DLL-005: nak_count={nak_count} > {self.NAK_WARN_THRESHOLD}. "
                "High NAK count indicates signal integrity degradation or excessive bit errors."
            )

        # PCIE5-DLL-006: ACK sequence progression
        if ack_seq_ok is False:
            warnings.append(
                "PCIE5-DLL-006: ack_seq_progression_consistent=false. "
                "ACK DLLP sequence number is not monotonically increasing within the replay window. "
                "May indicate DL replay storm or out-of-window ACK condition."
            )

        # PCIE5-DLL-008: DLLP CRC errors without recovery
        if isinstance(dllp_crc_errors, int) and dllp_crc_errors > 0:
            warnings.append(
                f"PCIE5-DLL-008: dllp_crc_error_count={dllp_crc_errors} > 0. "
                "DLLP CRC16 errors indicate physical layer noise. "
                "The receiver discards bad DLLPs silently; multiple errors may cause PM DLLP loss."
            )

        # PCIE5-DLL-009: FC credit types not all initialized
        if fc_all_initialized is False:
            warnings.append(
                "PCIE5-DLL-009: initfc_credit_type_all_initialized=false. "
                "Not all FC credit types (Posted, Non-Posted, Completion) were initialized. "
                "TLPs for uninitialized credit types must not flow until their InitFC completes."
            )

        # PCIE5-DLL-010: Sequence number wrap
        if seq_wrap is True:
            warnings.append(
                "PCIE5-DLL-010: sequence_number_wrap_observed=true. "
                "12-bit TLP sequence number wrapped (0xFFF→0x000). Verify replay buffer was "
                "drained (all prior TLPs ACK'd) before wrap to prevent sequence tracking ambiguity."
            )

        # PCIE5-DLL-011: PM DLLP before DL_Up
        if pm_dllp_before_dl_up is True:
            warnings.append(
                "PCIE5-DLL-011: pm_dllp_before_dl_up=true. "
                "PM DLLP (PM_Active_State_Request_L1 or similar) observed before InitFC completed. "
                "PM DLLPs must only appear after DL_Active; this is a PM sequencing violation."
            )

        if notes is not None and not (isinstance(notes, list) and all(isinstance(n, str) for n in notes)):
            violations.append("notes must be a list of strings when provided")

        return ValidatorResult(
            ok=len(violations) == 0,
            rule_ids=self.rule_ids,
            violations=violations,
            warnings=warnings,
            evidence_summary="Validated PCIe Data Link Layer JSON evidence",
            metadata={
                "mode": "enforcing",
                "report_present": True,
                "initfc_complete": initfc_complete,
                "dl_up_confirmed": dl_up_confirmed,
                "nak_observed": nak_observed,
                "nak_followed_by_replay": nak_followed_by_replay,
                "nak_count": nak_count,
                "updatefc_observed": updatefc_observed,
                "replay_num_rollover_observed": replay_rollover,
                "dllp_crc_error_count": dllp_crc_errors,
            },
        )
