# Separate GitHub Actions exercise (Task 6.6)

The assignment requires a small throwaway repository, with a 2-version
Python matrix and both a deliberately failed and passing CI run.
Create a SEPARATE temporary repository (e.g. visionguard-ci-toy).
Copy `toy.yml` to `.github/workflows/toy.yml` in that temporary repository.
Copy `test_calculator.py` to its root.

1. Push a first version where `test_addition` expects `2 + 2 == 5`.
   It should give an honest RED CI run. Capture the Actions page.
2. Change only the assertion to `2 + 2 == 4`, commit and push again.
   It should give a GREEN CI run for 3.11 and 3.12. Capture the page.
3. Do not intentionally fail the real VisionGuard CI workflow.

Keep repository secrets in GitHub Settings > Secrets and variables > Actions.
No secret values belong in workflow YAML.
