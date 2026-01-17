# Modern Medical UI/UX Design for VoicePerio
## Complete Design System & Implementation Guide

---

## 1. COLOR PALETTE & BRANDING

### Core Colors
```
Primary Background:    #FFFFFF (Pure White)
Primary Blue:          #0066CC (Medical Professional Blue)
Secondary Blue:        #0052A3 (Darker - for active states)
Light Blue:            #E3F2FD (Subtle backgrounds)
Accent:                #00A8E8 (Bright blue for highlights)
Text Primary:          #1A1A1A (Dark Gray-Black)
Text Secondary:        #666666 (Medium Gray)
Success:               #4CAF50 (Green - status indicators)
Warning:               #FF9800 (Orange - alerts)
Error:                 #F44336 (Red - errors)
Border:                #E0E0E0 (Light Gray)
Disabled:              #CCCCCC (Disabled state)
```

### Brand Consistency
- Match VoicePerio icon: Blue + White
- Medical industry standard colors
- Healthcare trust: Blue conveys professionalism & trust
- White: Clean, sterile, medical environment
- Minimalist: 60% white, 30% gray, 10% blue accents

---

## 2. TYPOGRAPHY SYSTEM

### Font Stack (Windows Medical UI)
```
Primary Font:   'Segoe UI', -apple-system, sans-serif
Fallback:       'Arial', 'Helvetica', sans-serif
Monospace:      'Courier New', monospace
```

### Type Scale
```
Display:        20px, 700, Line-height 1.2   (Window title)
Heading:        16px, 600, Line-height 1.3   (Section headers)
Body:           14px, 400, Line-height 1.5   (Main content)
Small:          12px, 400, Line-height 1.4   (Secondary text)
Label:          11px, 600, Line-height 1.4   (Field labels)
Compact:        10px, 400, Line-height 1.3   (Timestamps, notes)
```

### Typography Rules
- Limit to 3 font sizes maximum
- Use 600 weight for emphasis (never italics)
- 1.5 line-height for readability
- Max line length: 45 characters for labels
- All caps only for small labels (< 12px)

---

## 3. SPACING & LAYOUT SYSTEM

### 8px Grid System
```
xs:  4px    (minimum padding)
sm:  8px    (standard spacing)
md:  16px   (component spacing)
lg:  24px   (section spacing)
xl:  32px   (major divisions)
```

### Layout Dimensions
```
Window:       400px × 300px (fixed for docked position)
Content:      384px × 284px (16px padding all sides)
Column Gutters: 8px
Row Height:   28px (with 8px vertical spacing)
Icon Size:    24px (status indicators)
Button Height: 32px
Card Padding:  12px
```

### Responsive Spacing
- Minimum touch target: 32px × 32px (accessibility)
- Card margins: 8px
- Section dividers: 16px
- Status indicators: 8px margin from text

---

## 4. COMPONENT SPECIFICATIONS

### Status Indicator Component
```
Position:  Top-left, fixed
Size:      32px × 32px circle + 16px text
Colors:
  Listening:  #4CAF50 (Green) with pulsing animation
  Paused:     #FF9800 (Orange)
  Sleeping:   #CCCCCC (Gray)
  Ready:      #0066CC (Blue)
  
Animation: Subtle pulse on "Listening" state (0.5s cycle)
```

### Voice Feedback Panel
```
Height:    96px
Padding:   12px
Border:    1px solid #E0E0E0
Background: #F8F9FA (subtle gray)
Border-radius: 6px

Content:
  Command text: 16px, 600 weight, #1A1A1A
  Status icon: 20px
  Timestamp: 10px, #666666
  Feedback msg: 14px, #0066CC
```

### Real-time Information Panel
```
Height:    80px
Layout:    2 rows × 2 columns
Cell size: 92px × 36px

Elements:
  - Field counter: Large blue number
  - Status badge: Green/Orange/Gray
  - Session time: Compact font
  - Last entry: Confirmation text
```

### Command History List
```
Height:    92px (scrollable, max 3 items visible)
Item height: 28px
Padding:   8px
Font:      12px, monospace for commands

Styling:
  Hover:     #E3F2FD background
  Selected:  #0066CC text
  Icon:      12px gray
```

