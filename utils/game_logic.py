import json
import os
import random
from data.turkish_words import TURKISH_WORDS

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")

class GameManager:
    def __init__(self):
        self.word_set = set(w.lower() for w in TURKISH_WORDS if len(w) >= 3)
        self.games = {}
        self.scores = self._load_scores()

    def _load_scores(self):
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_scores(self):
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)

    def turkish_lower(self, text):
        text = text.replace("İ", "i").replace("I", "ı")
        text = text.replace("Ü", "ü").replace("Ö", "ö").replace("Ç", "ç")
        text = text.replace("Ş", "ş").replace("Ğ", "ğ")
        return text.lower()

    def get_last_letter(self, word):
        word = self.turkish_lower(word)
        return word[-1] if word else ""

    def is_valid_word(self, word):
        word_lower = self.turkish_lower(word.strip())
        return word_lower in self.word_set

    def start_game(self, guild_id, channel_id):
        word = random.choice(TURKISH_WORDS)
        word_lower = self.turkish_lower(word)
        self.games[guild_id] = {
            "channel_id": channel_id,
            "active": True,
            "current_letter": word_lower[-1],
            "used_words": [word_lower],
        }
        return word

    def end_game(self, guild_id):
        game = self.games.pop(guild_id, None)
        return game is not None

    def get_game(self, guild_id):
        return self.games.get(guild_id)

    def submit_word(self, guild_id, user_id, word):
        game = self.games.get(guild_id)
        if not game or not game["active"]:
            return None, "Oyun aktif değil. `/basla` ile başlat."

        word_lower = self.turkish_lower(word.strip())

        if len(word_lower) < 3:
            return None, "Kelime en az 3 harfli olmalı."

        if word_lower in game["used_words"]:
            return None, "Bu kelime zaten kullanıldı."

        expected = game["current_letter"]

        if expected == "ğ":
            if word_lower[0] not in ("g", "k"):
                return None, f"Son harf **ğ** olduğu için kelime **g** veya **k** ile başlamalı."
        elif word_lower[0] != expected:
            return None, f"Kelime **{expected.upper()}** harfi ile başlamalı."

        if not self.is_valid_word(word):
            return None, "Bu geçerli bir Türkçe kelime değil."

        game["used_words"].append(word_lower)
        last_letter = word_lower[-1]
        game["current_letter"] = last_letter

        guild_str = str(guild_id)
        user_id_str = str(user_id)
        if guild_str not in self.scores:
            self.scores[guild_str] = {}
        self.scores[guild_str][user_id_str] = self.scores[guild_str].get(user_id_str, 0) + len(word_lower)
        self._save_scores()

        return last_letter, None

    def get_score(self, guild_id, user_id):
        return self.scores.get(str(guild_id), {}).get(str(user_id), 0)

    def get_leaderboard(self, guild_id):
        scores = self.scores.get(str(guild_id), {})
        user_scores = {k: v for k, v in scores.items() if k.isdigit()}
        sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        return [(int(uid), score) for uid, score in sorted_scores[:10]]
