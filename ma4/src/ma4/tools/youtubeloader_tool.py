from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

from typing import List, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Sequence, Union
from urllib.parse import parse_qs, urlparse
import time

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_NETLOCS = {
    "youtu.be",
    "m.youtube.com",
    "youtube.com",
    "www.youtube.com",
    "www.youtube-nocookie.com",
    "vid.plus",
}

class MyYoutubeLoaderSchema(BaseModel):
    """Input for MyYoutubeLoaderSchema."""

    url: str = Field(
        ...,
        description="youtube url",
    )
    
    language: str = Field(
        ...,
        description="language fr or en",
    )


def _parse_video_id(url: str) -> Optional[str]:
    """Parse a YouTube URL and return the video ID if valid, otherwise None."""
    parsed_url = urlparse(url)

    if parsed_url.scheme not in ALLOWED_SCHEMES:
        return None

    if parsed_url.netloc not in ALLOWED_NETLOCS:
        return None

    path = parsed_url.path

    if path.endswith("/watch"):
        query = parsed_url.query
        parsed_query = parse_qs(query)
        if "v" in parsed_query:
            ids = parsed_query["v"]
            video_id = ids if isinstance(ids, str) else ids[0]
        else:
            return None
    else:
        path = parsed_url.path.lstrip("/")
        video_id = path.split("/")[-1]

    if len(video_id) != 11:  # Video IDs are 11 characters long
        return None

    return video_id


class YoutubeLoader:
    """Load `YouTube` video transcripts."""

    def __init__(
        self,
        video_id: str,
        language: Union[str, Sequence[str]] = "en",
    ):
        """Initialize with YouTube video ID."""
        _video_id = _parse_video_id(video_id)
        self.video_id = _video_id if _video_id is not None else video_id
        self._metadata = {"source": video_id}
        self.language = language
        if isinstance(language, str):
            self.language = [language]
        else:
            self.language = language

    def load(self) -> str:
        """Load YouTube transcripts into `Document` objects."""
        try:
            from youtube_transcript_api import (
                NoTranscriptFound,
                TranscriptsDisabled,
                YouTubeTranscriptApi,
            )
        except ImportError:
            raise ImportError(
                'Could not import "youtube_transcript_api" Python package. '
                "Please install it with `pip install youtube-transcript-api`."
            )

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
        except Exception as e:
            print(e)
            return []

        try:
            transcript = transcript_list.find_transcript(self.language)
        except NoTranscriptFound:
            transcript = transcript_list.find_transcript(["en"])

        transcript_pieces: List[Dict[str, Any]] = transcript.fetch()

        transcript = " ".join(
            map(
                lambda transcript_piece: transcript_piece["text"].strip(" "),
                transcript_pieces,
            )
        )
        return transcript


class MyYoutubeLoaderTool(BaseTool):
    name: str = "Direct Command Interpreter"
    description: str = "Interprets bash command strings with a final print statement."
    args_schema: Type[BaseModel] = MyYoutubeLoaderSchema
    url: Optional[str] = None  
    language: Optional[str] = None  

    def _run(self, **kwargs) -> str:
        url = kwargs.get("url", self.url)
        language = kwargs.get("language", self.language)

        try:
            youtubeLoader = YoutubeLoader(video_id = url, language = language)
            return youtubeLoader.load()
        except Exception as e:
            try:
                print("Warning loop")
                time.sleep(3)
                return youtubeLoader.load()
            except Exception as e:
                print("Warning loop")
                time.sleep(3)
                return youtubeLoader.load()
        
        
    


    