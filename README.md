# Obesity Dashboard

This project is a Flask-based web application for visualizing the influence of various factors on obesity. It uses Bokeh for interactive data visualization and provides multiple pages to explore different aspects of the data.

## Features

- **Home Page**: Visualizes the influence of eating habits on obesity by age and gender.
- **Page 2**: Explores the influence of healthy habits on obesity.
- **Page 3**: Examines the relationship between obesity and illnesses like diabetes, hypertension, or heart disease.

## Prerequisites

Before deploying the application, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/albert-queralto/dashboard_obesity_analysis.git
   cd dashboard_obesity_analysis
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Ensure the dataset file `final_dataset.parquet` is present in the root directory of the project.

## Running the Application Locally

1. Start the Flask development server:

   ```bash
   python dashboard.py
   ```

2. Open your web browser and navigate to:

   ```
   http://127.0.0.1:5000
   ```

## Deployment

To deploy this application to a production environment, follow these steps:

### 1. Install Gunicorn (for WSGI server)

Gunicorn is a Python WSGI HTTP server for UNIX. Install it using pip:

```bash
pip install gunicorn
```

### 2. Run the Application with Gunicorn

Run the application using Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 dashboard:app
```

- `-w 4`: Specifies the number of worker processes (adjust based on your server's resources).
- `-b 0.0.0.0:8000`: Binds the application to all network interfaces on port 8000.

### 3. Use a Reverse Proxy (Optional)

For production deployment, it is recommended to use a reverse proxy like Nginx or Apache to handle incoming requests and forward them to Gunicorn.

### 4. Deploy on a Cloud Platform (Optional)

You can deploy this application on cloud platforms like AWS, Azure, or Heroku. Follow the platform-specific instructions for deploying Flask applications.

## File Structure

```
.
├── dashboard.py          # Main Flask application
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates for the app
├── static/               # Static files (CSS, JS, etc.)
├── utils.py              # Utility functions
├── plots_index.py        # Plot generation for the index page
├── plots_page2.py        # Plot generation for page 2
├── plots_page3.py        # Plot generation for page 3
└── final_dataset.parquet # Dataset file (required)
```

## Notes

- Ensure that the `final_dataset.parquet` file is in the root directory before running the application.
- For production, disable Flask's debug mode by setting `debug=False` in `app.run()`.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
