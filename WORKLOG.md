# Worklog

## 2026-08-06 — Project Development Policy v1

### Policy Work

- Confirmed `fiverocksgames/investment-manager` as the canonical development repository.
- Created Issue #13 and branch `agent/project-policy-v1`.
- Added `PROJECT_POLICY.md` as the durable development-policy document.
- Standardized the Issue, documentation-first, branch, Draft PR, CI, approval, merge, and Issue-close workflow.
- Separated constitution documents from living operational documents.
- Updated contributor guidance to preserve Requirement traceability and AI handoff quality.

### Policy Completion

- Canonical repository decision documented.
- Project workflow documented as: Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close.
- Direct commits to `main` prohibited.
- Draft PR and explicit user-approval requirements documented.
- Security, architecture, data-integrity, and investment-safety priorities retained.

### Policy Validation

- Documentation changes are committed on `agent/project-policy-v1`.
- Draft PR #14 was created.
- Documentation run #40 failed only because the new Worklog entry reused headings from the previous entry.
- This follow-up commit gives the new entry unique headings so Markdownlint can pass.

### Policy Remaining Work

- Verify the new Documentation CI run.
- Mark PR #14 ready for review only after CI succeeds.
- Merge only after explicit user approval.
- Begin Phase 2 Data Platform design after policy adoption.
- Validate PWA installation and offline behavior separately.
- Generate `package-lock.json` and change CI from `npm install` to `npm ci`.
- Create user-owned database tables, default-deny RLS policies, and cross-user isolation tests.

### Policy Next Steps

1. Verify the replacement Documentation run.
2. Record the exact successful run evidence.
3. Mark PR #14 ready for review.
4. Request user approval before merge.
5. After merge, create the Phase 2 Data Platform design Issue.

### Policy Cautions

- The canonical-repository decision does not move or synchronize external repositories.
- Tool limitations must not weaken Issue, CI, review, or approval controls.
- Authentication proves identity but does not authorize access to future user-owned tables.
- PWA offline behavior has not yet been validated and must not be described as complete.

### Policy Issue, Branch, and PR

- Repository: `fiverocksgames/investment-manager`
- Issue: #13 — `docs: establish project development policy v1`
- Branch: `agent/project-policy-v1`
- PR: #14 — `docs: establish project development policy v1`
- Status: Draft PR; documentation fix pushed after run #40 failure

## 2026-08-06 — Phase 1 Closure

### Today’s Work

- Synchronized the Phase 1 implementation into `e20cboy/investment-manager`.
- Verified GitHub Pages deployment succeeded in the upstream repository.
- Registered `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` as upstream repository Variables.
- Verified the deployed app detected the Supabase configuration.
- Completed Google OAuth sign-in against the deployed application.
- Verified session persistence after page refresh and browser restart.
- Verified sign-out completed successfully.
- Created Issue #11 and branch `agent/phase-1-closeout` to record Phase 1 completion and prepare Phase 2.

### Completed

- React, TypeScript, Vite, Tailwind CSS, PWA manifest, and GitHub Pages baseline.
- Supabase browser client and authentication context.
- Google OAuth sign-in and sign-out.
- Session restoration and auth-state subscription.
- Safe missing-configuration behavior.
- GitHub Actions Variables wiring for public Supabase configuration.
- Production deployment and browser-level authentication validation.

### Validation Evidence

- Upstream GitHub Pages deployment completed successfully.
- Deployed application displayed Google sign-in after repository Variables were included in a new build.
- Google sign-in returned to the deployed application successfully.
- Authentication remained active after page refresh.
- Authentication remained active after browser restart.
- Sign-out returned the application to the signed-out state.

### Incomplete

- Validate PWA installation and offline behavior in a browser.
- Generate `package-lock.json` and change CI from `npm install` to `npm ci`.
- Create user-owned database tables, default-deny RLS policies, and cross-user isolation tests.
- Implement Phase 2 market, macro, and FX data collection.

### Next Work

1. Establish the canonical-repository development policy.
2. Create the Phase 2 Data Platform design issue and provider-independent data model.
3. Define freshness, source metadata, caching, retry, and failure-state rules before implementation.

### Cautions

- Authentication proves identity but does not authorize access to future user-owned tables.
- Default-deny RLS and isolation tests are required before storing personal portfolio data.
- Browser-visible publishable keys are not privileged credentials.
- PWA offline behavior has not yet been validated and must not be described as complete.

## 2026-08-06 — Upstream Synchronization

The Phase 1 frontend and Supabase authentication baseline was copied into the upstream repository through `agent/import-phase-1` and merged in upstream PR #4.

## 2026-08-05 — Supabase Authentication Bootstrap

PR #6 added the Supabase browser client, authentication context, Google OAuth actions, setup guidance, security boundaries, and feature traceability. Frontend run #15 and Documentation run #33 passed before merge.

## 2026-08-05 — Phase 1 Frontend Bootstrap

PR #4 established the React, TypeScript, Vite, Tailwind CSS, PWA, and GitHub Pages baseline. Frontend run #7 and Documentation run #26 passed before merge.

## 2026-08-05 — Project Bootstrap

PR #1 established governance, specifications, templates, documentation CI, ownership, and the MIT License. Documentation run #12 passed.
