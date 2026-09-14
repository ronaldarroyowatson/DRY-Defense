# DRY Defense

DRY Defense is a small desktop utility for converting lesson CSV files between FACTS and Planbook formats.

Version: 1.0.0

It is designed for a simple workflow:

- drag a CSV file onto the app window, or click the file box to choose a file
- the app detects whether the file is FACTS or Planbook format
- it converts the file to the opposite format automatically
- it saves a new file next to the original with a suffix such as `_Planbook.csv` or `_FACTS.csv`

## Why this exists

Teachers and staff often move lesson plan data between systems that use different CSV schemas. This tool reduces manual copying and reformatting while preserving the fields that matter most:

- LessonName
- LessonPlan
- HomeworkNotes
- Label1
- Label2
- Label3
- Label4

## Pragmatic Programmer rules

This project follows the core Pragmatic Programmer principles as a design and coding standard:

- Keep it simple
- Do not add complexity without a reason
- Automate repetitive work
- Write code that is easy to test and easy to reason about
- Keep the data contract explicit
- Prefer small, well-bounded modules and clear responsibilities
- Make the tool useful before trying to make it clever
- Validate behavior with tests before claiming the work is complete
- Make it easy to run, package, and recover from failures

## Project layout

- `lesson_converter_app/` – app logic and desktop UI
- `installer/` – installer and desktop shortcut setup
- `tests/` – converter regression tests
- `build_windows.py` – local Windows packaging helper
- `setup_installer.py` – rebuild and install helper

## Requirements

- Python 3.12+
- PySide6
- PyInstaller
- pytest

## Quick start

### Smart App Control safety (required for distribution)

Windows Smart App Control and Defender reputation checks commonly block unsigned executables that are downloaded from the internet. To avoid this, DRY Defense release binaries must be Authenticode-signed before publishing.

This repository enforces signing in the GitHub release workflow. If required signing secrets are missing, the release build fails instead of publishing an unsigned artifact.

Required repository secrets:

- WINDOWS_SIGNING_CERT_BASE64
- WINDOWS_SIGNING_CERT_PASSWORD

Set them once with GitHub CLI:

```powershell
Set-Location "c:\workspace\DRY Defense"
$pfxPath = "C:\path\to\your\code-signing-certificate.pfx"
$password = Read-Host "PFX password" -AsSecureString
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
$plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
try {
	$base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($pfxPath))
	$base64 | gh secret set WINDOWS_SIGNING_CERT_BASE64 -R ronaldarroyowatson/DRY-Defense
	$plain | gh secret set WINDOWS_SIGNING_CERT_PASSWORD -R ronaldarroyowatson/DRY-Defense
} finally {
	[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}
```

After secrets are set, publish a tag to trigger a signed release:

```powershell
Set-Location "c:\workspace\DRY Defense"
git tag v1.0.1
git push origin v1.0.1
```

For local signed packaging, run:

```powershell
Set-Location "c:\workspace\DRY Defense"
./sign_windows_release.ps1 -SubjectName "Your Code Signing Certificate Subject"
```

Distribute only signed release artifacts.

### Download and install the Windows app

Download the latest Windows release zip from the GitHub Releases page:

- https://github.com/ronaldarroyowatson/DRY-Defense/releases

Then:

1. Download the latest `DRY-Defense-Windows.zip`
2. Extract it to a folder on your PC
3. Right-click `install_dry_defense.ps1`
4. Choose `Run with PowerShell`
5. Allow the script to run if Windows asks

That script will:

- copy the app into `%LOCALAPPDATA%\DRYDefense`
- create a desktop shortcut named `DRY Defense`
- make installation automatic and easy

### Run from source

Create a virtual environment and install dependencies:

```bash
cd c:\workspace\DRY Defense
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install PySide6 PyInstaller pytest
```

Run the desktop app:

```bash
.venv\Scripts\python.exe -m lesson_converter_app
```

Run the tests:

```bash
.venv\Scripts\python.exe -m pytest tests/test_converter.py -q
```

Build a Windows app bundle:

```bash
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name DRYDefense lesson_converter_app\main.py
```

### Uninstall

Delete the app folder and desktop shortcut:

```powershell
Remove-Item "$env:LOCALAPPDATA\DRYDefense" -Recurse -Force
Remove-Item "$env:USERPROFILE\Desktop\DRY Defense.lnk" -Force -ErrorAction SilentlyContinue
```

## CSV support

The app detects the input format based on the header row.

### FACTS format

The FACTS CSV includes fields such as:

- LessonName
- LessonPlan
- HomeworkNotes
- Label1
- Label2
- Label3
- Label4

### Planbook format

The Planbook CSV includes fields such as:

- Lesson #
- Section 1 (Lesson)
- Section 2 (Homework)
- Section 3 (Notes)
- Section 4
- Section 5
- Section 6
- Lesson Title
- Unit ID
- Unit Title

## Conversion behavior

The tool converts in the opposite direction automatically:

- FACTS -> Planbook
- Planbook -> FACTS

It preserves the important lesson metadata needed for both systems and writes the resulting CSV next to the original file using a naming suffix.

## Development notes

This project is intentionally small and explicit. The converter logic is kept separate from the UI so it can be tested directly and reused without depending on the desktop shell.

That keeps the code aligned with Pragmatic Programmer guidance: easy to understand, easy to maintain, and easy to validate.

## License

This project is intended for local educational workflow use and is not published as a commercial product by default.
