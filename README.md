# Typress

Typst Mathematical Expression OCR.

## Run

### Clone the Repository

Clone this repo and enter it:

```sh
git clone https://github.com/ParaN3xus/typress
cd typress
```

### Set Up .env

Create a .env file in the repo root directory with the following content:

```sh
MODEL_PATH=path/to/your/model
```

### Install Dependencies

```sh
pip install -r requirements.txt
```

### Development Run

To run the application in development mode:

1. Ensure you are in the repo root directory.
2. Run the Flask application with debug mode enabled:

```sh
FLASK_ENV=development python app.py
```

### Production Run

To run the application in production mode, it is recommended to use a production-grade WSGI server such as `gunicorn`:

1. Ensure you are in the repo root directory.
2. Run the application using gunicorn:

```sh
gunicorn --bind 0.0.0.0:8000 app:app
```

## License

MIT
