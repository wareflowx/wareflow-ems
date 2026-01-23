# [CRITICAL] Missing Test Coverage for New Features

## Type
**Quality Assurance / Technical Debt**

## Severity
**CRITICAL** - Bugs reach production, regression issues, unreliable features

## Affected Components
- **Testing** - Test suite
- **Quality** - Bug detection
- **New Features** - Bootstrapper, updates, migration, etc.

## Description

As new features are added (bootstrapper, update mechanism, migration tools, etc.), no test coverage exists for these components. This leads to bugs reaching production, regression issues, and unreliable functionality.

## Current Test Coverage

### Existing Coverage (v1.x)

**Tested areas**:
- ✅ Employee models (CRUD operations)
- ✅ CACES models (CRUD operations)
- ✅ Medical visit models (CRUD operations)
- ✅ Basic CLI commands
- ✅ Some validation logic

**Coverage**: ~40% (as stated in README)

### Untested New Features (v2.0.0)

**Completely untested**:
- ❌ Bootstrapper (`wems init`)
- ❌ Configuration wizard
- ❌ Template system
- ❌ YAML configuration
- ❌ Update mechanism
- ❌ Migration tools
- ❌ Rollback functionality
- ❌ Health checks
- ❌ Build pipeline
- ❌ Installer

**Impact**: 0% confidence in new features

## Real-World Impact

### Scenario 1: Bootstrapper Bug

**Situation**: Edge case in `wems init` not tested

**Bug**:
```
User runs: wems init "Test Company"
User enters company name with special chars: "O'Reilly & Sons"
Bootstrapper creates directory: O'Reilly & Sons
Error: Directory name invalid on Windows
Result: Creation fails, partial state
User: Stuck with broken installation
```

**With tests**:
```python
def test_init_with_special_characters():
    """Test company name with special characters."""
    result = run_init("O'Reilly & Sons")
    assert result.success
    assert "directory_created" in result
```

**Result**: Bug caught before release

### Scenario 2: Migration Failure

**Situation**: Database migration not tested with real data

**Bug**:
```
User upgrades from v1.0.0 to v1.1.0
Migration adds department field
Migration fails silently on databases with > 1000 employees
Result: Database corrupted, data loss
User: Loses critical data
```

**With tests**:
```python
def test_migration_with_large_database():
    """Test migration with 1000+ employees."""
    db = create_test_database(num_employees=1500)
    migrate(db, from_v="1.0.0", to_v="1.1.0")
    assert db.employees.count() == 1500
    assert all(emp.department is not None for emp in db.employees)
```

**Result**: Migration tested with various data sizes

### Scenario 3: Update Mechanism Regression

**Situation**: Update code changes, breaks existing functionality

**Bug**:
```
Developer: Adds new feature to updater
Developer: Changes API of update checker
Developer: Forgets to update all callers
User: Runs wems update
Error: "TypeError: unexpected keyword argument"
Result: Update mechanism broken for all users
```

**With tests**:
```python
def test_update_command():
    """Test wems update command."""
    result = run_command("wems update")
    assert result.exit_code == 0
    assert "checking for updates" in result.output.lower()
```

**Result**: Regression caught in CI/CD

## Problems Created

### 1. Bugs Reach Production

**No testing means**:
- Edge cases not caught
- Error handling not tested
- Integration issues not found
- User-reported bugs

**Impact**: Poor user experience, emergency fixes

### 2. Regression Issues

**Code changes break existing functionality**:
- Refactoring breaks callers
- API changes not propagated
- Assumptions invalidated
- Silent failures

**Impact**: Features that worked before now broken

### 3. Fear of Changes

**Developers afraid to modify**:
- "What if I break something?"
- "I don't know what's tested"
- "Better not touch it"
- Technical debt accumulates

**Impact**: Slow development, stagnation

### 4. Poor Code Quality

**No tests encourages**:
- Quick fixes without testing
- Skipping error handling
- Making assumptions
- Cutting corners

**Impact**: Codebase degrades over time

### 5. Difficult Refactoring

**Want to refactor but**:
- No safety net of tests
- Don't know if breaking changes
- Fear of unintended consequences
- Manual testing only

**Impact**: Code becomes harder to maintain

### 6. Integration Issues

**Components work in isolation but**:
- Not tested together
- Contract violations
- Data flow issues
- State management bugs

**Impact**: System fails in production

### 7. Performance Regressions

**Changes can slow down**:
- Database queries
- File I/O
- Network operations
- Algorithm complexity

**No tests means**:
- Performance degrades unnoticed
- Users complain about slowness
- Hard to identify bottlenecks

**Impact**: Poor user experience

## Test Coverage Gaps

### Bootstrapper Tests (0% coverage)

**Missing tests**:
- `wems init` command
- Interactive wizard
- Template generation
- Directory creation
- Configuration generation
- Database initialization
- Error handling

**Risk**: Core functionality completely untested

### Update Mechanism Tests (0% coverage)

**Missing tests**:
- Version checking
- Download logic
- Backup creation
- Migration execution
- Rollback functionality
- Error handling

**Risk**: Update mechanism could break installations

### Migration Tests (0% coverage)

**Missing tests**:
- Config format conversion
- Database schema migrations
- Data integrity validation
- Rollback functionality
- Cross-version migrations

**Risk**: Data loss during upgrades

### YAML Configuration Tests (0% coverage)

**Missing tests**:
- YAML parsing
- Schema validation
- Configuration loading
- Error handling
- Edge cases

**Risk**: Configuration errors, application crashes

