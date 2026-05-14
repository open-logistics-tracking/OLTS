"""Tests for ``oltrack.state_machine``."""
from __future__ import annotations

import pytest

from oltrack import state_machine as sm


class TestBasicTransitions:
    def test_normal_transition(self):
        ok, _ = sm.is_valid_transition("picked_up", "arrived_at_hub")
        assert ok

    def test_invalid_transition(self):
        ok, reason = sm.is_valid_transition("delivered", "picked_up")
        assert not ok
        assert "terminal" in reason

    def test_same_code_always_valid(self):
        ok, reason = sm.is_valid_transition("in_transit", "in_transit")
        assert ok
        assert "same code" in reason

    def test_unknown_from_code(self):
        ok, reason = sm.is_valid_transition("not_real", "delivered")
        assert not ok
        assert "unknown from_code" in reason

    def test_unknown_to_code(self):
        ok, reason = sm.is_valid_transition("picked_up", "not_real")
        assert not ok
        assert "unknown to_code" in reason


class TestUniversalTransitions:
    @pytest.mark.parametrize("from_code", ["picked_up", "in_transit", "out_for_delivery", "delivered"])
    @pytest.mark.parametrize("to_code", ["exception", "damaged", "lost"])
    def test_any_to_universal_is_valid(self, from_code, to_code):
        ok, _ = sm.is_valid_transition(from_code, to_code)
        assert ok


class TestExceptionTransitions:
    def test_delivered_to_return_without_context_rejected(self):
        ok, reason = sm.is_valid_transition("delivered", "return_initiated")
        assert not ok
        assert "exception" in reason.lower() or "exceptional" in reason.lower()

    def test_delivered_to_return_with_rma_context_accepted(self):
        ok, reason = sm.is_valid_transition("delivered", "return_initiated", context={"rma": True})
        assert ok


class TestClassification:
    @pytest.mark.parametrize("code", ["delivered", "returned_to_sender", "lost", "order_cancelled", "signed_by_third_party"])
    def test_terminal(self, code):
        assert sm.is_terminal(code)
        assert sm.classify(code) == "terminal"

    @pytest.mark.parametrize("code", ["damaged", "exception", "refused"])
    def test_exceptional(self, code):
        assert not sm.is_terminal(code)
        assert sm.classify(code) == "exceptional"

    @pytest.mark.parametrize("code", ["picked_up", "in_transit", "out_for_delivery"])
    def test_active(self, code):
        assert not sm.is_terminal(code)
        assert sm.classify(code) == "active"


class TestNextPreviousStates:
    def test_next_states_includes_universal(self):
        nxt = sm.next_states("picked_up")
        assert "arrived_at_hub" in nxt
        assert "exception" in nxt
        assert "damaged" in nxt
        assert "lost" in nxt

    def test_next_states_excludes_self(self):
        assert "picked_up" not in sm.next_states("picked_up")

    def test_next_states_terminal_only_universal(self):
        nxt = sm.next_states("delivered")
        # delivered → return_initiated requires context, so it's not in next_states
        assert nxt == {"exception", "damaged", "lost"}

    def test_previous_states(self):
        prev = sm.previous_states("delivered")
        assert "out_for_delivery" in prev
        assert "delivery_to_locker" in prev
        assert "awaiting_pickup" in prev


class TestSequenceValidation:
    def test_happy_path_no_violations(self):
        seq = [
            "order_created", "picked_up", "arrived_at_hub",
            "departed_from_hub", "arrived_at_destination",
            "out_for_delivery", "delivered",
        ]
        assert sm.validate_event_sequence(seq) == []

    def test_cross_border_path_no_violations(self):
        seq = [
            "picked_up", "arrived_at_hub", "customs_declared",
            "customs_held", "customs_duty_paid", "customs_released",
            "clearance_completed", "arrived_at_destination",
            "out_for_delivery", "delivered",
        ]
        assert sm.validate_event_sequence(seq) == []

    def test_repeated_in_transit_ok(self):
        seq = ["picked_up", "in_transit", "in_transit", "in_transit", "arrived_at_destination"]
        assert sm.validate_event_sequence(seq) == []

    def test_invalid_step_reported(self):
        seq = ["delivered", "picked_up"]
        invalid = sm.validate_event_sequence(seq)
        assert len(invalid) == 1
        idx, frm, to, reason = invalid[0]
        assert idx == 1
        assert frm == "delivered"
        assert to == "picked_up"


class TestCsvIntegrity:
    def test_all_codes_in_csv_are_valid_ulsc(self):
        from oltrack.ulsc import ALL_CODES
        for t in sm.load_transitions():
            assert t.to_code in ALL_CODES, f"bad to_code: {t.to_code}"
            if t.from_code != "*":
                assert t.from_code in ALL_CODES, f"bad from_code: {t.from_code}"

    def test_universal_targets_are_exception_class(self):
        # These should be the only universal-from rows
        assert sm._UNIVERSAL_TARGETS == {"exception", "damaged", "lost"}
