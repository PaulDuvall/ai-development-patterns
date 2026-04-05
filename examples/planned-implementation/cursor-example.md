# Cursor Planning Example

This example demonstrates how to use Cursor's Composer and Chat features to plan and implement a React component library.

## Scenario
Building a reusable design system component library for a React application with TypeScript, Storybook, and automated testing.

## Step 1: Using Cursor's Composer for Planning

Open Cursor's Composer (Cmd+I / Ctrl+I) and describe the project:

```
Create a React component library with the following requirements:
- TypeScript support with strict typing
- Storybook for component documentation
- Jest testing with React Testing Library
- CSS-in-JS with styled-components
- Rollup for bundling
- Publishing to npm
- Components: Button, Input, Modal, Card

Start by creating an implementation plan before writing any code.
```

## Step 2: Cursor Generated Plan

**Cursor Planning Output:**

```markdown
# React Component Library Implementation Plan

## Project Structure
```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.stories.tsx
│   │   ├── Button.test.tsx
│   │   └── index.ts
│   ├── Input/
│   ├── Modal/
│   └── Card/
├── index.ts
└── types/
    └── index.ts
```

## Implementation Steps

### Phase 1: Project Setup (1-2 hours)
1. Initialize TypeScript React project
2. Configure Rollup for library bundling
3. Setup Storybook with TypeScript
4. Configure Jest and React Testing Library
5. Setup styled-components with TypeScript

### Phase 2: Base Components (3-4 hours)
1. Create Button component with variants
2. Implement Input component with validation
3. Build Modal with accessibility features
4. Design Card component with flexible layouts

### Phase 3: Documentation & Testing (2-3 hours)
1. Write comprehensive Storybook stories
2. Implement unit tests for all components
3. Add integration tests for complex interactions
4. Generate TypeScript declarations

### Phase 4: Build & Publish (1 hour)
1. Configure Rollup build process
2. Setup npm publishing workflow
3. Create usage documentation
4. Test package installation

## Key Considerations
- Accessibility (WCAG 2.1 AA compliance)
- Tree-shaking support for optimal bundle size
- Consistent theming system
- Responsive design patterns
```

## Step 3: Interactive Plan Refinement

Use Cursor's chat (Cmd+L / Ctrl+L) to iterate on the plan:

```
This plan looks great! Can you expand the theming section? I need:
- Dark/light theme support
- Custom color palette system
- Typography scale
- Spacing/layout tokens

Also, add ESLint and Prettier configuration to Phase 1.
```

**Updated Plan Section:**

```markdown
### Phase 1: Project Setup (Updated - 2-3 hours)
1. Initialize TypeScript React project
2. Configure ESLint with React/TypeScript rules
3. Setup Prettier with team code style
4. Configure Rollup for library bundling
5. Setup Storybook with TypeScript
6. Configure Jest and React Testing Library
7. Setup styled-components with TypeScript

### Phase 2: Design System Foundation (New - 1-2 hours)
1. Create theme provider and context
2. Define color palette (light/dark variants)
3. Establish typography scale
4. Set spacing and layout tokens
5. Build theme switching mechanism
```

## Step 4: Execute with Cursor

Start implementation using the Composer with plan reference:

```
Let's start with Phase 1. Begin by creating the package.json and TypeScript configuration according to our plan.
```

Cursor then generates code following the established plan structure.

## Step 5: Plan Progress Tracking

Use Cursor's inline comments to track progress:

```typescript
// ✓ Phase 1 Complete: Project setup finished
// → Phase 2: Currently implementing Button component
// TODO: Phase 3: Testing and documentation pending

export const Button = styled.button<ButtonProps>`
  // Implementation following plan specifications
`;
```

## Benefits Demonstrated

1. **Structured Planning**: Composer breaks work into logical phases
2. **Interactive Refinement**: Easy to modify plan based on new requirements
3. **Contextual Implementation**: Code generation follows plan structure
4. **Progress Visibility**: Clear tracking of implementation status
5. **Team Alignment**: Shareable plan format for collaboration

## Cursor-Specific Features Used

- **Composer (Cmd+I)**: Multi-file code generation following plan specifications
- **Chat (Cmd+L)**: Plan iteration, refinement, and asking questions with @codebase context
- **@codebase / @file references**: Provides context awareness of existing project structure
- **Inline edits (Cmd+K)**: Targeted code changes within plan specifications
- **`/fix` command**: Addresses failing tests during implementation

This example demonstrates how Cursor's planning features create a structured approach to complex component library development.