### Quick Action Buttons
```
Size:     32px × 32px (square) or 32px height (pill-shaped)
Padding:  8px
Spacing:  8px between buttons
Colors:
  Default:   White border, #0066CC text
  Hover:     #E3F2FD background
  Active:    #0066CC background, white text
  Disabled:  #CCCCCC border, #CCCCCC text

Icon:      16px, centered
Text:      10px, 600 weight (optional)
```

---

## 5. WINDOW LAYOUT MOCKUP

```
┌─────────────────────────────────────────────────────────────┐
│ VoicePerio  [🎤 Listening]                  [−] [□] [×]     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  🎤 LISTENING           [Status: Active]                     │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Command: three two three                           14:32│ │
│  │ Status: ✓ Entered (232)                                 │ │
│  │ Feedback: Moving to next field                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  Field: 3/6    Active    Time: 2:14    Last: 232            │
│                                                               │
│  Recent: next > skip > bleeding >                            │
│                                                               │
│  [Pause] [Save] [Settings]                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. PyQt6 STYLESHEET (QSS)

```qss
/* Main Window */
QMainWindow {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
}

QMainWindow::title {
    color: #1A1A1A;
    font-size: 14px;
    font-weight: 600;
    padding: 8px 12px;
}

/* Status Indicator */
#statusIndicator {
    background-color: #4CAF50;
    border-radius: 16px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    border: 2px solid #FFFFFF;
}

#statusIndicator[status="listening"] {
    background-color: #4CAF50;
    animation: pulse 1s infinite;
}

#statusIndicator[status="paused"] {
    background-color: #FF9800;
}

#statusIndicator[status="sleeping"] {
    background-color: #CCCCCC;
}

#statusIndicator[status="ready"] {
    background-color: #0066CC;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}

/* Status Text */
#statusText {
    color: #1A1A1A;
    font-size: 14px;
    font-weight: 600;
    margin-left: 8px;
}

/* Feedback Panel */
#feedbackPanel {
    background-color: #F8F9FA;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    padding: 12px;
    margin: 8px 0;
}

#commandText {
    color: #1A1A1A;
    font-size: 14px;
    font-weight: 600;
}

#feedbackMessage {
    color: #0066CC;
    font-size: 12px;
    font-weight: 400;
    margin-top: 4px;
}

#statusBadge {
    color: #4CAF50;
    font-size: 10px;
    font-weight: 600;
    background-color: #E8F5E9;
    padding: 2px 6px;
    border-radius: 3px;
    margin-left: 4px;
}

/* Info Panel */
#infoPanel {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    padding: 8px;
    margin: 8px 0;
}

#infoItem {
    color: #666666;
    font-size: 11px;
    padding: 4px;
}

#infoValue {
    color: #0066CC;
    font-size: 16px;
    font-weight: 600;
}

/* History List */
#historyList {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    max-height: 92px;
}

#historyItem {
    color: #1A1A1A;
    font-size: 12px;
    font-family: 'Courier New', monospace;
    padding: 6px 8px;
    border-bottom: 1px solid #F0F0F0;
}

#historyItem:hover {
    background-color: #E3F2FD;
}

#historyItem:last-child {
    border-bottom: none;
}

/* Buttons */
QPushButton {
    background-color: #FFFFFF;
    color: #0066CC;
    border: 2px solid #0066CC;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    min-height: 32px;
    min-width: 60px;
    cursor: pointer;
}

QPushButton:hover {
    background-color: #E3F2FD;
    border-color: #0052A3;
}

QPushButton:pressed {
    background-color: #0066CC;
    color: #FFFFFF;
}

QPushButton:disabled {
    background-color: #FFFFFF;
    color: #CCCCCC;
    border-color: #CCCCCC;
    cursor: not-allowed;
}

/* Primary Action Button */
QPushButton#primaryButton {
    background-color: #0066CC;
    color: #FFFFFF;
    border: 2px solid #0066CC;
}

QPushButton#primaryButton:hover {
    background-color: #0052A3;
    border-color: #0052A3;
}

/* Labels */
QLabel {
    color: #1A1A1A;
    font-size: 14px;
}

QLabel#small {
    font-size: 12px;
    color: #666666;
}

QLabel#compact {
    font-size: 10px;
    color: #999999;
    font-weight: 400;
}

/* Scrollbar Styling */
QScrollBar:vertical {
    background-color: #F8F9FA;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #CCCCCC;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #0066CC;
}

