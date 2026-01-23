# [MEDIUM] No GUI Configuration Editor

## Type
**User Experience / Configuration**

## Severity
**MEDIUM** - Configuration is possible but difficult for non-technical users

## Affected Components
- **Configuration** - config.yaml / config.json
- **GUI Application** - Settings interface
- **End Users** - Non-technical warehouse managers, HR staff

## Description

Users must edit configuration files with external text editors. There is no built-in GUI for editing configuration, no syntax highlighting, no validation, and no helpful error messages. This creates a high barrier for non-technical users who need to customize their application.

## Current Configuration Process

### What Users Must Do Today

#### Method 1: Text Editor

```
1. Open application
2. Remember config file location (data/config.yaml)
3. Close application
4. Navigate to data/ directory
5. Open config.yaml in Notepad/TextEdit
6. Edit configuration
7. Save file
8. Restart application
9. Hope configuration is valid
10. If error: repeat from step 5
```

**Problems**:
- No validation until restart
- Cryptic error messages if syntax error
- No context/help while editing
- Must remember where config file is

#### Method 2: Command Line

```
1. Open terminal
2. Navigate to application directory
3. Open config.yaml in vim/nano (requires technical knowledge)
4. Edit configuration
5. Save and exit
6. Restart application
```

**Problems**:
- Requires terminal knowledge
- Vim/nano learning curve
- Easy to make syntax errors
- No validation

## Real-World Impact

### Scenario 1: Warehouse Manager Adding New Workspace

**Task**: Add new workspace "Zone C" to configuration

**Current Process**:
```
1. User opens Notepad
2. Opens data/config.yaml
3. Sees:
   workspaces:
     - Quai
     - Zone A
     - Zone B
4. Adds:
     - Zone C
5. Saves
6. Restarts application
7. Application works! ✓
```

**BUT** if user makes mistake:
```
4. Adds (typo: missing hyphen):
     Zone C
5. Saves
6. Restarts application
7. Error: "Invalid YAML syntax"
8. User doesn't know what's wrong
9. Submits support ticket
```

**Impact**: Support burden, user frustration

### Scenario 2: HR Consultant Configuring Client Alerts

**Task**: Set alert thresholds for specific client requirements

**Current Process**:
```
1. Opens config.yaml
2. Sees:
   critical_days: 7
   warning_days: 30
3. Client wants 14 days for critical
4. Changes to:
   critical_days: 14
5. Saves
6. Restarts
7. Works, but user wonders: "What's reasonable? What do others use?"
```

**No guidance** on:
- What are common values?
- What's the range?
- What happens if I set 0 or 1000?
- What's the relationship between critical and warning?

**Impact**: Uncertainty, poor configuration choices

### Scenario 3: Multi-Site Configuration

**Task**: Configure 5 warehouse sites

**Current Process**:
```
1. Opens config.yaml in Notepad
2. Scrolls through 200+ lines
3. Gets lost in nested structure
4. Makes mistake in indentation
5. Saves
6. Error: "YAML indentation error"
7. Spots error (eventually)
8. Fixes
9. Restarts
10. Another error in different section
11. Gives up
```

**Impact**: Configuration errors, abandoned customizations

## Problems Created

### 1. No Real-Time Validation

**Current behavior**:
- User edits config file
- Saves file
- Restarts application
- **Then** discovers syntax error
- Must reopen, fix, save, restart again

**Impact**: Time-consuming, frustrating error loop

### 2. No Contextual Help

**User questions while editing**:
- What does this setting do?
- What are valid values?
- What's the recommended value?
- What happens if I change this?

**No answers** in text editor:
- Must open separate documentation
- Alt-tab between editor and docs
- Lose context, easy to make mistakes

### 3. No Syntax Highlighting

**Plain text editor** (Notepad):
```
workspaces:
- Quai
- Zone A
- Zone B
roles:
- Cariste
- Magasinier
```

All plain text, no color coding:
- Hard to distinguish keys from values
- Easy to miss indentation errors
- Difficult to scan large files

