# ISSUE-055: Weak Email Address Validation

## Description

The email address validation regex is too basic and doesn't properly validate TLD length or format. This could allow invalid email formats to bypass validation and be stored in the database.

## Affected Files

- **`src/utils/validation.py:183`** - Email validation logic

## Current State

```python
# src/utils/validation.py:183
email_pattern = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
```

### Problems

1. **TLD Validation Too Loose:** Accepts any TLD with 2+ characters, but doesn't validate against actual TLDs
2. **No International Support:** Doesn't support internationalized domain names (IDN)
3. **Missing Edge Cases:** Doesn't handle edge cases properly
4. **RFC 5322 Compliance:** Not fully compliant with email RFC

### Examples of Invalid Emails That Pass Validation

- `user@domain.abcdefg` - Invalid TLD
- `user@domain..com` - Double dots
- `user@.com` - Missing domain name
- `@domain.com` - Missing local part

## Expected Behavior

Email validation should:
1. Validate basic email format (local@domain.tld)
2. Validate TLD length (2-63 characters per RFC 1035)
3. Support international characters
4. Validate against common TLDs
5. Be RFC 5322 compliant (or close to it)

## Proposed Solution

### Option 1: Use `email-validator` Library (Recommended)

Add dependency and use a well-tested library:

```toml
# pyproject.toml
dependencies = [
    "email-validator>=2.0.0",
]
```

```python
# src/utils/validation.py
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email: str) -> tuple[bool, str]:
    """
    Validate email address using email-validator library.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return True, ""  # Optional field

    try:
        # Validate and normalize email
        valid = validate_email(email, check_deliverability=False)

        # Return normalized form
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)
```

**Benefits:**
- Well-tested and maintained
- RFC 5322 compliant
- Supports internationalized emails
- Validates TLD against IANA registry
- Handles edge cases properly
- Active development and updates

### Option 2: Enhanced Regex (Not Recommended)

If library cannot be used, enhance the regex:

```python
def validate_email_address(email: str) -> tuple[bool, str]:
    """Validate email address with enhanced regex."""
    if not email:
        return True, ""  # Optional field

    # Basic format validation
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+\-]+'  # Local part
        r'@'  # @ symbol
        r'[a-zA-Z0-9.\-]+'  # Domain
        r'\.[a-zA-Z]{2,63}$'  # TLD (2-63 chars)
    )

    if not email_pattern.match(email):
        return False, "Invalid email format"

    # Additional checks
    if '..' in email:
        return False, "Email cannot contain consecutive dots"

    if email.startswith('.') or email.startswith('@'):
        return False, "Email cannot start with . or @"

    if email.endswith('.') or email.endswith('@'):
        return False, "Email cannot end with . or @"

    # Check domain has at least one dot
    if email.count('@') != 1:
        return False, "Email must contain exactly one @ symbol"

    local, domain = email.split('@')
    if not local or not domain:
        return False, "Email local and domain parts required"

    if '.' not in domain:
        return False, "Email domain must contain at least one dot"

    return True, ""
```

**Note:** This is still not RFC 5322 compliant and may have edge cases.

### Option 3: Hybrid Approach

Use library for validation, but keep regex as fast pre-check:

```python
def validate_email_address(email: str) -> tuple[bool, str]:
    """Validate email address with hybrid approach."""
    if not email:
        return True, ""  # Optional field

    # Fast pre-check with regex
    quick_pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
    if not quick_pattern.match(email):
        return False, "Invalid email format"

    # Detailed validation with library
    try:
        valid = validate_email(email, check_deliverability=False)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)
```

## Implementation Steps

### Phase 1: Add Dependency (1 hour)

1. Add `email-validator>=2.0.0` to `pyproject.toml`
2. Run `uv sync`
3. Test import

### Phase 2: Update Validation Function (2 hours)

1. Update `src/utils/validation.py`
2. Replace regex with library call
3. Add comprehensive error messages
4. Handle optional field case

### Phase 3: Update Tests (2 hours)

1. Add unit tests for valid emails
2. Add unit tests for invalid emails
3. Test edge cases
4. Test international emails

## Test Cases

### Valid Emails (Should Pass)
- `test@example.com`
- `user.name@example.com`
- `user+tag@example.com`
- `user@subdomain.example.com`
- `user@example.co.uk`
- `user@example.fr`
- `tëst@example.com` (international)

### Invalid Emails (Should Fail)
- `plainaddress` (no @)
- `@example.com` (no local part)
- `user@` (no domain)
- `user@.com` (no domain name)
- `user@domain..com` (consecutive dots)
- `user@domain.abcdefg` (invalid TLD)
- `user@domain.c` (TLD too short)

## Dependencies

- **New dependency:** `email-validator>=2.0.0`

## Related Issues

- ISSUE-051: Missing Contact Information Fields
- ISSUE-067: Weak Phone Number Validation

## Acceptance Criteria

- [ ] email-validator dependency added
- [ ] validate_email_address() function updated
- [ ] Invalid emails rejected
- [ ] Valid emails accepted
- [ ] International emails supported
- [ ] Proper error messages returned
- [ ] Unit tests added
- [ ] All tests pass
- [ ] Code review approved

## Estimated Effort

**Total:** 1 day
- Add dependency and tests: 2 hours
- Update validation function: 2 hours
- Update related code: 2 hours
- Testing and validation: 2 hours

## Notes

Email validation is important for data quality, but don't over-validate. The goal is to catch obvious typos and invalid formats, not to verify deliverability. The `email-validator` library with `check_deliverability=False` is the recommended approach.

## Security Considerations

- Email validation is NOT a security measure
- Validating email format doesn't prevent injection attacks
- Always sanitize and escape email addresses in output
- Never use email addresses directly in SQL queries (use parameterized queries)

## References

- email-validator documentation: https://pypi.org/project/email-validator/
- RFC 5322 (Internet Message Format): https://tools.ietf.org/html/rfc5322
- RFC 5321 (SMTP): https://tools.ietf.org/html/rfc5321
- Email address validation best practices: https://emailregex.com/
