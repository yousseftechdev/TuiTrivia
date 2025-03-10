# TuiTrivia: A trivia game for the terminal

import requests
import json
import os
import threading
import time
import random
from player import Player
from termcolor import colored
from hashlib import sha256
from datetime import datetime

# Constants
TRIVIA_API_URL = "https://opentdb.com/api.php?amount=1&type=multiple"
SCORES_FILE = "scores.json"
USERS_FILE = "users.json"
CUSTOM_QUESTIONS_FILE = "custom_questions.json"
TIME_LIMIT = 30  # Time limit for answering questions in seconds
DEV_MODE = False  # Set to True to enable debug commands
# Add difficulty and category constants
DIFFICULTY = "easy"
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]
CATEGORY = "General Knowledge"

CATEGORIES = {
    "General Knowledge": 9,
    "Books": 10,
    "Film": 11,
    "Music": 12,
    "Musicals & Theatres": 13,
    "Television": 14,
    "Video Games": 15,
    "Board Games": 16,
    "Science & Nature": 17,
    "Computers": 18,
    "Mathematics": 19,
    "Mythology": 20,
    "Sports": 21,
    "Geography": 22,
    "History": 23,
    "Politics": 24,
    "Art": 25,
    "Celebrities": 26,
    "Animals": 27,
    "Vehicles": 28,
    "Comics": 29,
    "Gadgets": 30,
    "Anime & Manga": 31,
    "Cartoon & Animations": 32,
}


# Function to get a random trivia question
def get_random_question(difficulty=None, category=None):
    url = TRIVIA_API_URL
    if difficulty:
        url += f"&difficulty={difficulty}"
    if category:
        url += f"&category={category}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        question = data["results"][0]
        return question
    else:
        print(colored("Failed to fetch question", "red"))
        return None


# Function to load scores from a file
def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as file:
            return json.load(file)
    else:
        return {}


# Function to save scores to a file
def save_scores(scores):
    with open(SCORES_FILE, "w") as file:
        json.dump(scores, file, indent=4)


# Function to update user score
def update_score(username, score):
    scores = load_scores()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if username in scores:
        scores[username]["score"] += score
        scores[username]["date"] = date
    else:
        scores[username] = {"score": score, "date": date}
    save_scores(scores)


# Function to clear score for a user
def clear_score(username):
    scores = load_scores()
    if username in scores:
        del scores[username]
        save_scores(scores)
        print(colored(f"Score for {username} cleared", "green"))
    else:
        print(colored(f"No score found for {username}", "red"))


# Function to clear score for ALL users
def clear_all_scores():
    if os.path.exists(SCORES_FILE):
        os.remove(SCORES_FILE)
        print(colored("All scores cleared", "green"))
    else:
        print(colored("No scores found", "red"))


# Function to get high scores
def get_high_scores():
    scores = load_scores()
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    return sorted_scores


# Function to load users from a file
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    else:
        return {}


# Function to save users to a file
def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


# Function to hash a password
def hash_password(password):
    return sha256(password.encode()).hexdigest()


# Function to authenticate user
def authenticate_user():
    users = load_users()
    username = input("Enter your username: ")
    if username in users:
        password = input("Enter your password: ")
        if users[username] == hash_password(password):
            print(colored("Login successful", "green"))
            return username
        else:
            print(colored("Invalid password", "red"))
            return None
    else:
        print(colored("Username not found. Please register.", "red"))
        return None


# Function to register user
def register_user():
    users = load_users()
    username = input("Enter a new username: ")
    if username in users:
        print(
            colored(
                "Username already exists. Please choose a different username.", "red"
            )
        )
        return None
    password = input("Enter a new password: ")
    users[username] = hash_password(password)
    save_users(users)
    print(colored("Registration successful", "green"))
    return username


# Function to load custom questions from a file
def load_custom_questions():
    if os.path.exists(CUSTOM_QUESTIONS_FILE):
        with open(CUSTOM_QUESTIONS_FILE, "r") as file:
            return json.load(file)
    else:
        return []


# Function to save custom questions to a file
def save_custom_questions(questions):
    with open(CUSTOM_QUESTIONS_FILE, "w") as file:
        json.dump(questions, file, indent=4)


# Function to add a custom question
def add_custom_question():
    questions = load_custom_questions()
    question = input("Enter the question: ")
    correct_answer = input("Enter the correct answer: ")
    incorrect_answers = []
    for i in range(3):
        incorrect_answer = input(f"Enter incorrect answer {i+1}: ")
        incorrect_answers.append(incorrect_answer)
    questions.append(
        {
            "question": question,
            "correct_answer": correct_answer,
            "incorrect_answers": incorrect_answers,
        }
    )
    save_custom_questions(questions)
    print(colored("Custom question added", "green"))