### 4. No Input Controls

**Current approach**:
- Free-form text editing
- Can type anything
- No validation of data types
- No range checking

**Examples of invalid inputs**:
```yaml
critical_days: "seven"  # String instead of number
warning_days: -5        # Negative number
email: "not-an-email"   # Invalid format
workspaces: []          # Empty list
```

All these pass text editor but break application.

### 5. No Preview

**Current workflow**:
- Edit config file
- Save
- Restart application
- **Then** see the effect
- If wrong: repeat

**No way to**:
- Preview changes before applying
- Compare old vs new configuration
- Undo changes easily
- See what will change

### 6. Intimidating for Non-Technical Users

**Text editor approach** requires:
- Understanding file system navigation
- Understanding YAML syntax
- Understanding indentation
- Not afraid of "breaking" the application

**Impact**: Many users don't customize at all, missing out on features

## Missing Features

### GUI Configuration Editor
- [ ] Built-in configuration editor in application
- [ ] Form-based interface (no text editing)
- [ ] Real-time validation
- [ ] Contextual help and tooltips
- [ ] Syntax highlighting (for text mode)
- [ ] Preview changes
- [ ] Undo/Redo support

### Input Controls
- [ ] Number inputs (with min/max)
- [ ] Text inputs (with validation)
- [ ] Dropdowns (for enums)
- [ ] Multi-select (for lists)
- [ ] Checkboxes (for booleans)
- [ ] Date pickers (for dates)

### Organization
- [ ] Tabbed interface by section
- [ ] Search functionality
- [ ] Recent changes highlighting
- [ ] Reset to defaults button

### Safety
- [ ] Validation before saving
- [ ] Backup of old config
- [ ] Rollback capability
- [ ] Export/Import configuration

## Proposed Solution

### GUI Configuration Editor

Add "Settings" → "Configuration" menu in the application:

#### Main Interface

```
┌─────────────────────────────────────────────────────┐
│ ⚙️ Configuration                          [Save] [Reset] │
├─────────────────────────────────────────────────────┤
│                                                      │
│ [General] [Alerts] [Organization] [Database] [Advanced] │
│                                                      │
│ Alert Configuration                                 │
│ ─────────────────────────────────────────────────   │
│                                                      │
│   Critical threshold (days)                          │
│   ┌─────────────────────────────────┐               │
│   │ 7                    [▼]     │  Slider: [━━●━━]│
│   └─────────────────────────────────┘               │
│   💡 Alert when CACES/visits expire within 7 days   │
│   Valid range: 1-30 days                            │
│                                                      │
│   Warning threshold (days)                          │
│   ┌─────────────────────────────────┐               │
│   │ 30                   [▼]     │  Slider: [━━━●━]│
│   └─────────────────────────────────┘               │
│   💡 Alert when CACES/visits expire within 30 days  │
│   Valid range: 1-90 days                            │
│                                                      │
│   Email recipient (optional)                        │
│   ┌─────────────────────────────────┐               │
│   │ manager@company.com              │               │
│   └─────────────────────────────────┘               │
│                                                      │
│   [✓] Enable desktop notifications                 │
│                                                      │
│                                                      │
│                          [Cancel]           [Save]  │
└─────────────────────────────────────────────────────┘
```

#### Organization Section

