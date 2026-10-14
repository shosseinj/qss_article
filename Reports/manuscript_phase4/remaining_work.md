# Remaining scientific work — deferred by the user

No raw N-MNIST/checkpoints exist on this system. The user confirmed this and requested future-work tracking. Existing Phase 3 blockers and draft final-test lock are preserved.

1. Supply original or clearly new trained weights, metadata, raw-event data, split and sample manifests with hashes and licenses. Recover run logs, resolved configs and per-example outputs when possible.
2. Integrate the test-independent completion policy into a portable fresh training runner; remove test-outcome recipe/quality feedback without weakening validity/leakage/hash checks. Audit historical test-access chronology.
3. Run a real pilot: strict checkpoint loading, clean reconstruction, reset/order/chunk checks, gradients and same-candidate legacy versus any-valid-success selection. Record exact example IDs and first-success steps.
4. Tune attack strength only on development data; measure literal counters and synchronized raw timings including serial/chunk sensitivity, warm-up and verification. Freeze the final protocol before test.
5. Evaluate full10,000-example clean official test and a predeclared attacked manifest (initial target1000 joint-correct examples if resources permit), across independently pretrained pipelines. Keep IDs, clean errors and denominators.
6. Train final-model classical-head and no-entangler controls with fixed frontend/split/training; retain parameter counts, compute and uncertainty. Old154–274-parameter local-Z development models are not these controls.
7. Collect prespecified real exemplar/state/probability/margin records for failures and survivors. No synthetic illustration or unexecuted budget interpolation supplies evidence.
8. Resolve historical grid runtime settings and perform gradient-coverage/alternative-surrogate/search-strength and independent raw-data audits before causal architecture claims.

No ASR, selection difference, test accuracy, timing dispersion, ablation effect or state-margin scatter was newly measured in this revision.