# Function to get a random custom question
def get_random_custom_question():
    questions = load_custom_questions()
    if questions:
        return random.choice(questions)
    else:
        print(colored("No custom questions available", "red"))
        return None


# Function to timeout the player
def time_up():
    print(colored("\nTime's up!", "yellow"))
    raise TimeoutError


# Function to handle timed questions
def timed_input(prompt, timeout):
    timer = threading.Timer(timeout, time_up)
    timer.start()
    try:
        answer = input(prompt)
    except TimeoutError:
        answer = None
    timer.cancel()
    return answer


# Main function to run the trivia game
def main():
    global DEV_MODE, DIFFICULTY, CATEGORY

    print(colored("Welcome to TuiTrivia!", "cyan"))
    while True:
        choice = input("Do you want to (1) Login or (2) Register? ")
        if choice == "1":
            username = authenticate_user()
            if username:
                break
        elif choice == "2":
            username = register_user()
            if username:
                break
        else:
            print(colored("Invalid choice. Please enter 1 or 2.", "red"))

    while True:
        cmd = input(f"{username}> ")
        match cmd.split():
            case ["exit"]:
                break
            case ["help"]:
                print("Commands:")
                print("exit: Exit the game")
                print("help: Show this help message")
                print("clear: Clear the screen")
                print("scores: Show high scores")
                print("clearscore <username>: Clear your score")
                print("clearall: Clear all scores")
                print("trivia: Get a random trivia question")
                print("custom: Get a random custom trivia question")
                print("addcustom: Add a custom trivia question")
                print("edit <username> <score>: Edit a user's score")
                print("multiplayer: Start a multiplayer game")
                print("debug: Show debug information")
                print("debug color <color>: Test colored output")
                print("debug colors: Show available colors")
                print(
                    "debug timeout: Test timeout feature (this is for me cause the timeout function kept glitching)"
                )
                print("devmode: Enable/Disable developer mode")
                print("difficulty <level>: Set difficulty level (easy, medium, hard)")
                print("category <name>: Set question category")
            case ["about"]:
                print(
                    colored(
                        "TuiTrivia: A trivia game for the terminal", "white", "on_blue"
                    )
                )
                print(
                    "Note: When answering trivia questions, type the actual answer and not the number, and the time limit for answering is 30 seconds."
                )
            case ["devmode"]:
                if DEV_MODE:
                    DEV_MODE = False
                    print(colored("Developer mode disabled", "yellow"))
                else:
                    DEV_MODE = True
                    print(colored("Developer mode enabled", "yellow"))
            case ["edit", username, score]:
                try:
                    score = int(score)
                    update_score(username, score)
                except ValueError:
                    print(colored("Invalid score. Score must be an integer", "red"))
            case ["clear"]:
                print("\033c", end="")
            case ["scores"]:
                print("Scores:")
                for user, data in get_high_scores():
                    print(f"{user}: {data['score']} (Last updated: {data['date']})")
            case ["clearscore", username]:
                clear_score(username)
            case ["clearall"]:
                clear_all_scores()
            case ["trivia"]:
                incorrect = False
                while not incorrect:
                    question = get_random_question(DIFFICULTY, CATEGORY)
                    if question:
                        print(f"Question: {question['question']}")
                        for i, option in enumerate(
                            question["incorrect_answers"]
                            + [question["correct_answer"]],
                            1,
                        ):
                            print(f"{i}. {option}")
                        answer = timed_input("Your answer: ", TIME_LIMIT)
                        if answer == question["correct_answer"]:
                            print(colored("Correct!", "green"))
                            update_score(username, 10)
                        else:
                            print(colored("Incorrect!", "red"))
                            print(f"Correct answer: {question['correct_answer']}")
                            incorrect = True
                    print("High Scores:")
                    for user, data in get_high_scores():
                        print(f"{user}: {data['score']}")
            case ["difficulty"]:
                print("Current difficulty level:", DIFFICULTY)
                print("Available difficulty levels:", ", ".join(DIFFICULTY_LEVELS))
            case ["difficulty", level]:
                if level.lower() in DIFFICULTY_LEVELS:
                    DIFFICULTY = level.lower()
                    print(colored(f"Difficulty level set to {level.lower()}", "green"))
                else:
                    print(colored("Invalid difficulty level", "red"))
            case ["category"]:
                print("Current category:", CATEGORY)
                print("Available categories:")
                for name in CATEGORIES.keys():
                    print(f"{name}")
            case ["category", name]:
                if name in CATEGORIES:
                    CATEGORY = name
                    print(colored(f"Category set to {name}", "green"))
                else:
                    print(colored("Invalid category", "red"))
            case ["custom"]:
                incorrect = False
                while not incorrect:
                    question = get_random_custom_question()
                    if question:
                        print(f"Question: {question['question']}")
                        for i, option in enumerate(
                            question["incorrect_answers"]
                            + [question["correct_answer"]],
                            1,
                        ):
                            print(f"{i}. {option}")
                        answer = timed_input("Your answer: ", TIME_LIMIT)
                        if answer == question["correct_answer"]:
                            print(colored("Correct!", "green"))
                            update_score(username, 10)
                        else:
                            print(colored("Incorrect!", "red"))
                            print(f"Correct answer: {question['correct_answer']}")
                            incorrect = True
                    print("High Scores:")
                    for user, data in get_high_scores():
                        print(f"{user}: {data['score']}")
            case ["addcustom"]:
                add_custom_question()
            case ["multiplayer"]:
                players = input("Enter usernames of players (comma separated): ").split(
                    ","
                )
                players = [Player(player.strip()) for player in players]
                scores = {player.username: 0 for player in players}
                for i in range(10):
                    question = get_random_question()
                    if question:
                        print(f"Question no. {i+1}: {question['question']}")
                        for i, option in enumerate(
                            question["incorrect_answers"]
                            + [question["correct_answer"]],
                            1,
                        ):
                            print(f"{i}. {option}")
                        for player in players:
                            try:
                                player.getAnswer()
                                if player.answer == question["correct_answer"]:
                                    print(
                                        colored(
                                            f"{player.username} answered correctly!",
                                            "green",
                                        )
                                    )
                                    scores[player.username] += 10
                                else:
                                    print(
                                        colored(
                                            f"{player.username} answered incorrectly!",
                                            "red",
                                        )
                                    )
                                    incorrect = True
                            except TimeoutError:
                                print(
                                    colored(
                                        f"{player.username} did not answer in time!",
                                        "yellow",
                                    )
                                )
                                incorrect = True
                    print(f"Correct answer: {question['correct_answer']}")
                    print("Scores:")
                    for player, score in scores.items():
                        print(f"{player}: {score}")
            case ["debug"]:
                if DEV_MODE:
                    print("Scores:")
                    print(load_scores())
                    print("Users:")
                    print(load_users())
                    print("Custom Questions:")
                    print(load_custom_questions())
                else:
                    print(
                        colored(
                            "Invalid command. Type 'help' for a list of commands", "red"
                        )
                    )
            case ["debug", "users"]:
                if DEV_MODE:
                    print(load_users())
                else:
                    print(
                        colored(
                            "Invalid command. Type 'help' for a list of commands", "red"
                        )
                    )
            case ["debug", "custom"]:
                if DEV_MODE:
                    print(load_custom_questions())
                else:
                    print(
                        colored(
                            "Invalid command. Type 'help' for a list of commands", "red"
                        )
                    )
            case ["debug", "color", color]:
                if DEV_MODE:
                    try:
                        print(colored("This is a colored message", color))
                    except Exception as e:
                        print(colored(f"Error: {e}", "red"))
                else:
                    print(
                        colored(
                            "Invalid command. Type 'help' for a list of commands", "red"
                        )
                    )
            case ["debug", "colors"]:
                if DEV_MODE:
                    print("Colors:")
                    for color in [
                        "grey",
                        "red",
                        "green",
                        "yellow",
                        "blue",
                        "magenta",
                        "cyan",
                        "white",
                    ]:
                        print(colored(f"This is {color}", color))
                else:
                    print(
                        colored(
                            "Invalid command. Type 'help' for a list of commands", "red"
                        )
                    )
            case ["debug", "timeout"]:
                if DEV_MODE:
                    try:
                        time_up()
                    except TimeoutError:
                        print(
                            colored(
                                "If you can see this message and not an error, then the timeout feature is working correctly.",
                                "green",
                            )
                        )
                else:
                    print(
                        colored(
                            "Invalid command. Type 'help' for a list of commands", "red"
                        )
                    )
            case [""]:
                continue
            case _:
                print(
                    colored(
                        "Invalid command. Type 'help' for a list of commands", "red"
                    )
                )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\nExiting...", "yellow"))
