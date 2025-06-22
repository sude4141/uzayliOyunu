import tkinter as tk
from tkinter import messagebox
import random
import pygame
import time
from datetime import datetime #Tarih ve saat bilgisini skor dosyasına yazmak için.
import os


WORDS = ["rocket launch", "yazilim", "fenerbahçe", "dart vader", "jarjarbinks"]
TRAP_LETTERS = ['x', 'z', 'j', 'q']
MAX_MISTAKES = 6
INITIAL_TIME = 20
GUESS_TIME_LIMIT = 10


pygame.mixer.init()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

def play_sound(filename):
    sound_path = os.path.join(SOUNDS_DIR, filename)
    if not os.path.isfile(sound_path):
        print(f"Ses dosyası bulunamadı: {sound_path}")
        return
    try:
        sound = pygame.mixer.Sound(sound_path)
        sound.play()
    except Exception as e:
        print(f"Ses oynatma hatası: {e}")


class AlienEscapeGame:
    def __init__(self, root):
        self.root = root #Gelen root parametresini, sınıf içinde kullanmak üzere self.root olarak saklar.
        self.timer_id = None
        self.game_started = False
        self.root.title("Uzaylıdan Kaçış - Şifreli Mesaj")
        self.root.geometry("700x450")
        self.root.configure(bg="#0b0c1a")
        self.create_widgets()

    def create_widgets(self):
        self.word_label = tk.Label(self.root, text="", font=("Courier New", 28, "bold"),
                                   bg="#0b0c1a", fg="#adebeb")
        self.word_label.pack(pady=15)

        self.entry = tk.Entry(self.root, font=("Consolas", 18), width=4, justify="center", state="disabled")
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda event: self.check_letter())

        btn_frame = tk.Frame(self.root, bg="#0b0c1a")
        btn_frame.pack(pady=10)

        self.check_button = tk.Button(btn_frame, text="Tahmin Et", font=("Arial", 14, "bold"),
                                      bg="#30a0f0", fg="white", activebackground="#1d78c1",
                                      width=12, relief="raised", bd=3, command=self.check_letter, state="disabled")
        self.check_button.grid(row=0, column=0, padx=15)

        self.hint_button = tk.Button(btn_frame, text="İpucu Al (1 Hak)", font=("Arial", 14, "bold"),
                                     bg="#f0a830", fg="white", activebackground="#c17a1d",
                                     width=12, relief="raised", bd=3, command=self.use_hint, state="disabled")
        self.hint_button.grid(row=0, column=1, padx=15)

        self.status_label = tk.Label(self.root, text="", font=("Consolas", 14),
                                     bg="#14213d", fg="#e5e5e5", bd=2, relief="sunken",
                                     width=40, height=2)
        self.status_label.pack(pady=8)

        self.timer_label = tk.Label(self.root, text="Kalan Süre: --",
                                    font=("Consolas", 16, "bold"),
                                    bg="#14213d", fg="#fca311", bd=2, relief="sunken",
                                    width=20)
        self.timer_label.pack(pady=8)

        self.alien_label = tk.Label(self.root, text="", font=("Courier New", 26, "bold"),
                                    bg="#0b0c1a", fg="#adebeb")
        self.alien_label.pack(pady=15)

        self.start_button = tk.Button(self.root, text="Oyuna Başla", font=("Arial", 16, "bold"),
                                      bg="#28a745", fg="white", width=20, command=self.start_game)
        self.start_button.pack(pady=20)

    def start_game(self):
        self.word = random.choice(WORDS)
        self.guessed = ["_" if c != " " else " " for c in self.word]
        self.mistakes = 0
        self.used_letters = set()
        self.hint_used = False
        self.game_over = False
        self.start_time = time.time()

        self.timer = INITIAL_TIME
        self.first_guess = True

        self.entry.config(state="normal")
        self.check_button.config(state="normal")
        self.hint_button.config(state="normal")
        self.start_button.config(state="disabled")
        self.update_display()
        self.start_timer()

    def update_display(self):
        self.word_label.config(text=" ".join(self.guessed))
        self.alien_label.config(text=f"🚀{'-' * (6 - self.mistakes)}👽")
        self.status_label.config(text=f"Tahmin edilen harfler: {', '.join(sorted(self.used_letters))}")
        self.timer_label.config(text=f"Kalan Süre: {self.timer}")

        if "_" not in self.guessed:
            self.finish_game(win=True)

        if self.mistakes >= MAX_MISTAKES:
            self.finish_game(win=False)

    def check_letter(self):
        if self.game_over:
            return
        letter = self.entry.get().lower().strip()
        self.entry.delete(0, tk.END)
        self.cancel_timer()

        if not letter or len(letter) != 1 or not letter.isalpha():
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir harf giriniz.")
            self.reset_timer()
            return

        if letter in self.used_letters:
            self.reset_timer()
            return

        self.used_letters.add(letter)

        if letter in self.word:
            for i, c in enumerate(self.word):
                if c == letter:
                    self.guessed[i] = letter
            play_sound("correct.wav")
        else:
            self.mistakes += 2 if letter in TRAP_LETTERS else 1
            play_sound("wrong.wav")

        self.first_guess = False
        self.reset_timer()
        self.update_display()

    def use_hint(self):
        if not self.hint_used:
            self.guessed[0] = self.word[0]
            self.hint_used = True
            self.mistakes += 1
            self.update_display()

    def start_timer(self):
        self.timer_label.config(text=f"Kalan Süre: {self.timer}")
        if self.timer > 0 and not self.game_over:
            self.timer -= 1
            self.timer_id = self.root.after(1000, self.start_timer)
        else:
            if not self.game_over:
                self.mistakes += 1
                play_sound("wrong.wav")
                self.first_guess = False
                self.timer = GUESS_TIME_LIMIT
                self.update_display()
                self.start_timer()

    def reset_timer(self):
        self.timer = INITIAL_TIME if self.first_guess else GUESS_TIME_LIMIT
        self.start_timer()

    def cancel_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def finish_game(self, win):
        self.game_over = True
        self.cancel_timer()
        duration = int(time.time() - self.start_time)
        result = "KAZANDI" if win else "KAYBETTİ"
        messagebox.showinfo("Sonuç", f"Oyun Bitti - {result}!\nDoğru kelime: {self.word}")
        play_sound("win.wav" if win else "lose.wav")

        score_file_path = os.path.join(BASE_DIR, "scores.txt")
        try:
            with open(score_file_path, "a", encoding="utf-8") as file:
                file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')} | {result} | {self.word} | {duration} saniye\n")
        except Exception as e:
            print(f"Skor dosyasına yazma hatası: {e}")

        self.check_button.config(state="disabled")
        self.hint_button.config(state="disabled")
        self.entry.config(state="disabled")
        self.start_button.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = AlienEscapeGame(root)
    root.mainloop()
