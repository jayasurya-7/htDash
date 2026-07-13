"""
Randomized scenario injection for training realism.

Generates training scenarios: adverse events, robot issues, patient calls, etc.
with plausible suggested field values that trainee must replicate in htDash.
"""

import random
from typing import Dict, Any, Optional, List
from datetime import datetime


class ScenarioGenerator:
    """Generate randomized training scenarios."""

    # Adverse event severity levels
    AE_SEVERITIES = ['Investigator', 'Consultant', 'IRB']

    # Plausible adverse event descriptions
    AE_DESCRIPTIONS = [
        'Patient reported increased muscle soreness post-training',
        'Mild swelling observed in training arm',
        'Patient experienced difficulty with prescribed exercises',
        'Joint pain reported during therapy session',
        'Patient fatigue after training session',
        'Slight skin irritation from device wear',
    ]

    # Call mode options
    CALL_MODES = ['audio', 'video', 'text']

    # Robot issue device outcomes
    RI_OUTCOMES = ['resolved', 'visit_required']

    # Device issue descriptions
    DEVICE_ISSUES = [
        'Device not charging properly',
        'Device pairing lost',
        'Sensor readings inconsistent',
        'Device connectivity issues',
    ]

    # Patient call reasons (therapist-initiated)
    CALL_REASONS = [
        'Check on exercise progress',
        'Clarify exercise technique',
        'Discuss adherence challenges',
        'Provide motivation and support',
        'Troubleshoot device issues',
    ]

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize scenario generator.

        Args:
            seed: Random seed for reproducibility (useful for testing).
        """
        if seed is not None:
            random.seed(seed)

    def generate_adverse_event(self) -> Dict[str, Any]:
        """
        Generate a suggested adverse event scenario.

        Returns:
            Dict with keys: description, action_taken, training_blocked, severity.
        """
        return {
            'description': random.choice(self.AE_DESCRIPTIONS),
            'action_taken': 'Discussed with patient and provided modified exercise recommendations',
            'training_blocked': random.choice([True, False]),
            'severity': random.choice(self.AE_SEVERITIES),
        }

    def generate_robot_issue_call(self) -> Dict[str, Any]:
        """
        Generate a robot issue call scenario (experimental patients only).

        Returns:
            Dict with keys: device, outcome, call_mode, duration_minutes.
        """
        device = random.choice(['pluto', 'mars'])
        return {
            'device': device,
            'outcome': random.choice(self.RI_OUTCOMES),
            'call_mode': random.choice(self.CALL_MODES),
            'duration_minutes': random.randint(5, 20),
            'notes': f'Discussed {device} device issue with patient',
        }

    def generate_other_device_issue_call(self) -> Dict[str, Any]:
        """
        Generate an other device issue call scenario (experimental patients only).

        Returns:
            Dict with keys: device_type, outcome, call_mode, duration_minutes.
        """
        device_type = random.choice(['modems', 'laptops', 'sims'])
        return {
            'device_type': device_type,
            'outcome': random.choice(['resolved_over_call', 'visit_required']),
            'call_mode': random.choice(self.CALL_MODES),
            'duration_minutes': random.randint(5, 15),
            'issue_description': random.choice(self.DEVICE_ISSUES),
            'notes': f'Called patient about {device_type} issue',
        }

    def generate_patient_call(self) -> Dict[str, Any]:
        """
        Generate a patient call scenario.

        Returns:
            Dict with keys: call_mode, duration_minutes, reason, notes.
        """
        return {
            'call_mode': random.choice(self.CALL_MODES),
            'duration_minutes': random.randint(5, 30),
            'reason': random.choice(self.CALL_REASONS),
            'notes': 'Call completed as scheduled',
        }

    def roll_scenario_injection(
        self,
        patient_group: str,
        injection_probability: float = 0.3,
    ) -> Optional[Dict[str, Any]]:
        """
        Randomly decide whether to inject a scenario today.

        Args:
            patient_group: 'experimental' or 'control'.
            injection_probability: Chance (0.0–1.0) of injecting a scenario.

        Returns:
            Dict with scenario type and suggested values, or None if no injection.
        """
        if random.random() > injection_probability:
            return None

        # Scenarios available to all patients
        all_scenarios = [
            ('adverse_event', self.generate_adverse_event),
            ('patient_call', self.generate_patient_call),
        ]

        # Additional scenarios for experimental patients only
        exp_scenarios = [
            ('robot_issue_call', self.generate_robot_issue_call),
            ('other_device_issue_call', self.generate_other_device_issue_call),
        ]

        available = all_scenarios + (exp_scenarios if patient_group == 'experimental' else [])
        scenario_type, generator = random.choice(available)

        return {
            'type': scenario_type,
            'suggested_values': generator(),
        }

    def get_scenario_instruction(self, scenario: Dict[str, Any]) -> str:
        """
        Convert a scenario dict into a plain-English instruction for the trainee.

        Args:
            scenario: Dict from roll_scenario_injection.

        Returns:
            Human-readable instruction string.
        """
        scenario_type = scenario.get('type', 'unknown')
        values = scenario.get('suggested_values', {})

        if scenario_type == 'adverse_event':
            return (
                f"File an Adverse Event: '{values.get('description', '…')}'. "
                f"Action taken: '{values.get('action_taken', '…')}'. "
                f"Training blocked: {values.get('training_blocked', False)}. "
                f"Severity: {values.get('severity', 'Investigator')}."
            )
        elif scenario_type == 'robot_issue_call':
            return (
                f"File a Robot Issue Call: Device {values.get('device', '?').upper()} issue. "
                f"Outcome: {values.get('outcome', '?')}. "
                f"Call mode: {values.get('call_mode', 'audio')}. "
                f"Duration: {values.get('duration_minutes', 10)} minutes."
            )
        elif scenario_type == 'other_device_issue_call':
            return (
                f"File an Other Device Issue Call: {values.get('device_type', '?')} issue. "
                f"Issue: '{values.get('issue_description', '…')}'. "
                f"Outcome: {values.get('outcome', '?')}. "
                f"Call mode: {values.get('call_mode', 'audio')}."
            )
        elif scenario_type == 'patient_call':
            return (
                f"Log a Patient Call: Reason '{values.get('reason', '…')}'. "
                f"Call mode: {values.get('call_mode', 'audio')}. "
                f"Duration: {values.get('duration_minutes', 15)} minutes."
            )
        else:
            return f"Complete event: {scenario_type}"
