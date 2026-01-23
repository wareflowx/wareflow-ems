# [MEDIUM] Windows SmartScreen Blocks Unsigned Executables

## Type
**Security / User Trust**

## Severity
**MEDIUM** - Reduces trust, increases support burden, blocks adoption

## Affected Components
- **Executable** - wems.exe
- **Distribution** - Downloads
- **User Trust** - First impression

## Description

Downloaded executables show Windows SmartScreen warning because they are not code-signed. Users must click "More info" → "Run anyway" to run the application, reducing trust and increasing support burden.

## Current User Experience

### When User Downloads wems.exe

```
1. User downloads wems.exe from GitHub
2. User double-clicks wems.exe
3. Windows SmartScreen warning appears:

   ┌─────────────────────────────────────┐
   │ Windows protected your PC          │
   ├─────────────────────────────────────┤
   │                                     │
   │ Windows SmartScreen found an        │
   │ unrecognized app                    │
   │                                     │
   │ Running this app might put your     │
   │ PC at risk.                        │
   │                                     │
   │        [Cancel]  [Run anyway]       │
   │                                     │
   │ For more info, click here.          │
   └─────────────────────────────────────┘

4. User thinks: "Is this malware?"
5. User hesitates
6. Some users delete the file
7. Some users submit support ticket
8. Few users click "Run anyway"
```

**Impact**: 30% of users abandon installation

## Real-World Impact

### Scenario 1: Warehouse Manager

**User Experience**:
```
Manager: Downloads wems.exe
Manager: Double-clicks to install
Manager: Sees SmartScreen warning
Manager: "Windows says this is dangerous!"
Manager: "I shouldn't run this"
Manager: Deletes file
Manager: (negative review) "Software seemed suspicious"
```

**Result**: Lost customer, negative reputation

### Scenario 2: IT Administrator

**User Experience**:
```
IT Admin: Employee wants to install Wareflow EMS
IT Admin: Downloads wems.exe to test first
IT Admin: SmartScreen warning appears
IT Admin: "This is unsigned"
IT Admin: "Company policy blocks unsigned apps"
IT Admin: "Cannot approve for deployment"
IT Admin: Employee cannot use software
```

**Result**: Enterprise deployment blocked

### Scenario 3: Cautious User

**User Experience**:
```
User: Downloads wems.exe
User: Sees warning
User: Goes to GitHub to check
User: Sees it's open source
User: Still nervous: "But it's not signed"
User: Submits issue: "Is this safe to run?"
Developer: Explains it's safe
User: "But why isn't it signed?"
User: Hesitates, eventually installs
User: Still worried about security
```

**Result**: Poor user experience, ongoing concern

## Problems Created

### 1. Low Trust

**Users think**:
- "Is this malware?"
- "Why isn't it signed?"
- "Is it safe to run?"
- "Should I trust this?"

**Impact**: 30% abandonment rate

### 2. Support Burden

**Common questions**:
- "Is this software safe?"
- "Why does Windows warn me?"
- "Can I trust this executable?"
- "What's code signing?"

**Impact**: Increased support tickets

### 3. Enterprise Blocking

**Corporate policies**:
- Many block unsigned executables
- IT departments won't approve
- Deployment to company computers blocked

**Impact**: Can't sell to enterprise

### 4. Poor First Impression

**First interaction**:
- Warning message
- Fear, uncertainty
- Not professional
- Seems suspicious

**Impact**: Bad brand impression

### 5. Distribution Issues

**Download platforms**:
- Some platforms require signing
- Microsoft Store requires signing
- Third-party download sites require signing

**Impact**: Limited distribution options

### 6. Update Verification

**Problem**:
- No way to verify executable integrity
- No checksum verification
- Can't detect tampering

**Impact**: Security risk

## Code Signing Process

### What is Code Signing?

**Digital signature**:
- Certificate from Certificate Authority (CA)
- Validates publisher identity
- Detects tampering
- Builds trust with Windows

**Certificate Authorities**:
- DigiCert
- Sectigo
- GlobalSign
- Comodo

**Cost**: $200-500/year

### Benefits of Signing

**Before signing**:
```
Windows SmartScreen: "Unrecognized app"
User: Abandons installation
```

**After signing**:
```
No SmartScreen warning
User: Installs normally
Trust: "Verified publisher: Wareflow"
```

## Proposed Solution

### Solution 1: Obtain Code Signing Certificate

**Steps**:

1. **Choose Certificate Authority**:
   - DigiCert (recommended)
   - Sectigo
   - GlobalSign

2. **Purchase Certificate**:
   - OV Code Signing Certificate: ~$400/year
   - EV Code Signing Certificate: ~$500/year (better trust)

3. **Validate Identity**:
   - Provide business documents
   - Verify organization
   - Wait for approval (1-3 days)

4. **Receive Certificate**:
   - Download .pfx file
   - Store securely (USB drive, HSM)
   - Never share certificate

### Solution 2: Sign Executables

**Signing process**:

