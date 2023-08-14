import requests
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Max

from ..models import Match, Prediction, User
import requests, zipfile, io, csv, re
from datetime import datetime
from bs4 import BeautifulSoup

