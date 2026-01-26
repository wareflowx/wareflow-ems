# [MEDIUM] No Automated Release Pipeline with Windows Executable

## Type
**Deployment / Distribution**

## Severity
**MEDIUM** - Blocks easy distribution to non-technical users, increases deployment friction

## Affected Components
- **Distribution** - No downloadable Windows executable
- **Release Process** - Manual and error-prone
- **GitHub Actions** - No CI/CD pipeline
- **User Experience** - Requires Python runtime installation

## Description

Wareflow EMS currently has no automated release pipeline. Distributing the application to end users requires manual steps and technical knowledge, creating significant barriers to adoption.

### Current Release Process

To create a release, developers must:
1. Update version number manually in multiple files
2. Create Git tag manually (`git tag v1.0.0 && git push --tags`)
3. Create GitHub release manually through web interface
4. Build Windows executable locally using PyInstaller (manual command)
5. Upload .exe to GitHub release manually
6. Test the downloaded executable
7. Create release notes manually

**Time required**: 1-2 hours per release
**Error-prone**: Manual steps can be missed or done incorrectly

### Real-World Impact

**Scenario 1: Bug Fix Release**
```
Day 1: Critical bug discovered in production
Day 1: Developer fixes bug (15 minutes)
Day 1: Developer needs to create release for users
        - Update version numbers (5 min)
        - Create Git tag (2 min)
        - Build .exe locally (10 min)
        - Create GitHub release (5 min)
        - Upload .exe (5 min)
        - Test .exe (10 min)
        Total: 37 minutes + 15 min dev = 52 minutes

Day 1: Users download .exe and install

Day 2: User reports issue - .exe doesn't work!
        Problem: Developer forgot to include data files in PyInstaller config
        Rollback: Panic, manual fix, rebuild (another 30 minutes)
```

**Scenario 2: Non-Technical User Wants to Try App**
```
User: "I want to try this employee management app"

Current requirements:
1. Install Python 3.14+ (confusing for non-devs)
2. Learn to use command line
3. Install Git (what is Git?)
4. Clone repository (what does clone mean?)
5. Install uv (another tool?)
6. Run uv sync (what is sync?)
7. Run python -m src.main

User gives up after step 1, uninstalls Python
```

**Scenario 3: Quarterly Feature Release**
```
Q1: New features developed (great!)
Q1: Time to release to users...

Developer tasks:
- Create tag v1.1.0
- Update CHANGELOG.md manually (30 min reviewing git log)
- Build .exe (10 min)
- Test .exe (10 min)
- Create GitHub release (10 min)
- Upload .exe (5 min)
- Write release email to users (15 min)
- Send release announcement

Total: 90 minutes of manual work
Risk: Forgot to update version in one file → users see wrong version
Risk: Uploaded wrong .exe → 50 users download broken version
Risk: No rollback plan → users stuck with broken version
```

## Problems Created

### 1. No Windows Executable Distribution
**Current limitation**: Users must install Python runtime
- Python 3.14 is not standard on Windows
- Installation requires 200+ MB download
- Installation requires admin privileges
- Installation modifies system PATH
- Confusing for non-technical users
- Many corporate IT policies forbid Python installation

**User friction**:
```
Non-technical HR manager wants to use app:
→ Downloads installer
→ "Wait, I need to install Python?"
→ Downloads Python installer
→ "Add to PATH? What's PATH?"
→ Checks "Add Python to PATH" (hopes it's right)
→ "Now what? uv sync?"
→ Gives up
```

### 2. Manual Release Process
**Current limitation**: All steps are manual and error-prone
- Version numbers in multiple files can get out of sync
- Easy to forget to update CHANGELOG
- Easy to upload wrong .exe
- No automated testing of .exe before release
- No rollback if bad release
- Human error inevitable

**Example errors**:
- Forgot to tag → users can't identify version
- Tagged but didn't push tag → no release created
- Created release but forgot .exe → users have nothing to download
- Uploaded debug .exe instead of release → 50x slower
- Forgot to update version in UI → users see "v0.0.1" when it's v1.0.0

### 3. No Continuous Integration/Continuous Deployment
**Current limitation**: No automated testing or building
- Every commit is not tested
- Bugs can slip into releases
- No confidence that release works
- Manual testing required
- Slow feedback loop