/* Focus & Accessibility */
*:focus {
    outline: 2px solid #0066CC;
    outline-offset: 2px;
}

/* Animation Classes */
.pulse-animation {
    animation: pulse 1s ease-in-out infinite;
}

.fade-in {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideIn {
    from { transform: translateY(8px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
```

---

## 7. COMPONENT HIERARCHY

```
┌─ MainWindow (400×300px, docked)
│
├─ HeaderBar
│  ├─ StatusIndicator (animated circle)
│  └─ StatusText ("Listening", "Paused", etc.)
│
├─ FeedbackPanel
│  ├─ CommandText (last command)
│  ├─ ExecutionStatus (✓ Entered)
│  └─ FeedbackMessage (confirmation/error)
│
├─ InfoPanel
│  ├─ FieldCounter (3/6)
│  ├─ SessionStatus (Active/Paused)
│  ├─ SessionTime (elapsed)
│  └─ LastEntry (confirmation)
│
├─ CommandHistory
│  └─ HistoryItems (scrollable list, max 3)
│
└─ ActionBar
   ├─ PauseButton
   ├─ SaveButton
   └─ SettingsButton
```

---

## 8. ACCESSIBILITY GUIDELINES

### WCAG 2.1 Compliance
- **Color Contrast**: All text >7:1 ratio (AAA compliant)
- **Focus Indicators**: Blue outline (2px, 2px offset)
- **Keyboard Navigation**: Tab order logical, Escape to close
- **Font Sizing**: Minimum 11px for all text
- **Interactive Elements**: Minimum 32×32px touch targets
- **Status Indicators**: Not color-only; include icons/text
- **Animations**: Respect `prefers-reduced-motion`

### Medical Context
- Clear status information (no ambiguity)
- Confirmation for critical actions
- Readable from 2 meters away (high contrast)
- Professional appearance (builds trust)

---

## 9. ANIMATION & TRANSITIONS

### Subtle, Professional Animations
```
Status Pulse:       0.5s infinite, 0.7 opacity min
Feedback Enter:     0.3s ease-in from bottom
Button Hover:       0.15s ease-out, color shift
Status Change:      0.2s fade transition
History Scroll:     0.1s ease-out
```

### Animation Principles
- Quick, snappy transitions (< 300ms)
- Easing: ease-in-out for natural feel
- Avoid: Bouncing, overshoot, flare
- Purpose: Feedback to user actions
- Accessibility: Respect `prefers-reduced-motion`

---

## 10. WINDOW POSITIONING & BEHAVIOR

### Docked Position
```
Position:        Bottom-right of screen
Distance from taskbar: 8px above
Distance from screen edge: 8px from right
Pinned:           Always above other windows
Draggable:        Allow repositioning
Resizable:        Optional (maintain aspect ratio if enabled)
```

### State Behavior
- **Minimized**: Remains in system tray
- **Closed**: Minimize to tray (don't exit)
- **Focus**: Brings window to front
- **Unfocus**: Stays on top, doesn't hide

---

## 11. IMPLEMENTATION CHECKLIST

### Phase 1: Core Structure
- [ ] Create modern medical UI components
- [ ] Implement PyQt6 stylesheet
- [ ] Build window docking system
- [ ] Set up status indicators

### Phase 2: Interactions
- [ ] Add button functionality
- [ ] Implement animations
- [ ] Create command history
- [ ] Add feedback messages

### Phase 3: Polish & Testing
- [ ] Test WCAG accessibility
- [ ] Verify color contrast
- [ ] Test on different screen sizes
- [ ] Performance optimization

---

## 12. DESIGN RATIONALE

### Why This Design?
1. **White Background**: Clean, medical, professional
2. **Blue Accents**: Trust, healthcare standard, matches brand
3. **Minimalist**: Reduces cognitive load, focuses on essential info
4. **Docked Window**: Always accessible, out of way, space-efficient
5. **Modern Typography**: Segoe UI is Windows standard, professional
6. **8px Grid**: Consistency, maintainability, scalability
7. **Animations**: User feedback without distraction
8. **Accessibility**: WCAG AAA - inclusive design for all users

---

## Files to Reference
- Design System: This document
- Implementation: `modern_medical_ui.py` (to be created)
- Stylesheet: Included in QSS section above
- Assets: Icons to be designed
