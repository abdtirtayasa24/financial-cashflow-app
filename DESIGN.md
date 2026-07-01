---
name: Financial Cashflow
description: Cashflow recording and BI reporting application
colors:
  deep-confident-blue: "#4f5390"
  deep-confident-blue-hover: "#464887"
  deep-confident-blue-active: "#3f407e"
  deep-confident-blue-soft: "#e7efff"
  deep-confident-blue-soft-hover: "#e0e8ff"
  deep-confident-blue-text: "#404378"
  deep-confident-blue-on: "#f6fcff"
  cool-canvas: "#f7fcff"
  cool-surface: "#f1f7ff"
  cool-surface-2: "#eef3ff"
  cool-surface-3: "#e7edfb"
  cool-surface-hover: "#e9eefd"
  carbon-ink: "#191b22"
  carbon-secondary: "#50525c"
  carbon-tertiary: "#666973"
  cool-border: "#dfe4f2"
  cool-border-strong: "#c6cad8"
  focus-ring: "#5f64a3"
  danger: "#826235"
  danger-hover: "#755422"
  danger-soft: "#eeedf0"
  danger-text: "#69502c"
  success: "#546d4f"
  success-soft: "#e5eff3"
  success-text: "#374b33"
  warning: "#8d8438"
  warning-soft: "#ebeee2"
  warning-text: "#5c530e"
  info: "#6a73ad"
  info-soft: "#e7efff"
  info-text: "#484e7b"
typography:
  heading-xl:
    fontFamily: "var(--font-inter), system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  heading-lg:
    fontFamily: "var(--font-inter), system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  heading-md:
    fontFamily: "var(--font-inter), system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  body:
    fontFamily: "var(--font-inter), system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  body-sm:
    fontFamily: "var(--font-inter), system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: "var(--font-inter), system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "normal"
  caption:
    fontFamily: "var(--font-inter), system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "0.02em"
  table-header:
    fontFamily: "var(--font-inter), system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "0.02em"
  mono:
    fontFamily: "SF Mono, Cascadia Code, Fira Code, Menlo, Consolas, monospace"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
rounded:
  sm: "4px"
  default: "6px"
  md: "8px"
  lg: "12px"
  full: "9999px"
spacing:
  "0": "0"
  xs: "4px"
  sm: "8px"
  md: "12px"
  base: "16px"
  lg: "20px"
  xl: "24px"
  "2xl": "32px"
  "3xl": "40px"
  "4xl": "48px"
  "5xl": "64px"
  "6xl": "96px"
components:
  button-primary:
    backgroundColor: "{colors.deep-confident-blue}"
    textColor: "{colors.deep-confident-blue-on}"
    rounded: "{rounded.default}"
    padding: "8px 16px"
  button-primary-hover:
    backgroundColor: "{colors.deep-confident-blue-hover}"
    textColor: "{colors.deep-confident-blue-on}"
    rounded: "{rounded.default}"
    padding: "8px 16px"
  button-primary-active:
    backgroundColor: "{colors.deep-confident-blue-active}"
    textColor: "{colors.deep-confident-blue-on}"
    rounded: "{rounded.default}"
    padding: "8px 16px"
  button-danger:
    backgroundColor: "{colors.cool-canvas}"
    textColor: "{colors.danger-text}"
    rounded: "{rounded.default}"
    padding: "8px 16px"
  button-danger-hover:
    backgroundColor: "{colors.danger}"
    textColor: "{colors.deep-confident-blue-on}"
    rounded: "{rounded.default}"
    padding: "8px 16px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.carbon-secondary}"
    rounded: "{rounded.default}"
    padding: "8px 16px"
  button-ghost-hover:
    backgroundColor: "{colors.cool-surface-hover}"
    textColor: "{colors.carbon-ink}"
    rounded: "{rounded.default}"
    padding: "8px 16px"
  button-sm:
    backgroundColor: "{colors.deep-confident-blue}"
    textColor: "{colors.deep-confident-blue-on}"
    rounded: "{rounded.sm}"
    padding: "4px 12px"
  input-default:
    backgroundColor: "{colors.cool-canvas}"
    textColor: "{colors.carbon-ink}"
    rounded: "{rounded.default}"
    padding: "8px 12px"
  input-focus:
    backgroundColor: "{colors.cool-canvas}"
    textColor: "{colors.carbon-ink}"
    rounded: "{rounded.default}"
    padding: "8px 12px"
  card:
    backgroundColor: "{colors.cool-surface}"
    textColor: "{colors.carbon-ink}"
    rounded: "{rounded.md}"
    padding: "20px"
  table-wrap:
    backgroundColor: "{colors.cool-surface}"
    textColor: "{colors.carbon-ink}"
    rounded: "{rounded.md}"
  badge-active:
    backgroundColor: "{colors.success-soft}"
    textColor: "{colors.success-text}"
    rounded: "{rounded.full}"
    padding: "2px 8px"
  badge-inactive:
    backgroundColor: "{colors.danger-soft}"
    textColor: "{colors.danger-text}"
    rounded: "{rounded.full}"
    padding: "2px 8px"
  sidebar-link:
    backgroundColor: "transparent"
    textColor: "{colors.carbon-secondary}"
    rounded: "{rounded.default}"
    padding: "8px 12px"
  sidebar-link-active:
    backgroundColor: "{colors.deep-confident-blue-soft}"
    textColor: "{colors.deep-confident-blue-text}"
    rounded: "{rounded.default}"
    padding: "8px 12px"
