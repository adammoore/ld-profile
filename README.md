# Learning Disability Profile Creator

A Streamlit application for creating and managing profiles for young people with learning disabilities, based on the Herbert and Philomena protocols. This tool helps create one-page profiles and can generate missing person information if needed.

## Features

- **Profile Creation**: Create comprehensive profiles including personal details, preferences, support needs, and communication methods
- **Missing Person Support**: Update with critical information if the person becomes missing
- **Document Generation**: Generate PDF one-page profiles and missing person posters
- **Image Management**: Upload and manage profile photos and additional images
- **GDPR Compliant**: Built with UK data protection laws in mind
- **Secure Storage**: Database or local encrypted storage of sensitive information

## Background

This application was developed to support the implementation of the Herbert and Philomena protocols in the UK. These protocols help gather important information about vulnerable people that can be shared with emergency services if they go missing.

- **Herbert Protocol**: Designed for people with dementia or memory impairment
- **Philomena Protocol**: Focused on young people and individuals with learning disabilities

The one-page profile approach is widely used in person-centered care to clearly communicate how best to support an individual.

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

4. (Optional) For database support:
   ```bash
   pip install sqlalchemy pymysql cryptography
   ```

5. Create required directories:
   ```bash
   mkdir -p profile_data
   ```

6. Run the application:
   ```bash
   streamlit run app.py
   ```

7. Open your browser and navigate to `http://localhost:8501`

### Streamlit Cloud Deployment

This application can be directly deployed to Streamlit Cloud:

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app, pointing to your forked repository
4. Select the main branch and app.py as the entry point

## Usage

### Creating a Profile

1. Select "Create New Profile" from the sidebar
2. Fill in the person's details in the form
   - Basic personal information
   - Physical description (height, build, etc.)
   - One-page profile information (what's important, how to support, etc.)
   - Herbert/Philomena protocol information
3. Upload a profile picture if available
4. Click "Save Profile"

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

## Data Storage Options

The application supports two storage options:

1. **Session Storage** (Default): Data is stored in the browser session and will be lost when the browser is closed
2. **Database Storage**: For persistent storage, the application can use SQLAlchemy with various database backends

To enable database storage, ensure `db_helper.py` is in the same directory as `app.py` and install the required dependencies.

## Data Privacy & GDPR

This application is designed with UK GDPR compliance in mind:

- Data is encrypted for security
- Clear purpose limitation and data minimization
- Support for data subject rights (access, rectification, erasure)
- Appropriate security measures for sensitive personal data

For organizational use, consider implementing additional security measures as outlined in the GDPR documentation.

## Customization

You can customize the application appearance by modifying the `.streamlit/config.toml` file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Author

Created by Adam Vials Moore

---

This project is intended to support individuals with learning disabilities and their caregivers. It is not a replacement for professional advice or established safeguarding procedures.
