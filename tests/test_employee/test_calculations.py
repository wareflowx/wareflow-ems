"""Tests for Employee calculations."""

import pytest
from datetime import date, timedelta
from freezegun import freeze_time

from employee.models import Employee, Caces, MedicalVisit, OnlineTraining
from employee import calculations


class TestCalculateSeniority:
    """Tests for calculate_seniority function."""

    def test_calculates_years_correctly(self, db):
        """Should calculate complete years since entry_date."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 15)
        )

        with freeze_time('2026-01-16'):
            seniority = calculations.calculate_seniority(employee)
            assert seniority == 6

    def test_handles_leap_years_correctly(self, db):
        """Should handle leap years correctly using relativedelta."""
        # Employee hired on Feb 29, 2020 (leap year)
        employee = Employee.create(
            first_name='Leap',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 2, 29)
        )

        with freeze_time('2025-02-28'):
            seniority = calculations.calculate_seniority(employee)
            # relativedelta counts full years, so Feb 29, 2020 -> Feb 28, 2025 is 5 years
            assert seniority == 5

    def test_returns_zero_for_future_entry_date(self, db):
        """Should return 0 if entry_date is in the future."""
        # We can't create an employee with future entry_date due to validation
        # So we test the calculation function directly with a mock employee
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date.today()
        )

        # Manually set entry_date to future (bypassing validation)
        # This tests the calculation logic, not the model validation
        employee.entry_date = date(2030, 1, 1)

        seniority = calculations.calculate_seniority(employee)
        assert seniority == 0

    def test_returns_zero_for_partial_year(self, db):
        """Should return 0 for less than a complete year."""
        employee = Employee.create(
            first_name='New',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date.today() - timedelta(days=180)
        )

        seniority = calculations.calculate_seniority(employee)
        assert seniority == 0


class TestCalculateComplianceScore:
    """Tests for calculate_compliance_score function."""

    def test_perfect_score_for_all_valid_items(self, db):
        """Should return 100 for all valid compliance items."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create valid CACES (5 years from today)
        Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date.today(),
            document_path='/test.pdf'
        )

        # Create valid medical visit
        MedicalVisit.create(
            employee=employee,
            visit_type='periodic',
            visit_date=date.today(),
            result='fit',
            document_path='/test.pdf'
        )

        score = calculations.calculate_compliance_score(employee)

        assert score['score'] == 100
        assert score['total_items'] == 2
        assert score['valid_items'] == 2
        assert score['critical_items'] == 0
        assert score['expired_items'] == 0

    def test_low_score_for_expired_items(self, db):
        """Should return low score for expired compliance items."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expired CACES
        expiration_date = date.today() - timedelta(days=10)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2015, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        score = calculations.calculate_compliance_score(employee)

        assert score['score'] < 50  # Should be low
        assert score['expired_items'] == 1

    def test_medium_score_for_critical_items(self, db):
        """Should return medium score for critical items."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create critical CACES (expiring in 15 days)
        expiration_date = date.today() + timedelta(days=15)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        score = calculations.calculate_compliance_score(employee)

        # Critical item: -30 points, normalized: (-30 + 100) / 2 = 35
        assert score['score'] == 35
        assert score['critical_items'] == 1

    def test_ignores_permanent_trainings(self, db):
        """Should not include permanent trainings in score."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create permanent training
        OnlineTraining.create(
            employee=employee,
            title='General Orientation',
            completion_date=date.today(),
            validity_months=None,
            certificate_path='/test.pdf'
        )

        score = calculations.calculate_compliance_score(employee)

        # Permanent trainings shouldn't affect score
        assert score['total_items'] == 0
        assert score['score'] == 100

    def test_handles_no_compliance_items(self, db):
        """Should return neutral score when no compliance items exist."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        score = calculations.calculate_compliance_score(employee)

        assert score['score'] == 100
        assert score['total_items'] == 0