---

# Design System: Financial Cashflow

## 1. Overview

**Creative North Star: "The Precision Instrument"**

This is the design system for a financial cashflow recording and BI reporting application used daily by Finance Admins, Department Managers, and Management. The interface should feel like a well-calibrated instrument — every detail deliberate, every pixel earning its place. Confidence comes from clarity, not decoration.

The system is restrained by design. One accent color (Deep Confident Blue) carries primary actions and active states across the entire interface; everything else is cool neutral. Tactile and confident components respond to interaction with ambient shadow elevation and precise state transitions. Typography is a single well-tuned sans (Inter) at a fixed rem scale — no fluid sizing, no display fonts, no decorative pairings. The hierarchy is built from weight, size, and space alone.

This system explicitly rejects: generic SaaS dashboard templates (card grids, hero-metric templates, default blue-on-white scaffolds); purple-ish AI slop (violet gradients, glassmorphism, aurora backgrounds, gradient text); generic AI-generated design (identical card grids, uppercase tracked eyebrows on every section, numbered section markers, decorative motion); and consumer-playful aesthetics (cartoonish rounding, playful copy, decorative color).

**Key Characteristics:**
- Restrained color strategy: one accent ≤10% of any screen, cool neutrals everywhere else
- Fixed rem type scale (1.125–1.2 ratio) with tabular numbers for financial data
- Ambient shadow elevation — surfaces carry gentle depth at rest
- Tactile and confident components with full state vocabulary (hover, focus, active, disabled, loading)
- Structural responsive behavior — sidebar collapses, tables scroll, not fluid typography
- WCAG 2.1 AA throughout — all text ≥4.5:1, touch targets ≥40px, reduced motion supported
- Semantic z-index scale (sticky 100 → overlay 150 → sidebar 200 → modal 500 → toast 600)

## 2. Colors

The palette is a cool, slightly blue-tinted neutral system anchored by one deep accent. Neutrals carry 90%+ of any screen; the accent is reserved for primary actions, active states, and focus rings. All semantic states (danger, success, warning, info) use soft tinted backgrounds with dark readable text — never color-only indicators.

Canonical format is OKLCH; hex values in frontmatter are sRGB approximations for tooling compatibility.

