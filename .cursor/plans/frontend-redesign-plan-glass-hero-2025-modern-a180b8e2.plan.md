<!-- a180b8e2-f251-4e08-9f88-cd4e05dba4cb abf9ebe2-b2d3-46fb-a941-b4a30313c275 -->
# Frontend Redesign Plan: "Glass & Hero" (2025 Modern)

This plan transforms the current functional UI into a polished, consumer-facing application with a focus on visual hierarchy, "glassmorphism" effects, and a prominent search experience.

## 1. Global Visual Updates

- **Theme**: Enhance `globals.css` with glassmorphism utility variables (translucent backgrounds).
- **Background**: Add a subtle "Aurora" or gradient background mesh to the `body` in [`frontend/app/layout.tsx`](frontend/app/layout.tsx).
- **Typography**: Ensure headings are bold and spacious (using existing Geist font).

## 2. Layout & Header

- **Floating Header**: Redesign the header in [`frontend/app/page.tsx`](frontend/app/page.tsx) (or extract to `components/layout/header.tsx`) to be sticky, semi-transparent (glass), and detached from the very top margin.
- **Hero Section**: Create a prominent area above the fold.
- Large, inviting text: "Find the Perfect Food for Your Cat".
- Centralized, large Search Bar.

## 3. Component Modernization

### Search Bar (`components/search/search-bar.tsx`)

- **Style**: Change to a large, pill-shaped input with a prominent shadow (`shadow-lg`).
- **Interaction**: Add focus rings and scale animation on focus.
- **Icon**: Move the search button inside the pill or make it a distinct floating action button.

### Product Card (`components/products/product-card.tsx`)

- **Glass Effect**: Use `bg-white/10` or `bg-card/50` with `backdrop-blur-md` for the card background.
- **Borders**: Add subtle gradients or white borders (`border-white/20`).
- **Layout**: Increase padding, use larger rounded corners (`rounded-xl` or `rounded-2xl`).
- **Hover**: Add `hover:scale-[1.02] `and `hover:shadow-xl` transitions.

### Filter Panel (`components/products/filter-panel.tsx`)

- **Refinement**: Simplify visual noise. Use lighter borders and "ghost" styling for inputs.
- **Structure**: Keep the sidebar but make it visually distinct (e.g., transparent background) or collapsible on mobile.

## 4. Implementation Steps

1.  **Styles**: Update [`frontend/app/globals.css`](frontend/app/globals.css) with new utility classes/variables for glass effects.
2.  **Components**:

- Refactor `SearchBar` for the "Hero" look.
- Refactor `ProductCard` for the "Glass" look.

3.  **Pages**:

- Update [`frontend/app/page.tsx`](frontend/app/page.tsx) to implement the Hero Layout + Sidebar Grid.
- Add the background graphic/gradient.

## 5. Mobile Responsiveness

- Ensure the sidebar collapses into a Sheet/Drawer on mobile (using standard responsive Tailwind classes).
- Stack the Hero section vertically.

### To-dos

- [ ] Update globals.css with glassmorphism variables and background patterns
- [ ] Redesign SearchBar component (Hero style)
- [ ] Redesign ProductCard component (Glass style)
- [ ] Refactor FilterPanel for cleaner aesthetic
- [ ] Rebuild Home Page with Hero Section and new Layout
