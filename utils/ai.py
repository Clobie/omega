# utils/openai.py

from openai import OpenAI
import tiktoken
import json
from utils.common import common
from utils.config import cfg
from utils.log import logger
from utils.credit import credit

class AI:
    def __init__(self):
        self.client = OpenAI()
        self.total_cost = self.load_cost_from_file()
    
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

    def generate_image(self, model, prompt):
        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    
    def load_cost_from_file(self):
        """Load accumulated cost from a file."""
        try:
            with open("./config/cost_data.json", "r") as file:
                cost_data = json.load(file)
                return round(cost_data.get("total_cost", 0.0), 6)
        except FileNotFoundError:
            logger.warning("cost_data.json not found. Starting with a cost of 0.")
            return 0.0

    def save_cost_to_file(self):
        """Save the accumulated cost to a file."""
        cost_data = {"total_cost": round(self.total_cost, 6)}
        with open("./config/cost_data.json", "w") as file:
            json.dump(cost_data, file, indent=4)
        logger.debug("Saved accumulated cost to file.")

    def estimate_tokens(self, text, model):
        """Estimate the number of tokens used in a given text."""
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))

    def update_cost(self, model, result, full_context, cpm_input, cpm_output):
        result_tokens = self.estimate_tokens(result, model)
        context_text = "\n".join([f"{entry['role']}: {entry['content']}" for entry in full_context])
        context_tokens = self.estimate_tokens(context_text, model)
        total_tokens = context_tokens + result_tokens
        cost_estimate = ((context_tokens / 1_000_000) * cpm_input) + \
                        ((result_tokens / 1_000_000) * cpm_output)
        cost_estimate = round(cost_estimate, 6)
        self.total_cost += cost_estimate
        self.save_cost_to_file()

        return total_tokens, cost_estimate, credit.convert_cost_to_credits(cost_estimate)
    
    def update_cost_static(self, cost):
        self.total_cost += round(cost, 6)
        self.save_cost_to_file()

    def get_footer(self, total_tokens, cost_estimate):
        text = common.to_superscript(f"{total_tokens}tk - {cost_estimate:.6f}cents")
        footer = f"\n\n*{text}*"
        return footer
    
    def get_total_cost(self):
        return round(self.total_cost, 6)

    def log_usage(self, user_id, tokens, cost, usage_type):
        script = f"""
        INSERT INTO openapi_usage (user_id, tokens, cost_value, usage_type)
        VALUES ({user_id}, {tokens}, '{cost}', {usage_type})
        """
        self.db.run_script(script)

ai = AI()