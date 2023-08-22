# YouTube Audio Recognition using Shazam

This project is built on the FastAPI framework and incorporates async SQLAlchemy, Alembic, Postgres, Redis, and Docker. In addition, it leverages pytube, pydub, and shazamio to achieve its functionalities.

## Quickstart Guide

To initiate the service:
```
$ docker-compose up -d --build
```

This command starts the setup process by constructing all the essential components required to run the service. This includes setting up a PostgreSQL database, a Redis database for caching, applying necessary migrations, and hosting the service at `localhost:8004`.

## Recognizing YouTube Songs

To recognize a song from a YouTube video, you can make a query to the `/url` endpoint and provide the YouTube URL as a query parameter.

Example:

```
$ curl -X GET "http://localhost:8004/url/?youtube_url=https://www.youtube.com/watch?v=rYEDA3JcQqw"
```
The expected response:
```
{"title":"Rolling in the Deep (Official Music Video)","author":"Adele","views":2303911435}
```

Upon query submission, relevant YouTube metadata will be provided for the specific video. Simultaneously, it will start a background task for downloading and recognizing the audio using shazamio. If recognized sucessful it will also save the retrived Shazam metadata.

## How it works

![alt text](https://github.com/panagiotisfe/youtube-download-serivce/blob/master/img/app_flow.png?raw=true)

The following is a typical flow for the youtube-download-service:

- User sumbits the youtube url by querying the url endpoint.
- Service is fetching related YouTube data using pytube library.
- It saves the related data in the database.
- Then if the song has not been recognized before it starts a background task.
- The background task downloads only the audio of the video using pytube library.
- The audio is being downloaded in memory.
- After that using the shazamio library it recognizes the song.
- Fetches metadata from shazam and saves them in the database.

## Important decisions and assumptions

- The primary assumption is that its main purpose is to receive and handle youtube urls. It is designed to provide YouTube metadata as a response and concurrently process the url through a background task.
- The YouTube video duration must be less than an hour
- The shazamio library is capable of accurately identifying a song from a 20-second segment, regardless of where that segment occurs within the song.
- Given the above assumption there is no need for the whole audio to be processed but only a part of it.
- The initial concept was to store the downloaded file in a specific directory and then have the background task retrieve it from there for song recognition and metadata storage. However, due to the small size of the segments, it proves to be more efficient to retain them in memory, thus eliminating the resource-intensive I/O operations associated with disk usage. To achieve this, I implemented a solution that utilizes buffers.

## Improvements

- Better testing including end-to-end testing.
- Introduction of Dev Containers (more info [here](https://code.visualstudio.com/docs/devcontainers/containers))
- Possibly a more refined implementation of caching
