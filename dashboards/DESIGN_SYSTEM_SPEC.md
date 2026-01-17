# HTML Dashboard Design System Specification

**Version:** 1.0.0  
**Last Updated:** 2026-01-20  
**Purpose:** Standardized design tokens, components, and patterns for all HTML-only dashboards

---

## Table of Contents

1. [Design Tokens (CSS Variables)](#design-tokens-css-variables)
2. [Color Palette](#color-palette)
3. [Typography Scale](#typography-scale)
4. [Spacing System](#spacing-system)
5. [Shadow System](#shadow-system)
6. [Component Specifications](#component-specifications)
7. [Layout Patterns](#layout-patterns)
8. [Implementation Guide](#implementation-guide)
9. [Migration Strategy](#migration-strategy)
10. [Component Examples](#component-examples)

---

## Design Tokens (CSS Variables)

### Complete CSS Variables Template

Copy this entire block into the `<style>` tag at the top of any dashboard HTML file:

```css
:root {
  /* ============================================
     COLOR TOKENS - Primary & Status
     ============================================ */
  
  /* Primary Colors */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-primary-light: #dbeafe;
  --color-primary-dark: #1e40af;
  
  /* Status Colors */
  --color-success: #10b981;
  --color-success-hover: #059669;
  --color-success-light: #d1fae5;
  --color-success-dark: #065f46;
  
  --color-warning: #f59e0b;
  --color-warning-hover: #d97706;
  --color-warning-light: #fef3c7;
  --color-warning-dark: #92400e;
  
  --color-error: #ef4444;
  --color-error-hover: #dc2626;
  --color-error-light: #fee2e2;
  --color-error-dark: #991b1b;
  
  --color-info: #3b82f6;
  --color-info-hover: #2563eb;
  --color-info-light: #dbeafe;
  --color-info-dark: #1e40af;
  
  /* ============================================
     COLOR TOKENS - Legislative States
     ============================================ */
  
  --color-state-pre-evt: #3b82f6;
  --color-state-pre-evt-light: #dbeafe;
  --color-state-intro-evt: #10b981;
  --color-state-intro-evt-light: #d1fae5;
  --color-state-comm-evt: #f59e0b;
  --color-state-comm-evt-light: #fef3c7;
  --color-state-floor-evt: #ef4444;
  --color-state-floor-evt-light: #fee2e2;
  --color-state-final-evt: #8b5cf6;
  --color-state-final-evt-light: #ede9fe;
  --color-state-impl-evt: #6b7280;
  --color-state-impl-evt-light: #f3f4f6;
  
  /* ============================================
     COLOR TOKENS - Agent Types
     ============================================ */
  
  --color-agent-intelligence: #3b82f6;
  --color-agent-intelligence-bg: #dbeafe;
  --color-agent-drafting: #f59e0b;
  --color-agent-drafting-bg: #fef3c7;
  --color-agent-execution: #ef4444;
  --color-agent-execution-bg: #fee2e2;
  --color-agent-learning: #10b981;
  --color-agent-learning-bg: #d1fae5;
  
  /* ============================================
     COLOR TOKENS - Agent Status
     ============================================ */
  
  --color-status-running: #3b82f6;
  --color-status-running-bg: #dbeafe;
  --color-status-idle: #6b7280;
  --color-status-idle-bg: #e5e7eb;
  --color-status-waiting: #f59e0b;
  --color-status-waiting-bg: #fef3c7;
  --color-status-blocked: #ef4444;
  --color-status-blocked-bg: #fee2e2;
  --color-status-terminated: #6b7280;
  --color-status-terminated-bg: #f3f4f6;
  
  /* ============================================
     COLOR TOKENS - Neutral Colors
     ============================================ */
  
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  
  /* Semantic Neutral Colors */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f5f5f5;
  --color-bg-tertiary: #f9fafb;
  --color-text-primary: #1a1a1a;
  --color-text-secondary: #6b7280;
  --color-text-tertiary: #9ca3af;
  --color-border: #e5e7eb;
  --color-border-light: #f3f4f6;
  --color-border-dark: #d1d5db;
  
  /* ============================================
     TYPOGRAPHY TOKENS
     ============================================ */
  
  /* Font Families */
  --font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  --font-family-mono: 'Courier New', monospace;
  
  /* Font Sizes */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;   /* 20px */
  --font-size-2xl: 1.5rem;   /* 24px */
  --font-size-3xl: 1.875rem; /* 30px */
  --font-size-4xl: 2.25rem;  /* 36px */
  
  /* Font Weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Line Heights */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
  
  /* ============================================
     SPACING TOKENS
     ============================================ */
  
  /* Base Unit: 0.25rem (4px) */
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */
  --spacing-2xl: 3rem;     /* 48px */
  --spacing-3xl: 4rem;     /* 64px */
  
  /* ============================================
     BORDER RADIUS TOKENS
     ============================================ */
  
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-full: 9999px;   /* For pills/badges */
  
  /* ============================================
     SHADOW TOKENS (Elevation)
     ============================================ */
  
  --shadow-0: none;
  --shadow-1: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-2: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-3: 0 4px 8px rgba(0, 0, 0, 0.15);
  --shadow-4: 0 8px 16px rgba(0, 0, 0, 0.2);
  --shadow-5: 0 16px 32px rgba(0, 0, 0, 0.25);
  
  /* ============================================
     LAYOUT TOKENS
     ============================================ */
  
  --container-max-width: 1400px;
  --container-max-width-wide: 1600px;
  --container-padding: 2rem;
  
  /* ============================================
     TRANSITION TOKENS
     ============================================ */
  
  --transition-fast: 0.15s;
  --transition-base: 0.2s;
  --transition-slow: 0.3s;
  --transition-ease: ease;
}
```

---

## Color Palette

### Primary Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Primary Blue | `#3b82f6` | Primary actions, links, focus states |
| Primary Blue Hover | `#2563eb` | Hover state for primary elements |
| Primary Blue Light | `#dbeafe` | Backgrounds, highlights |
| Primary Blue Dark | `#1e40af` | Active states, emphasis |

### Status Colors

| Status | Hex | Usage |
|--------|-----|-------|
| Success | `#10b981` | Success messages, completed states |
| Warning | `#f59e0b` | Warnings, pending states |
| Error | `#ef4444` | Errors, failed states |
| Info | `#3b82f6` | Informational messages |

### Legislative State Colors

| State | Hex | Border Color | Background |
|-------|-----|--------------|------------|
| PRE_EVT | `#3b82f6` | `--color-state-pre-evt` | `--color-state-pre-evt-light` |
| INTRO_EVT | `#10b981` | `--color-state-intro-evt` | `--color-state-intro-evt-light` |
| COMM_EVT | `#f59e0b` | `--color-state-comm-evt` | `--color-state-comm-evt-light` |
| FLOOR_EVT | `#ef4444` | `--color-state-floor-evt` | `--color-state-floor-evt-light` |
| FINAL_EVT | `#8b5cf6` | `--color-state-final-evt` | `--color-state-final-evt-light` |
| IMPL_EVT | `#6b7280` | `--color-state-impl-evt` | `--color-state-impl-evt-light` |

### Agent Type Colors

| Type | Text Color | Background |
|------|------------|------------|
| Intelligence | `--color-agent-intelligence` | `--color-agent-intelligence-bg` |
| Drafting | `--color-agent-drafting` | `--color-agent-drafting-bg` |
| Execution | `--color-agent-execution` | `--color-agent-execution-bg` |
| Learning | `--color-agent-learning` | `--color-agent-learning-bg` |

### Agent Status Colors

| Status | Text Color | Background |
|--------|------------|------------|
| RUNNING | `--color-status-running` | `--color-status-running-bg` |
| IDLE | `--color-status-idle` | `--color-status-idle-bg` |
| WAITING_REVIEW | `--color-status-waiting` | `--color-status-waiting-bg` |
| BLOCKED | `--color-status-blocked` | `--color-status-blocked-bg` |
| TERMINATED | `--color-status-terminated` | `--color-status-terminated-bg` |

### Neutral Colors

| Usage | Color Variable | Hex |
|-------|----------------|-----|
| Primary Background | `--color-bg-primary` | `#ffffff` |
| Secondary Background | `--color-bg-secondary` | `#f5f5f5` |
| Primary Text | `--color-text-primary` | `#1a1a1a` |
| Secondary Text | `--color-text-secondary` | `#6b7280` |
| Border | `--color-border` | `#e5e7eb` |

---

## Typography Scale

### Font Families

- **Sans-serif (default):** `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif`
- **Monospace:** `'Courier New', monospace` (for code, commands, file paths)

### Font Size Scale

| Size | Variable | Rem | Pixels | Usage |
|------|----------|-----|--------|-------|
| xs | `--font-size-xs` | 0.75rem | 12px | Labels, captions |
| sm | `--font-size-sm` | 0.875rem | 14px | Secondary text, small buttons |
| base | `--font-size-base` | 1rem | 16px | Body text (default) |
| lg | `--font-size-lg` | 1.125rem | 18px | Large body text |
| xl | `--font-size-xl` | 1.25rem | 20px | Section headers |
| 2xl | `--font-size-2xl` | 1.5rem | 24px | Page titles |
| 3xl | `--font-size-3xl` | 1.875rem | 30px | Large page titles |
| 4xl | `--font-size-4xl` | 2.25rem | 36px | Hero titles |

### Font Weights

| Weight | Variable | Value | Usage |
|--------|----------|-------|-------|
| Normal | `--font-weight-normal` | 400 | Body text |
| Medium | `--font-weight-medium` | 500 | Emphasized text, labels |
| Semibold | `--font-weight-semibold` | 600 | Headings, buttons |
| Bold | `--font-weight-bold` | 700 | Strong emphasis |

### Line Heights

| Height | Variable | Value | Usage |
|--------|----------|-------|-------|
| Tight | `--line-height-tight` | 1.25 | Headings |
| Normal | `--line-height-normal` | 1.5 | Body text (default) |
| Relaxed | `--line-height-relaxed` | 1.75 | Long-form content |

---

## Spacing System

### Base Unit

**4px (0.25rem)** - All spacing values are multiples of this base unit.

### Spacing Scale

| Size | Variable | Rem | Pixels | Usage |
|------|----------|-----|--------|-------|
| xs | `--spacing-xs` | 0.25rem | 4px | Tight spacing, icon padding |
| sm | `--spacing-sm` | 0.5rem | 8px | Small gaps, compact layouts |
| md | `--spacing-md` | 1rem | 16px | Standard spacing (default) |
| lg | `--spacing-lg` | 1.5rem | 24px | Section spacing |
| xl | `--spacing-xl` | 2rem | 32px | Large section spacing |
| 2xl | `--spacing-2xl` | 3rem | 48px | Major section breaks |
| 3xl | `--spacing-3xl` | 4rem | 64px | Page-level spacing |

### Border Radius

| Size | Variable | Value | Usage |
|------|----------|-------|-------|
| sm | `--radius-sm` | 4px | Small elements, inputs |
| md | `--radius-md` | 6px | Buttons, cards (small) |
| lg | `--radius-lg` | 8px | Cards, panels (standard) |
| xl | `--radius-xl` | 12px | Large cards, modals |
| 2xl | `--radius-2xl` | 16px | Extra large elements |
| full | `--radius-full` | 9999px | Pills, badges, circular |

---

## Shadow System

### Elevation Levels

| Level | Variable | Value | Usage |
|-------|----------|-------|-------|
| 0 | `--shadow-0` | `none` | Flat elements |
| 1 | `--shadow-1` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle elevation |
| 2 | `--shadow-2` | `0 2px 4px rgba(0,0,0,0.1)` | Cards, panels (standard) |
| 3 | `--shadow-3` | `0 4px 8px rgba(0,0,0,0.15)` | Elevated cards |
| 4 | `--shadow-4` | `0 8px 16px rgba(0,0,0,0.2)` | Modals, dropdowns |
| 5 | `--shadow-5` | `0 16px 32px rgba(0,0,0,0.25)` | Maximum elevation |

### Usage Guidelines

- **Level 0:** Body background, flat surfaces
- **Level 1:** Subtle separations, hover states
- **Level 2:** Standard cards, panels, headers (most common)
- **Level 3:** Interactive elements, hovered cards
- **Level 4:** Dropdowns, popovers, floating elements
- **Level 5:** Modals, dialogs, overlays

---

## Component Specifications

### Buttons

#### Variants

**Primary Button:**
- Background: `var(--color-primary)`
- Text: White
- Hover: `var(--color-primary-hover)`
- Padding: `0.5rem 1rem` (8px 16px)
- Border-radius: `var(--radius-md)` (6px)
- Font-size: `var(--font-size-sm)` (14px)
- Font-weight: `var(--font-weight-medium)` (500)
- Transition: `background var(--transition-base) var(--transition-ease)`

**Secondary Button:**
- Background: `var(--color-gray-500)`
- Text: White
- Hover: `var(--color-gray-600)`
- Same padding, border-radius, font-size as primary

**Success Button:**
- Background: `var(--color-success)`
- Text: White
- Hover: `var(--color-success-hover)`
- Same dimensions as primary

**Danger Button:**
- Background: `var(--color-error)`
- Text: White
- Hover: `var(--color-error-hover)`
- Same dimensions as primary

**Info Button:**
- Background: `var(--color-info)`
- Text: White
- Hover: `var(--color-info-hover)`
- Same dimensions as primary

#### Sizes

| Size | Padding | Font Size | Usage |
|------|---------|-----------|-------|
| Small | `0.375rem 0.75rem` (6px 12px) | `var(--font-size-xs)` (12px) | Compact spaces, inline actions |
| Medium (default) | `0.5rem 1rem` (8px 16px) | `var(--font-size-sm)` (14px) | Standard buttons |
| Large | `0.75rem 1.5rem` (12px 24px) | `var(--font-size-base)` (16px) | Primary CTAs, prominent actions |

#### States

- **Default:** Standard styling as defined above
- **Hover:** Darker background color, cursor: pointer
- **Active:** Slightly darker than hover, may add slight scale transform
- **Disabled:** Opacity: 0.5, cursor: not-allowed, no hover effects

#### Example CSS

```css
.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: background var(--transition-base) var(--transition-ease);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Cards

#### Standard Card

- Background: `var(--color-bg-primary)` (white)
- Padding: `var(--spacing-md)` (1rem / 16px)
- Border-radius: `var(--radius-lg)` (8px)
- Box-shadow: `var(--shadow-2)` (standard elevation)
- Margin-bottom: `var(--spacing-md)` (1rem / 16px)

#### Card Header

- Padding: `var(--spacing-md) var(--spacing-lg)` (16px 24px)
- Border-bottom: `1px solid var(--color-border)`
- Background: `var(--color-bg-tertiary)` (optional, for distinction)

#### Card Body

- Padding: `var(--spacing-md)` (16px)
- Default padding for card content

#### Card Footer

- Padding: `var(--spacing-md) var(--spacing-lg)` (16px 24px)
- Border-top: `1px solid var(--color-border)`
- Background: `var(--color-bg-tertiary)` (optional)

#### Card Variants

**Highlighted Card:**
- Border-left: `4px solid var(--color-primary)`
- Background: `var(--color-primary-light)` (subtle tint)

**Bordered Card:**
- Border: `1px solid var(--color-border)`
- Box-shadow: `var(--shadow-1)` (lighter shadow)

**Elevated Card:**
- Box-shadow: `var(--shadow-3)` (higher elevation)

#### Example CSS

```css
.card {
  background: var(--color-bg-primary);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-2);
  margin-bottom: var(--spacing-md);
}

.card-header {
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.card-body {
  padding: var(--spacing-md);
}

.card-footer {
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}
```

### Status Badges

#### Agent Status Badges

**RUNNING:**
- Background: `var(--color-status-running-bg)`
- Color: `var(--color-status-running)`
- Padding: `0.25rem 0.5rem` (4px 8px)
- Border-radius: `var(--radius-full)` (pill shape)
- Font-size: `var(--font-size-xs)` (12px)
- Font-weight: `var(--font-weight-semibold)` (600)
- Text-transform: `uppercase`

**IDLE:**
- Background: `var(--color-status-idle-bg)`
- Color: `var(--color-status-idle)`
- Same dimensions as RUNNING

**WAITING_REVIEW:**
- Background: `var(--color-status-waiting-bg)`
- Color: `var(--color-status-waiting)`
- Same dimensions as RUNNING

**BLOCKED:**
- Background: `var(--color-status-blocked-bg)`
- Color: `var(--color-status-blocked)`
- Same dimensions as RUNNING

#### Legislative State Badges

- Border-left: `3px solid` (using state color variable)
- Background: Light variant of state color
- Padding: `var(--spacing-sm) var(--spacing-md)` (8px 16px)
- Border-radius: `var(--radius-md)` (6px)
- Font-size: `var(--font-size-sm)` (14px)
- Font-weight: `var(--font-weight-semibold)` (600)

#### Agent Type Badges

- Background: Agent type background color variable
- Color: Agent type text color variable
- Padding: `0.25rem 0.5rem` (4px 8px)
- Border-radius: `var(--radius-sm)` (4px)
- Font-size: `var(--font-size-xs)` (12px)
- Font-weight: `var(--font-weight-medium)` (500)
- Text-transform: `uppercase`

#### Example CSS

```css
.badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
}

.badge-status-running {
  background: var(--color-status-running-bg);
  color: var(--color-status-running);
}

.badge-state-pre-evt {
  border-left: 3px solid var(--color-state-pre-evt);
  background: var(--color-state-pre-evt-light);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
}
```

### Form Elements

#### Text Input

- Padding: `0.5rem` (8px)
- Border: `1px solid var(--color-border)`
- Border-radius: `var(--radius-sm)` (4px)
- Font-size: `var(--font-size-sm)` (14px)
- Background: `var(--color-bg-primary)` (white)
- Focus: Border color `var(--color-primary)`, outline: `2px solid var(--color-primary-light)`

#### Select Dropdown

- Same styling as text input
- Padding: `0.5rem` (8px)
- Background: `var(--color-bg-primary)` (white)
- Cursor: pointer

#### File Input

- Hidden by default (use custom label styling)
- Custom label: Button-style appearance using primary button styles

#### Labels

- Font-size: `var(--font-size-sm)` (14px)
- Font-weight: `var(--font-weight-medium)` (500)
- Color: `var(--color-text-primary)`
- Margin-bottom: `var(--spacing-xs)` (4px)

#### Filter Panel

- Background: `var(--color-bg-primary)` (white)
- Padding: `var(--spacing-md)` (16px)
- Border-radius: `var(--radius-lg)` (8px)
- Box-shadow: `var(--shadow-2)`
- Display: flex with gap: `var(--spacing-md)` (16px)
- Flex-wrap: wrap

#### Example CSS

```css
input[type="text"],
input[type="number"],
select {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  background: var(--color-bg-primary);
}

input:focus,
select:focus {
  outline: 2px solid var(--color-primary-light);
  outline-offset: 2px;
  border-color: var(--color-primary);
}

label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
  display: block;
}
```

### Navigation

#### Tabs

- Background: `var(--color-bg-tertiary)` (light gray)
- Border-bottom: `3px solid var(--color-border)`
- Display: flex
- Tab padding: `var(--spacing-md)` (16px)
- Active tab: Background white, border-bottom color `var(--color-primary)`
- Hover: Background `var(--color-bg-secondary)`

#### Section Headers

- Font-size: `var(--font-size-xl)` (20px)
- Font-weight: `var(--font-weight-semibold)` (600)
- Color: `var(--color-text-primary)`
- Margin-bottom: `var(--spacing-md)` (16px)
- Border-bottom: `2px solid var(--color-border)` (optional)

### Data Display

#### Tables

- Width: 100%
- Border-collapse: collapse
- Background: `var(--color-bg-primary)` (white)
- Border-radius: `var(--radius-lg)` (8px)
- Overflow: hidden

**Table Header:**
- Background: `var(--color-gray-100)`
- Padding: `0.75rem 1rem` (12px 16px)
- Font-size: `var(--font-size-xs)` (12px)
- Font-weight: `var(--font-weight-semibold)` (600)
- Text-transform: uppercase
- Color: `var(--color-text-secondary)`
- Border-bottom: `2px solid var(--color-border)`

**Table Body:**
- Row padding: `0.75rem 1rem` (12px 16px)
- Font-size: `var(--font-size-sm)` (14px)
- Border-bottom: `1px solid var(--color-border-light)`
- Hover: Background `var(--color-gray-100)`

#### Grid Layouts

**Agent Grid:**
- Display: grid
- Grid-template-columns: `repeat(auto-fill, minmax(300px, 1fr))`
- Gap: `var(--spacing-md)` (16px)

**Card Grid:**
- Same as agent grid
- Minmax can be adjusted: `minmax(250px, 1fr)` for smaller cards

#### Empty States

- Text-align: center
- Padding: `var(--spacing-2xl)` (48px)
- Color: `var(--color-text-secondary)`
- Font-size: `var(--font-size-base)` (16px)

#### Loading States

- Text-align: center
- Padding: `var(--spacing-xl)` (32px)
- Color: `var(--color-text-secondary)`
- Font-size: `var(--font-size-sm)` (14px)

---

## Layout Patterns

### Container Pattern

**Standard Container:**
```css
.container {
  max-width: var(--container-max-width); /* 1400px */
  margin: 0 auto;
  padding: var(--container-padding); /* 2rem */
}
```

**Wide Container:**
```css
.container-wide {
  max-width: var(--container-max-width-wide); /* 1600px */
  margin: 0 auto;
  padding: var(--container-padding);
}
```

### Header Pattern

```css
header {
  background: var(--color-bg-primary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-2);
  margin-bottom: var(--spacing-xl);
}

header h1 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

header .subtitle {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}
```

### Section Pattern

```css
.section {
  margin-bottom: var(--spacing-xl);
}

.section-header {
  background: var(--color-bg-primary);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  border-bottom: 3px solid var(--color-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-2);
}

.section-header h3 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.section-content {
  background: var(--color-bg-primary);
  padding: var(--spacing-md);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
  box-shadow: var(--shadow-2);
}
```

### Grid Patterns

**Agent Grid:**
```css
.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-md);
}
```

**Card Grid:**
```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--spacing-md);
}
```

**Responsive Breakpoints:**
- No media queries needed for HTML-only dashboards (use auto-fill)
- For specific breakpoints, use: `@media (max-width: 768px) { grid-template-columns: 1fr; }`

---

## Implementation Guide

### Step 1: Embed CSS Variables

Copy the complete CSS variables block from the [Design Tokens](#design-tokens-css-variables) section into the `<style>` tag at the top of your HTML file, inside `:root {}`.

### Step 2: Apply Base Styles

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family-sans);
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  line-height: var(--line-height-normal);
  padding: var(--spacing-xl);
}
```

### Step 3: Use Semantic Class Names

- Use `.btn-primary` not `.blue-button`
- Use `.card` not `.white-box`
- Use `.badge-status-running` not `.green-badge`
- Follow BEM-like naming: `.card-header`, `.card-body`, `.card-footer`

### Step 4: Replace Hardcoded Values

**Before:**
```css
.button {
  background: #3b82f6;
  padding: 10px 20px;
  border-radius: 6px;
}
```

**After:**
```css
.button {
  background: var(--color-primary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
}
```

### Step 5: Maintain HTML-Only Constraints

- All styles must be in `<style>` tag (no external CSS files)
- No build step required
- No preprocessors (Sass, Less)
- Use CSS variables for all design tokens

---

## Migration Strategy

### Phase 1: New Dashboards

- All new dashboards MUST use the design system
- Copy CSS variables block into new dashboard
- Use semantic class names from component specs

### Phase 2: High-Traffic Dashboards

Migrate these dashboards first:
1. `agent_runner_cockpit.html` (most used)
2. `cockpit_batch_review.html` (critical workflow)
3. `artifact_review_dashboard.html` (review interface)

**Migration Steps:**
1. Add CSS variables block to `<style>` tag
2. Replace hardcoded colors with variables
3. Replace hardcoded spacing with variables
4. Update component classes to match specs
5. Test visual consistency

### Phase 3: Remaining Dashboards

- Gradually migrate remaining dashboards
- Document any deviations and rationale
- Update this spec if patterns emerge

### Common Replacements

| Old Pattern | New Pattern |
|-------------|-------------|
| `#3b82f6` or `#007bff` | `var(--color-primary)` |
| `#10b981` or `#28a745` | `var(--color-success)` |
| `#ef4444` or `#dc3545` | `var(--color-error)` |
| `padding: 20px` | `padding: var(--spacing-xl)` |
| `border-radius: 8px` | `border-radius: var(--radius-lg)` |
| `box-shadow: 0 2px 4px rgba(0,0,0,0.1)` | `box-shadow: var(--shadow-2)` |

---

## Component Examples

### Complete Button Example

```html
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-secondary">Secondary Action</button>
<button class="btn btn-success">Success Action</button>
<button class="btn btn-danger">Danger Action</button>
<button class="btn btn-primary" disabled>Disabled</button>
```

```css
.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: background var(--transition-base) var(--transition-ease);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-secondary {
  background: var(--color-gray-500);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-gray-600);
}

.btn-success {
  background: var(--color-success);
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: var(--color-success-hover);
}

.btn-danger {
  background: var(--color-error);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: var(--color-error-hover);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Complete Card Example

```html
<div class="card">
  <div class="card-header">
    <h3>Card Title</h3>
  </div>
  <div class="card-body">
    <p>Card content goes here.</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">Action</button>
  </div>
</div>
```

```css
.card {
  background: var(--color-bg-primary);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-2);
  margin-bottom: var(--spacing-md);
}

.card-header {
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
  margin: calc(-1 * var(--spacing-md)) calc(-1 * var(--spacing-md)) var(--spacing-md);
}

.card-body {
  padding: 0; /* Header and footer handle padding */
}

.card-footer {
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--color-border);
  margin: var(--spacing-md) calc(-1 * var(--spacing-md)) calc(-1 * var(--spacing-md));
  display: flex;
  gap: var(--spacing-sm);
}
```

### Complete Badge Example

```html
<span class="badge badge-status-running">RUNNING</span>
<span class="badge badge-status-idle">IDLE</span>
<span class="badge badge-status-waiting">WAITING_REVIEW</span>
<span class="badge badge-status-blocked">BLOCKED</span>

<span class="badge badge-state-pre-evt">PRE_EVT</span>
<span class="badge badge-agent-intelligence">Intelligence</span>
```

```css
.badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
}

.badge-status-running {
  background: var(--color-status-running-bg);
  color: var(--color-status-running);
}

.badge-status-idle {
  background: var(--color-status-idle-bg);
  color: var(--color-status-idle);
}

.badge-status-waiting {
  background: var(--color-status-waiting-bg);
  color: var(--color-status-waiting);
}

.badge-status-blocked {
  background: var(--color-status-blocked-bg);
  color: var(--color-status-blocked);
}

.badge-state-pre-evt {
  border-left: 3px solid var(--color-state-pre-evt);
  background: var(--color-state-pre-evt-light);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  text-transform: none;
}

.badge-agent-intelligence {
  background: var(--color-agent-intelligence-bg);
  color: var(--color-agent-intelligence);
}
```

### Complete Form Example

```html
<div class="filter-panel">
  <div class="filter-group">
    <label for="state-filter">State:</label>
    <select id="state-filter">
      <option value="">All States</option>
      <option value="PRE_EVT">PRE_EVT</option>
    </select>
  </div>
  <div class="filter-group">
    <label for="search">Search:</label>
    <input type="text" id="search" placeholder="Search...">
  </div>
</div>
```

```css
.filter-panel {
  background: var(--color-bg-primary);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-2);
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.filter-group {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.filter-group label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.filter-group select,
.filter-group input[type="text"] {
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  background: var(--color-bg-primary);
}

.filter-group select:focus,
.filter-group input[type="text"]:focus {
  outline: 2px solid var(--color-primary-light);
  outline-offset: 2px;
  border-color: var(--color-primary);
}
```

---

## Accessibility Guidelines

### Color Contrast

All color combinations must meet WCAG AA standards:
- Normal text: 4.5:1 contrast ratio minimum
- Large text (18px+): 3:1 contrast ratio minimum
- Interactive elements: 3:1 contrast ratio minimum

### Focus States

All interactive elements must have visible focus indicators:

```css
button:focus,
input:focus,
select:focus,
a:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

### Semantic HTML

- Use `<button>` for actions, not `<div>` with onclick
- Use `<nav>` for navigation
- Use proper heading hierarchy (h1 → h2 → h3)
- Use `<label>` for form inputs
- Use ARIA labels when needed

---

## Version History

- **1.0.0** (2026-01-20): Initial design system specification

---

## Questions or Updates

If you need to extend this design system or have questions about implementation, document the rationale and update this specification to maintain consistency across all dashboards.
