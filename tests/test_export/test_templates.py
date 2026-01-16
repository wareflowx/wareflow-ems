"""Tests for export templates."""

import pytest

from export import templates


class TestColumnDefinitions:
    """Tests for column definition constants."""

    def test_employee_columns_structure(self):
        """Should have correct structure for employee columns."""
        assert len(templates.EMPLOYEE_COLUMNS) == 8

        # First column should be external_id
        assert templates.EMPLOYEE_COLUMNS[0]['key'] == 'external_id'
        assert templates.EMPLOYEE_COLUMNS[0]['header'] == 'ID WMS'
        assert templates.EMPLOYEE_COLUMNS[0]['width'] == 15

        # Last column should be status
        assert templates.EMPLOYEE_COLUMNS[-1]['key'] == 'status'
        assert templates.EMPLOYEE_COLUMNS[-1]['header'] == 'Statut'

    def test_caces_columns_structure(self):
        """Should have correct structure for CACES columns."""
        assert len(templates.CACES_COLUMNS) == 8

        # Should have employee reference
        assert templates.CACES_COLUMNS[0]['key'] == 'employee_external_id'
        assert templates.CACES_COLUMNS[1]['key'] == 'employee_name'

        # Should have kind, dates, and status
        keys = [col['key'] for col in templates.CACES_COLUMNS]
        assert 'kind' in keys
        assert 'completion_date' in keys
        assert 'expiration_date' in keys
        assert 'days_until_expiration' in keys
        assert 'status' in keys

    def test_medical_columns_structure(self):
        """Should have correct structure for medical visit columns."""
        assert len(templates.MEDICAL_COLUMNS) == 9

        keys = [col['key'] for col in templates.MEDICAL_COLUMNS]
        assert 'visit_type' in keys
        assert 'visit_date' in keys
        assert 'result' in keys

    def test_training_columns_structure(self):
        """Should have correct structure for training columns."""
        assert len(templates.TRAINING_COLUMNS) == 8

        # Should have title instead of kind
        keys = [col['key'] for col in templates.TRAINING_COLUMNS]
        assert 'title' in keys
        assert 'completion_date' in keys

    def test_summary_columns_structure(self):
        """Should have simple structure for summary."""
        assert len(templates.SUMMARY_COLUMNS) == 2
        assert templates.SUMMARY_COLUMNS[0]['key'] == 'metric'
        assert templates.SUMMARY_COLUMNS[1]['key'] == 'value'


class TestStyleDefinitions:
    """Tests for style definition constants."""

    def test_header_style_has_required_keys(self):
        """Should have all required style keys."""
        assert 'font' in templates.HEADER_STYLE
        assert 'fill' in templates.HEADER_STYLE
        assert 'alignment' in templates.HEADER_STYLE
        assert 'border' in templates.HEADER_STYLE

    def test_header_style_is_blue(self):
        """Should have blue background."""
        assert templates.HEADER_STYLE['fill']['fgColor'] == '4472C4'
        assert templates.HEADER_STYLE['font']['color'] == 'FFFFFF'

    def test_critical_style_is_red(self):
        """Should have red background."""
        assert templates.CRITICAL_STYLE['fill']['fgColor'] == 'C0504D'

    def test_warning_style_is_yellow(self):
        """Should have yellow background."""
        assert templates.WARNING_STYLE['fill']['fgColor'] == 'FFEB9C'

    def test_valid_style_is_green(self):
        """Should have green background."""
        assert templates.VALID_STYLE['fill']['fgColor'] == 'C6EFCE'

    def test_all_styles_have_borders(self):
        """All styles should have border definitions."""
        styles = [
            templates.HEADER_STYLE,
            templates.CRITICAL_STYLE,
            templates.WARNING_STYLE,
            templates.VALID_STYLE,
            templates.DEFAULT_STYLE,
        ]

        for style in styles:
            assert 'border' in style
            assert 'top' in style['border']
            assert 'left' in style['border']
            assert 'bottom' in style['border']
            assert 'right' in style['border']


class TestGetColumnWidths:
    """Tests for get_column_widths function."""

    def test_extracts_widths_from_columns(self):
        """Should extract widths from column definitions."""
        widths = templates.get_column_widths(templates.EMPLOYEE_COLUMNS)

        assert len(widths) == 8
        assert widths[0] == 15
        assert widths[1] == 25

    def test_returns_list(self):
        """Should return a list."""
        widths = templates.get_column_widths(templates.CACES_COLUMNS)

        assert isinstance(widths, list)
        assert all(isinstance(w, int) for w in widths)