### Primary
- **Deep Confident Blue** (#4f5390 / oklch(0.44 0.13 245)): The single accent. Used for primary buttons, active sidebar links, focus rings, and link text. Never decorative. Its rarity is its strength — when it appears, it means "act here" or "this is current."
- **Deep Confident Blue Hover** (#464887 / oklch(0.40 0.14 245)): Hover state on primary buttons.
- **Deep Confident Blue Active** (#3f407e / oklch(0.37 0.14 245)): Pressed state on primary buttons.
- **Deep Confident Blue Soft** (#e7efff / oklch(0.95 0.025 245)): Very light tint for active sidebar link backgrounds and selected states.
- **Deep Confident Blue Text** (#404378 / oklch(0.38 0.12 245)): Text color used with the soft tint — links, active nav text, accent-colored labels.

### Neutral
- **Cool Canvas** (#f7fcff / oklch(0.992 0.002 255)): Page background. Near-white with the faintest cool tint. Never warm, never cream.
- **Cool Surface** (#f1f7ff / oklch(0.975 0.004 255)): Cards, table wrappers. One step darker than canvas.
- **Cool Surface 2** (#eef3ff / oklch(0.965 0.005 255)): Sidebar background, table headers. A distinct second layer for navigation and structural surfaces.
- **Cool Surface 3** (#e7edfb / oklch(0.945 0.006 255)): Default badge background, tertiary panels.
- **Cool Surface Hover** (#e9eefd / oklch(0.95 0.006 255)): Hover state for table rows, sidebar links, ghost buttons.
- **Carbon Ink** (#191b22 / oklch(0.22 0.015 255)): Primary text color. Near-black with slight cool tint. 16.64:1 contrast on canvas.
- **Carbon Secondary** (#50525c / oklch(0.44 0.012 255)): Secondary text — table data, descriptions. 7.52:1 on canvas, 6.99:1 on sidebar.
- **Carbon Tertiary** (#666973 / oklch(0.52 0.01 255)): Tertiary text — timestamps, metadata, captions. 5.30:1 on canvas.
- **Cool Border** (#dfe4f2 / oklch(0.92 0.005 255)): Default borders and dividers.
- **Cool Border Strong** (#c6cad8 / oklch(0.84 0.008 255)): Form control borders, stronger dividers.
- **Focus Ring** (#5f64a3 / oklch(0.50 0.13 245)): Focus outline color, a lighter variant of the accent.

### Semantic States
- **Danger** (#826235 / oklch(0.52 0.19 27)): Destructive actions, error text. Soft variant (#eeedf0) for badge backgrounds; text variant (#69502c) for readable danger text on soft backgrounds.
- **Success** (#546d4f / oklch(0.52 0.13 150)): Active status, approved transactions. Soft (#e5eff3) for backgrounds; text (#374b33) on soft.
- **Warning** (#8d8438 / oklch(0.62 0.14 70)): Pending status. Soft (#ebeee2) for backgrounds; text (#5c530e) on soft.
- **Info** (#6a73ad / oklch(0.55 0.12 240)): Draft status. Soft (#e7efff) for backgrounds; text (#484e7b) on soft.

### Named Rules
**The One Voice Rule.** Deep Confident Blue is the only accent. It appears on ≤10% of any screen — primary buttons, active nav, focus rings, links. Its rarity is the point. When everything is accented, nothing is.

**The No-Color-Only Rule.** Every status indicator pairs color with text and a dot. A green badge says "Active" with a dot — never just a green swatch. Color supports meaning; text carries it.

## 3. Typography

**Display/Body Font:** Inter (via next/font/google, CSS variable `--font-inter`) with system-ui fallback
**Mono Font:** SF Mono, Cascadia Code, Fira Code, Menlo, Consolas

**Character:** One well-tuned sans carries the entire UI — headings, buttons, labels, data, body. No display font, no pairing. Hierarchy comes from weight (400 → 500 → 600), size (fixed rem scale), and space. Tabular numbers are available via `.tnum` for all financial data.

### Hierarchy
- **Heading XL** (600, 1.5rem/24px, 1.25, -0.01em): Page titles (`h1`). One per page.
- **Heading LG** (600, 1.25rem/20px, 1.25, -0.01em): Section titles (`h2`), login card title.
- **Heading MD** (600, 1.125rem/18px, 1.25, -0.01em): Subsection titles (`h3`), login card brand name.
- **Body** (400, 1rem/16px, 1.5, normal): Default body text, form input text. Max line length 65–75ch for prose.
- **Body SM** (400, 0.875rem/14px, 1.5, normal): Secondary text, table data, nav items, descriptions.
- **Label** (500, 0.875rem/14px, 1.5, normal): Form labels, button text, table row primary data.
- **Caption** (500, 0.75rem/12px, 1.5, 0.02em): Table headers (uppercase), section labels in sidebar nav (uppercase), timestamps, metadata.
- **Mono** (400, 0.75rem/12px, 1.5, normal): Settings keys, code-like data. Uses `--font-mono` stack.

### Named Rules
**The Fixed Scale Rule.** No `clamp()`, no fluid sizing. Product UI needs spatial predictability — a heading in a sidebar must not shrink because the viewport is narrow. The type scale is fixed rem; responsive behavior is structural (layout changes), not typographic.

**The Tabular Numbers Rule.** All financial figures — amounts, balances, codes — use `font-variant-numeric: tabular-nums` (via `.tnum` class). Numbers align in columns; digits don't dance.

## 4. Elevation

This system uses ambient shadow elevation. Surfaces carry gentle depth at rest — not flat-to-shadow on interaction only, but a consistent tonal + shadow hierarchy that communicates layering. The shadow vocabulary is subtle: the difference between a card and the page beneath it is a 1px border plus a barely-there shadow, not a dramatic lift.

Depth is also conveyed through tonal layering: the sidebar is one step darker than the main canvas, table headers are one step darker than table rows, and hover states are a gentle step toward the next surface level. Shadows reinforce this, they don't replace it.

### Shadow Vocabulary
- **Ambient XS** (`0 1px 2px 0 rgb(0 0 0 / 0.04)`): Subtle resting depth. Used on elements that need the faintest separation from their parent.
- **Ambient SM** (`0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px 0 rgb(0 0 0 / 0.04)`): Default card elevation. Cards at rest.
- **Ambient MD** (`0 4px 12px -2px rgb(0 0 0 / 0.08), 0 2px 6px -2px rgb(0 0 0 / 0.05)`): Login card, elevated panels. Used when a surface needs to feel lifted from the page.
- **Ambient LG** (`0 12px 32px -4px rgb(0 0 0 / 0.12), 0 4px 12px -2px rgb(0 0 0 / 0.06)`): Mobile sidebar shadow. Used only for the sliding sidebar on mobile.

### Named Rules
**The Ambient Rule.** Shadows are part of the resting state, not a reaction. A card at rest has shadow-sm; it doesn't need to "lift" on hover to prove it's interactive. Hover changes the background tone, not the shadow.

## 5. Components

Components are tactile and confident — they respond to interaction with clear, immediate feedback. Every interactive component has default, hover, focus-visible, active, and disabled states. The same component vocabulary repeats across every screen; variation without purpose is noise.

### Buttons
- **Shape:** 6px radius (var(--radius)), 38px min-height, 14px font, 500 weight. Small variant: 4px radius, 30px min-height, 12px font.
- **Primary:** Deep Confident Blue background, near-white text. Hover darkens to accent-hover; active presses to accent-active. Full-width on login form.
- **Danger:** Canvas background, danger-text color, danger-tinted border. Hover fills with danger red and flips text to white. Used for delete actions.
- **Ghost:** Transparent background, secondary text, strong border. Hover fills with surface-hover and darkens text. Used for secondary actions (deactivate, cancel).
- **Focus:** 3px ring at 12-15% accent opacity, no outline. Visible on keyboard navigation.
- **Icon Buttons:** 40×40px, padding: 0, 22px icons. Used in topbar (menu, notifications). `flex-shrink: 0` to prevent icon compression.

### Inputs / Fields
- **Style:** 6px radius, 38px min-height, 14px font, strong border (cool-border-strong). Canvas background. Placeholder text uses carbon-tertiary (passes 4.5:1).
- **Focus:** Border shifts to accent blue; 3px box-shadow ring at 12% accent opacity. No outline.
- **Hover:** Border darkens slightly. Disabled state: surface-2 background, tertiary text, not-allowed cursor.
- **Select:** Native select with custom dropdown arrow (inline SVG), appearance: none. Right-padded to clear the arrow.
- **Field structure:** Label above input (14px, 500 weight), optional hint below (12px, tertiary).

### Cards / Containers
- **Corner Style:** 8px radius (var(--radius-md)).
- **Background:** Cool Surface (#f1f7ff), one step darker than canvas.
- **Border:** 1px cool-border.
- **Shadow Strategy:** Ambient SM at rest (see Elevation). No shadow change on hover.
- **Internal Padding:** 20px (var(--space-5)); 16px on mobile.
- **Usage:** Form containers, settings panels. Not used for decoration — cards group related form fields or data sections.

### Tables
- **Wrapper:** 8px radius, 1px cool-border, Cool Surface background, `overflow-x: auto` for horizontal scroll on mobile.
- **Headers:** 12px, 500 weight, uppercase, 0.02em tracking, carbon-tertiary text, surface-2 background, sticky top.
- **Rows:** 14px body text, bottom border, hover state (surface-hover background). Last row has no border.
- **Data alignment:** Tabular numbers (`.tnum`) right-aligned for amounts and codes. Primary data in 500 weight; secondary data in carbon-secondary.
- **Row actions:** Flex row, 8px gap, ghost/danger button variants.

### Badges
- **Shape:** Full radius (pill), 12px font, 500 weight, 2px×8px padding.
- **Variants:** Active (success-soft/success-text), Inactive (danger-soft/danger-text), Pending (warning-soft/warning-text), Approved (success), Rejected (danger), Draft (info), Voided (surface-3/tertiary).
- **Dot:** 6px circular dot in currentColor at 70% opacity, paired with text label. Never color-only.

### Navigation
- **Sidebar:** 248px fixed left, surface-2 background, cool-border right divider. Brand mark (28px accent square with dollar-sign SVG) + "Financial Cashflow" at top. Nav items grouped: Main (Dashboard) and Administration (Users, Departments, Categories, Payment Methods, Cash Accounts, Settings).
- **Nav Links:** 14px, 500 weight, carbon-secondary text, 6px radius, 36px min-height. 18px lucide icons at 70% opacity. Active state: accent-soft background, accent-text color, 600 weight, full-opacity icon. Hover: surface-hover background, ink text.
- **Nav Labels:** 12px, 500 weight, uppercase, 0.02em tracking, carbon-tertiary. Used for section grouping ("Administration"), not as decorative eyebrows.
- **Sidebar Footer:** User avatar (32px, accent-soft circle with initials), name + role, sign-out button (full width, ghost style, danger-text on hover).
- **Topbar:** 56px, sticky, canvas background, bottom border. Left: hamburger menu (mobile only). Right: notification bell (40×40 icon button).
- **Mobile:** Sidebar slides in from left with translateX, backdrop overlay at 150 z-index, sidebar at 200. Closes on link click or backdrop click. Hamburger menu button appears at <768px.

### Empty States
- **Structure:** Centered icon circle (48px, surface-2 background, tertiary icon) → title (14px, 600, ink) → description (14px, secondary, max 32ch).
- **Voice:** Teaching, not declarative. "Create your first user using the form above" — not "No users found."
- **Contextual icons:** Each empty state uses an SVG icon relevant to its content (users, building, tags, credit card, wallet, settings, chart).

### Skeleton Loading
- **Shimmer animation:** Linear gradient sweep (surface-2 → surface-3 → surface-2), 1.5s linear infinite. Reduced motion: static surface-3 background, no animation.
- **Variants:** `--text` (14px height), `--title` (24px height, 200px width), `--row` (40px height, full width).

### Login Card
- **Standalone:** Full-screen surface-2 background, centered card (380px max-width, 12px radius, shadow-md).
- **Structure:** Brand mark + name → "Welcome back" heading → subtitle → form (email, password, full-width button) → inline error with icon.
- **Mobile:** Card becomes borderless, shadowless, full-width (transparent background) at <480px.

## 6. Do's and Don'ts

### Do:
- **Do** use Deep Confident Blue (#4f5390) exclusively for primary actions, active states, and focus rings. Its scarcity is its power.
- **Do** use tabular numbers (`.tnum`) for all financial figures, amounts, and codes. Numbers must align in columns.
- **Do** pair every status color with a text label and a dot. "Active" with a green dot — never a green swatch alone.
- **Do** build responsive behavior structurally — collapse the sidebar, scroll tables horizontally, stack form rows. Not fluid typography.
- **Do** use the fixed rem type scale (12/14/16/18/20/24px). No `clamp()`, no fluid sizing. Product UI needs spatial predictability.
- **Do** include full state coverage on every interactive component: default, hover, focus-visible, active, disabled. Half the states is half the component.
- **Do** use teaching empty states that explain what to do next, not just what's missing.
- **Do** use ambient shadows at rest. Cards don't need to "lift" on hover to prove they're interactive.
- **Do** verify contrast at ≥4.5:1 for all text against its actual background surface — secondary text on the sidebar is a different ratio than on the canvas.

### Don't:
- **Don't** use border-left or border-right greater than 1px as a colored accent stripe. Full borders, background tints, or nothing.
- **Don't** use gradient text (`background-clip: text` + gradient). Solid color only. Emphasis via weight or size.
- **Don't** use glassmorphism — blurs and glass cards as decoration. Rare and purposeful, or nothing.
- **Don't** build the hero-metric template (big number, small label, supporting stats, gradient accent). It's a SaaS cliché.
- **Don't** use identical card grids with icon + heading + text repeated endlessly. Vary the structure to match the content.
- **Don't** put tiny uppercase tracked eyebrows above every section. One named kicker as a deliberate system is voice; an eyebrow on every section is AI grammar.
- **Don't** use numbered section markers (01 / 02 / 03) as default scaffolding. Numbers earn their place only when the section IS a sequence and order carries information.
- **Don't** use purple/violet gradient accents, aurora backgrounds, or any "purple-ish AI slop" aesthetic.
- **Don't** use warm cream, sand, or beige body backgrounds. The neutrals are cool-tinted toward the accent hue, never toward warmth.
- **Don't** introduce a second accent color. One voice, one accent. If a second color seems necessary, use a semantic state color (danger/success/warning/info) instead.
- **Don't** animate layout properties (width, height, top, left). Use transform and opacity for motion.
- **Don't** ship any animation without a `prefers-reduced-motion` alternative (crossfade or instant).
- **Don't** use `window.confirm` for destructive actions in production — use inline confirmation or a proper dialog.
- **Don't** create nested cards. A card inside a card is always wrong.