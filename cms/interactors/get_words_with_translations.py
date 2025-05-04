def get_words_with_translations(text: str, frontend: str) -> list:
    """Get words and translations for a given text based on the frontend language"""
    if frontend == Frontend.ARABIC:
        prompt = (
            "You are an expert in Spoken, Egyptian Arabic. "
            "Extract language learning vocabulary from the following natural language transcript, ignoring proper nouns like restaurant names, "
            "exclamations such as 'oh', and other non-translatable words. For each extracted word, provide an English translation suitable to learn the word on its own."
            "Retain correct capitalization and spelling. If a word appears in a declined, conjugated, or plural form, "
            "add both the occurring and base form as separate entries (e.g. for 'أشجار' and 'شجرة', or 'بناكل' and 'كل'), both including the translation. Return your answer as a structured list of vocab."
        )
    else:  # German
        prompt = (
            "You are an expert in German. "
            "Extract language learning vocabulary from the following text, ignoring proper nouns like restaurant names, "
            "exclamations such as 'oh', and other non-translatable words. For each extracted word, provide an English translation suitable to learn the word on its own."
            "Retain correct capitalization and spelling. If a word appears in a declined, conjugated, or plural form, "
            "add both the occurring and base form as separate entries (e.g. for 'Bäume' and 'Baum', or 'Sie lief' and 'laufen'), both including the translation. Return your answer as a structured list of vocab."
        )
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt + f"\n\nText: {text}\n\nOutput JSON:"}
            ],
            response_format=WordEntryResponse,
        )
        return response.choices[0].message.parsed.words
    except Exception as e:
        print(f"Error processing text snippet: {e}")
        return []