class TestGetStyleForStatus:
    """Tests for get_style_for_status function."""

    def test_returns_critical_style_for_critical(self):
        """Should return CRITICAL_STYLE for 'critical'."""
        style = templates.get_style_for_status('critical')

        assert style == templates.CRITICAL_STYLE

    def test_returns_critical_style_for_expired(self):
        """Should return CRITICAL_STYLE for 'expired'."""
        style = templates.get_style_for_status('expired')

        assert style == templates.CRITICAL_STYLE

    def test_returns_critical_style_for_unfit(self):
        """Should return CRITICAL_STYLE for 'unfit'."""
        style = templates.get_style_for_status('unfit')

        assert style == templates.CRITICAL_STYLE

    def test_returns_warning_style_for_warning(self):
        """Should return WARNING_STYLE for 'warning'."""
        style = templates.get_style_for_status('warning')

        assert style == templates.WARNING_STYLE

    def test_returns_valid_style_for_valid(self):
        """Should return VALID_STYLE for 'valid'."""
        style = templates.get_style_for_status('valid')

        assert style == templates.VALID_STYLE

    def test_returns_valid_style_for_compliant(self):
        """Should return VALID_STYLE for 'compliant'."""
        style = templates.get_style_for_status('compliant')

        assert style == templates.VALID_STYLE

    def test_returns_valid_style_for_fit(self):
        """Should return VALID_STYLE for 'fit'."""
        style = templates.get_style_for_status('fit')

        assert style == templates.VALID_STYLE

    def test_case_insensitive(self):
        """Should be case insensitive."""
        style1 = templates.get_style_for_status('CRITICAL')
        style2 = templates.get_style_for_status('Critical')
        style3 = templates.get_style_for_status('critical')

        assert style1 == style2 == style3 == templates.CRITICAL_STYLE

    def test_returns_default_for_unknown_status(self):
        """Should return DEFAULT_STYLE for unknown status."""
        style = templates.get_style_for_status('unknown_status')

        assert style == templates.DEFAULT_STYLE


class TestGetHeadersForColumns:
    """Tests for get_headers_for_columns function."""

    def test_extracts_headers_from_employee_columns(self):
        """Should extract headers from employee columns."""
        headers = templates.get_headers_for_columns(templates.EMPLOYEE_COLUMNS)

        assert len(headers) == 8
        assert headers[0] == 'ID WMS'
        assert headers[1] == 'Nom Complet'
        assert headers[-1] == 'Statut'

    def test_extracts_headers_from_caces_columns(self):
        """Should extract headers from CACES columns."""
        headers = templates.get_headers_for_columns(templates.CACES_COLUMNS)

        assert len(headers) == 8
        assert 'Type CACES' in headers
        assert 'Statut' in headers


class TestGetKeysForColumns:
    """Tests for get_keys_for_columns function."""

    def test_extracts_keys_from_employee_columns(self):
        """Should extract keys from employee columns."""
        keys = templates.get_keys_for_columns(templates.EMPLOYEE_COLUMNS)

        assert len(keys) == 8
        assert keys[0] == 'external_id'
        assert keys[1] == 'full_name'
        assert keys[-1] == 'status'

    def test_extracts_keys_from_medical_columns(self):
        """Should extract keys from medical columns."""
        keys = templates.get_keys_for_columns(templates.MEDICAL_COLUMNS)

        assert 'employee_external_id' in keys
        assert 'visit_type' in keys
        assert 'result' in keys


class TestGetAllColumnDefinitions:
    """Tests for get_all_column_definitions function."""

    def test_returns_dict_with_all_types(self):
        """Should return dict with all entity types."""
        columns = templates.get_all_column_definitions()

        assert isinstance(columns, dict)
        assert 'employees' in columns
        assert 'caces' in columns
        assert 'medical' in columns
        assert 'training' in columns
        assert 'summary' in columns

    def test_each_type_has_list_of_columns(self):
        """Each type should have a list of column definitions."""
        columns = templates.get_all_column_definitions()

        for entity_type, col_list in columns.items():
            assert isinstance(col_list, list)
            assert len(col_list) > 0
            assert all('key' in col for col in col_list)
            assert all('header' in col for col in col_list)
            assert all('width' in col for col in col_list)
