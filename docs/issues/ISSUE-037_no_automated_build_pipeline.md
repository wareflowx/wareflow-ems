# [HIGH] No Automated Build Pipeline

## Type
**DevOps / Release Management**

## Severity
**HIGH** - Manual builds are error-prone, inconsistent, delay releases

## Affected Components
- **Build Process** - Creating executables and distributions
- **Releases** - Publishing new versions
- **Quality Assurance** - Testing before release

## Description

Building executables and creating releases is a manual, error-prone process with no CI/CD pipeline. This leads to inconsistent builds, delayed releases, and human error.

## Current Build Process

### Manual Build Steps

```bash
# Step 1: Update version
# Manually edit version in multiple files
# src/__init__.py: __version__ = "1.2.0"
# pyproject.toml: version = "1.2.0"
# README.md: update version references

# Step 2: Run tests
uv run pytest
# Manually review test results
# Fix any failures
# Re-run tests

# Step 3: Build executable
# Remember PyInstaller command
pyinstaller --name wems \
  --windowed \
  --onefile \
  --icon assets/icon.ico \
  --add-data "src:src" \
  --hidden-import customtkinter \
  --hidden-import peewee \
  --hidden-import openpyxl

# Step 4: Test executable
# Manually run dist/wems.exe
# Click through application
# Test basic functionality
# Hope nothing broken

# Step 5: Create release
# Go to GitHub website
# Click "Create new release"
# Enter tag name (v1.2.0)
# Paste release notes (manually written)
# Upload dist/wems.exe as asset
# Click "Publish release"

# Time: 2-3 hours
# Errors: Common (wrong version, missing asset, etc.)
```

## Real-World Impact

### Scenario 1: Bug Fix Release

**Situation**: Critical bug found, need quick release

**Current Process**:
```
Developer: Fixes bug
Developer: "Need to release v1.2.1"
Developer: Updates version in 3 files
Developer: Runs tests (waits 5 minutes)
Developer: Builds executable (waits 10 minutes)
Developer: Tests executable (10 minutes)
Developer: Creates GitHub release (5 minutes)
Developer: Uploads asset (depends on internet speed)

Total time: 45-60 minutes
During which: Users affected by bug
```

**With CI/CD**: 10 minutes total

### Scenario 2: Inconsistent Builds

**Situation**: Different builds behave differently

**Current Process**:
```
Build 1 (Developer A's machine):
  Python 3.14.0, Windows 11
  Builds wems.exe (45 MB)
  Works on Windows 11
  Fails on Windows 10

Build 2 (Developer B's machine):
  Python 3.14.1, Windows 10
  Builds wems.exe (47 MB)
  Works on Windows 10
  Fails on Windows 11

Result: Inconsistent behavior, hard to reproduce
```

**With CI/CD**: Consistent build environment

### Scenario 3: Forgotten Steps

**Situation**: Release missing assets or wrong version

**Current Process**:
```
Developer: Creates release v1.3.0
Developer: Uploads wems.exe
Developer: Publishes release

User: "Where's the changelog?"
Developer: "Oops, forgot release notes"

User: "What's the checksum?"
Developer: "Oops, forgot to generate"

User: "Where's the macOS build?"
Developer: "Oops, forgot to build on Mac"

Result: Incomplete releases, must republish
```

**With CI/CD**: Automated, complete releases

## Problems Created

### 1. Manual Version Updates

**Version in multiple files**:
- `src/__init__.py`
- `pyproject.toml`
- `README.md`
- `docs/**/*.md`

**Must be updated manually**:
- Easy to miss one file
- Easy to use wrong version
- Inconsistent versions across files

### 2. No Automated Testing

**Current process**:
- Run tests manually
- Review results manually
- Easy to skip tests "just this once"
- Easy to miss failing tests

**Impact**: Bugs reach production

### 3. Build Environment Differences

**Different machines**:
- Different Python versions
- Different OS versions
- Different dependency versions
- Different environment variables

**Impact**: Inconsistent builds

### 4. No Build Artifacts

**Current process**:
- Build executable locally
- No checksums generated
- No build logs saved
- No reproducible builds

**Impact**: Can't verify build integrity

### 5. Slow Release Process

**Current timeline**:
- Build: 15-30 minutes
- Test: 10-15 minutes
- Release creation: 10-15 minutes
- Asset upload: 5-10 minutes

**Total**: 45-70 minutes per release

**Impact**: Slow response to bugs

### 6. Human Error

**Common mistakes**:
- Wrong version number
- Missing assets
- Incomplete changelog
- Forgot to tag git
- Released from wrong branch

**Impact**: Must delete and recreate release

### 7. No Multi-Platform Builds

**Current process**:
- Build on Windows for Windows
- Build on macOS for macOS
- Build on Linux for Linux
- Need access to all platforms

**Impact**: Incomplete platform support

## Missing Features

### CI/CD Pipeline
- [ ] Automated builds on push
- [ ] Automated testing
- [ ] Multi-platform builds
- [ ] Artifact generation
- [ ] GitHub Releases integration

### Build Automation
- [ ] Version injection
- [ ] Changelog generation
- [ ] Checksum generation
- [ ] Code signing
- [ ] Asset upload

### Quality Gates
- [ ] Tests must pass
- [ ] Code coverage threshold
- [ ] Linting must pass
- [ ] Security scans
- [ ] Integration tests

### Release Automation
- [ ] Automatic version bump
- [ ] Release notes from commits
- [ ] Git tag creation
- [ ] GitHub release creation
- [ ] Asset upload

## Proposed Solution

### Solution 1: GitHub Actions CI/CD

Automated build pipeline:

```yaml
# .github/workflows/build.yml
name: Build and Release

on:
  push:
    tags:
      - 'v*.*.*'
  pull_request:
    branches: [main]

jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
        python-version: ['3.14']

    runs-on: ${{ matrix.os }}

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install uv
          uv sync

      - name: Run tests
        run: uv run pytest --cov

      - name: Build executable
        run: uv run python build/build_exe.py

      - name: Generate checksums
        run: sha256sum dist/wems.* > checksums.txt

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: wems-${{ matrix.os }}
          path: |
            dist/wems.*
            checksums.txt

  release:
    needs: build
    if: startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest

    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            wems-*/*.*
            checksums.txt
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Solution 2: Build Script

Consistent build script:

```python
# build/build_exe.py
import os
import sys
import subprocess
from pathlib import Path

def get_version():
    """Get version from git tags."""
    result = subprocess.run(
        ['git', 'describe', '--tags', '--always'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def build_executable(version, platform):
    """Build executable for platform."""
    cmd = [
        'pyinstaller',
        '--name', 'wems',
        '--windowed',
        '--onefile',
        f'--version={version}',
        f'--target-platform={platform}',
        '--icon', 'assets/icon.ico',
        '--add-data', 'src:src',
        '--hidden-import', 'customtkinter',
        '--hidden-import', 'peewee',
        '--hidden-import', 'openpyxl',
    ]
    subprocess.run(cmd, check=True)

def main():
    version = get_version()
    print(f"Building wems version {version}")

    # Run tests first
    subprocess.run(['pytest', '--cov'], check=True)

    # Build executable
    build_executable(version, sys.platform)

    # Generate checksums
    exe_path = Path('dist/wems.exe')
    checksum = hashlib.sha256(exe_path.read_bytes()).hexdigest()

    # Save checksum
    with open('dist/checksums.txt', 'w') as f:
        f.write(f"{checksum}  wems.exe\n")

    print(f"Build complete: {exe_path}")
    print(f"Checksum: {checksum}")

if __name__ == '__main__':
    main()
```

### Solution 3: Automated Versioning

Version from git tags:

```python
# src/__init__.py
__version__ = "2.0.0"  # Updated by CI/CD

# Build script injects version:
def inject_version(version):
    """Inject version into source files."""
    init_file = Path('src/__init__.py')
    content = init_file.read_text()
    content = content.replace(
        '__version__ = "2.0.0"',
        f'__version__ = "{version}"'
    )
    init_file.write_text(content)
```

### Solution 4: Changelog Generation

Automatic release notes:

```bash
# Use git commits to generate changelog
$ git log v1.2.0..v1.3.0 --oneline

abc1234 Fixed CACES expiration calculation
def5678 Added bulk Excel import
ghi8901 Improved performance
```

**GitHub Actions** can generate release notes automatically.

### Solution 5: Multi-Platform Builds

Build matrix:

```yaml
strategy:
  matrix:
    include:
      - os: windows-latest
        asset_name: wems-windows.exe
        platform: windows-x64
      - os: macos-latest
        asset_name: wems-macos
        platform: macos-universal
      - os: ubuntu-latest
        asset_name: wems-linux
        platform: linux-x64
```

## Implementation Plan

### Phase 1: Basic CI/CD (1 week)
1. Create `.github/workflows/build.yml`
2. Setup automated tests
3. Add build step
4. Generate artifacts

### Phase 2: Release Automation (1 week)
1. Automatic version injection
2. Changelog generation
3. GitHub release creation
4. Asset upload

### Phase 3: Multi-Platform (1 week)
1. Build matrix for Windows
2. Build matrix for macOS
3. Build matrix for Linux
4. Platform-specific optimizations

### Phase 4: Quality Gates (3 days)
1. Code coverage checks
2. Linting checks
3. Security scans
4. Integration tests

## Files to Create

- `.github/workflows/build.yml`
- `.github/workflows/test.yml`
- `build/build_exe.py`
- `build/inject_version.py`
- `build/generate_changelog.py`

## Files to Modify

- `src/__init__.py` - Support version injection
- `pyproject.toml` - Add build dependencies

## Dependencies to Add

```toml
[project.optional-dependencies]
build = [
    "pyinstaller>=6.0.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]
```

## Testing Requirements

- Test CI/CD triggers on push
- Test CI/CD triggers on tag
- Test multi-platform builds
- Test artifact generation
- Test GitHub release creation
- Test rollback on failure

## Benefits

### For Developers
- **Consistent**: Same build environment every time
- **Fast**: 10-minute releases vs 45-minute
- **Reliable**: Automated testing catches bugs
- **Easy**: Push tag, release created automatically

### For Users
- **Quick**: Bug fixes released faster
- **Complete**: All platforms, all assets
- **Verified**: Builds tested before release
- **Trust**: Checksums verify integrity

### For Quality
- **Gates**: Tests must pass
- **Coverage**: Minimum coverage enforced
- **Security**: Automated security scans
- **Consistency**: Reproducible builds

## Success Metrics

- [ ] Build time reduced from 45 minutes to 10 minutes
- [ ] Release failure rate < 1%
- [ ] All releases include all platforms
- [ ] All releases have checksums
- [ ] Zero manual build steps

## Related Issues

- #027: Application Requires Python Runtime Installation (CI/CD builds executables)
- #038: No Windows Installer (CI/CD creates installers)

## Priority

**HIGH** - Significantly improves release quality and speed

## Estimated Effort

3 weeks (basic CI/CD + release automation + multi-platform + quality gates)

## Mitigation

While waiting for CI/CD:
1. Document build process
2. Create build checklist
3. Use consistent build environment
4. Add pre-build testing steps
5. Double-check releases before publishing
