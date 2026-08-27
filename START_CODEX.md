# One-time prompt to start Codex autonomously

Use this after copying this planning bundle into the root of the `aws-document-rag` repository.

---

Read `AGENTS.md`, `PLAN.md`, `docs/plan/PROGRESS.md`, `docs/plan/GATES.md` and every phase file under `docs/plan/phases/` before starting.

You are responsible for advancing this repository autonomously from the current phase through the final phase.

Follow the phase order strictly. `AGENTS.md` is the permanent operating policy.

For each phase, independently:

1. inspect the real repository state;
2. create the phase branch;
3. implement the plan;
4. run all applicable checks;
5. update documentation and `PROGRESS.md`;
6. commit;
7. push;
8. create a PR;
9. monitor/fix CI;
10. merge the PR when green and when no critical gate is pending;
11. update local `main` and continue to the next phase.

Do not stop for routine implementation choices, branch creation, commits, pushes, PRs or merges. Make a sensible engineering decision, document it, and continue.

STOP and ask the user only when `AGENTS.md` or `GATES.md` requires a critical gate, or when required authentication/credentials are genuinely unavailable and cannot be resolved from the environment.

At a critical gate, do all preparatory work first. Then present a concise gate report containing the exact proposed action, infrastructure/IAM changes, current pricing verification where relevant, bounded expected cost, security consequences, rollback/disable path, and what you need the user to approve. Do not perform the gated action until approved.

Never bypass a gate to keep moving.

CI must exist from the beginning and evolve with every phase. CD must not be enabled until the manual deployment is proven stable and Gate E is approved.

Begin with the current phase recorded in `docs/plan/PROGRESS.md`.
