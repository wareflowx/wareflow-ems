# ISSUE-056: Aggressive Path Sanitization

## Description

The path sanitization in `src/utils/file_validation.py` is overly aggressive, removing all path separators (`/` and `\`). This results in flat filenames and can cause file collisions when different files have the same name but different paths.

## Affected Files

- **`src/utils/file_validation.py:182-190`** - Path sanitization logic

## Current State

```python
# src/utils/file_validation.py:182-190
def sanitize_file_path(file_path: str) -> str:
    """Sanitize file path to prevent path traversal attacks."""
    sanitized = file_path.replace("..", "").replace("\\", "").replace("/", "")
    return sanitized
```

### Problems

1. **Removes All Path Separators:** All `/` and `\` characters are removed
2. **Causes File Collisions:** Different files map to same filename
3. **Loses Directory Structure:** Cannot preserve subdirectories
4. **Breaks Legitimate Paths:** Valid paths with subdirectories break

### Example of the Problem

```python
sanitize_file_path("documents/2024/report.pdf")
# Returns: "documents2024report.pdf"

sanitize_file_path("documents/2023/report.pdf")
# Returns: "documents2023report.pdf"

sanitize_file_path("reports/report.pdf")
# Returns: "reportsreport.pdf"
```

All three files would collide if stored in same directory!

## Expected Behavior

Path sanitization should:
1. **Prevent path traversal** (block `../` and absolute paths)
2. **Preserve safe directory structure**
3. **Maintain file organization**
4. **Prevent file name collisions**

## Proposed Solution

### Phase 1: Implement Safe Path Sanitization (1 day)

```python
# src/utils/file_validation.py
from pathlib import Path
import re

def sanitize_file_path(file_path: str, base_dir: str = None) -> str:
    """
    Sanitize file path to prevent path traversal while preserving directory structure.

    Args:
        file_path: File path to sanitize
        base_dir: Base directory for relative paths (optional)

    Returns:
        Sanitized, safe file path relative to base_dir

    Raises:
        ValueError: If path is unsafe (traversal attempt)
    """
    # Convert to Path object
    path = Path(file_path)

    # If base_dir provided, resolve relative to it
    if base_dir:
        base = Path(base_dir).resolve()
        try:
            # Resolve the full path
            full_path = (base / path).resolve()

            # Check if result is within base_dir (prevent traversal)
            if not str(full_path).startswith(str(base)):
                raise ValueError(
                    f"Path traversal detected: {file_path} attempts to access "
                    f"files outside base directory"
                )

            # Return relative path from base_dir
            return full_path.relative_to(base)

    else:
        # Without base_dir, just check for traversal attempts
        # Convert to absolute path to detect traversal
        try:
            resolved = path.resolve()
        except:
            # If resolution fails, path is invalid
            raise ValueError(f"Invalid file path: {file_path}")

        # Check for suspicious patterns
        if ".." in file_path or file_path.startswith(("/", "\\")):
            raise ValueError(
                f"Unsafe path detected: {file_path} contains absolute "
                f"path or traversal patterns"
            )

        return path
```

### Phase 2: Add File Collision Detection (1 day)

```python
def generate_safe_filename(file_path: str, base_dir: str) -> str:
    """
    Generate a safe filename that avoids collisions.

    Args:
        file_path: Original file path
        base_dir: Base directory for storage

    Returns:
        Safe filename path, adding numeric suffix if collision exists
    """
    sanitized = sanitize_file_path(file_path, base_dir)
    full_path = Path(base_dir) / sanitized

    # If file doesn't exist, return as-is
    if not full_path.exists():
        return str(sanitized)

    # Add numeric suffix to avoid collision
    counter = 1
    stem = sanitized.stem
    suffix = sanitized.suffix
    parent = sanitized.parent

    while True:
        new_name = parent / f"{stem}_{counter}{suffix}"
        full_path = Path(base_dir) / new_name

        if not full_path.exists():
            return str(new_name)

        counter += 1

        # Safety limit
        if counter > 1000:
            raise ValueError(
                f"Cannot generate unique filename: {sanitized} "
                f"(too many collisions)"
            )
```

### Phase 3: Add Path Validation Tests (1 day)

```python
# tests/test_utils/test_file_validation.py
import pytest
from utils.file_validation import sanitize_file_path, generate_safe_filename

def test_sanitization_prevents_traversal():
    """Test that path traversal is prevented."""
    with pytest.raises(ValueError, match="traversal"):
        sanitize_file_path("../../etc/passwd", "/safe/base")

    with pytest.raises(ValueError, match="traversal"):
        sanitize_file_path("./../../../secrets.txt", "/safe/base")

def test_sanitization_preserves_structure():
    """Test that safe directory structure is preserved."""
    result = sanitize_file_path("documents/2024/report.pdf", "/safe/base")
    assert result == Path("documents/2024/report.pdf")

def test_sanitization_blocks_absolute_paths():
    """Test that absolute paths are blocked."""
    with pytest.raises(ValueError, match="Unsafe path"):
        sanitize_file_path("/etc/passwd")

def test_collision_detection():
    """Test that file collisions are handled."""
    # Create test file
    base = Path("/tmp/test_collision")
    base.mkdir(exist_ok=True)
    (base / "test.txt").write_text("existing")

    result = generate_safe_filename("test.txt", str(base))
    assert result == "test_1.txt"

    # Cleanup
    (base / "test.txt").unlink()
    base.rmdir()
```

## Implementation Strategy

1. **Phase 1:** Implement safe path sanitization
2. **Phase 2:** Add collision detection
3. **Phase 3:** Add comprehensive tests
4. **Phase 4:** Update all callers of the function
5. **Phase 5:** Integration testing

## Security Considerations

### Path Traversal Prevention

The new implementation prevents path traversal by:
1. Resolving the full path
2. Checking if the result is within the base directory
3. Rejecting paths with `..` or absolute paths (when no base_dir)

### Attack Scenarios Prevented

```python
# Attempt to access system files
sanitize_file_path("../../../Windows/System32/config/SAM", "C:/app/data")
# Raises: ValueError

# Attempt to overwrite application files
sanitize_file_path("../../src/main.py", "C:/app/data")
# Raises: ValueError

# Attempt absolute path escape
sanitize_file_path("/etc/passwd", "/app/data")
# Raises: ValueError
```

## Dependencies

- None - uses only Python standard library

## Related Issues

- ISSUE-001: Path Traversal Vulnerability (historical)
- ISSUE-064: File Upload and Storage

## Acceptance Criteria

- [ ] Path traversal attacks prevented
- [ ] Safe directory structure preserved
- [ ] File collisions handled gracefully
- [ ] Absolute paths blocked
- [ ] Relative paths work correctly
- [ ] Comprehensive tests added
- [ ] All existing tests pass
- [ ] Security review completed
- [ ] Code review approved

## Estimated Effort

**Total:** 2-3 days
- Implement safe sanitization: 1 day
- Add collision detection: 1 day
- Add comprehensive tests: 1 day
- Update callers and integration testing: 0.5 day

## Notes

This is a security issue that should be fixed carefully. The current implementation is "secure" in that it prevents path traversal, but it breaks legitimate use cases. The new implementation maintains security while preserving functionality.

## Migration Guide

For existing code using the old function:

```python
# Old code
safe_path = sanitize_file_path(user_input)

# New code
safe_path = sanitize_file_path(user_input, base_dir="/app/data/uploads")
```

All callers need to provide a `base_dir` parameter for proper security.

## References

- OWASP Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal
- Python pathlib documentation: https://docs.python.org/3/library/pathlib.html
- Secure file upload handling: https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload
