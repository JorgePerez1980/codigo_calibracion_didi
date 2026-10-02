"""
Read environment variables.

This file can also be imported as a module and expose variables.
"""
import os
from dotenv import load_dotenv

# Cargar el archivo .env en las variables de entorno
load_dotenv()

GIA_PROJECT = os.getenv("GIA_PROJECT") 
GIA_LOCATION = os.getenv("GIA_LOCATION") 
GIA_MODEL = os.getenv("GIA_MODEL") 
GIA_MAX_OUTPUT_TOKENS = os.getenv("GIA_MAX_OUTPUT_TOKENS") 
GIA_TEMPERATURE = os.getenv("GIA_TEMPERATURE") 
GIA_TOP_P = os.getenv("GIA_TOP_P") 
GIA_TOP_K = os.getenv("GIA_TOP_K") 
GIA_CANDIDATE_COUNT = os.getenv("GIA_CANDIDATE_COUNT") 
DATASET = os.getenv("DATASET") 
TABLE = os.getenv("TABLE") 
GIA_TEXT_VAR = os.getenv("GIA_TEXT_VAR") 
TMO_TARGET = os.getenv("TMO_TARGET") 
GIA_TEXT_BUCKET = os.getenv("GIA_TEXT_BUCKET")
GIA_AUDIO_METADATA = os.getenv("GIA_AUDIO_METADATA")
BUCKET_STRUCTURE_CATEGORIZED = os.getenv("BUCKET_STRUCTURE_CATEGORIZED")
FILE_STRUCTURE_CATEGORIZED = os.getenv("FILE_STRUCTURE_CATEGORIZED")
TIME_ZONE = os.getenv("TIME_ZONE")
CSAT = os.getenv("CSAT")
WAITING_TIME = os.getenv("WAITING_TIME")
SEED = os.getenv("SEED")

