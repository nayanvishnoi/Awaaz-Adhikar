# Awaaz Adhikar — Full Fresh Project

This ZIP contains **the entire updated Django project** with a fresh SQLite database. You do not need to copy files from any older ZIP.

## New: Speaker approves each researcher

1. **Speaker:** Register, record/upload audio, open **My Recordings**, and tick **Research** (or another desired use). Save Permissions.
2. **Researcher:** Register separately, log in, pick a recording and a purpose, then press **Request Permission**. No file downloads at this stage.
3. **Speaker:** Log back in, open **Dashboard → Access Requests**, see the researcher's **username**, recording and purpose. Click **Allow Access** or **Reject**.
4. **Council:** For the recording's language, a trusted Council profile must set the same purpose to **Allow**.
5. **Researcher:** Return to **Dashboard → My Requests**. If the speaker approved, click **Download Voice**. The server checks the named researcher's approval, general speaker consent, and council rule **again** before delivering audio.
6. **Speaker:** To stop future downloads for a person, open **My Recordings → Who Has Asked for Access? → Revoke Access**. You can also withdraw/delete the recording to block all future platform downloads.

Note: A speaker approval **alone** is not enough for download. Missing/blocked Council rules reject it, and previously downloaded files cannot be remotely erased.

## NEW: Community Council Dashboard (joining approval FIX)

The original project placed Council tools inside the generic dashboard and did not show a dedicated Council link. This edition includes:

- **Council Login** link in the navbar for logged-out users.
- **Council Dashboard** and **Join Requests** in the navbar for appointed Council users.
- **Council Setup** link in the navbar for the superuser (administrator) only.
- A Council-login/management button on **Communities** page, and an indicator showing whether each community has a Council representative.

### Step-by-step demo

1. Register a Speaker and request to join **Bhojpuri** on the Communities page. The speaker sees **Request pending**.
2. Register another normal account for the Council representative (you can sign out and register as any normal user).
3. Log in as your **superuser** (created via CREATE_ADMIN_WINDOWS.bat). Click **⚙ Council Setup** in the navbar, or go to **http://127.0.0.1:8000/council/setup/**.
4. Choose the second user's username, choose **Bhojpuri**, and click **Assign Council Role**. Only a superuser can do this.
5. Log out and log back in as that Council user. Click **👥 Council Dashboard** in the navbar, or open **http://127.0.0.1:8000/council/dashboard/**.
6. Under **Community Management → Join Requests**, you will see the speaker's username. Click **Approve** or **Reject**.
7. Log in as the Speaker again. **Communities → Bhojpuri** will now show **✓ Member** if approved.

**Security:** A normal account cannot appoint itself as Council. The appointed Council can only approve requests for its own assigned community language.

## Preview the dashboard (no server required)

Double-click **UI_PREVIEW.html** to see an offline *sample-data* preview of the Speaker, Researcher and Council dashboards. The preview's sample buttons do not affect your database; the real application runs through **RUN_WINDOWS.bat**.

## Government references

- Header: Government-hosted public portraits of **Prime Minister Narendra Modi** (PM India) and **Union Home Minister Amit Shah** (Ministry of Home Affairs), with links to their official profiles, plus a **G20 India 2023 historical-reference badge**.
- Footer: links to India.gov.in, BHASHINI and National Cyber Crime Reporting Portal; official public helplines **1930** (cyber financial fraud) and **1915** (consumer grievances).
- These resources are **references only**. The site is an independent student project, **not** a government website or a government-endorsed service.

## New in the redesigned edition

- Polished Indian public-service-inspired homepage with tricolour accent, voice graphic, accessible navigation and clearer role descriptions.
- Redesigned Login and Signup screens, plus dashboard styling for Speaker / Researcher / Council.
- Accessible text-size and high-contrast toggles in the top bar (stored only in your browser).
- **Language Services** page with official BHASHINI and data.gov.in onboarding links and honest API connection status.
- Government API calls are **not enabled**: BHASHINI requires registration and approval, and this ZIP contains no credentials. All existing voice/consent features work locally without it.
- The project is independent and is **not an official government service**.

## Windows — easiest way

1. Extract the whole ZIP.
2. Open the `awaaz-adhikar-ready` folder.
3. Double-click **`RUN_WINDOWS.bat`**. The first run installs the dependencies and may take a few minutes.
4. In your browser, open **http://127.0.0.1:8000/**.
5. Choose **Register** to create a new Speaker or Researcher account.

For Django Admin, first run `RUN_WINDOWS.bat`, then double-click `CREATE_ADMIN_WINDOWS.bat` to create your own admin username and strong password. Admin URL: http://127.0.0.1:8000/admin/ .

## VS Code alternative

Open this folder in VS Code and in PowerShell run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

If PowerShell blocks activation, skip that command and run `.\.venv\Scripts\python.exe manage.py runserver` after installing with `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

## Important

- This is a **new project**. The included `db.sqlite3` has the table schema and starter language communities but **no user accounts**.
- Your old project's users and audio files remain in your old project folder; they are not transferred into this new one.
- Community Council accounts cannot be selected during public signup. After registering a Council candidate, use the simple **Council Setup** page as superuser to assign them to a language. The old Django Admin → Profiles method still works if you prefer it.
- The application is a hackathon prototype, not a government service or production-ready personal-data platform.
- Session duration is 45 minutes. Speaker recordings have a separate **My Recordings** menu, delete popup, consent, withdrawal and per-researcher revoke controls.