**Impact**:
```
Developer: Pushes bug fix
Week later: Time to release
Developer: Creates release
        - Builds .exe
        - Tests manually (10 min)
        - Discovers: Tests fail! Fix introduced bug
Developer: Fixes bug, rebuilds, retests (another 20 min)
Developer: Finally releases

Total time: 30 minutes wasted on manual testing
```

### 4. No Automated Release Notes
**Current limitation**: CHANGELOG must be written manually
- Developer must review git log
- Developer must categorize commits (feat/fix/docs/etc)
- Developer must write user-friendly descriptions
- Easy to miss important changes
- Easy to forget to update

**Quality impact**:
- Inconsistent release notes
- Important changes not mentioned
- Users don't know what's new
- Users don't know if they should upgrade

### 5. Windows SmartScreen Warnings
**Current limitation**: Unsigned .exe triggers security warnings
- Windows SmartScreen blocks unsigned executables
- Users see scary warning: "Windows protected your PC"
- Users must click "More info" → "Run anyway"
- Reduces trust in application
- Some users won't run it at all

**User experience**:
```
User: Downloads wems-1.0.0.exe
User: Double-clicks to run
Windows: 🛑 "Windows protected your PC"
        "SmartScreen prevented an unrecognized app from starting"
        "Running this app might put your PC at risk"

User: Panic! Is this a virus?
User: Sees "More info" link
User: Clicks it
User: Sees "Run anyway" button
User: Hesitates... should I trust this?
User: Closes app, uninstalls
```

## Missing Features

### Build Automation
- [ ] GitHub Actions workflow for automated builds
- [ ] Trigger build on Git tag push
- [ ] Automated PyInstaller execution
- [ ] Automated artifact generation
- [ ] Automated GitHub release creation

### Testing Automation
- [ ] Automated tests run on every commit
- [ ] Tests run before release
- [ ] Release blocked if tests fail
- [ ] Automated smoke tests of .exe

### Release Automation
- [ ] Automatic version number extraction
- [ ] Automatic CHANGELOG generation
- [ ] Automatic GitHub release creation
- [ ] Automatic .exe attachment to release
- [ ] Automatic release notes from commits

### Code Signing
- [ ] Code signing certificate
- [ ] Signed Windows executable
- [ ] No SmartScreen warnings
- [ ] Professional appearance

### Distribution
- [ ] Windows .exe (one-file or one-dir)
- [ ] Optional: macOS .app bundle
- [ ] Optional: Linux AppImage
- [ ] Automatic upload to GitHub Releases
- [ ] Update notification in-app

## Proposed Solution

### Solution 1: GitHub Actions CI/CD Pipeline

Implement complete automated release pipeline:

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: windows-latest
    steps:
      - Checkout code
      - Setup Python
      - Install dependencies
      - Run tests
      - Build Windows .exe with PyInstaller
      - Create GitHub Release
      - Upload .exe artifact
```

**Workflow**:
1. Developer creates Git tag: `git tag v1.0.0 && git push --tags`
2. GitHub Actions detects tag push
3. Actions runs automated tests
4. If tests pass, builds .exe with PyInstaller
5. Actions creates GitHub release automatically
6. Actions uploads .exe to release
7. Actions generates release notes from commits
8. Users download .exe from GitHub Releases page

**Benefits**:
- Release time: 30 seconds (git push) instead of 1-2 hours
- No manual steps
- No human error
- Tests always run before release
- Consistent releases every time
- Rollback easy (just tag previous version)

### Solution 2: PyInstaller Configuration

Create `wareflow-ems.spec` for Windows executable:

```python
# wems.spec
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui_ctk/assets', 'ui_ctk/assets'),
        ('src/excel_import/templates', 'excel_import/templates'),
    ],
    hiddenimports=[
        'customtkinter',
        'peewee',
        'PIL',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tests', 'pytest'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Wareflow EMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/ui_ctk/assets/icon.ico',  # Optional app icon
)
```

**Configuration options**:
- **One-file mode**: Single .exe (~100 MB)
  - Pros: Single file to download
  - Cons: Slower startup (must unpack)

- **One-dir mode**: Folder with .exe + dependencies (~50 MB)
  - Pros: Faster startup
  - Cons: Multiple files, must zip for distribution

**Recommendation**: Start with one-file for simplicity

### Solution 3: Automated Version Management

Centralized version definition and extraction:

```toml
# pyproject.toml
[project]
name = "wareflow-ems"
version = "1.0.0"  # Single source of truth
```

```python
# src/version.py (auto-generated from pyproject.toml)
__version__ = "1.0.0"
```

```yaml
# .github/workflows/release.yml
- name: Extract version
  run: |
    VERSION=$(echo '${{ github.ref }}' | sed -n 's|refs/tags/v||p')
    echo "VERSION=$VERSION" >> $GITHUB_ENV

