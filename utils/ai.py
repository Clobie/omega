# utils/openai.py

from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AI:
    def __init__(self):
        self.client = OpenAI()
        # put these in the config eventually
        # also add system prompts to the config
        self.image_generation_model = "dall-e-3"
        self.image_generation_size = "1024x1024"
        self.image_generation_quality = "standard"
        self.sentiment_model = "gpt-4o-mini"
        self.gif_string_model = "gpt-4o-mini"
        self.conversate_model = "gpt-4o-mini"

    def chat_completion(self, model, system_prompt, user_prompt):
        try:
            completion = self.client.chat.completions.create(model=model,messages=[{"role": "system", "content": system_prompt},{"role": "user", "content": user_prompt}])
            result = completion.choices[0].message.content.strip()
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_completion_context(self, model, context):
        try:
            completion = self.client.chat.completions.create(model=model,messages=context)
            result = completion.choices[0].message.content.strip()
            return result
        except Exception as e:
            print(context)
            return f"Error: {str(e)}"

    def get_emoji_sentiment(self, prompt):
        return self.chat_completion(
            model = self.sentiment_model,
            system_prompt = 'Perform sentiment analysis on the text. Estimate the sentiment a user may feel when reading it. Respond using only one sentiment from the following list: "happy", "sad", "angry", "love", "surprised", "confused", "scared", "bored", "disgusted", "excited", "neutral", "tired", "annoyed", "shy", "hopeful", "peaceful", "proud", "jealous", "embarrassed", "horny", "curious", "frustrated", "relaxed", "grateful", "guilty", "nostalgic", "lonely", "content", "ecstatic". Response must be a single sentiment and nothing else.',
            user_prompt = prompt
        )
    
    def generate_gif_search_string(self, prompt):
        return self.chat_completion(
            self.gif_string_model,
            "Analyze the text and suggest a concise search string for finding a relevant GIF. Your search string should be short and relevant.",
            prompt
        )
    
    def conversate_no_context(self, prompt):
        return self.chat_completion(
            self.conversate_model,
            "You are an AI assistant named Omega.  Your response should be casual and short.",
            prompt
        )

    def generate_image(self, prompt):
        response = self.client.images.generate(
            model=self.image_generation_model,
            prompt=prompt,
            size=self.image_generation_size,
            quality=self.image_generation_quality,
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    
def instantiate():
    return AI()