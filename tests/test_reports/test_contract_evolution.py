"""Tests for contract evolution reporting."""

import pytest
from datetime import date

from employee.models import Contract
from reports.contract_evolution import (
    ContractEvolutionReport,
    DepartmentChange,
    EmploymentGap,
    PositionChange,
    SalaryChange,
    detect_employment_patterns,
    generate_contract_evolution_report,
    generate_evolution_timeline_report,
)


class TestContractEvolutionReport:
    """Tests for ContractEvolutionReport dataclass."""

    def test_generate_report_for_employee_no_contracts(self, db, sample_employee):
        """Test generating report for employee with no contracts."""
        report = generate_contract_evolution_report(sample_employee)

        assert report.employee == sample_employee
        assert report.total_contracts == 0
        assert report.total_tenure_days >= 0
        assert report.total_experience_years >= 0
        assert report.has_gaps is False

    def test_generate_report_single_contract(self, db, sample_employee):
        """Test generating report with single contract."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2020, 1, 1),
            position="Operator",
            department="Logistics",
            gross_salary=2000.00,
        )

        report = generate_contract_evolution_report(sample_employee)

        assert report.total_contracts == 1
        assert report.position_count == 0  # No changes yet
        assert report.department_count == 0
        assert report.starting_salary == 2000.00
        assert report.current_salary == 2000.00

    def test_generate_report_multiple_contracts(self, db, sample_employee):
        """Test generating report with multiple contracts showing progression."""
        # First contract: Worker position
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            position="Worker",
            department="Logistics",
            gross_salary=1800.00,
        )

        # Second contract: Promotion to Operator
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2021, 1, 1),
            position="Operator",
            department="Shipping",
            gross_salary=2100.00,
        )

        # Third contract: Promotion to Supervisor
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2022, 1, 1),
            position="Supervisor",
            department="Logistics",
            gross_salary=2500.00,
        )

        report = generate_contract_evolution_report(sample_employee)

        assert report.total_contracts == 3
        assert report.total_contracts == 3
        assert report.position_count == 2  # Worker → Operator, Operator → Supervisor
        assert report.department_count == 2  # Logistics → Shipping, Shipping → Logistics (2 unique destinations)
        assert report.starting_salary == 1800.00
        assert report.current_salary == 2500.00
        assert report.total_salary_increase == 700.00  # 1800 → 2100 → 2500

    def test_report_detects_position_changes(self, db, sample_employee):
        """Test that report correctly detects position changes."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            position="Worker",
            department="Logistics",
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2021, 1, 1),
            position="Operator",
            department="Logistics",
        )

        report = generate_contract_evolution_report(sample_employee)

        assert len(report.position_changes) == 1
        assert report.position_changes[0].from_position == "Worker"
        assert report.position_changes[0].to_position == "Operator"
        assert report.position_changes[0].change_date == date(2021, 1, 1)

    def test_report_detects_department_changes(self, db, sample_employee):
        """Test that report correctly detects department transfers."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2020, 1, 1),
            position="Operator",
            department="Logistics",
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2021, 1, 1),
            position="Operator",
            department="Shipping",
        )

        report = generate_contract_evolution_report(sample_employee)

        assert len(report.department_changes) == 1
        assert report.department_changes[0].from_department == "Logistics"
        assert report.department_changes[0].to_department == "Shipping"

    def test_report_detects_salary_evolution(self, db, sample_employee):
        """Test that report tracks salary progression."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            position="Worker",
            department="Logistics",
            gross_salary=1800.00,
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2021, 1, 1),
            position="Operator",
            department="Logistics",
            gross_salary=2000.00,
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2022, 1, 1),
            position="Supervisor",
            department="Logistics",
            gross_salary=2500.00,
        )

        report = generate_contract_evolution_report(sample_employee)

        assert len(report.salary_evolution) == 3
        assert report.salary_evolution[0].salary == 1800.00
        assert report.salary_evolution[1].salary == 2000.00
        assert report.salary_evolution[2].salary == 2500.00

        # Check percentage calculation for first increase
        assert report.salary_evolution[1].change_percentage == pytest.approx(11.11, rel=0.1)

    def test_report_detects_employment_gaps(self, db, sample_employee):
        """Test that report detects gaps in employment."""
        # First contract ends 2020-12-31
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            position="Worker",
            department="Logistics",
        )

        # Gap: 6 months (2021-01-01 to 2021-06-30)
        # Second contract starts 2021-07-01
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2021, 7, 1),
            end_date=date(2021, 12, 31),
            position="Worker",
            department="Logistics",
        )

        report = generate_contract_evolution_report(sample_employee)

        assert report.has_gaps is True
        assert len(report.employment_gaps) == 1
        assert report.employment_gaps[0].gap_days == 182  # ~6 months
        assert report.employment_gaps[0].previous_contract_type == "CDD"
        assert report.employment_gaps[0].next_contract_type == "CDD"

    def test_report_has_gaps_property(self, db, sample_employee):
        """Test has_gaps property shortcut."""
        # No gaps
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2020, 1, 1),
            position="Worker",
            department="Logistics",
        )

        report = generate_contract_evolution_report(sample_employee)
        assert report.has_gaps is False

    def test_report_to_dict(self, db, sample_employee):
        """Test converting report to dictionary."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2020, 1, 1),
            position="Operator",
            department="Logistics",
            gross_salary=2000.00,
        )

        report = generate_contract_evolution_report(sample_employee)
        report_dict = report.to_dict()

        assert "employee_id" in report_dict
        assert "employee_name" in report_dict
        assert "total_contracts" in report_dict
        assert "position_changes" in report_dict
        assert "salary_evolution" in report_dict
        assert isinstance(report_dict["position_changes"], list)
        assert isinstance(report_dict["salary_evolution"], list)

    def test_calculate_average_tenure_per_contract(self, db, sample_employee):
        """Test average tenure calculation."""
        # Two contracts: 1 year each
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            position="Worker",
            department="Logistics",
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2021, 1, 1),
            end_date=date(2021, 12, 31),
            position="Operator",
            department="Logistics",
        )

        report = generate_contract_evolution_report(sample_employee)

        # Average tenure: (365 + 365) / 2 = 365 days
        assert report.average_tenure_per_contract == pytest.approx(365, rel=0.1)

    def test_calculate_total_gap_days(self, db, sample_employee):
        """Test total gap days calculation."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 6, 30),  # Ends June 30
            position="Worker",
            department="Logistics",
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 8, 1),  # Starts Aug 1 (30 day gap)
            end_date=date(2020, 12, 31),
            position="Worker",
            department="Logistics",
        )

        report = generate_contract_evolution_report(sample_employee)

        # Gap: June 30 to August 1 = 32 days (July has 31 days)
        assert report.total_gap_days == 32