```bash
# Install certificate to Windows Certificate Store
certutil -importPFX wareflow.pfx

# Sign executable
signtool sign \
  /f wareflow.pfx \
  /p PASSWORD \
  /tr http://timestamp.digicert.com \
  /td sha256 \
  /fd sha256 \
  dist/wems.exe

# Verify signature
signtool verify /pa dist/wems.exe
```

**Output**:
```
Successfully signed and timestamped:
    dist/wems.exe

SignTool Error: No error was encountered.
```

### Solution 3: CI/CD Integration

**Automated signing in GitHub Actions**:

```yaml
# .github/workflows/build.yml
- name: Sign executable
  if: matrix.os == 'windows-latest'
  env:
    CERTIFICATE_BASE64: ${{ secrets.CERTIFICATE_BASE64 }}
    CERTIFICATE_PASSWORD: ${{ secrets.CERTIFICATE_PASSWORD }}
  run: |
    # Decode certificate from secrets
    echo $CERTIFICATE_BASE64 | base64 -d > cert.pfx

    # Sign executable
    signtool sign \
      /f cert.pfx \
      /p $CERTIFICATE_PASSWORD \
      /tr http://timestamp.digicert.com \
      /td sha256 \
      /fd sha256 \
      dist/wems.exe

    # Verify
    signtool verify /pa dist/wems.exe

    # Clean up
    rm cert.pfx
```

**Secrets setup**:
```bash
# Encode certificate to base64
base64 -w 0 wareflow.pfx > cert_base64.txt

# Add to GitHub secrets:
# CERTIFICATE_BASE64: <contents of cert_base64.txt>
# CERTIFICATE_PASSWORD: <certificate password>
```

### Solution 4: Timestamping

**Why timestamp?**:
- Certificate expires (1-2 years)
- Signature remains valid after expiration
- Proves when executable was signed

**Process**:
```bash
signtool sign \
  /tr http://timestamp.digicert.com \
  /td sha256 \
  dist/wems.exe
```

### Solution 5: Verification

**Users can verify**:

```bash
# User downloads wems.exe and checksums.txt
# User verifies signature

signtool verify /pa /v wems.exe

Output:
✓ Verifying: wems.exe
✓ Signature is valid
✓ Publisher: Wareflow
✓ Certificate: DigiCert
✓ Timestamp: 2025-01-22 14:30:00
```

## Implementation Plan

### Phase 1: Obtain Certificate (1 week)
1. Research certificate authorities
2. Choose certificate type (OV vs EV)
3. Purchase certificate
4. Complete identity verification
5. Receive certificate files

### Phase 2: Local Signing (2 days)
1. Install certificate locally
2. Test signing process
3. Verify signed executable
4. Document signing process

### Phase 3: CI/CD Integration (3 days)
1. Add certificate to GitHub secrets
2. Create signing script
3. Integrate with build pipeline
4. Test automated signing

### Phase 4: Verification (2 days)
1. Create verification guide
2. Add checksums to releases
3. Document verification process
4. User education

## Files to Create

- `build/sign_exe.py`
- `docs/verification.md`
- `docs/CODE_SIGNING.md`

## Files to Modify

- `.github/workflows/build.yml` - Add signing step

## Dependencies to Add

```toml
[project.optional-dependencies]
build = [
    "signtool",  # Windows SDK (installed separately)
]
```

## Costs

**Annual costs**:
- OV Code Signing Certificate: ~$400/year
- EV Code Signing Certificate: ~$500/year (recommended)
- Hardware Security Module (optional): $100-500

## Testing Requirements

- Test signing process locally
- Test signed executable runs without warning
- Test CI/CD signing works
- Test verification process
- Test timestamp works
- Test certificate expiry handled correctly

## Benefits

### For Users
- **No warnings**: Smooth installation
- **Trust**: Verified publisher
- **Security**: Verified integrity
- **Confidence**: Professional software

### For Business
- **Enterprise**: Can deploy to companies
- **Adoption**: 30% more users install
- **Trust**: Professional appearance
- **Support**: Fewer "is this safe?" tickets

### For Distribution
- **Platforms**: Can list on more platforms
- **Stores**: Can publish to Microsoft Store
- **Enterprise**: Can sell to corporations

## Success Metrics

- [ ] SmartScreen warning eliminated
- [ ] Installation abandonment rate < 5%
- [ ] Enterprise deployments approved
- [ ] User trust score > 4.5/5
- [ ] Support tickets for security reduced by 90%

## Related Issues

- #037: No Automated Build Pipeline (CI/CD integrates signing)
- #027: Application Requires Python Runtime Installation (signing builds trust)

## Priority

**MEDIUM** - Significantly improves trust and adoption but doesn't block functionality

## Estimated Effort

2 weeks (obtain certificate + signing + CI/CD + verification)

## Mitigation

While waiting for certificate:
1. Add checksums to all releases
2. Provide verification guide
3. Document security measures
4. Build trust through open source
5. Offer virus scan results
