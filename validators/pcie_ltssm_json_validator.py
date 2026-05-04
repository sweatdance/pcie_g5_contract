#!/usr/bin/env python3
"""Advisory validator for PCIe Gen5 LTSSM JSON evidence."""

from governance_tools.validator_interface import DomainValidator, ValidatorResult


class PcieLtssmJsonValidator(DomainValidator):
    SUPPORTED_SCHEMA_VERSION = "1.0"
    REQUIRED_KEYS = {
        "schema_version",
        "target_speed_gtps",
        "negotiated_speed_gtps",
        "target_width",
        "negotiated_width",
        "ltssm_final_state",
        "ltssm_trace_summary",
        "equalization_complete",
        "equalization_phase_summary",
        "lane_failures",
        "downtrained",
        "recovery_triggered",
    }
    REQUIRED_LTSSM_TRACE_KEYS = {"visited_states", "illegal_transition_count", "reached_recovery"}
    REQUIRED_EQUALIZATION_KEYS = {"completed_phases", "failed_phases"}
    REQUIRED_GEN5_PHASES = ["phase0", "phase1", "phase2", "phase3"]
    NOMINAL_FINAL_STATE = "L0"

    @property
    def rule_ids(self) -> list[str]:
        return ["pcie-ltssm", "pcie-eq", "pcie-link-negotiation", "PCIE5-LTSSM-JSON-001"]

    @staticmethod
    def _is_list_of_strings(value: object) -> bool:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)

    @staticmethod
    def _is_number(value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @staticmethod
    def _is_positive_int(value: object) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and value > 0

    @staticmethod
    def _normalize_states(states: list[str]) -> set[str]:
        normalized = set()
        for state in states:
            normalized.add(state)
            normalized.add(state.split(".", 1)[0])
        return normalized

    def validate(self, payload: dict) -> ValidatorResult:
        checks = payload.get("checks") or {}
        report = checks.get("pcie_ltssm_report") or {}

        if not report:
            return ValidatorResult(
                ok=True,
                rule_ids=self.rule_ids,
                warnings=["PCIe LTSSM JSON report not provided; validator ran in advisory no-evidence mode"],
                evidence_summary="No pcie_ltssm_report object found in checks",
                metadata={"mode": "advisory", "report_present": False},
            )

        missing = sorted(self.REQUIRED_KEYS - set(report))
        warnings: list[str] = []
        violations: list[str] = []

        if missing:
            violations.append(f"Missing required report keys: {', '.join(missing)}")

        schema_version = report.get("schema_version")
        if not isinstance(schema_version, str) or not schema_version.strip():
            violations.append("schema_version must be a non-empty string")
        elif schema_version.strip() != self.SUPPORTED_SCHEMA_VERSION:
            violations.append(
                f"Unsupported schema_version: {schema_version!r}; expected {self.SUPPORTED_SCHEMA_VERSION!r}"
            )

        scenario = report.get("scenario")
        if scenario is not None and (not isinstance(scenario, str) or not scenario.strip()):
            violations.append("scenario must be a non-empty string when provided")

        topology = report.get("topology")
        if topology is not None and (not isinstance(topology, str) or not topology.strip()):
            violations.append("topology must be a non-empty string when provided")

        notes = report.get("notes")
        if notes is not None and not self._is_list_of_strings(notes):
            violations.append("notes must be a list of strings when provided")

        final_state = str(report.get("ltssm_final_state", "")).strip()
        if final_state != self.NOMINAL_FINAL_STATE:
            violations.append(f"Final LTSSM state is not L0: {final_state or '<missing>'}")

        ltssm_trace_summary = report.get("ltssm_trace_summary")
        illegal_transition_count = None
        visited_state_count = None
        reached_recovery_trace = None
        if not isinstance(ltssm_trace_summary, dict):
            violations.append("ltssm_trace_summary must be an object")
        else:
            missing_trace = sorted(self.REQUIRED_LTSSM_TRACE_KEYS - set(ltssm_trace_summary))
            if missing_trace:
                violations.append(f"ltssm_trace_summary missing keys: {', '.join(missing_trace)}")
            visited_states = ltssm_trace_summary.get("visited_states")
            if not self._is_list_of_strings(visited_states):
                violations.append("ltssm_trace_summary.visited_states must be a list of strings")
            else:
                visited_state_count = len(visited_states)
                normalized_states = self._normalize_states(visited_states)
                if self.NOMINAL_FINAL_STATE not in normalized_states:
                    warnings.append("Visited-state summary does not explicitly include L0")
                if final_state and final_state not in normalized_states:
                    violations.append(
                        f"ltssm_final_state {final_state!r} is inconsistent with visited_states summary"
                    )
            illegal_transition_count = ltssm_trace_summary.get("illegal_transition_count")
            if not isinstance(illegal_transition_count, int):
                violations.append("ltssm_trace_summary.illegal_transition_count must be an integer")
            elif illegal_transition_count != 0:
                violations.append(
                    f"Illegal LTSSM transitions reported: illegal_transition_count={illegal_transition_count}"
                )
            reached_recovery_trace = ltssm_trace_summary.get("reached_recovery")
            if not isinstance(reached_recovery_trace, bool):
                violations.append("ltssm_trace_summary.reached_recovery must be a boolean")
            elif isinstance(visited_states, list):
                saw_recovery_state = any(str(state).startswith("Recovery") for state in visited_states)
                if reached_recovery_trace != saw_recovery_state:
                    violations.append(
                        "ltssm_trace_summary.reached_recovery is inconsistent with visited_states"
                    )

        target_speed = report.get("target_speed_gtps")
        negotiated_speed = report.get("negotiated_speed_gtps")
        if not self._is_number(target_speed) or target_speed <= 0:
            violations.append("target_speed_gtps must be a positive number")
        if not self._is_number(negotiated_speed) or negotiated_speed <= 0:
            violations.append("negotiated_speed_gtps must be a positive number")
        if self._is_number(target_speed) and self._is_number(negotiated_speed) and target_speed != negotiated_speed:
            violations.append(
                f"Negotiated speed does not match target speed: target={target_speed}, negotiated={negotiated_speed}"
            )

        target_width = report.get("target_width")
        negotiated_width = report.get("negotiated_width")
        degraded_width_expected = report.get("degraded_width_expected")
        degraded_width_reason = str(report.get("degraded_width_reason") or "").strip()
        if not self._is_positive_int(target_width):
            violations.append("target_width must be a positive integer")
        if not self._is_positive_int(negotiated_width):
            violations.append("negotiated_width must be a positive integer")
        if degraded_width_expected is not None and not isinstance(degraded_width_expected, bool):
            violations.append("degraded_width_expected must be a boolean when provided")
        if (
            self._is_positive_int(target_width)
            and self._is_positive_int(negotiated_width)
            and target_width != negotiated_width
        ):
            if degraded_width_expected is True and degraded_width_reason:
                warnings.append(
                    f"Negotiated width differs from target width as expected: target={target_width}, negotiated={negotiated_width}, reason={degraded_width_reason}"
                )
            else:
                violations.append(
                    f"Negotiated width does not match target width without explicit degraded-width expectation: target={target_width}, negotiated={negotiated_width}"
                )
        elif degraded_width_expected is True:
            warnings.append(
                "degraded_width_expected is true, but negotiated width matches target width"
            )
        elif degraded_width_reason:
            warnings.append("degraded_width_reason was provided without degraded_width_expected=true")

        equalization_complete = report.get("equalization_complete")
        if equalization_complete is not True:
            violations.append("Equalization did not complete successfully")
        elif self._is_number(target_speed) and float(target_speed) >= 32.0:
            # Nominal Gen5 evidence should show all four equalization phases.
            pass

        equalization_phase_summary = report.get("equalization_phase_summary")
        failed_phase_count = None
        completed_phase_count = None
        if not isinstance(equalization_phase_summary, dict):
            violations.append("equalization_phase_summary must be an object")
        else:
            missing_eq = sorted(self.REQUIRED_EQUALIZATION_KEYS - set(equalization_phase_summary))
            if missing_eq:
                violations.append(f"equalization_phase_summary missing keys: {', '.join(missing_eq)}")
            completed_phases = equalization_phase_summary.get("completed_phases")
            failed_phases = equalization_phase_summary.get("failed_phases")
            if not self._is_list_of_strings(completed_phases):
                violations.append("equalization_phase_summary.completed_phases must be a list of strings")
                completed_phases = []
            else:
                completed_phase_count = len(completed_phases)
            if not self._is_list_of_strings(failed_phases):
                violations.append("equalization_phase_summary.failed_phases must be a list of strings")
                failed_phases = []
            elif failed_phases:
                failed_phase_count = len(failed_phases)
                warnings.append(f"Equalization failed phases reported: {failed_phases}")
            else:
                failed_phase_count = 0

            if completed_phases and len(completed_phases) != len(set(completed_phases)):
                violations.append("equalization_phase_summary.completed_phases must not contain duplicates")
            if failed_phases and len(failed_phases) != len(set(failed_phases)):
                violations.append("equalization_phase_summary.failed_phases must not contain duplicates")
            overlap = sorted(set(completed_phases) & set(failed_phases))
            if overlap:
                violations.append(
                    f"Equalization phases cannot be both completed and failed: {overlap}"
                )
            if equalization_complete is True:
                missing_nominal_phases = [
                    phase for phase in self.REQUIRED_GEN5_PHASES if phase not in set(completed_phases)
                ]
                if missing_nominal_phases:
                    violations.append(
                        f"Equalization marked complete but missing nominal phases: {missing_nominal_phases}"
                    )
                if failed_phases:
                    violations.append("Equalization marked complete but failed_phases is not empty")
            elif equalization_complete is False and not failed_phases:
                violations.append("Equalization failed but failed_phases is empty")

        lane_failures = report.get("lane_failures")
        if not isinstance(lane_failures, list):
            violations.append("lane_failures must be a list")
            lane_failure_count = None
        else:
            lane_failure_count = len(lane_failures)
            if not all(isinstance(item, str) and item.strip() for item in lane_failures):
                violations.append("lane_failures must contain only non-empty strings")
            if lane_failures:
                warnings.append(f"Lane failures reported: {lane_failures}")

        downtrained = report.get("downtrained")
        fallback_reason = str(report.get("fallback_reason") or "").strip()
        if not isinstance(downtrained, bool):
            violations.append("downtrained must be a boolean")
        elif downtrained:
            if fallback_reason:
                warnings.append(f"Downtraining reported: {fallback_reason}")
            else:
                violations.append("Downtraining requires fallback_reason")
            if (
                self._is_positive_int(target_width)
                and self._is_positive_int(negotiated_width)
                and self._is_number(target_speed)
                and self._is_number(negotiated_speed)
                and target_width == negotiated_width
                and target_speed == negotiated_speed
            ):
                violations.append(
                    "downtrained is true, but both negotiated width and speed match target values"
                )
        elif fallback_reason:
            warnings.append("fallback_reason was provided while downtrained is false")

        recovery_triggered = report.get("recovery_triggered")
        recovery_reason = str(report.get("recovery_reason") or "").strip()
        retry_count = report.get("retry_count", 0)
        if not isinstance(recovery_triggered, bool):
            violations.append("recovery_triggered must be a boolean")
        elif recovery_triggered and not recovery_reason:
            warnings.append("Recovery was triggered but recovery_reason is missing")
        elif not recovery_triggered and recovery_reason:
            warnings.append("recovery_reason was provided while recovery_triggered is false")
        if not isinstance(retry_count, int):
            violations.append("retry_count must be an integer")
        elif retry_count < 0:
            violations.append("retry_count must be >= 0")
        elif retry_count > 0 and not recovery_triggered:
            violations.append("retry_count is non-zero while recovery_triggered is false")

        if isinstance(recovery_triggered, bool) and isinstance(reached_recovery_trace, bool):
            if recovery_triggered and not reached_recovery_trace:
                violations.append(
                    "recovery_triggered is true, but ltssm_trace_summary.reached_recovery is false"
                )
            if reached_recovery_trace and not recovery_triggered:
                warnings.append(
                    "Recovery states were observed, but recovery_triggered is false"
                )

        if lane_failure_count and equalization_complete is True:
            warnings.append("Lane failures were reported even though equalization_complete is true")

        return ValidatorResult(
            ok=len(violations) == 0,
            rule_ids=self.rule_ids,
            violations=violations,
            warnings=warnings,
            evidence_summary="Validated PCIe Gen5 LTSSM JSON evidence",
            metadata={
                "mode": "enforcing",
                "report_present": True,
                "final_state": final_state,
                "illegal_transition_count": illegal_transition_count,
                "visited_state_count": visited_state_count,
                "reached_recovery_trace": reached_recovery_trace,
                "target_speed_gtps": target_speed,
                "negotiated_speed_gtps": negotiated_speed,
                "target_width": target_width,
                "negotiated_width": negotiated_width,
                "degraded_width_expected": degraded_width_expected,
                "recovery_triggered": recovery_triggered,
                "retry_count": retry_count,
                "failed_phase_count": failed_phase_count,
                "completed_phase_count": completed_phase_count,
                "lane_failure_count": lane_failure_count,
            },
        )
