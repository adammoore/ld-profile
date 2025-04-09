# Learning Disability Profile Creator

A Streamlit application for creating and managing profiles for young people with learning disabilities, based on the Herbert and Philomena protocols. This tool helps create one-page profiles and can generate missing person information if needed.

## Features

- **Profile Creation**: Create comprehensive profiles including personal details, preferences, support needs, and communication methods
- **Missing Person Support**: Update with critical information if the person becomes missing
- **Document Generation**: Generate PDF one-page profiles and missing person posters
- **Image Management**: Upload and manage profile photos and additional images
- **GDPR Compliant**: Built with UK data protection laws in mind
- **Secure Storage**: Database-backed with encryption for sensitive information

## Application Structure

The application has been refactored into a modular structure:

```
learning-disability-profile/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── database.py            # Database connection and operations
├── models.py              # Data models and schemas
├── pdf_generator.py       # PDF generation functionality
├── utils.py               # Utility functions
├── ui/                    # UI components
│   ├── __init__.py
│   ├── profile_form.py
│   ├── missing_person_form.py
│   ├── document_generator.py
│   └── sidebar.py
├── data/                  # Data directory (created at runtime)
│   ├── profile_data/      # Profile data storage
│   └── profiles.db        # SQLite database
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Installation

### Local Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/adammoore/ld-profile.git
   cd ld-profile
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

5. Open your browser and navigate to `http://localhost:8501`

### Streamlit Cloud Deployment

This application can be directly deployed to Streamlit Cloud:

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app, pointing to your forked repository
4. Select the main branch and app.py as the entry point

## Database Configuration

The application uses SQLite as the default database. The database file is created at `data/profiles.db`.

### Using a Different Database

To use a different database backend, update the database settings in `config.py`:

```python
# For MySQL
DB_TYPE = "mysql"
DB_USER = "yourusername"
DB_PASSWORD = "yourpassword"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "profiles"

# For PostgreSQL
DB_TYPE = "postgresql"
DB_USER = "yourusername"
DB_PASSWORD = "yourpassword"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "profiles"
```

For production deployments, you can use environment variables or Streamlit secrets to store database credentials securely.

## Usage

### Creating a Profile

1. Select "Create New Profile" from the sidebar
2. Fill in the person's details in the form
3. Upload a profile picture if available
4. Complete all sections, including the one-page profile information and Herbert/Philomena Protocol details
5. Click "Save Profile"

### Updating Missing Person Information

1. Select the profile from the sidebar
2. Choose "Missing Person Information" from the navigation
3. Enter details about when and where the person was last seen
4. Upload additional photos if available
5. Click "Update Missing Person Information"

### Generating Documents

1. Select the profile from the sidebar
2. Choose "Generate Documents" from the navigation
3. Click "Generate One-Page Profile" or "Generate Missing Person Poster"
4. Download the resulting PDF

## Data Privacy & GDPR

This application is designed with UK GDPR compliance in mind:

- Data is encrypted before storage in the database
- Data is stored locally by default (SQLite)
- Clear purpose limitation and data minimization
- Support for data subject rights
- Appropriate security measures for sensitive personal data

## Customization

You can customize the application appearance and behavior