- name: Build
  run: |
    python build.py --version $VERSION
```

**Benefits**:
- Version defined in one place
- Version extracted automatically from Git tag
- No manual version updates
- No version mismatches

### Solution 4: Automated CHANGELOG Generation

Use conventional commits with automatic changelog:

```
feat: add employee search feature
fix: correct CACES expiration calculation
docs: update installation instructions
```

GitHub Actions generates release notes:
```markdown
## What's Changed

* ✨ New employee search feature by @author
* 🐛 Fix CACES expiration calculation by @author
* 📝 Update installation docs by @author

**Full Changelog**: https://github.com/wareflowx/wareflow-ems/compare/v0.9.0...v1.0.0
```

**Tools**:
- GitHub Release Notes Generator (built-in)
- Or: release-drafter GitHub Action
- Or: conventional-changelog tool

### Solution 5: Code Signing (Optional, Recommended)

Sign Windows executable to avoid SmartScreen warnings:

1. **Purchase code signing certificate** (~$100-500/year)
   - DigiCert
   - Sectigo
   - GlobalSign

2. **Configure GitHub Actions**:

```yaml
- name: Sign executable
  run: |
    signtool sign /f certificate.pfx /p "${{ secrets.CERT_PASSWORD }}" wems.exe
  env:
    CERT_PASSWORD: ${{ secrets.CERTIFICATE_PASSWORD }}
```

3. **Benefits**:
   - No SmartScreen warnings
   - Professional appearance
   - Increased user trust
   - Verified publisher in file properties

**Alternative (free but less effective)**:
- Use Windows SmartScreen Application Reputation
- Build exe on many fresh Windows VMs
- Over time, SmartScreen learns to trust it

## Implementation Plan

### Phase 1: Basic GitHub Actions (1 day)
1. Create `.github/workflows/test.yml`
   - Run tests on every push
   - Run tests on every PR
   - Block merge if tests fail

2. Create `.github/workflows/release.yml`
   - Trigger on Git tag push
   - Setup Python environment
   - Install dependencies
   - Run tests
   - Block release if tests fail

### Phase 2: PyInstaller Build (2 days)
1. Create `wareflow-ems.spec` file
2. Configure PyInstaller settings
   - Entry point: src/main.py
   - Include data files
   - Hidden imports
   - Icon (optional)
3. Test build locally
   - Run `pyinstaller wems.spec`
   - Test generated .exe
   - Fix missing imports
4. Add PyInstaller to dependencies
5. Add build step to GitHub Actions

### Phase 3: Release Automation (1 day)
1. Update GitHub Actions workflow
   - Extract version from Git tag
   - Build .exe
   - Create GitHub release
   - Upload .exe artifact
2. Test end-to-end
   - Create test tag
   - Verify Actions runs
   - Verify .exe builds
   - Verify release created
   - Verify .exe downloadable
3. Document release process

### Phase 4: Automated Release Notes (1 day)
1. Enforce conventional commits
2. Configure GitHub Release Notes generator
3. Test automatic changelog generation
4. Customize release notes template
5. Document commit conventions

### Phase 5: Code Signing (Optional, 1 day)
1. Purchase code signing certificate
2. Store certificate in GitHub Secrets
3. Configure signing step in GitHub Actions
4. Test signed executable
5. Verify no SmartScreen warnings

## Files to Create

- `.github/workflows/test.yml` - CI pipeline for tests
- `.github/workflows/release.yml` - CD pipeline for releases
- `wareflow-ems.spec` - PyInstaller configuration
- `build.py` - Optional local build script
- `.github/release-templates/release.md` - Release notes template
- `src/ui_ctk/assets/icon.ico` - Application icon (optional)

## Files to Modify

- `pyproject.toml` - Add PyInstaller dependency
- `src/main.py` - Ensure proper entry point for PyInstaller
- `src/version.py` - Centralize version definition
- `.gitignore` - Ignore build artifacts
- `README.md` - Add download link to Releases page
- `CONTRIBUTING.md` - Document release process

## Dependencies to Add

```toml
[project.dependencies]
"pyinstaller>=6.0.0"  # Windows executable building