class TestGetComplianceStatus:
    """Tests for get_compliance_status function."""

    def test_returns_critical_for_expired_items(self, db):
        """Should return 'critical' when employee has expired items."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expired CACES
        expiration_date = date.today() - timedelta(days=10)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2015, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        status = calculations.get_compliance_status(employee)
        assert status == 'critical'

    def test_returns_warning_for_critical_items(self, db):
        """Should return 'warning' when items expiring soon but none expired."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create critical CACES (expiring in 15 days)
        expiration_date = date.today() + timedelta(days=15)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        status = calculations.get_compliance_status(employee)
        assert status == 'warning'

    def test_returns_compliant_for_all_valid(self, db):
        """Should return 'compliant' when all items are valid."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create valid CACES
        Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date.today(),
            document_path='/test.pdf'
        )

        status = calculations.get_compliance_status(employee)
        assert status == 'compliant'


class TestCalculateNextActions:
    """Tests for calculate_next_actions function."""

    def test_prioritizes_expired_items(self, db):
        """Should prioritize expired items as urgent."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expired CACES
        expiration_date = date.today() - timedelta(days=10)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2015, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        actions = calculations.calculate_next_actions(employee)

        assert len(actions) == 1
        assert actions[0]['priority'] == 'urgent'
        assert 'expired' in actions[0]['description'].lower()

    def test_sorts_by_priority_and_days(self, db):
        """Should sort actions by priority then by days until."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create CACES expiring in 20 days (urgent)
        expiration_date1 = date.today() + timedelta(days=20)
        caces1 = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test1.pdf'
        )
        caces1.expiration_date = expiration_date1
        caces1.save()

        # Create CACES expiring in 15 days (urgent, should come first)
        expiration_date2 = date.today() + timedelta(days=15)
        caces2 = Caces.create(
            employee=employee,
            kind='R489-1B',
            completion_date=date(2020, 1, 1),
            document_path='/test2.pdf'
        )
        caces2.expiration_date = expiration_date2
        caces2.save()

        actions = calculations.calculate_next_actions(employee)

        assert len(actions) == 2
        assert actions[0]['days_until'] < actions[1]['days_until']

    def test_ignores_valid_items(self, db):
        """Should not include actions for valid items."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create valid CACES
        Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date.today(),
            document_path='/test.pdf'
        )

        actions = calculations.calculate_next_actions(employee)

        assert len(actions) == 0

    def test_includes_all_item_types(self, db):
        """Should include CACES, medical visits, and trainings."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create expiring CACES
        expiration_date = date.today() + timedelta(days=15)
        caces = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test.pdf'
        )
        caces.expiration_date = expiration_date
        caces.save()

        # Create expiring medical visit
        expiration_date = date.today() + timedelta(days=20)
        visit = MedicalVisit.create(
            employee=employee,
            visit_type='periodic',
            visit_date=date.today(),
            result='fit',
            document_path='/test.pdf'
        )
        visit.expiration_date = expiration_date
        visit.save()

        # Create expiring training
        expiration_date = date.today() + timedelta(days=10)
        training = OnlineTraining.create(
            employee=employee,
            title='Safety Training',
            completion_date=date.today(),
            validity_months=12,
            certificate_path='/test.pdf'
        )
        training.expiration_date = expiration_date
        training.save()

        actions = calculations.calculate_next_actions(employee)

        assert len(actions) == 3
        action_types = {a['type'] for a in actions}
        assert action_types == {'caces', 'medical', 'training'}


class TestDaysUntilNextAction:
    """Tests for days_until_next_action function."""

    def test_returns_min_days_until_expiration(self, db):
        """Should return minimum days until any item expires."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create CACES expiring in 30 days
        expiration_date1 = date.today() + timedelta(days=30)
        caces1 = Caces.create(
            employee=employee,
            kind='R489-1A',
            completion_date=date(2020, 1, 1),
            document_path='/test1.pdf'
        )
        caces1.expiration_date = expiration_date1
        caces1.save()

        # Create CACES expiring in 15 days (should be returned)
        expiration_date2 = date.today() + timedelta(days=15)
        caces2 = Caces.create(
            employee=employee,
            kind='R489-1B',
            completion_date=date(2020, 1, 1),
            document_path='/test2.pdf'
        )
        caces2.expiration_date = expiration_date2
        caces2.save()

        days = calculations.days_until_next_action(employee)
        assert days == 15

    def test_returns_9999_for_no_items(self, db):
        """Should return 9999 when employee has no compliance items."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        days = calculations.days_until_next_action(employee)
        assert days == 9999

    def test_ignores_permanent_trainings(self, db):
        """Should ignore permanent trainings in calculation."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # Create permanent training
        OnlineTraining.create(
            employee=employee,
            title='General Orientation',
            completion_date=date.today(),
            validity_months=None,
            certificate_path='/test.pdf'
        )

        days = calculations.days_until_next_action(employee)
        assert days == 9999  # No expiring items


class TestCalculateAge:
    """Tests for calculate_age function."""

    def test_returns_none_for_missing_birth_date(self, db):
        """Should return None when birth_date is not available."""
        employee = Employee.create(
            first_name='Test',
            last_name='User',
            current_status='active',
            workspace='Quai',
            role='Préparateur',
            contract_type='CDI',
            entry_date=date(2020, 1, 1)
        )

        # birth_date field doesn't exist yet in Employee model
        age = calculations.calculate_age(employee)
        assert age is None
