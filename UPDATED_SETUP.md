# Awaaz Adhikar — Full PS 5.5 upgrade

This is an upgrade of the **uploaded project**, retaining the existing frontend, dashboards, migrations, and sample SQLite database. Back up your existing database before replacing anything.

## Windows setup
```powershell
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ and log in. Admin: /admin/.

## Approval workflow
1. Admin: /council/setup/ — assign an existing user as council representative for the correct language.
2. Council Dashboard — set language/purpose policy (e.g. Bhojpuri + Academic Research = Allow).
3. Researcher Dashboard — request recording/purpose.
4. Speaker Dashboard — approve that named request; speaker recording consent must allow that purpose.
5. Council Dashboard → **Researcher Download Approvals** — approve that individual request.
6. Researcher Dashboard → My Requests → Download Voice.

All three approvals (speaker individual request, speaker purpose consent, council language policy) **plus council individual approval** must remain active. Missing permissions deny access.

## Revocation
Speaker can revoke an individual request or withdraw/delete the recording; council can block a purpose or revoke a named request. New download attempts are denied and logged. Previous downloads and past AI training cannot be undone.

See `CANCELLATION_RESEARCH.md` for the problem-statement investigation and demo script.

## Note
No live Django integration test was run in the build environment. Run `python manage.py test core` locally. Older tests may require updating to account for the additional individual council approval requirement.
