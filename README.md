# Tennis Court Checker - Setup Instructions

## Prerequisites
- Python 3.8 or higher
- Chrome browser installed
- Internet connection

## Setup Steps

### Option 1: Automatic Setup (Linux/Mac/Git Bash)

1. Make the setup script executable:
```bash
chmod +x setup.sh
```

2. Run the setup script:
```bash
./setup.sh
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

### Option 2: Manual Setup (All Platforms)

#### Step 1: Create Virtual Environment

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

#### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install selenium webdriver-manager python-dotenv
```

#### Step 3: Create .env File

Create a file named `.env` in the same directory as the script with the following content:

```env
HEADLESS=true
DAYS_AHEAD=7
BOOKING_URL=https://tampereentenniskeskus.cintoia.com/
ELEMENT_WAIT_TIMEOUT=10
PAGE_LOAD_TIMEOUT=30
ACTION_DELAY=2
SAVE_SCREENSHOTS=false
SCREENSHOT_DIR=./screenshots
VERBOSE=false
```

## Running the Script

1. Make sure your virtual environment is activated (you should see `(venv)` in your terminal)

2. Run the script:
```bash
python tennis_checker.py
```

## Configuration Options

Edit the `.env` file to customize behavior:

- **HEADLESS**: Set to `false` to see the browser window
- **DAYS_AHEAD**: Number of days to check (1-30)
- **SAVE_SCREENSHOTS**: Set to `true` to save screenshots for debugging
- **VERBOSE**: Set to `true` for detailed output

## Troubleshooting

### Python not found
- Make sure Python 3.8+ is installed: `python3 --version` or `python --version`
- Download from: https://www.python.org/downloads/

### Chrome driver issues
- Make sure Chrome browser is installed
- The script will automatically download the correct ChromeDriver version

### Permission denied (Linux/Mac)
```bash
chmod +x setup.sh
```

### Virtual environment activation issues (Windows PowerShell)
If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Deactivating Virtual Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```

## Project Structure

```
tennis-checker/
├── tennis_checker.py      # Main script
├── requirements.txt       # Python dependencies
├── .env                   # Configuration file
├── setup.sh              # Setup script (Linux/Mac)
├── venv/                 # Virtual environment (created during setup)
└── screenshots/          # Screenshots (if enabled)
```

## Daily Usage

Every time you want to run the script:

1. Navigate to the project directory
2. Activate virtual environment:
    - Linux/Mac: `source venv/bin/activate`
    - Windows: `venv\Scripts\activate`
3. Run: `python tennis_checker.py`
4. Deactivate when done: `deactivate`