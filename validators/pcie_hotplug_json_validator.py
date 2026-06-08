#!/usr/bin/env python3
"""Advisory validator for PCIe Hot-Plug Lifecycle JSON evidence."""

from governance_tools.validator_interface import DomainValidator, ValidatorResult


class PcieHotplugJsonValidator(DomainValidator):
    SUPPORTED_SCHEMA_VERSION = "1.0"
    REQUIRED_KEYS = {
        "pm_l1_before_enum_complete",
        "pm_request_ack_in_enum_window",
        "aer_cleared_before_new_enum",
        "upstream_ts1_rate_at_first_linkup",
    }
    # Minimum safe gap between Surprise Down and first CfgRd in milliseconds
    MIN_SAFE_GAP_MS = 500.0

    @property
    def rule_ids(self) -> list[str]:
        return [
            "pcie-hotplug",
            "PCIE5-HP-001", "PCIE5-HP-002", "PCIE5-HP-003",
            "PCIE5-HP-004", "PCIE5-HP-005", "PCIE5-HP-006", "PCIE5-HP-007",
            "PCIE5-HP-008", "PCIE5-HP-009", "PCIE5-HP-010", "PCIE5-HP-011",
            "PCIE5-HP-012", "PCIE5-HP-013", "PCIE5-HP-014", "PCIE5-HP-015", "PCIE5-HP-016",
        ]

    @staticmethod
    def _is_number(value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def validate(self, payload: dict) -> ValidatorResult:
        checks = payload.get("checks") or {}
        report = checks.get("pcie_hotplug_report") or {}

        if not report:
            return ValidatorResult(
                ok=True,
                rule_ids=self.rule_ids,
                warnings=["PCIe Hot-Plug JSON report not provided; validator ran in advisory no-evidence mode"],
                evidence_summary="No pcie_hotplug_report object found in checks",
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

        pm_l1_before_enum = report.get("pm_l1_before_enum_complete")
        pm_ack_in_window = report.get("pm_request_ack_in_enum_window")
        aer_cleared = report.get("aer_cleared_before_new_enum")
        ts1_rate = report.get("upstream_ts1_rate_at_first_linkup")
        time_gap_ms = report.get("time_surprise_down_to_first_cfgrd_ms")
        slot_aspm_disabled = report.get("slot_aspm_disabled_at_new_link_up")
        mux_scenario = report.get("mux_scenario")
        new_device_max_speed = report.get("new_device_max_speed_gtps")
        link_cycling_count = report.get("link_cycling_count", 0)
        notes = report.get("notes")

        for key, value in [
            ("pm_l1_before_enum_complete", pm_l1_before_enum),
            ("pm_request_ack_in_enum_window", pm_ack_in_window),
            ("aer_cleared_before_new_enum", aer_cleared),
        ]:
            if value is not None and not isinstance(value, bool):
                violations.append(f"{key} must be a boolean")

        if ts1_rate is not None and not isinstance(ts1_rate, str):
            violations.append("upstream_ts1_rate_at_first_linkup must be a string")

        # PCIE5-HP-001: PM L1 before enumeration complete
        if pm_l1_before_enum is True:
            violations.append(
                "PCIE5-HP-001: PM_Active_State_Request_L1 observed before new device enumeration "
                "was complete (before first CfgRd 0x000 VID/DID). PM L1 must not interrupt enumeration."
            )

        # PCIE5-HP-002: Host ACK during enumeration window
        if pm_ack_in_window is True:
            violations.append(
                "PCIE5-HP-002: PM_Request_Ack sent by host downstream port before new device "
                "VID/DID was read. Host ACKed L1 during the critical enumeration window."
            )

        # PCIE5-HP-003: Stale AER not cleared before new enumeration
        if aer_cleared is False:
            violations.append(
                "PCIE5-HP-003: AER status registers were not cleared before new device enumeration. "
                "Stale AER error bits from the previous device removal must be cleared first."
            )

        # PCIE5-HP-004: Warn if gap too short
        if self._is_number(time_gap_ms) and time_gap_ms < self.MIN_SAFE_GAP_MS:
            warnings.append(
                f"PCIE5-HP-004: time_surprise_down_to_first_cfgrd_ms={time_gap_ms:.1f}ms is below "
                f"the recommended minimum of {self.MIN_SAFE_GAP_MS}ms. OS hot-plug remove sequence "
                "may not have completed before new device enumeration started."
            )

        # PCIE5-HP-005: Warn if ASPM state unknown
        if slot_aspm_disabled is None:
            warnings.append(
                "PCIE5-HP-005: slot_aspm_disabled_at_new_link_up is unknown (null). "
                "Host downstream port ASPM state at new device Link Up cannot be confirmed."
            )

        # PCIE5-HP-006: MUX scenario — TS1 rate vs device max speed
        if mux_scenario is True and isinstance(ts1_rate, str) and self._is_number(new_device_max_speed):
            # Check if any rate in the TS1 string exceeds device max
            detected_speeds = []
            for token in ts1_rate.replace(",", " ").split():
                try:
                    speed = float(token)
                    detected_speeds.append(speed)
                except ValueError:
                    pass
            if detected_speeds:
                max_detected = max(detected_speeds)
                if max_detected > float(new_device_max_speed):
                    warnings.append(
                        f"PCIE5-HP-006: Upstream TS1 advertises {max_detected} GT/s but new device "
                        f"max is {new_device_max_speed} GT/s. Possible MUX switching artifact or "
                        "residual signal from previous device."
                    )

        # PCIE5-HP-007: Excessive link cycling
        if isinstance(link_cycling_count, int) and link_cycling_count > 5:
            warnings.append(
                f"PCIE5-HP-007: link_cycling_count={link_cycling_count} > 5. "
                "Excessive short-duration link cycles may indicate MUX timing or SI issue."
            )

        # MUX scenario consistency checks
        if mux_scenario is True:
            if new_device_max_speed is None:
                warnings.append("new_device_max_speed_gtps should be provided when mux_scenario = true")
            if report.get("mux_switch_time_ms") is None:
                warnings.append("mux_switch_time_ms should be provided when mux_scenario = true")

        # ---- HPC register sequence rules ----
        cmd_completed_ok = report.get("command_completed_before_next_cmd")
        pds_before_powerup = report.get("presence_detect_state_before_powerup")
        dllsc_triggered = report.get("dllsc_triggered_enumeration")
        pwr_blink = report.get("power_indicator_blink_observed")
        t_power_up_ms = report.get("t_power_up_ms")
        attn_cleared = report.get("attention_indicator_cleared_after_enum")

        # PCIE5-HP-010: Power removed while device active (hard stop)
        slot_ctrl_seq = report.get("slot_control_sequence")
        if isinstance(slot_ctrl_seq, list):
            seq_str = " ".join(str(s) for s in slot_ctrl_seq)
            if "power_off" in seq_str.lower() and "perst_assert" not in seq_str.lower():
                violations.append(
                    "PCIE5-HP-010: Slot Control Power Controller set to Off observed in sequence "
                    "without prior PERST# assertion evidence. Removing power from active device "
                    "without PERST# is a hard stop."
                )

        # PCIE5-HP-011: Back-to-back SlotCtl without CommandCompleted
        if cmd_completed_ok is False:
            violations.append(
                "PCIE5-HP-011: command_completed_before_next_cmd=false. A Slot Control write was "
                "issued before the previous CommandCompleted=1 in Slot Status. This is a spec "
                "violation that can cause the HPC state machine to malfunction."
            )

        # PCIE5-HP-008: Power Indicator not Blink during power-up
        if pwr_blink is False:
            warnings.append(
                "PCIE5-HP-008: power_indicator_blink_observed=false; Power Indicator should be "
                "set to Blink (SlotCtl bits[9:8]=10b) during the power-up sequence per PCIe spec."
            )

        # PCIE5-HP-009: T_Power_Up too short
        if self._is_number(t_power_up_ms) and t_power_up_ms < 100:
            warnings.append(
                f"PCIE5-HP-009: t_power_up_ms={t_power_up_ms:.1f}ms is below 100ms minimum. "
                "PERST# must not be de-asserted until slot power has been stable for ≥100ms."
            )

        # PCIE5-HP-012: DLLSC not cleared after new link up
        if dllsc_triggered is False and report.get("new_device_first_cfgrd_timestamp") is not None:
            warnings.append(
                "PCIE5-HP-012: dllsc_triggered_enumeration=false but new device CfgRd was seen; "
                "DLLSC (Slot Status bit8) should be the trigger for starting enumeration."
            )

        # PCIE5-HP-014: Attention Indicator not cleared after enumeration
        if attn_cleared is False:
            warnings.append(
                "PCIE5-HP-014: attention_indicator_cleared_after_enum=false; "
                "Attention Indicator should be set to Off after successful hot-add enumeration."
            )

        if notes is not None and not (isinstance(notes, list) and all(isinstance(n, str) for n in notes)):
            violations.append("notes must be a list of strings when provided")

        return ValidatorResult(
            ok=len(violations) == 0,
            rule_ids=self.rule_ids,
            violations=violations,
            warnings=warnings,
            evidence_summary="Validated PCIe Hot-Plug Lifecycle JSON evidence",
            metadata={
                "mode": "enforcing",
                "report_present": True,
                "pm_l1_before_enum_complete": pm_l1_before_enum,
                "pm_request_ack_in_enum_window": pm_ack_in_window,
                "aer_cleared_before_new_enum": aer_cleared,
                "time_surprise_down_to_first_cfgrd_ms": time_gap_ms,
                "slot_aspm_disabled_at_new_link_up": slot_aspm_disabled,
                "mux_scenario": mux_scenario,
                "upstream_ts1_rate_at_first_linkup": ts1_rate,
                "link_cycling_count": link_cycling_count,
            },
        )
