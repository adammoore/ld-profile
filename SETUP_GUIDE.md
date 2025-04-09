# Setup Guide for Learning Disability Profile Application

This document provides detailed instructions for setting up and deploying the Learning Disability Profile application in various environments.

## Local Development Setup

### Prerequisites

- Python 3.8 or newer
- Git
- Basic knowledge of command line operations

### Step-by-Step Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/adammoore/ld-profile.git
   cd ld-profile
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**

   ```bash
   streamlit run app.py
   ```

5. **Access the Application**

   Open your web browser and go to `http://localhost:8501`

## SQLite Database Setup (Default)

By default, the application uses SQLite for database storage, which requires no additional configuration. The database file will be automatically created in the `data/` directory when the application is first run.

## MySQL Database Setup (Optional)

For production environments, you may prefer to use MySQL for improved performance and concurrent access.

### Prerequisites

- MySQL server installed and running
- MySQL client libraries
- Access credentials with database creation permissions

### Step-by-Step Setup

1. **Install MySQL Driver**

   ```bash
   pip install pymysql
   ```

2. **Create MySQL Database and User**

   ```sql
   CREATE DATABASE ld_profiles CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'ld_profiles_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON ld_profiles.* TO 'ld_profiles_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Update Configuration**

   Edit `config.py` to use MySQL:

   ```python
   # Database settings
   DB_TYPE = "mysql"
   DB_NAME = "ld_profiles"
   
   # For production, use environment variables or secrets
   DB_USER = "ld_profiles_user"
   DB_PASSWORD = "your_secure_password"
   DB_HOST = "localhost"
   DB_PORT = "3306"
   ```

## PostgreSQL Database Setup (Optional)

PostgreSQL is another excellent choice for production environments.

### Prerequisites

- PostgreSQL server installed and running
- PostgreSQL client libraries
- Access credentials with database creation permissions

### Step-by-Step Setup

1. **Install PostgreSQL Driver**

   ```bash
   pip install psycopg2-binary
   ```

2. **Create PostgreSQL Database and User**

   ```sql
   CREATE DATABASE ld_profiles;
   CREATE USER ld_profiles_user WITH ENCRYPTED PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE ld_profiles TO ld_profiles_user;
   ```

3. **Update Configuration**

   Edit `config.py` to use PostgreSQL:

   ```python
   # Database settings
   DB_TYPE = "postgresql"
   DB_NAME = "ld_profiles"
   
   # For production, use environment variables or secrets
   DB_USER = "ld_profiles_user"
   DB_PASSWORD = "your_secure_password"
   DB_HOST = "localhost"
   DB_PORT = "5432"
   ```

## Streamlit Cloud Deployment

### Prerequisites

- GitHub account
- Repository with the application code
- Streamlit Cloud account (free tier available)

### Step-by-Step Deployment

1. **Fork or Push the Repository to GitHub**

   Ensure your repository contains all necessary files:
   - All Python modules
   - requirements.txt
   - README.md

2. **Create a `.streamlit` Directory and Configuration File**

   ```bash
   mkdir -p .streamlit
   ```

   Create a file named `.streamlit/config.toml` with:

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

3. **Deploy to Streamlit Cloud**

   - Go to [Streamlit Cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository
   - Select the branch (usually "main")
   - Specify the path to the app entry point: `app.py`
   - Click "Deploy!"

4. **Configure Secrets for Database Connection**

   If you're using a remote database:
   
   - Go to your app in Streamlit Cloud
   - Click on "Settings" (⚙️) > "Secrets"
   - Add your database credentials as secrets:

   ```toml
   [database]
   type = "mysql"
   user = "username"
   password = "password"
   host = "db.example.com"
   port = "3306"
   name = "ld_profiles"
   
   [security]
   encryption_key = "your-generated-encryption-key"
   ```

   - Update `config.py` to use these secrets:
   
   ```python
   import streamlit as st
   
   # Get database settings from secrets in production
   if 'database' in st.secrets:
       DB_TYPE = st.secrets.database.type
       DB_NAME = st.secrets.database.name
       DB_USER = st.secrets.database.user
       DB_PASSWORD = st.secrets.database.password
       DB_HOST = st.secrets.database.host
       DB_PORT = st.secrets.database.port
   ```

## Security Enhancements

### Generating a Persistent Encryption Key

For production use, you should generate a persistent encryption key:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Store this key securely
```

