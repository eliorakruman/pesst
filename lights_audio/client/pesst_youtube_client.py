import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from pickle import load, dump


@dataclass
class Song:
    title: str
    channel_title: str
    video_id: str
    channel_id: str

    def get_url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"
        

class YoutubeAPIV3Client:

    api_service_name = "youtube"
    api_version = "v3"
    scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    pickle_file = Path(".youtubeapiv3client_credentials")
        
    def __init__(self, client_secrets_file: Path, https_verification: bool = True):
        if not https_verification:
            # Disable OAuthlib's HTTPS verification when running locally.
            # *DO NOT* leave this option enabled in production.
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        self.client_secrets_file = client_secrets_file

        self.api_session = None
    
    def try_load_credentials(self) -> Optional[object]:
        if not self.pickle_file.exists():
            return None
        with open(self.pickle_file, "rb") as f:
            return load(f)
    
    def store_credentials(self, credentials):
        with open(self.pickle_file, "wb") as f:
            dump(credentials, f)
  
    def initalize_session(self):
        if maybe_credentials := self.try_load_credentials():
            credentials = maybe_credentials
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, self.scopes)
            flow.run_local_server()
            session = flow.authorized_session()
            credentials = session.credentials
            self.store_credentials(credentials)

        self.api_session = googleapiclient.discovery.build(
            self.api_service_name, 
            self.api_version, 
            credentials=credentials
        )

    def search_for_song(self, song_name: str, max_results: int = 5) -> list[Song]:
        if self.api_session is None:
            raise RuntimeError("Must initialize session before searching")

        request = self.api_session.search().list(
            part="snippet",
            eventType="none",
            type="video",
            maxResults=max_results,
            q=song_name
        )
        json_response: dict = request.execute()

        songs: list[Song] = []
        for json_song in json_response["items"]:
            song = Song(
                json_song["snippet"]["title"],
                json_song["snippet"]["channelTitle"],
                json_song["id"]["videoId"],
                json_song["snippet"]["channelId"]
            )
            songs.append(song)
        return songs


if __name__ == "__main__":
    youtube_client = YoutubeAPIV3Client(Path("./client_secret_251006524266-bp7ejcoqlqk03ml9o789cn84sl90nk3k.apps.googleusercontent.com.json"), False)
    youtube_client.initalize_session()
    result = youtube_client.search_for_song("doses and mimosas", 5)
    print(result)