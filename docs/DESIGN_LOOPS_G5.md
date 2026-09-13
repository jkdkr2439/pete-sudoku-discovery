# Pete UI Design Loops — G5

Date: 2026-09-14
Target: src/pete_discovery/static/
Render viewport: 1600 x 1300

## Input state

The G4 UI exposes all required information but behaves like a document made of independent cards.

Measured gaps from the first render:

1. The title occupies about one quarter of the first viewport and delays the running state.
2. Architecture is explained by three static cards; the active IPOD route is not visible as a connected process.
3. Substrate, Sandbox and source viewer are spatially correct but do not read as one instrument.
4. The Sudoku board lacks 3 x 3 visual grouping, reducing scan speed for the human observer.
5. Evidence begins below the fold without a compact live summary.

## Collapse metrics

- H1 — Authority: the substrate board must be the largest single visual object.
- H2 — Process: current phase must be visible without reading event text.
- H3 — Separation: Sandbox must remain visually smaller and distinct.
- H4 — Trace: current file/function/source must remain visible beside the world.
- H5 — Density: core state should fit in the first 1300 px at 1600 px width.
- H6 — Honesty: display changes must not alter cognition, Fieldmap, body or substrate.

## Loop 1 — hierarchy

Selected direction: compact laboratory console with a status header, live process rail, dominant world panel and stacked instrument column.

Pending render review.
## Loop 1 — render result

Passed H1, H3, H4 and H5. The substrate is the dominant object, Sandbox is visibly subordinate, source remains adjacent, and the evidence row enters the first viewport.

Observed gap: phase items lacked the selector class used by the renderer. Labels therefore collapsed horizontally and active/done states could not be applied. This is a display wiring defect, not a cognitive process defect.

## Loop 2 — process legibility

Input gap: phase nodes need explicit DOM identity so runtime phases can alter their state.

Collapsed change:
- bind every rail item to phase-step;
- retain one line for the phase name and one for its IPOD role;
- use done/active state from the runtime phase rather than decorative animation;
- keep source code and Sandbox in the same instrument column.

Pending render review.

## Loop 2 — render result

Passed H2. Six phase nodes now remain separated at 1600 px, their IPOD roles are legible, and SOLVED produces a complete rail rather than an unstructured text trace. Source route and world state still align spatially.

## Loop 3 — responsive and interaction polish

A 1280 x 900 render preserved the two-column authority hierarchy, kept controls on one line, and showed the phase rail without horizontal overflow. The viewport intentionally scrolls vertically because the 9 x 9 board must remain legible.

Final collapse:
- add minimum-width containment to grid instruments;
- add keyboard focus treatment to controls;
- expose runtime and code-phase changes through polite live regions;
- retain native vertical scrolling instead of shrinking the authoritative board below useful size.

All six collapse metrics pass. No cognition, Fieldmap, body, Sandbox, substrate or server behavior changed during G5.

## Final verification

- DOM id contract: PASS
- JavaScript syntax: PASS
- architecture boundary audit: PASS
- git diff whitespace check: PASS
- Python test suite: 12 passed in 46.50 seconds
- final render: runtime/ui-g5-final.png
- server error: none

Result: G5 PASS.