[project.optional-dependencies]
build = [
    "pyinstaller>=6.0.0",
]
```

## Testing Requirements

### Test PyInstaller Build Locally
- [ ] Build .exe with `pyinstaller wems.spec`
- [ ] Run .exe on Windows 10
- [ ] Run .exe on Windows 11
- [ ] Verify all features work
- [ ] Verify no missing files
- [ ] Verify no import errors

### Test GitHub Actions
- [ ] Push test tag (v0.0.0-test)
- [ ] Verify Actions workflow triggers
- [ ] Verify tests run and pass
- [ ] Verify .exe builds successfully
- [ ] Verify release created
- [ ] Verify .exe attached to release
- [ ] Download and test .exe from release

### Test Release Process
- [ ] Create real release tag (v1.0.0)
- [ ] Verify all automated steps
- [ ] Verify release notes generated
- [ ] Verify users can download .exe
- [ ] Verify .exe runs without issues

### Test Code Signing (Optional)
- [ ] Verify signed .exe
- [ ] Verify publisher information shown
- [ ] Verify no SmartScreen warnings
- [ ] Verify certificate valid

## User Benefits

### For End Users
- **Simplicity**: Download .exe and run, no Python needed
- **Speed**: 5 minutes to try app vs 30+ minutes installing Python
- **Confidence**: Official tested release, not random code
- **Trust**: Signed executable, verified publisher
- **Updates**: Clear version numbers and release notes

### For Developers
- **Efficiency**: Release in 30 seconds vs 1-2 hours
- **Consistency**: Automated process, no human error
- **Quality**: Tests always run before release
- **Confidence**: Know release will work
- **Time**: Focus on development, not release mechanics

### For Project
- **Professional**: Proper CI/CD pipeline
- **Reliable**: Automated testing prevents bugs
- **Scalable**: Easy to release frequently
- **Discoverable**: Releases page on GitHub
- **Trusted**: Signed executables, verified publisher

## Success Metrics

- [ ] Release time reduced from 1-2 hours to 30 seconds
- [ ] 100% of releases tested before publication
- [ ] Zero manual steps in release process
- [ ] Zero version mismatch errors
- [ ] Zero missing file errors
- [ ] 90% reduction in support requests related to installation
- [ ] User satisfaction with install process > 4.5/5

## Related Issues

- #027: Requires Python Runtime Installation (solved by .exe distribution)
- #038: SmartScreen Blocks Unsigned Executable (solved by code signing)
- #043: No Structured Release Process (solved by CI/CD pipeline)

## Priority

**MEDIUM** - Important for user adoption and distribution, but app is usable without it

## Estimated Effort

3-5 days (basic pipeline + build + automation, optional code signing +1 day)

## Mitigation

While waiting for automated release pipeline:
1. Document manual release process thoroughly
2. Create release checklist document
3. Use build scripts to reduce manual steps
4. Test releases thoroughly before publishing
5. Provide detailed installation instructions for non-technical users
6. Consider offering pre-built .exe on request (manual build)

## Example Workflow (After Implementation)

```bash
# Developer finishes feature
git add .
git commit -m "feat: add dark mode support"
git push origin main

# Time to release!
git tag v1.1.0
git push --tags

# That's it! GitHub Actions does the rest:
# 1. Runs tests ✓
# 2. Builds .exe ✓
# 3. Creates release ✓
# 4. Uploads .exe ✓
# 5. Generates release notes ✓

# 5 minutes later, users download v1.1.0 from:
# https://github.com/wareflowx/wareflow-ems/releases
```
