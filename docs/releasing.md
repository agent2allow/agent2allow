# Releasing

## Versioning
- Use semantic versioning (`MAJOR.MINOR.PATCH`).
- `0.x` releases may change internals quickly, but public docs and API behavior should remain stable within a minor line.

## Release Checklist
1. Ensure all CI checks on `main` are green.
2. Update `CHANGELOG.md` with release notes.
3. Create an annotated tag (example):
   - `git tag -a v0.1.0 -m "Agent2Allow v0.1.0"`
4. Push tags:
   - `git push origin --tags`
5. Create GitHub Release from tag and paste changelog section.

## Patch Releases
- Keep changes minimal and low-risk.
- Mention migration notes if any config/env behavior changed.
