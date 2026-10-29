# PS 5.5 final verification checklist

## Included in this build
- Speaker uploads and selects permitted purposes.
- Named researcher requests; speaker approves/rejects/revokes.
- Assigned council reviews named requests and sets language/purpose rules.
- Download checks current speaker, council, withdrawal, and purpose permissions on every attempt.
- Usage logs and cancellation research document.
- Speaker withdrawal and deletion block future platform downloads.
- Regression tests added for council approval/rejection, unauthorized council, speaker revocation, purpose cancellation, and audit events.

## Before demo
1. Back up the existing SQLite database and private media.
2. Install requirements, migrate, then run `python manage.py test core`.
3. Log in as speaker, researcher and assigned council; test each dashboard and download flow.
4. Show a successful download, revoke council approval, then show blocked download and usage log.
5. Explain that previously shared files and past model training cannot be recalled.

## Limits
- No remote-copy recall, past-training rollback, or third-party deletion guarantee.
- This build was syntax-checked, but Django could not be installed in the build environment, so live tests were not executed here.
- Review deployment security and privacy before accepting real recordings.
