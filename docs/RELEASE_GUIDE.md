# Release Guide for Wareflow EMS

This guide explains how to create automated releases of Wareflow EMS with Windows executables.

## Quick Start

Creating a release is now automated and takes just 30 seconds:

```bash
# 1. Make sure your changes are committed and pushed
git add .
git commit -m "feat: add new feature"
git push origin main

# 2. Create and push a version tag
git tag v1.0.0
git push --tags

# That's it! GitHub Actions will:
# - Run tests
# - Build Windows .exe
# - Create GitHub release
# - Upload executable
```

## Version Numbering

Wareflow EMS uses [Semantic Versioning](https://semver.org/):

- **Major version** (X.0.0): Breaking changes
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

Examples:
- `v1.0.0` - First stable release
- `v1.1.0` - Added new feature
- `v1.1.1` - Bug fix
- `v2.0.0` - Breaking changes

## Automated Release Process

When you push a version tag (e.g., `v1.0.0`), GitHub Actions automatically:

1. **Runs Tests**
   - Executes pytest test suite
   - Ensures code quality
   - Blocks release if tests fail

2. **Builds Windows Executable**
   - Uses PyInstaller with `wareflow-ems.spec`
   - Creates single .exe file (~100 MB)
   - Includes all dependencies
   - Bundles application icon

3. **Creates GitHub Release**
   - Generates release notes
   - Attaches .exe file
   - Includes SHA256 checksum
   - Marks as latest release

4. **Uploads Artifacts**
   - Stores .exe for 90 days
   - Provides download link
   - Shows file size and checksum

## Local Build Testing

Before creating an official release, you can test the build locally:

### Prerequisites

```bash
# Install build dependencies
uv sync --extra build
```

### Build Executable

```bash
# Using the build script (recommended)
python scripts/build.py

# Or using PyInstaller directly
pyinstaller wareflow-ems.spec --clean --noconfirm
```

The executable will be created at: `dist/Wareflow EMS.exe`

### Test the Executable

```bash
# Run the built executable
./dist/Wareflow\ EMS.exe

# Or from Windows Explorer
# Navigate to dist/ folder and double-click Wareflow EMS.exe
```

## Release Checklist

Before creating a release, ensure:

- [ ] All changes are committed to `main` branch
- [ ] Tests pass locally: `uv run pytest tests/`
- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG.md updated with changes
- [ ] Tested local build successfully
- [ ] No critical bugs outstanding

## Creating a Release Step-by-Step

### 1. Update Version

Edit `pyproject.toml`:

```toml
[project]
version = "1.0.0"  # Update this
```

### 2. Update CHANGELOG

Edit `CHANGELOG.md`:

```markdown
## [1.0.0] - 2025-01-26

### Added
- New feature A
- New feature B

### Fixed
- Bug fix C
- Bug fix D

### Changed
- Improvement E
```

### 3. Commit and Push

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v1.0.0"
git push origin main
```

### 4. Create Tag

```bash
git tag v1.0.0
git push --tags
```

### 5. Monitor Build

Go to: https://github.com/wareflowx/wareflow-ems/actions

Wait for the "Release" workflow to complete (typically 5-10 minutes).

### 6. Verify Release

Go to: https://github.com/wareflowx/wareflow-ems/releases

Verify:
- Release created with correct version
- .exe file attached
- File size is reasonable (~100 MB)
- Release notes are correct
- SHA256 checksum provided

### 7. Test Download

Download the .exe and test on a clean Windows system:

```bash
# Install and run
# Verify no errors
# Check all features work
# Confirm database creation
```

## Troubleshooting

### Build Failures

**Problem**: PyInstaller build fails

**Solutions**:
```bash
# Clean build artifacts
rm -rf build/ dist/

# Try building with verbose output
pyinstaller wareflow-ems.spec --clean --noconfirm --log-level DEBUG

# Check for missing imports
# Add to hiddenimports in wareflow-ems.spec if needed
```

### Large File Size

**Problem**: .exe is too large (> 200 MB)

**Solutions**:
- Check `upx=True` is enabled in spec
- Exclude unnecessary modules
- Use `--exclude-module` for unused packages
- Optimize imports

### Missing Dependencies

**Problem**: .exe crashes on startup

**Solutions**:
```bash
# Test with console to see errors
# Change console=True in wareflow-ems.spec temporarily

# Check hiddenimports in spec
# Add missing modules
```

### GitHub Actions Timeout

**Problem**: Build times out on GitHub

**Solutions**:
- Check .yml timeout setting
- Optimize test suite speed
- Reduce dependencies
- Check GitHub Actions status page

## Release Notes Template

```
## Wareflow EMS {VERSION}

### 🎉 Highlights
- Main feature or improvement

### ✨ New Features
- Feature A
- Feature B

### 🐛 Bug Fixes
- Fix C
- Fix D

### 🔧 Improvements
- Improvement E
- Improvement F

### 📝 Documentation
- Doc update G

### 🚀 Performance
- Performance improvement H

### 📦 Installation
Windows: Download `Wareflow-EMS-{VERSION}.exe` below
- No Python installation required
- All dependencies bundled
- SHA256 checksum provided

### 🖥️ System Requirements
- Windows 10 or later
- 100 MB free disk space
- No additional dependencies

---

**Full Changelog**: https://github.com/wareflowx/wareflow-ems/compare/v{PREVIOUS}...v{VERSION}
```

## Automated Changelog Generation

For automatic changelog from commits:

```bash
# Install git-changelog
pip install git-changelog

# Generate changelog
git-changelog > CHANGELOG.md
```

Commit messages should follow conventions:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements

## Security Considerations

### Code Signing

The current build does not include code signing. This means:
- Windows may show SmartScreen warning
- Users must click "Run anyway"

To enable code signing (optional):
1. Purchase code signing certificate (~$100-500/year)
2. Add certificate to GitHub Secrets
3. Update `.github/workflows/release.yml` to sign .exe

### Checksum Verification

Users can verify the downloaded .exe:

**Windows PowerShell**:
```powershell
certutil -hashfile Wareflow-EMS-1.0.0.exe SHA256
```

**Linux/Mac**:
```bash
shasum -a 256 Wareflow-EMS-1.0.0.exe
```

Compare the output with the provided `.exe.sha256` file.

## Release Rollback

If a critical issue is discovered:

1. **Delete the release** (from GitHub releases page)
2. **Delete the tag**:
   ```bash
   git tag -d v1.0.0
   git push --delete origin v1.0.0
   ```
3. **Fix the issue** and create new tag (e.g., `v1.0.1`)
4. **Document the rollback** in CHANGELOG

## Best Practices

1. **Test thoroughly** before releasing
2. **Use semantic versioning** consistently
3. **Update CHANGELOG** with every release
4. **Monitor GitHub Actions** for build failures
5. **Test download** on clean Windows system
6. **Keep releases backward compatible** when possible
7. **Document breaking changes** clearly
8. **Tag releases** in git for easy rollback

## Advanced Topics

### Beta Releases

For pre-release testing:

```bash
git tag v1.1.0-beta.1
git push --tags
```

The workflow will still create a release, but users will know it's a beta.

### Hotfix Releases

For critical bug fixes:

```bash
# Create hotfix branch from tag
git checkout -b hotfix/v1.0.1 v1.0.0

# Make fix
git commit -m "fix: critical bug"

# Create hotfix tag
git tag v1.0.1
git push --tags
```

### Automated Releases from Main

For continuous releases from main branch:
1. Remove `tags` trigger from `.github/workflows/release.yml`
2. Add `push: branches: [main]` trigger
3. Auto-increment version on each push

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Semantic Versioning](https://semver.org/)
- [Release Drifter GitHub Action](https://github.com/release-drafter/release-drafter)

## Support

If you encounter issues:

1. Check GitHub Actions logs
2. Review this guide's troubleshooting section
3. Search existing GitHub issues
4. Create new issue with details

---

**Happy releasing!** 🚀
