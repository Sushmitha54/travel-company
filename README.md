# Station Ride Share

A web application for travelers at stations (like railway stations) to group up with strangers going to the same destination to reduce transportation fares by sharing rides.

## Features

- User registration and login
- Set current location and destination
- Find companions going to the same destination
- Group travelers for shared rides

## API Endpoints

- GET /health - Health check
- POST /register - Register a new user
- POST /login - Login user
- POST /destination - Set user's destination
- GET /find_companions - Find groups of travelers

## Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python app.py`
3. Or with Gunicorn: `gunicorn app:app --bind 0.0.0.0:5000`

## Deployment

Deployed on Render with Gunicorn.
