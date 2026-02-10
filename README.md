### Spotify Concert Recommender

Author : Hannah Fielding

#### Overview

This web application integrates the Spotify and Ticketmaster APIs to recommend live concerts
based on a user's listening preferences. After authenticating with Spotify, the application
analyzes the user's playlists and saved tracks to identify their most frequently listened-to
artists, then retrieves upcoming U.S. concert events from Ticketmaster.

This project demonstrates backend API orchestration, OAuth 2.0 authentication, 
data aggregation at scale, and resilient handling of third-party rate limits.

---
#### Features

- Spotify OAuth 2.0 authentication flow
- Access to user playlists and saved tracks
- Aggregation and ranking of most-listened-to artists
- Ticketmaster API integration for event discovery
- Filtering for U.S. events currently marked as “onsale”
- Basic rate-limit handling for Spotify API (HTTP 429 retry logic)
- Session-based token management with refresh support
---
#### Tech Stack

- Python
- Flask
- Spotify Web API
- Ticketmaster Discovery API
- Requests
- HTML Templates
---
#### System Design

1. User authenticates via Spotify OAuth.
2. Access token is stored in session.
3. User playlist and saved track data are fetched.
4. Artists are aggregated and ranked by frequency.
5. Ticketmaster API is queried using artist names.
6. Matching events are filtered and displayed to the user.
---
#### Known Limitations

- Ticketmaster’s onsale status does not guarantee actual ticket availability.
- Full inventory availability requires partner-level API access not publicly available.
- Event data accuracy depends on third-party API responses.
- Application is not currently deployed to a cloud environment.
---
#### Setup & Installation

Step 1 - (Bash) Clone Respository:

    git clone https://github.com/yourusername/spotify-concert-recommender.git
    cd spotify-concert-recommender
    pip install -r requirements.txt

Step 2 - (Code) Create a .env file with:

    SPOTIFY_CLIENT_ID=your_client_id
    SPOTIFY_CLIENT_SECRET=your_client_secret
    TICKETMASTER_API_KEY=your_api_key

Step 3 - (Bash) Run the application:

    python main.py

Step 4 - (Code) Navigate to:

    http://127.0.0.1:8888