class TestTimelineReport:
    """Tests for timeline visualization report."""

    def test_generate_timeline_single_contract(self, db, sample_employee):
        """Test timeline for single contract."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2020, 1, 1),
            trial_period_end=date(2020, 3, 1),
            position="Operator",
            department="Logistics",
        )

        timeline = generate_evolution_timeline_report(sample_employee)

        assert len(timeline) == 2  # Start + trial period end
        assert timeline[0]["event_type"] == "contract_start"
        assert timeline[1]["event_type"] == "trial_period_end"

    def test_generate_timeline_multiple_contracts(self, db, sample_employee):
        """Test timeline with multiple contracts including gaps."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            position="Worker",
            department="Logistics",
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2021, 1, 1),
            position="Operator",
            department="Shipping",
        )

        timeline = generate_evolution_timeline_report(sample_employee)

        # Should have: start (contract 1), end (contract 1), start (contract 2)
        assert len(timeline) >= 2
        assert any(t["event_type"] == "contract_start" for t in timeline)

    def test_timeline_includes_all_required_fields(self, db, sample_employee):
        """Test that timeline events include all required fields."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            position="Operator",
            department="Logistics",
        )

        timeline = generate_evolution_timeline_report(sample_employee)

        # Check first event structure
        first_event = timeline[0]
        assert "date" in first_event
        assert "event_type" in first_event
        assert "title" in first_event
        assert "description" in first_event
        assert "contract_type" in first_event
        assert "position" in first_event
        assert "department" in first_event


class TestEmploymentPatterns:
    """Tests for employment pattern detection."""

    def test_detect_patterns_no_contracts(self):
        """Test pattern detection with no contracts."""
        patterns = detect_employment_patterns([])

        assert patterns["total_contracts"] == 0
        assert patterns["contract_types"] == {}
        assert patterns["most_common_position"] is None
        assert patterns["average_contract_duration_days"] is None

    def test_detect_patterns_contracts_only_cdi(self, db, sample_employee):
        """Test pattern detection with only CDI contracts."""
        for i in range(3):
            Contract.create(
                employee=sample_employee,
                contract_type="CDI",
                start_date=date(2020 + i, 1, 1),
                position="Operator",
                department="Logistics",
            )

        contracts = list(Contract.select().where(Contract.employee == sample_employee))
        patterns = detect_employment_patterns(contracts)

        assert patterns["total_contracts"] == 3
        assert patterns["contract_types"]["CDI"] == 3
        assert patterns["most_common_position"] == "Operator"
        assert patterns["most_common_department"] == "Logistics"
        assert patterns["has_permanent_contract"] is True

    def test_detect_patterns_mixed_contracts(self, db, sample_employee):
        """Test pattern detection with mixed contract types."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 12, 31),
            position="Worker",
            department="Logistics",
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDI",
            start_date=date(2021, 1, 1),
            position="Operator",
            department="Logistics",
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2022, 1, 1),
            end_date=date(2022, 6, 30),
            position="Worker",
            department="Shipping",
        )

        contracts = list(Contract.select().where(Contract.employee == sample_employee))
        patterns = detect_employment_patterns(contracts)

        assert patterns["total_contracts"] == 3
        assert patterns["contract_types"]["CDD"] == 2
        assert patterns["contract_types"]["CDI"] == 1
        assert patterns["has_permanent_contract"] is True

    def test_detect_patterns_average_duration(self, db, sample_employee):
        """Test average contract duration calculation."""
        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 6, 30),  # 180 days
            position="Worker",
            department="Logistics",
        )

        Contract.create(
            employee=sample_employee,
            contract_type="CDD",
            start_date=date(2021, 1, 1),
            end_date=date(2021, 12, 31),  # 364 days
            position="Worker",
            department="Logistics",
        )

        contracts = list(Contract.select().where(Contract.employee == sample_employee))
        patterns = detect_employment_patterns(contracts)

        # Average: (180 + 364) / 2 = 272
        assert patterns["average_contract_duration_days"] == pytest.approx(272, rel=0.1)
