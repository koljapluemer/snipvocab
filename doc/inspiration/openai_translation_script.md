## Adding Content

- [youtube short with subtitle search](https://www.youtube.com/results?search_query=+%D8%A7%D9%84%D9%82%D8%A7%D9%87%D8%B1%D8%A9&sp=EgQYASgB)

1. find a video you like, and copy only the id in `videos/management/commands/in/$country_code.txt` as its own line
2. make/go into `venv` at root of project
3. run `python manage.py create_static_data_from_yt`
    - actually, it's now `python manage.py create_static_data_from_yt_with_deepl`


- to also make this work in heroku, do the following:

1. `python manage.py dumpdata videos.Language videos.Video videos.Snippet videos.Word --indent 2 > videos_fixture.json`
2. commit and push the json fixture
3. `heroku run python manage.py loaddata videos_fixture.json`

```python

import os
import json
from django.core.management.base import BaseCommand
from videos.models import Language, Video, Snippet, Word

from tqdm import tqdm
from openai import OpenAI, beta
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

INPUT_FOLDER = "videos/management/commands/in"

# Load environment variables from the .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # ensure this is set in your environment
client = OpenAI(api_key=OPENAI_API_KEY)

class WordEntry(BaseModel):
    word: str
    meaning: str

class WordEntryResponse(BaseModel):
    words: list[WordEntry]

class Command(BaseCommand):
    help = "Imports static video data from list of youtube videos."

    def get_language_description(self, lang_code: str) -> str:
        """Return a language description for the LLM prompt based on the language code."""
        mapping = {
            "arz": "Egyptian Arabic (spoken in Cairo)",
            "it": "Italian",
            "de": "German",
        }
        return mapping.get(lang_code.lower(), lang_code)
    
    
    def get_words_with_translations(self, text: str, lang_code: str) -> list:
        language_desc = self.get_language_description(lang_code)
        prompt = (
            f"You are an expert in {language_desc}. "
            "Extract language learning vocab from the following text, ignoring proper nouns like restaurant names, "
            "exclamations such as 'oh', and other non-translatable words. For each extracted word, provide an English translation suitable to learn the word on its own."
            "Retain correct capitalization and spelling. If a word appears in a declined, conjugated, or plural form, "
            "add both the occurring and base form as separate entries (e.g. for 'trees' and 'tree', or 'She ran' and 'running'), both including the translation. Return your answer as a structured list of vocab."
        )
        try:
            # Using the beta chat method to parse the response with the structured output
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt + f"\n\nText: {text}\n\nOutput JSON:"}
                ],
                response_format=WordEntryResponse,  # This will return a parsed structured response
            )
            
            # Now you can directly access the structured output, which is parsed into your Pydantic model
            word_entries = response.choices[0].message.parsed.words
            return word_entries
        except Exception as e:
            print(f"Error processing text snippet: {e}")
            return []
    def process_video(self, video_id: str, lang_code: str) -> None:
        language, _ = Language.objects.get_or_create(code=lang_code, defaults={"name": lang_code.capitalize()})
        print("Integrating video:", video_id)

        video_obj, was_created = Video.objects.get_or_create(
                            youtube_id=video_id,
                            defaults={'language': language}
                        )
        
        if not was_created:
            return

        transcript_lang = "ar" if lang_code.lower() == "arz" else lang_code
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[transcript_lang])
        except Exception as e:
            print(f"Error fetching transcript for video '{video_id}': {e}")
            return

        for index, segment in enumerate(transcript):
            text = segment.get("text", "")
            start = segment.get("start", 0)
            duration = segment.get("duration", 0)
            snippet_obj, _ = Snippet.objects.get_or_create(
                                        video=video_obj,
                                        index=index,
                                        defaults={
                                            "start": start,
                                            "duration": duration,
                                        }
                                    )
            words_with_translations = self.get_words_with_translations(text, lang_code)
            for word_entry in words_with_translations:
                word_obj, _ = Word.objects.get_or_create(
                                original_word=word_entry.word,
                                defaults={'meanings': []}
                            )
                
                word_obj.occurs_in_snippets.add(snippet_obj)
                if word_entry.meaning not in word_obj.meanings:
                    word_obj.meanings.append(word_entry.meaning)
                    word_obj.save()

    def process_language_file(self, file_path: str) -> None:
        """
        Process one language file (e.g. "arz.txt") containing video IDs.
        """
        lang_code = os.path.splitext(os.path.basename(file_path))[0]
        with open(file_path, "r", encoding="utf-8") as f:
            video_ids = [line.strip() for line in f if line.strip()]
        
        for video_id in tqdm(video_ids, desc=f"Processing videos for {lang_code}"):
            self.process_video(video_id, lang_code)

    def handle(self, *args, **options):
        if not os.path.exists(INPUT_FOLDER):
                print(f"Input folder {INPUT_FOLDER} does not exist.")
                return
        for filename in os.listdir(INPUT_FOLDER):
            if filename.endswith(".txt"):
                file_path = os.path.join(INPUT_FOLDER, filename)
                print(f"Processing language file: {filename}")
                self.process_language_file(file_path)

        self.stdout.write(self.style.SUCCESS("✅ Static data generation complete!"))
        
```