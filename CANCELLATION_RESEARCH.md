# PS 5.5 — Investigation: Why ordinary cancellation is inadequate

## Problem analysis (design comparison, not an empirical user study)

| Typical approach | Gap | Our system |
| --- | --- | --- |
| Remove a public link | Existing downloaded files remain | Future downloads require live permission checks |
| One-time blanket consent | No purpose-specific limits | Speaker chooses research/education/AI/commercial separately |
| Dataset-wide administrator decision | Community lacks agency | Assigned council sets language policy and reviews each request |
| Delete a file | Does not undo external sharing or model training | Warn users, log withdrawals, block future platform-controlled access |
| No access history | Speakers cannot audit access | Logs record grants, denials, downloads and policy changes |

## Honest limitations
- This project controls downloads **through this Django application**, not files already copied elsewhere.
- It cannot reverse past AI training, force third parties to erase copies, or verify all downstream uses.
- A download-start log does not prove complete delivery or compliant downstream use.
- For production: independent research/user interviews, legal review, threat modeling, virus scanning, object storage with private access, secure deployment and data retention policies are needed.

## Live demo
1. Admin assigns a council account using `/council/setup/`.
2. Speaker uploads a Bhojpuri recording and enables Academic Research.
3. Council allows Bhojpuri + Academic Research via Council Dashboard.
4. Researcher requests Academic Research. Speaker approves.
5. Council reviews that individual request and approves. Researcher downloads.
6. Council blocks the individual request or community-wide research policy. A new download is denied.
7. Speaker withdraws the recording. Future downloads remain denied, and the user sees the irreversible-copy warning.
8. Show audit logs to the judges.

This is a feature/design investigation, not a claim that existing products were systematically tested.
