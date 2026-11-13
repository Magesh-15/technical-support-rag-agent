"""Print the Groq model names your key can use. Put one in .env as GROQ_MODEL."""
from src import config
from groq import Groq

for m in Groq(api_key=config.GROQ_API_KEY).models.list().data:
    print(m.id)
