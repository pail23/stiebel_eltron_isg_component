# Release artifact verification

Status: proposed

The release ZIP should contain exactly the Git-tracked files below
`custom_components/stiebel_eltron_isg`, placed at the ZIP root for HACS. Its
`manifest.json` version must equal the release tag.

The builder:

- excludes untracked caches and editor files by construction;
- rejects tracked symlinks instead of dereferencing files outside the component;
- updates the manifest only inside the artifact;
- rejects unsafe paths and duplicate entries;
- parses every JSON file;
- compares every archived file with its intended source bytes and verifies the
  embedded manifest version;
- pins third-party workflow actions to reviewed commit SHAs;
- writes deterministic ZIP metadata and reports a SHA-256 digest;
- atomically replaces the output only after verification.

The checked-in manifest version is not required to equal the release tag. That
is deliberate and preserves the current release process: the tag version
replaces it only in the artifact. The manifest is normalized as indented JSON;
every other component file must match the checked-out source byte for byte.

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

The reported SHA-256 is written to the workflow job summary, but is not yet a
separate release asset or a provenance attestation. ZIP metadata is fixed and
the builder is reproducible in the same environment; compressed bytes may
still differ between zlib versions.
