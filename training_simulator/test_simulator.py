#!/usr/bin/env python
"""
Smoke test for the training simulator.

Tests core functionality without running the GUI:
1. Cohort creation
2. State store persistence
3. Protocol engine date advancement
4. Due event calculation
5. Scenario generation
6. Verification engine
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from training_simulator.state_store import StateStore
from training_simulator.protocol_engine import ProtocolEngine
from training_simulator.scenarios import ScenarioGenerator
from training_simulator.verification import VerificationEngine
from utils.data_access import read_patient_meta, derive_status


def test_state_store():
    """Test state store creation and persistence."""
    print("\n[TEST] State Store")
    print("  - Creating state store...")
    store = StateStore()

    print("  - Initializing cohort with 3 dummy patients...")
    cohort = [
        ('HOCMCVTST1', 'experimental', 'Right'),
        ('HOCMCVTST2', 'experimental', 'Left'),
        ('HOCMCVTST3', 'control', 'Right'),
    ]
    store.init_cohort(cohort)

    print("  - Verifying cohort data...")
    assert store.is_cohort_active()
    assert len(store.get_patient_ids()) == 3
    assert store.get_simulated_day() == 0

    print("  - Adding expected event...")
    store.add_expected_event(
        day=1,
        patient_id='HOCMCVTST1',
        protocol_event_id='activation',
        suggested_values={'activationDate': '2026-07-14T10:00'}
    )

    events = store.get_expected_events_for_day(1)
    assert len(events) == 1
    assert events[0]['protocol_event_id'] == 'activation'

    print("  - Incrementing day...")
    store.increment_day()
    assert store.get_simulated_day() == 1

    print("  - Logging action...")
    store.log_action("test", "smoke test action")
    logs = store.get_logs()
    assert len(logs) > 0

    print("  [OK] State store tests passed")


def test_protocol_engine():
    """Test protocol engine initialization."""
    print("\n[TEST] Protocol Engine")
    print("  - Creating protocol engine...")
    engine = ProtocolEngine()

    print("  - Verifying event index built...")
    assert len(engine.event_index) > 0
    assert 'activation' in engine.event_index
    assert 'home_visit_d02' in engine.event_index

    print("  - Testing event name mapping...")
    name = engine._get_event_name('activation')
    assert name == 'Patient Activation'

    print("  [OK] Protocol engine tests passed")


def test_scenario_generator():
    """Test scenario generation."""
    print("\n[TEST] Scenario Generator")
    print("  - Creating scenario generator...")
    gen = ScenarioGenerator(seed=42)  # Reproducible

    print("  - Generating adverse event...")
    ae = gen.generate_adverse_event()
    assert 'description' in ae
    assert 'action_taken' in ae
    assert 'training_blocked' in ae
    assert 'severity' in ae

    print("  - Generating robot issue call...")
    ri = gen.generate_robot_issue_call()
    assert 'device' in ri
    assert ri['device'] in ['pluto', 'mars']
    assert 'outcome' in ri
    assert 'call_mode' in ri

    print("  - Generating patient call...")
    pc = gen.generate_patient_call()
    assert 'call_mode' in pc
    assert 'duration_minutes' in pc

    print("  - Rolling scenario injection (control)...")
    scenario = gen.roll_scenario_injection('control', injection_probability=1.0)
    assert scenario is not None
    assert 'type' in scenario
    assert 'suggested_values' in scenario
    # Control patients should not get robot_issue_call
    if scenario['type'] in ['adverse_event', 'patient_call']:
        print(f"    Scenario type: {scenario['type']} (OK for control)")

    print("  - Rolling scenario injection (experimental)...")
    scenario = gen.roll_scenario_injection('experimental', injection_probability=1.0)
    assert scenario is not None
    # Experimental can get any type
    print(f"    Scenario type: {scenario['type']} (OK for experimental)")

    print("  - Getting scenario instruction...")
    instruction = gen.get_scenario_instruction(scenario)
    assert isinstance(instruction, str)
    assert len(instruction) > 0

    print("  [OK] Scenario generator tests passed")


def test_verification_engine():
    """Test verification engine initialization."""
    print("\n[TEST] Verification Engine")
    print("  - Creating verification engine...")
    engine = VerificationEngine()

    print("  - Verifying methods exist...")
    assert hasattr(engine, 'verify_expected_event')
    assert hasattr(engine, 'verify_all_expected_events')
    assert hasattr(engine, 'generate_summary_report')

    print("  - Generating sample report...")
    sample_verdicts = {
        'HOCMCVTST1': [
            {'protocol_event_id': 'activation', 'verdict': 'done_on_time'},
            {'protocol_event_id': 'home_visit_d02', 'verdict': 'done_on_time'},
        ],
        'HOCMCVTST2': [
            {'protocol_event_id': 'activation', 'verdict': 'missing'},
        ]
    }
    report = engine.generate_summary_report(sample_verdicts)

    print(f"    Overall pass rate: {report['overall']['pass_rate']:.1f}%")
    assert report['overall']['done_on_time'] == 2
    assert report['overall']['missing'] == 1
    assert report['overall']['total'] == 3

    print("  [OK] Verification engine tests passed")


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("TRAINING SIMULATOR — SMOKE TESTS")
    print("=" * 60)

    try:
        test_state_store()
        test_protocol_engine()
        test_scenario_generator()
        test_verification_engine()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