Store this key in environment variables or Streamlit secrets, and update `database.py` to use it.

### Adding Authentication

To add basic authentication to your Streamlit app:

1. **Install Streamlit Authenticator**

   ```bash
   pip install streamlit-authenticator
   ```

2. **Generate Hashed Passwords**

   ```python
   import streamlit_authenticator as stauth
   
   hashed_password = stauth.Hasher(['your-password']).generate()[0]
   print(hashed_password)
   ```

3. **Create a Config File**

   Create a file `.streamlit/auth.yaml`:

   ```yaml
   credentials:
     usernames:
       admin:
         email: admin@example.com
         name: Admin User
         password: the-hashed-password-from-above
   cookie:
     expiry_days: 30
     key: some-random-key
     name: ld_profiles_auth
   preauthorized:
     emails:
       - admin@example.com
   ```

4. **Implement Authentication in `app.py`**

   ```python
   import streamlit_authenticator as stauth
   import yaml
   from yaml.loader import SafeLoader
   
   # Load authentication config
   with open('.streamlit/auth.yaml') as file:
       config = yaml.load(file, Loader=SafeLoader)
   
   # Set up authenticator
   authenticator = stauth.Authenticate(
       config['credentials'],
       config['cookie']['name'],
       config['cookie']['key'],
       config['cookie']['expiry_days'],
       config['preauthorized']
   )
   
   # Add login widget
   name, authentication_status, username = authenticator.login('Login', 'main')
   
   # Show app only if authenticated
   if authentication_status:
       # Your existing app code here
       main()
   elif authentication_status == False:
       st.error('Username/password is incorrect')
   elif authentication_status == None:
       st.warning('Please enter your username and password')
   ```

## Backup and Maintenance

### Database Backup

For SQLite:

```bash
# Create a backup script
echo '#!/bin/bash
DATE=$(date +%Y-%m-%d-%H%M)
sqlite3 data/profiles.db ".backup data/backups/profiles-$DATE.db"
' > backup.sh

chmod +x backup.sh

# Create backups directory
mkdir -p data/backups

# Run manually or set up a cron job
./backup.sh
```

For MySQL:

```bash
# Create a backup script
echo '#!/bin/bash
DATE=$(date +%Y-%m-%d-%H%M)
mysqldump -u ld_profiles_user -p"your_secure_password" ld_profiles > data/backups/profiles-$DATE.sql
' > backup.sh

chmod +x backup.sh
```

### Regular Maintenance Tasks

1. **Clean up old files**

   The application includes a utility function `cleanup_old_files()` that can be used to remove temporary files older than a specified age. This can be called from a maintenance script.

2. **Check database integrity**

   For SQLite:
   ```bash
   sqlite3 data/profiles.db "PRAGMA integrity_check;"
   ```

3. **Update dependencies**

   Regularly update dependencies to ensure security patches are applied:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

## Troubleshooting Common Issues

### Application Won't Start

- Check Python version: `python --version` (should be 3.8+)
- Verify all dependencies are installed: `pip list`
- Check for syntax errors in your custom code
- Look for error messages in the terminal or log file

### Database Connection Errors

- Verify the database server is running
- Check connection credentials
- Ensure the database and tables exist
- Check network connectivity and firewall rules

### PDF Generation Errors

- Verify that ReportLab and FPDF are correctly installed
- Check that all required fonts are available
- Ensure all image paths are valid

### Image Upload Issues

- Check that the `data/profile_data/images` directory exists and is writable
- Verify the file formats are supported
- Check for file size limits