```
┌─────────────────────────────────────────────────────┐
│ Organization                                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│   Company Information                                │
│   ──────────────────────────────────────────────   │
│                                                      │
│   Company name:                                      │
│   ┌──────────────────────────────────────┐          │
│   │ Mon Entrepôt SARL                      │          │
│   └──────────────────────────────────────┘          │
│                                                      │
│   SIRET:                                             │
│   ┌──────────────────────────────────────┐          │
│   │ 12345678900012                         │          │
│   └──────────────────────────────────────┘          │
│                                                      │
│   Workspaces                                         │
│   ──────────────────────────────────────────────   │
│   ┌─────────────────────────────────────────────┐  │
│   │ Quai                       [Remove]  [↑] [↓]│  │
│   │ Zone A                     [Remove]  [↑] [↓]│  │
│   │ Zone B                     [Remove]  [↑] [↓]│  │
│   │ Bureau                     [Remove]  [↑] [↓]│  │
│   │                                            │  │
│   │ [+ Add workspace]                         │  │
│   └─────────────────────────────────────────────┘  │
│                                                      │
│   Roles                                               │
│   ──────────────────────────────────────────────   │
│   ┌─────────────────────────────────────────────┐  │
│   │ Cariste                    [Remove]  [↑] [↓]│  │
│   │ Magasinier                 [Remove]  [↑] [↓]│  │
│   │ Préparateur                [Remove]  [↑] [↓]│  │
│   │                                            │  │
│   │ [+ Add role]                               │  │
│   └─────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### Features

**Real-Time Validation**:
- Red border around invalid inputs
- Inline error messages
- "Save" button disabled until valid

**Contextual Help**:
- Tooltips on each field
- "?" icon linking to documentation
- Example values shown
- Valid ranges displayed

**Preview**:
- "Preview Changes" button
- Diff view showing old vs new
- Summary of changes
- Confirm before saving

**Backup**:
- Automatic backup before saving
- "Revert to Backup" button
- Show backup history

**Import/Export**:
- Export configuration to file
- Import configuration from file
- Copy/paste configuration
- Share configurations between instances

## Implementation Plan

### Phase 1: Configuration Framework (1 week)
1. Create `src/ui_ctk/views/config_editor.py`
2. Create form widgets (number input, text input, dropdown)
3. Implement validation framework
4. Add help/tooltips system

### Phase 2: Sections (1 week)
1. General section (alerts, interface)
2. Organization section (company, workspaces, roles)
3. Database section (filename, backups)
4. Advanced section (multi-site, audit, API)

### Phase 3: Features (3 days)
1. Real-time validation
2. Preview changes
3. Backup/restore
4. Import/export

### Phase 4: Polish (2 days)
1. Tabbed interface
2. Search functionality
3. Keyboard shortcuts
4. Accessibility

## Files to Create

- `src/ui_ctk/views/config_editor.py`
- `src/ui_ctk/widgets/form_controls.py`
- `src/utils/config_validator.py`
- `src/utils/config_backup.py`

## Files to Modify

- `src/ui_ctk/main_window.py` - Add Settings menu
- `src/utils/config.py` - Add save/validation hooks

## Testing Requirements

- Test all form controls work correctly
- Test validation catches invalid inputs
- Test help tooltips display correctly
- Test preview shows correct diff
- Test backup creates before save
- Test revert restores correctly
- Test import/export works
- Test keyboard shortcuts
- Test accessibility (tab order, screen reader)

## Benefits

### For End Users
- **Ease**: No text editor required
- **Validation**: Immediate feedback on errors
- **Guidance**: Help and examples shown inline
- **Confidence**: Preview changes before applying

### For Support
- **Fewer errors**: Validation prevents syntax errors
- **Self-service**: Users can fix config themselves
- **Consistency**: GUI enforces valid values

### For Product
- **Adoption**: More users customize settings
- **Satisfaction**: Better configuration experience
- **Professional**: Matches other software expectations

## Success Metrics

- [ ] 80% of users use GUI editor instead of text files
- [ ] Configuration errors reduced by 90%
- [ ] Average configuration time reduced by 50%
- [ ] User satisfaction > 4.5/5

## Related Issues

- #029: JSON Configuration Files Are Not User-Friendly (GUI editor solves this)
- #028: Each Installation Requires Manual Configuration (GUI editor helps)

## Priority

**MEDIUM** - Improves user experience but configuration is possible without it

## Estimated Effort

3 weeks (framework + sections + features + polish)

## Mitigation

While waiting for GUI editor:
1. Provide online YAML editor with validation
2. Create configuration wizard in CLI
3. Add extensive validation with helpful error messages
4. Provide example configurations for common scenarios
5. Create video tutorials for configuration
