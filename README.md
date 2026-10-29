# Awaaz Adhikar — Complete Django Project (Step 5)

Government-style hackathon prototype with SQLite, registration, login/logout, and three role-based dashboards.

## Run in Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ in the browser.

Public signup offers **Speaker** and **Researcher** roles. To authorize a Council user, create or select their Profile under `/admin/`, then change their role to **Community Council**. Never allow the council role through public signup.

## Update an existing Step 1 installation

1. Stop the Django server using `Ctrl+C`.
2. Back up your existing project folder. **Do not delete or overwrite `db.sqlite3`**, because it contains your users and admin account.
3. Copy the new code files from this ZIP into the matching existing project folders, replacing Step 1 code files. Do not copy a database or a virtual environment.
4. Run `python manage.py migrate` and then `python manage.py runserver`.
5. Sign in with a **Speaker** account. The dashboard now shows Start Recording, Stop Recording, Upload/Save and My Recordings.

Microphone capture works on localhost in modern browsers once microphone access is allowed. Browser recording saves as WebM/OGG/M4A depending on support. Files are stored under `private_media/`, while SQLite stores recording metadata. Audio playback is checked against the logged-in speaker; raw media URL routing is not enabled.

## Step 3: Consent and community council

Existing accounts and recordings stay intact when you copy updated code and keep your own `db.sqlite3` and `private_media/` folders. Stop the server, back up your project, replace the matching code files from this ZIP, then run:

```powershell
python manage.py migrate
python manage.py runserver
```

1. **Speaker:** Sign in, upload an audio file, and tick permissions under its recording. Consent defaults to **deny**.
2. **Council:** In Django Admin, select a user Profile, set role to `Community Council`, and set Community name to the exact language (e.g. `Bhojpuri`). Sign in as that account and choose Allow/Block for each use. Missing rules deny access.
3. **Researcher:** Sign in and request access with a purpose. The file downloads only when both the speaker's consent and the council's current language policy allow it. Allowed/denied requests are logged.
4. **Withdrawal:** The speaker clicks Withdraw Permission. Future platform-controlled researcher access is denied; withdrawn recordings cannot be reactivated through the consent screen.

This is a hackathon prototype. Council rules are grouped by exact language name; production governance would need verified community memberships, disputes/appeals, proper identity checks, immutable audit storage, download-recipient notifications, and data security hardening. It cannot erase copies already downloaded or automatically undo past AI training. **Do not upload sensitive participant recordings yet.**

## Step 4: Communities and membership management

- The navigation includes `/communities/`, where speakers can explore Bhojpuri, Awadhi, Maithili, Bundeli and Hindi communities.
- Speakers can submit one join request per community and see pending/approved/rejected status.
- Council dashboard shows the pending requests, approved members and total language recordings. Its council members can approve or reject **only requests for their admin-assigned language**.
- Existing policy decisions continue to require both speaker consent and a matching language council permission, regardless of membership status.
- An admin can add/edit more communities via `/admin/` → Communities. Set the Council Profile's Community name to the exact community language (e.g. `Bhojpuri`).

For existing Step 3 users: keep your original `db.sqlite3` and `private_media/` folders, back up your project, replace the code files with this Step 4 ZIP, then run:

```powershell
python manage.py migrate
python manage.py runserver
```

This migration seeds starter communities without deleting existing recordings or accounts. The demo does not yet enforce community membership as a prerequisite for contributing recordings; community join approvals are a separate governance feature.

## Step 5: Judge-friendly interface, My Recordings & session control

- Cleaner Speaker, Researcher and Community Council dashboards with clear three-step instructions.
- Speaker has a **separate My Recordings link** in the navigation, at `/my-recordings/`.
- Speaker can play recordings, edit consent, withdraw consent, and delete an audio file. The Delete button opens a browser confirmation popup. The backend also requires a signed-in owner, POST, CSRF, and `confirm_delete=yes`.
- On deletion, the original audio file is removed and the recording becomes hidden. The database keeps a deleted metadata row and its audit history.
- Successful login, registration, logout, upload, consent changes and deletion produce visible feedback banners.
- Session lasts **45 minutes from sign-in**, not 45 minutes per request. A countdown appears in the top navigation; the next request after expiration requires a fresh login.

### Updating an existing Step 4 project

1. Stop the server and back up the project folder.
2. Extract the Step 5 ZIP and replace **code files** with their new versions.
3. Keep your original `db.sqlite3`, `private_media/`, and `venv/` untouched. These are not included in the ZIP.
4. Run:

```powershell
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`, sign in, and use the `My Recordings` menu. Existing users and uploaded files are preserved when their folders are retained.

### Judge demonstration in 2 minutes

1. **Speaker:** Log in, upload an audio, open My Recordings, check **Research**, and save consent.
2. **Council:** Log in with a council account whose Profile has `Community name = Bhojpuri`. Allow **Academic Research** for Bhojpuri.
3. **Researcher:** Log in, select that recording and `Academic Research`, then request access. The download is allowed.
4. **Speaker:** Withdraw permission from My Recordings.
5. **Researcher:** Request again. A clear **Access denied** message appears.
6. **Speaker:** Click Delete Recording. The confirmation popup appears and, once confirmed, the audio is removed from the platform. Audit history remains.

Council authorization must be assigned by the Django admin; public users cannot register as Council. This is a hackathon demonstration, **not production-safe identity verification**. Downloads already made by others are not erased and completed AI training is not reversed.

**Production caution:** Configure `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, HTTPS, backups, and private audio storage before real-world deployment. Do not collect real participant audio with this starter.
