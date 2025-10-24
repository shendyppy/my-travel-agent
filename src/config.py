"""
Configuration module for Travel Buddy AI Assistant

This module contains all constants and configuration settings for the Travel Buddy application.
It's the single source of truth for settings, preventing hardcoded values scattered throughout the code.
"""

import logging

# ============================================================================
# LLM MODEL CONFIGURATION
# ============================================================================

# The Gemini model to use for the Travel Buddy agent
# gemini-2.5-flash: Fast, efficient model good for conversations
MODEL = "gemini-2.5-flash"

# Thinking budget for Gemini's extended thinking feature
# Higher values = more reasoning (better quality, more tokens used)
# 0 = disabled, 5000-10000 = good balance for travel planning
THINKING_BUDGET = 5000

# ============================================================================
# AI AGENT PERSONA & BEHAVIOR
# ============================================================================

# System prompt that defines the Travel Buddy's personality and behavior
# This is crucial for shaping how the AI responds to users
TRAVEL_PERSONA = (
    "Anda adalah 'Travel Buddy', seorang asisten perjalanan AI yang sangat ramah, antusias, dan berpengalaman. "
    "Anda adalah ahli dalam menemukan penerbangan murah, merencanakan rute perjalanan, dan memberikan rekomendasi destinasi. "
    "\n\nGaya bahasa Anda:\n"
    "- Santai dan menggerakkan semangat\n"
    "- Selalu memberikan tips praktis dan unik tentang destinasi\n"
    "- Perhatian terhadap detail seperti harga, tanggal, dan preferensi pengguna\n"
    "- Selalu tanya pertanyaan lanjutan untuk memahami kebutuhan perjalanan mereka\n"
    "\n\nTugas utama Anda:\n"
    "- Membantu pengguna menemukan penerbangan dengan harga terbaik\n"
    "- Membandingkan rute dan pilihan destinasi\n"
    "- Merencanakan itinerary perjalanan\n"
    "- Memberikan saran budaya dan praktis tentang destinasi\n"
    "\n\nBatasan:\n"
    "- Jika pertanyaan tidak terkait dengan perjalanan (seperti resep masakan, olahraga, dll), "
    "jawab dengan sopan bahwa Anda fokus pada perjalanan dan tawarkan untuk membantu dengan rencana perjalanan mereka.\n"
    "- Setiap respons HARUS dimulai dengan sapaan yang bersemangat (misalnya, 'Wah, destinasi yang bagus!', 'Seru banget idenya!', atau 'Aku suka rencana itu!')\n"
    "- Akhiri respons dengan ajakan atau pertanyaan yang mendorong perencanaan lebih lanjut.\n"
)

# ============================================================================
# INPUT VALIDATION RULES
# ============================================================================

# Commands that signal user wants to exit the application
EXIT_COMMANDS = ["keluar", "exit", "quit", "stop"]

# Maximum input length to prevent prompt injection attacks
MAX_INPUT_LENGTH = 5000

# ============================================================================
# USER INTERFACE MESSAGES
# ============================================================================

# Header displayed when app starts
UI_HEADER = (
    "\n" + "=" * 50 + "\n"
    "🌍 TRAVEL BUDDY - AI Travel Assistant 🌍\n" + "=" * 50 + "\n"
)

# Instructions shown to user on startup
UI_INSTRUCTIONS = (
    f"Model: {MODEL} | Thinking Budget: {THINKING_BUDGET}\n"
    "Ketik 'keluar', 'exit', 'quit', atau 'stop' untuk mengakhiri.\n"
    "=" * 50 + "\n"
)

# Message shown when user exits gracefully
UI_EXIT_MESSAGE = (
    "\n✈️  Sampai jumpa! Selamat menikmati perjalanan Anda! Safe travels! 🌴\n"
)

# Message shown when user provides empty input
UI_EMPTY_INPUT = "❌ Silakan masukkan pertanyaan Anda.\n"

# Message shown while AI is processing
UI_THINKING = "Travel Buddy sedang memikirkan..."

# Error message prefix (followed by error details)
UI_ERROR_PREFIX = "❌ Terjadi kesalahan: "

# ============================================================================
# ERROR MESSAGES
# ============================================================================

ERROR_EMPTY_INPUT = "Input tidak boleh kosong"
ERROR_INPUT_TOO_LONG = f"Input terlalu panjang (maksimal {MAX_INPUT_LENGTH} karakter)"
ERROR_API_KEY_MISSING = "GEMINI_API_KEY tidak ditemukan. Cek file .env Anda."
ERROR_GEMINI_INIT_FAILED = "Gagal menginisialisasi klien Gemini."
ERROR_NETWORK = "❌ Kesalahan jaringan. Periksa koneksi internet Anda."
ERROR_API = "❌ Kesalahan layanan. Coba lagi nanti."
ERROR_UNEXPECTED = "❌ Kesalahan tidak terduga."

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = logging.INFO

# Log message format: includes timestamp, level, logger name, and message
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Log file location (optional, comment out to disable file logging)
LOG_FILE = "travel_buddy.log"
