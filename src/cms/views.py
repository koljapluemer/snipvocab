from django.shortcuts import render, redirect
from django.conf import settings
from googleapiclient.discovery import build
from shared.models import Video, VideoStatus, Snippet, Word, Meaning, Frontend, Tag, TagType
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from django.contrib import messages
from openai import OpenAI, beta
from pydantic import BaseModel
from typing import List
import re
import csv
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.urls import reverse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from frontend.models import VideoProgress, VocabPractice, SnippetPractice
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_page, never_cache
from django.utils.decorators import method_decorator

client = OpenAI(api_key=settings.OPENAI_API_KEY)






