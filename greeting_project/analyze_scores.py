import matplotlib.pyplot as plt
from pymongo import MongoClient
from collections import defaultdict

# -----------------------------------
# STEP 1: CONNECT TO MONGODB ATLAS
# -----------------------------------
MONGO_URI = MONGODB_URI="mongodb+srv://ibehopeful_db_user:3jm869YmMeWVgbNS@users.recrjei.mongodb.net/"
DB_NAME = "rocket_game"
COLLECTION_NAME = "scores"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
scores_collection = db[COLLECTION_NAME]


# -----------------------------------
# HELPER
# -----------------------------------
def divider(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def get_all_scores():
    return list(scores_collection.find().sort("played_at", 1))


# -----------------------------------
# 1. GROUP BY PLAYER
# -----------------------------------
def group_scores_by_player(scores):
    grouped = defaultdict(list)

    for score in scores:
        player_name = score.get("player_name", "Unknown")
        grouped[player_name].append(score)

    return grouped


# -----------------------------------
# 2. HIGHEST SCORE PER PLAYER
# -----------------------------------
def print_highest_score_per_player(grouped_scores):
    divider("HIGHEST SCORE PER PLAYER")

    for player, games in grouped_scores.items():
        highest = max(game.get("score", 0) for game in games)
        print(f"{player}: {highest}")


# -----------------------------------
# 3. NUMBER OF GAMES PLAYED
# -----------------------------------
def print_games_played(grouped_scores):
    divider("NUMBER OF GAMES PLAYED")

    for player, games in grouped_scores.items():
        print(f"{player}: {len(games)} games")


# -----------------------------------
# 4. AVERAGE SCORE PER PLAYER
# -----------------------------------
def print_average_score_per_player(grouped_scores):
    divider("AVERAGE SCORE PER PLAYER")

    for player, games in grouped_scores.items():
        total = sum(game.get("score", 0) for game in games)
        average = total / len(games)
        print(f"{player}: {average:.2f}")


# -----------------------------------
# 5. SIMPLE TREND CHECK
# -----------------------------------
def print_player_trends(grouped_scores):
    divider("PLAYER IMPROVEMENT TRENDS")

    for player, games in grouped_scores.items():
        scores = [game.get("score", 0) for game in games]

        if len(scores) < 2:
            print(f"{player}: Not enough games to see a trend")
            continue

        first_score = scores[0]
        last_score = scores[-1]

        if last_score > first_score:
            print(f"{player}: Improving ({first_score} → {last_score})")
        elif last_score < first_score:
            print(f"{player}: Declining ({first_score} → {last_score})")
        else:
            print(f"{player}: No change ({first_score} → {last_score})")


# -----------------------------------
# 6. TOP PLAYERS BY BEST SCORE
# -----------------------------------
def print_top_players(grouped_scores):
    divider("TOP PLAYERS BY BEST SCORE")

    player_best_scores = []

    for player, games in grouped_scores.items():
        highest = max(game.get("score", 0) for game in games)
        player_best_scores.append((player, highest))

    player_best_scores.sort(key=lambda x: x[1], reverse=True)

    for rank, (player, best_score) in enumerate(player_best_scores, start=1):
        print(f"{rank}. {player} - {best_score}")


# -----------------------------------
# 7. Bar Chart for Top Players
# -----------------------------------
def plot_top_players(grouped_scores):
    divider("CREATING TOP PLAYERS CHART")

    player_best_scores = []

    for player, games in grouped_scores.items():
        highest = max(game.get("score", 0) for game in games)
        player_best_scores.append((player, highest))

    # Sort descending
    player_best_scores.sort(key=lambda x: x[1], reverse=True)

    players = [p[0] for p in player_best_scores]
    scores = [p[1] for p in player_best_scores]

    plt.figure()
    plt.bar(players, scores)
    plt.title("Top Players by Best Score")
    plt.xlabel("Player")
    plt.ylabel("Score")

    plt.show()


# -----------------------------------
# 8. line Chart for Scores Over Time
# -----------------------------------
def plot_scores_over_time(scores):
    divider("CREATING SCORE OVER TIME CHART")

    dates = []
    values = []

    for score in scores:
        dates.append(score.get("played_at"))
        values.append(score.get("score", 0))

    plt.figure()
    plt.plot(dates, values, marker='o')
    plt.title("Scores Over Time")
    plt.xlabel("Time")
    plt.ylabel("Score")

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()


# -----------------------------------
# 9. Histogram for Score Distribution
# -----------------------------------
def plot_score_distribution(scores):
    divider("CREATING SCORE DISTRIBUTION")

    values = [score.get("score", 0) for score in scores]

    plt.figure()
    plt.hist(values, bins=10)
    plt.title("Score Distribution")
    plt.xlabel("Score")
    plt.ylabel("Frequency")

    plt.show()


# -----------------------------------
# MAIN
# -----------------------------------
if __name__ == "__main__":
    all_scores = get_all_scores()
    grouped_scores = group_scores_by_player(all_scores)

    print_highest_score_per_player(grouped_scores)
    print_games_played(grouped_scores)
    print_average_score_per_player(grouped_scores)
    print_player_trends(grouped_scores)
    print_top_players(grouped_scores)

    # NEW: charts
    plot_top_players(grouped_scores)
    plot_scores_over_time(all_scores)
    plot_score_distribution(all_scores)

    client.close()