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

You can customize the application appearance and behavior by modifying the following files:

### UI Customization

- **config.py**: Update the icons, colors, and other UI constants
- **.streamlit/config.toml**: Add this file to customize Streamlit's theme (an example is provided below)

Example `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 20

[browser]
gatherUsageStats = false
```

### Database Customization

For production environments, you might want to use a more robust database like MySQL or PostgreSQL. To do this:

1. Install the necessary database drivers:
   ```bash
   pip install pymysql  # For MySQL
   # or
   pip install psycopg2-binary  # For PostgreSQL
   ```

2. Update the database configuration in `config.py`

3. Create the database with appropriate permissions:
   ```sql
   CREATE DATABASE profiles;
   CREATE USER 'profiles_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON profiles.* TO 'profiles_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

## Security Considerations

### Encryption Key Management

The application generates an encryption key at runtime and stores it in the session state. For production deployments, you should:

1. Generate a persistent encryption key
2. Store it securely (e.g., using environment variables or Streamlit secrets)
3. Update the `database.py` file to use this key

Example:
```python
# In database.py
encryption_key = os.environ.get('ENCRYPTION_KEY')
if not encryption_key:
    encryption_key = st.secrets.get('encryption_key')
```

### Access Control

The application does not include user authentication. For production use, consider adding:

1. User authentication with Streamlit Authenticator or another authentication mechanism
2. Role-based access control to limit who can create, edit, or delete profiles
3. Audit logging to track who has accessed or modified profiles

## Troubleshooting

### Database Issues

If you encounter database errors:

1. Check that the database exists and is accessible
2. Verify that the user has appropriate permissions
3. Look for error messages in the logs (in the `data/app.log` file)

### PDF Generation Errors

If you encounter errors when generating PDFs:

1. Check that the ReportLab and FPDF libraries are installed correctly
2. Verify that the profile contains all required fields
3. Check that image paths are valid and images are accessible

### Image Handling

If images are not displaying correctly:

1. Verify that the image files exist in the expected location
2. Check that the file formats are supported (JPG, JPEG, PNG)
3. Ensure the application has read permissions for the image files

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -am 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Create a new Pull Request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Author

Created by Adam Vials Moore

---

This project is intended to support individuals with learning disabilities and their caregivers. It is not a replacement for professional advice or established safeguarding procedures.
