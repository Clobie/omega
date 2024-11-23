# utils/openai.py

from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AI:
    def __init__(self):
        self.client = OpenAI()

    def chat_completion(self, model, system_prompt, user_prompt):
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            result = completion.choices[0].message.content.strip()
            print('\nDEBUG\n' + result)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    def get_emoji_sentiment(self, prompt):
        return self.chat_completion(
            model = "gpt-4o-mini",
            system_prompt = 'Perform sentiment analysis on the text. Estimate the sentiment a user may feel when reading it. Respond using only one sentiment from the following list: "happy", "sad", "angry", "love", "surprised", "confused", "scared", "bored", "disgusted", "excited", "neutral", "tired", "annoyed", "shy", "hopeful", "peaceful", "proud", "jealous", "embarrassed", "horny", "curious", "frustrated", "relaxed", "grateful", "guilty", "nostalgic", "lonely", "content", "ecstatic". Response must be a single sentiment and nothing else.',
            user_prompt = prompt
        )
    
    def generate_gif_search_string(self, prompt):
        return self.chat_completion(
            "gpt-4o-mini",
            "Analyze the text and suggest a concise search string for finding a relevant GIF. Your search string should be short and relevant.",
            prompt
        )
    
    def conversate_no_context(self, prompt):
        return self.chat_completion(
            "gpt-4o-mini",
            "You are just a normal, chill, witty person.  Your response should be casual and short.  You are to pretend you are not an AI, and act like you are just one of the homies, adding your own flair to the conversation.",
            prompt
        )
    
    def generate_image(self, prompt):
        response = self.client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    
def instantiate():
    return AI()