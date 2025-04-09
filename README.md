# Learning Disability Profile Creator

A Streamlit application for creating and managing profiles for young people with learning disabilities based on the Herbert and Philomena protocols.

## Overview

This application allows carers, family members, and professionals to create detailed profiles for individuals with learning disabilities. It includes features to:

- Create comprehensive one-page profiles
- Update information if the person becomes missing
- Upload and manage photos
- Generate PDF profiles and missing person posters
- Store data securely in compliance with UK GDPR regulations

## Features

### Profile Creation
- Personal details and physical description
- What's important to the person and how best to support them
- Communication preferences and methods
- Medical information and needs
- Places they might go and travel patterns

### Missing Person Support
- Quick update of missing person information
- Additional photo management
- Generation of missing person posters with key details

### Document Generation
- One-page profile PDF export
- Missing person poster generation
- Professional-looking, accessible layouts

### Privacy and Security
- Local data storage with encryption
- GDPR-compliant data handling
- Consent tracking and management

## Installation

### Prerequisites
- Python 3.8 or newer

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/adammoore/ld-profile.git
cd ld-profile
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

5. Access the application:
Open a web browser and go to `http://localhost:8501`

## Deployment to Streamlit Cloud

This application can be easily deployed using Streamlit Cloud:

1. Fork or push this repository to your GitHub account
2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and select this repository
4. Deploy and share with your organization

## Data Storage

By default, the application stores data locally in the `profile_data` directory. For production use, consider implementing:

- Database storage (SQL or NoSQL)
- Enhanced encryption
- Proper backup procedures

## GDPR Compliance

The application is designed with UK GDPR requirements in mind. For more details, see the [GDPR and Privacy Information](GDPR-PRIVACY.md) document.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Author

Adam Vials Moore

## Acknowledgments

- Herbert Protocol - A national scheme adopted by police forces to help find people with dementia who go missing
- Philomena Protocol - A similar scheme focused on young people in care/residential homes
