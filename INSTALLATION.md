# Installation Guide

This guide provides step-by-step instructions for installing and running the Learning Disability Profile application.

## Quick Start

For those familiar with Python and Streamlit, here's a quick start guide:

```bash
# Clone the repository
git clone https://github.com/adammoore/ld-profile.git
cd ld-profile

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

The application will be available at http://localhost:8501

## Detailed Installation

### Prerequisites

Before installing the application, you need:

1. **Python 3.8 or newer**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version`

2. **Git** (optional, for cloning the repository)
   - Download from [git-scm.com](https://git-scm.com/downloads)
   - Verify installation: `git --version`

3. **pip** (Python package installer, usually included with Python)
   - Verify installation: `pip --version`

### Installation Steps

#### 1. Get the Code

**Option A: Clone with Git**

```bash
git clone https://github.com/adammoore/ld-profile.git
cd ld-profile
```

**Option B: Download ZIP**

- Go to https://github.com/adammoore/ld-profile
- Click "Code" > "Download ZIP"
- Extract the ZIP file
- Navigate to the extracted directory

#### 2. Create a Virtual Environment

A virtual environment keeps dependencies required by this project separate from your global Python installation.

**On macOS/Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

Your command prompt should now show `(venv)` at the beginning, indicating the virtual environment is active.

#### 3. Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This installs all the Python libraries needed for the application.

#### 4. Create Required Directories

The application needs certain directories to store data:

```bash
mkdir -p data/profile_data/images
```

#### 5. Run the Application

```bash
streamlit run app.py
```

The application should start and a browser window should open automatically. If not, you can access it at http://localhost:8501

#### 6. (Optional) Create a .streamlit Directory for Customization

```bash
mkdir -p .streamlit
cp examples/config.toml .streamlit/
```

This will copy the example configuration file to the correct location.

## Troubleshooting Installation Issues

### Python Version Issues

If you encounter errors about Python version:

```bash
# Check your Python version
python --version

# If you have multiple Python versions, you might need to use python3 explicitly
python3 -m venv venv
```

### Package Installation Errors

If you encounter errors installing packages:

```bash
# Update pip first
pip install --upgrade pip

# Install packages one by one to identify problematic packages
pip install streamlit
pip install pandas
# etc.
```

### Streamlit Port Already in Use

If port 8501 is already in use:

```bash
# Run on a different port
streamlit run app.py --server.port=8502
```

### Database Issues

By default, the application uses SQLite which should work without additional configuration. If you see database errors:

```bash
# Check if the data directory exists and is writable
ls -la data/

# For permission issues, change permissions
chmod -R 755 data/
```

## Updating the Application

To update the application to the latest version:

```bash
# If you used Git to install
git pull

# Activate the virtual environment (if not already activated)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Running in Production

For production deployments, consider:

1. Using a production-grade database (MySQL/PostgreSQL)
2. Setting up authentication
3. Configuring a secure encryption key

See the SETUP_GUIDE.md for more details on production deployments.
