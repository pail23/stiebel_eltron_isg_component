# Release artifact verification

Status: proposed

The release ZIP should contain exactly the Git-tracked files below
`custom_components/stiebel_eltron_isg`, placed at the ZIP root for HACS. Its
`manifest.json` version must equal the release tag.

The builder:

- excludes untracked caches and editor files by construction;
- updates the manifest only inside the artifact;
- rejects unsafe paths and duplicate entries;
- parses every JSON file;
- verifies the complete tracked-file list and manifest version;
- writes deterministic ZIP metadata and reports a SHA-256 digest;
- atomically replaces the output only after verification.

The current GitHub workflow runs on `release: published`. Using the builder
there verifies the asset before upload, but the GitHub release itself already
exists at that point. It therefore closes the artifact-integrity gap, not the
publication-order gap.

Strict pre-publication verification requires an explicit release-process
change. Recommended later workflow:

1. trigger on a version tag or a manual version input;
2. check out the exact target commit;
3. run tests and build/verify the artifact;
4. create and publish the GitHub release only after all checks pass.

That change should be agreed with the maintainer because it replaces the
existing manual "publish release, then attach asset" flow and needs an explicit
policy for beta tags and release notes.
