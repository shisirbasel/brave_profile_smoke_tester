# Brave Profile Smoke Tester

This project is a Python automation script that uses Playwright to test multiple Brave browser profiles by launching each profile, navigating to a specified URL, and verifying successful operation.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

Make sure you have the following installed on your machine:
- Python
- pip (or any other python package installer)
- Brave Browser

### Installation

1. Clone the repository:
```bash
   git clone https://github.com/shisirbasel/brave_profile_smoke_tester.git
```

2. Create a virtual environment (recommended):
   
   **Windows:**
```bash
   python -m venv venv
   venv\Scripts\activate
```
   
   **macOS/Linux:**
```bash
   python3 -m venv venv
   source venv/bin/activate
```

4. Install dependencies:
```bash
   pip install -r requirements.txt
```


### Running the Project

Run the script with the following command:
```bash
python main.py --brave-path "path/to/brave/executable" --profiles-root "path/to/profiles/folder" --url "https://example.com" --headless
```

#### Command-Line Arguments

- `--brave-path` (required): Full path to the Brave browser executable
- `--profiles-root` (required): Path to the root directory containing multiple profile subdirectories
- `--url` (required): The URL to navigate to during testing
- `--headless` (optional): Run browser in headless mode (default: False)
- `--page-load-timeout` (optional): Timeout in milliseconds for page load (default: 30000)

---

## Expected Issues and Behavior

### 1. Wrong Path to Brave Executable

**Issue:** If you provide an incorrect path to the Brave executable:
```bash
--brave-path "C:/wrong/path/brave.exe"
```

**What happens:**
- The script will immediately exit with an error message
- No profile tests will be run
- Error message: `Error: Brave executable not found at: C:/wrong/path/brave.exe`

**Solution:** Verify the correct path to your Brave installation and try again.

---

### 2. Empty Profile Directories

**Issue:** If your `--profiles-root` folder is empty or contains no subdirectories:

**What happens:**
- The script will exit with an error message
- Error message: `Error: No profile directories found.`

**Solution:** Ensure your profiles root folder contains at least one profile subdirectory.

---

### 3. Non-Existent Profile Directory

**Issue:** If a profile subdirectory doesn't exist or was deleted:

**What happens:**
- That specific profile test will fail
- Other profiles will continue to be tested
- Error message in summary: `FAIL (Profile directory does not exist: ...)`

**Solution:** Remove the reference or create the missing profile directory.

---

### 4. Chrome Crash URLs (`chrome://crash` and `chrome://gpucrash`)

**Issue:** When navigating to intentional crash URLs like `chrome://crash` or `chrome://gpucrash`:

**What happens:**
- These URLs intentionally crash the Brave renderer process
- The script will still work and handle these gracefully
- The test will complete, but may show as FAIL due to navigation errors
- This is expected behavior when testing crash scenarios

**Example:**
```bash
python main.py --brave-path "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe" --profiles-root "./profiles/" --url "chrome://gpucrash" --headless
```

**Note:** These URLs are useful for testing how the browser handles crashes, but should not be used for normal smoke testing.

## Exit Codes

- **Exit Code 0**: All profiles passed
- **Exit Code 1**: One or more profiles failed, or validation errors occurred


