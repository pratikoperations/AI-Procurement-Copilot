# Mobile Readiness Assurance Pack

## Target

Produce defensible evidence that the hosted interview and portfolio application is usable on representative Android, foldable and tablet browser viewports without changing procurement logic or authority.

## Frozen starting baseline

- Main SHA: `970786c185dc8dffb57c469e8798fe7ce8f38ceb`
- Native mobile application: excluded
- Framework migration: excluded
- Business-logic changes: prohibited
- Human procurement review: mandatory

## Governed viewport matrix

| Profile | CSS viewport | Intended coverage |
| --- | ---: | --- |
| Small Android | 360 × 740 | constrained phone and browser chrome |
| Standard Android | 390 × 844 | common modern Android phone |
| Large Android | 412 × 915 | large phone |
| Foldable inner display | 673 × 841 | foldable and compact tablet |
| Tablet portrait | 768 × 1024 | portrait tablet |
| Tablet landscape | 1024 × 768 | landscape tablet |

## Automated acceptance contract

Each viewport must prove:

1. the Streamlit application renders;
2. the page has no horizontal overflow;
3. visible primary buttons are touch-operable;
4. SourceMate opens, remains within the viewport and closes;
5. the SourceMate input remains focusable;
6. browser-test failures retain trace, screenshot and video evidence;
7. the application remains read-only and human-review gated.

## Responsive implementation contract

- Use dynamic viewport height where supported.
- Respect safe-area insets.
- Keep touch targets at least 44 CSS pixels high on coarse pointers.
- Preserve internal table scrolling while preventing page-level horizontal scroll.
- Use one column on narrow touch screens and two columns on foldable/tablet touch screens.
- Keep fixed overlays clear of safe areas and core Streamlit controls.
- Respect reduced-motion preferences.

## Real-device acceptance ledger

Automated emulation is necessary but not sufficient for the final score above 9.5.
Complete the following ledger against the hosted application after automated CI is green.

| Device/browser | Orientation | Font/zoom | Core workflow | SourceMate | Tables | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Samsung Android / Chrome | Portrait | Default | Pending | Pending | Pending | Pending | Pending |
| Samsung Android / Chrome | Landscape | Default | Pending | Pending | Pending | Pending | Pending |
| Android / Chrome | Portrait | 200% zoom | Pending | Pending | Pending | Pending | Pending |
| Samsung Internet | Portrait | Default | Pending | Pending | Pending | Pending | Pending |
| Foldable or tablet | Portrait | Large system font | Pending | Pending | Pending | Pending | Pending |
| Foldable or tablet | Landscape | Default | Pending | Pending | Pending | Pending | Pending |

## Completion gate

The pack can be represented as above 9.5/10 only when:

- Quality Checks pass;
- Mobile Browser Acceptance passes across all six profiles;
- no unresolved browser-test defect remains;
- hosted real-device acceptance is completed with screenshots;
- no material procurement or authority behavior changes;
- the feature branch receives governed final review before merge.
