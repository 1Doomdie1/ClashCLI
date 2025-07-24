from pyclash import Clash
from dotenv import load_dotenv
from os import getenv

load_dotenv()

API_KEY = getenv("API_KEY")

clash = Clash(API_KEY)
clans = clash.clans.list(limit=1)

print(clans.body.model_dump_json(indent = 4))