### Build Pipeline Tests (0% coverage)

**Missing tests**:
- Build script
- Signing process
- Artifact generation
- Multi-platform builds

**Risk**: Broken builds, failed releases

## Proposed Solution

### Solution 1: Comprehensive Test Suite

**Test structure**:
```
tests/
├── test_bootstrapper/
│   ├── test_init_command.py
│   ├── test_wizard.py
│   ├── test_templates.py
│   └── test_config_generator.py
├── test_update/
│   ├── test_update_checker.py
│   ├── test_updater.py
│   ├── test_rollback.py
│   └── test_integration.py
├── test_migration/
│   ├── test_config_migrator.py
│   ├── test_db_migrator.py
│   ├── test_validation.py
│   └── test_rollback.py
├── test_yaml/
│   ├── test_parser.py
│   ├── test_validator.py
│   ├── test_loader.py
│   └── test_edge_cases.py
├── test_build/
│   ├── test_build_script.py
│   ├── test_signing.py
│   └── test_artifacts.py
└── test_integration/
    ├── test_e2e_bootstrapper.py
    ├── test_e2e_update.py
    └── test_e2e_migration.py
```

### Solution 2: Test Coverage Goals

**Target coverage**:
- **Bootstrapper**: 90%+
- **Update mechanism**: 90%+
- **Migration tools**: 95%+ (critical for data safety)
- **YAML config**: 85%+
- **Build pipeline**: 80%+

**Overall**: 70%+ (up from 40%)

### Solution 3: Test Types

#### Unit Tests

**Test individual functions**:
```python
def test_validate_company_name():
    """Test company name validation."""
    # Valid names
    assert validate_company_name("Acme Corp") == "Acme Corp"
    assert validate_company_name("O'Reilly") == "O'Reilly"

    # Invalid names
    with pytest.raises(ValidationError):
        validate_company_name("")  # Empty

    with pytest.raises(ValidationError):
        validate_company_name("A" * 200)  # Too long
```

#### Integration Tests

**Test component interactions**:
```python
def test_init_creates_working_application():
    """Test that init creates a working application."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_init("Test Company", output_dir=tmpdir)

        # Verify files created
        assert Path(tmpdir, "config.yaml").exists()
        assert Path(tmpdir, "data", "test_company.db").exists()

        # Verify database is valid
        db = Database(Path(tmpdir, "data", "test_company.db"))
        assert db.is_valid()

        # Verify application can start
        app = Application(config_path=Path(tmpdir, "config.yaml"))
        assert app.start() == True
```

#### End-to-End Tests

**Test complete workflows**:
```python
def test_full_upgrade_workflow():
    """Test complete upgrade from v1.0.0 to v1.1.0."""
    # Setup v1.0.0 installation
    install_v100()
    add_test_data()

    # Run upgrade
    result = run_upgrade(to_version="v1.1.0")
    assert result.success

    # Verify upgrade
    assert get_version() == "v1.1.0"
    assert all_data_present()
    assert application_works()
```

### Solution 4: CI/CD Integration

**Automated testing**:
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.14'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync

      - name: Run tests
        run: |
          uv run pytest --cov=src --cov-report=xml

      - name: Check coverage
        run: |
          coverage report --fail-under=70

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

**Quality gates**:
- All tests must pass
- Coverage must be ≥ 70%
- No new code without tests

## Implementation Plan

### Phase 1: Bootstrapper Tests (1 week)
1. Test `wems init` command
2. Test wizard
3. Test templates
4. Test configuration generation
5. Test error handling

### Phase 2: Update & Migration Tests (1 week)
1. Test update mechanism
2. Test rollback
3. Test config migration
4. Test database migration
5. Test data validation

### Phase 3: YAML Tests (3 days)
1. Test parsing
2. Test validation
3. Test loading
4. Test edge cases

### Phase 4: Integration Tests (1 week)
1. End-to-end workflows
2. Multi-component tests
3. Real-world scenarios
4. Performance tests

## Files to Create

- `tests/test_bootstrapper/` - 4 test files
- `tests/test_update/` - 4 test files
- `tests/test_migration/` - 4 test files
- `tests/test_yaml/` - 4 test files
- `tests/test_build/` - 3 test files
- `tests/test_integration/` - 3 test files

**Total**: 22 new test files

## Testing Requirements

- All new features must have tests
- Coverage minimum: 70%
- All tests must pass in CI/CD
- No regressions allowed
- Performance tests for critical paths

## Benefits

### For Quality
- **Bug prevention**: Catch bugs before release
- **Regression detection**: Know if changes break existing features
- **Confidence**: Deploy with confidence

### For Development
- **Refactoring**: Safe to refactor with tests
- **Speed**: Faster development with immediate feedback
- **Documentation**: Tests serve as usage examples

### For Users
- **Reliability**: Fewer bugs in production
- **Stability**: Features work consistently
- **Trust**: Professional quality

## Success Metrics

- [ ] Test coverage ≥ 70%
- [ ] All new features have tests
- [ ] Zero regressions in production
- [ ] CI/CD tests pass 100% of time
- [ ] Bug reports reduced by 80%

## Related Issues

- All v2.0.0 issues require testing

## Priority

**CRITICAL** - Unreliable features, data loss risk, poor quality

## Estimated Effort

4 weeks (bootstrapper + update/migration + yaml + integration tests)

## Mitigation

While building test suite:
1. Write tests alongside feature development
2. Start with critical paths (migration, update)
3. Use TDD for new features
4. Add tests for bugs as they're found
5. Gradually increase coverage
