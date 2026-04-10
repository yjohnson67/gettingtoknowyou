from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
import json
import io
import base64
from statistics import mean

import matplotlib
matplotlib.use("Agg")  # important for Django/server use
import matplotlib.pyplot as plt

from .mongodb import scores_collection


def home(request):
    if request.method == "POST":
        name = request.POST.get("name")
        color = request.POST.get("color")

        if not name:
            return render(request, "home.html", {"error": "Name required"})

        return render(request, "result.html", {"name": name, "color": color})

    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


@csrf_exempt
def save_test_score(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "POST only"},
            status=405
        )

    try:
        data = json.loads(request.body)

        player_name = data.get("player_name")
        rocket_color = data.get("rocket_color")
        score = data.get("score")

        if not player_name:
            return JsonResponse(
                {"success": False, "error": "player_name is required"},
                status=400
            )

        if score is None:
            return JsonResponse(
                {"success": False, "error": "score is required"},
                status=400
            )

        try:
            score = int(score)
        except (TypeError, ValueError):
            return JsonResponse(
                {"success": False, "error": "score must be a number"},
                status=400
            )

        result = scores_collection.insert_one({
            "player_name": player_name,
            "rocket_color": rocket_color,
            "score": score,
            "played_at": now().isoformat(),
        })

        return JsonResponse({
            "success": True,
            "inserted_id": str(result.inserted_id),
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400
        )
    except Exception as e:
        print("SAVE ERROR:", str(e))
        return JsonResponse(
            {"success": False, "error": str(e)},
            status=500
        )


def fig_to_base64():
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    return graphic.decode("utf-8")


def build_player_line_chart(player_name, scores):
    if not scores:
        return None

    plt.figure(figsize=(6, 4))
    x_values = list(range(1, len(scores) + 1))
    plt.plot(x_values, scores, marker="o")
    plt.title(f"{player_name} Score History")
    plt.xlabel("Game Number")
    plt.ylabel("Score")
    chart = fig_to_base64()
    plt.close()
    return chart


def build_player_distribution_chart(scores):
    if not scores:
        return None

    plt.figure(figsize=(6, 4))
    bins = min(10, max(1, len(scores)))
    plt.hist(scores, bins=bins)
    plt.title("Score Distribution")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    chart = fig_to_base64()
    plt.close()
    return chart


def build_dashboard_top10_chart(leaderboard_data):
    if not leaderboard_data:
        return None

    players = [item["player_name"] for item in leaderboard_data]
    scores = [item["best_score"] for item in leaderboard_data]

    plt.figure(figsize=(8, 5))
    plt.bar(players, scores)
    plt.title("Top 10 Players")
    plt.xlabel("Player")
    plt.ylabel("Best Score")
    plt.xticks(rotation=45)
    chart = fig_to_base64()
    plt.close()
    return chart


def build_dashboard_scores_over_time_chart(all_games):
    if not all_games:
        return None

    sorted_games = sorted(all_games, key=lambda game: game.get("played_at", ""))
    x_values = list(range(1, len(sorted_games) + 1))
    y_values = []

    for game in sorted_games:
        try:
            y_values.append(int(game.get("score", 0)))
        except (TypeError, ValueError):
            y_values.append(0)

    plt.figure(figsize=(8, 5))
    plt.plot(x_values, y_values, marker="o")
    plt.title("All Scores Over Time")
    plt.xlabel("Game Number")
    plt.ylabel("Score")
    chart = fig_to_base64()
    plt.close()
    return chart


def leaderboard(request):
    try:
        all_scores = list(scores_collection.find())

        player_best_scores = {}

        for game in all_scores:
            player_name = game.get("player_name", "Unknown")
            score = game.get("score", 0)

            try:
                score = int(score)
            except (TypeError, ValueError):
                score = 0

            if player_name not in player_best_scores or score > player_best_scores[player_name]:
                player_best_scores[player_name] = score

        leaderboard_data = []
        for player_name, best_score in player_best_scores.items():
            leaderboard_data.append({
                "player_name": player_name,
                "best_score": best_score,
            })

        leaderboard_data.sort(key=lambda player: player["best_score"], reverse=True)
        leaderboard_data = leaderboard_data[:10]

        return render(request, "leaderboard.html", {
            "leaderboard": leaderboard_data
        })

    except Exception as e:
        return render(request, "leaderboard.html", {
            "leaderboard": [],
            "error": str(e)
        })


def leaderboard_api(request):
    try:
        all_scores = list(scores_collection.find())

        player_best_scores = {}

        for game in all_scores:
            player_name = game.get("player_name", "Unknown")
            score = game.get("score", 0)

            try:
                score = int(score)
            except (TypeError, ValueError):
                score = 0

            if player_name not in player_best_scores or score > player_best_scores[player_name]:
                player_best_scores[player_name] = score

        leaderboard_data = []
        for player_name, best_score in player_best_scores.items():
            leaderboard_data.append({
                "player_name": player_name,
                "best_score": best_score,
            })

        leaderboard_data.sort(key=lambda player: player["best_score"], reverse=True)
        leaderboard_data = leaderboard_data[:10]

        return JsonResponse({
            "success": True,
            "leaderboard": leaderboard_data
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


def player_stats(request, player_name):
    try:
        player_games = list(scores_collection.find({
            "player_name": player_name
        }).sort("played_at", 1))

        if not player_games:
            return render(request, "player_stats.html", {
                "player_name": player_name,
                "error": "No data found for this player."
            })

        scores = []
        played_at_list = []

        for game in player_games:
            try:
                scores.append(int(game.get("score", 0)))
            except (TypeError, ValueError):
                scores.append(0)

            played_at_list.append(game.get("played_at", "Unknown"))

        games_played = len(scores)
        best_score = max(scores)
        average_score = round(mean(scores), 2)

        trend = "No change"
        if len(scores) >= 2:
            if scores[-1] > scores[0]:
                trend = "Improving"
            elif scores[-1] < scores[0]:
                trend = "Declining"

        line_chart = build_player_line_chart(player_name, scores)
        distribution_chart = build_player_distribution_chart(scores)

        score_history = []
        for index, score in enumerate(scores):
            score_history.append({
                "game_number": index + 1,
                "score": score,
                "played_at": played_at_list[index],
            })

        return render(request, "player_stats.html", {
            "player_name": player_name,
            "games_played": games_played,
            "best_score": best_score,
            "average_score": average_score,
            "trend": trend,
            "scores": scores,
            "score_history": score_history,
            "line_chart": line_chart,
            "distribution_chart": distribution_chart,
        })

    except Exception as e:
        return render(request, "player_stats.html", {
            "player_name": player_name,
            "error": str(e)
        })


def dashboard(request):
    try:
        all_games = list(scores_collection.find())

        clean_scores = []
        player_best_scores = {}
        total_players_set = set()

        for game in all_games:
            player_name = game.get("player_name", "Unknown")
            total_players_set.add(player_name)

            try:
                score = int(game.get("score", 0))
            except (TypeError, ValueError):
                score = 0

            clean_scores.append(score)

            if player_name not in player_best_scores or score > player_best_scores[player_name]:
                player_best_scores[player_name] = score

        leaderboard_data = []
        for player_name, best_score in player_best_scores.items():
            leaderboard_data.append({
                "player_name": player_name,
                "best_score": best_score,
            })

        leaderboard_data.sort(key=lambda player: player["best_score"], reverse=True)
        top_ten = leaderboard_data[:10]

        total_games = len(clean_scores)
        total_players = len(total_players_set)
        average_score = round(mean(clean_scores), 2) if clean_scores else 0
        highest_score = max(clean_scores) if clean_scores else 0

        top10_chart = build_dashboard_top10_chart(top_ten)
        time_chart = build_dashboard_scores_over_time_chart(all_games)

        return render(request, "dashboard.html", {
            "top_ten": top_ten,
            "total_games": total_games,
            "total_players": total_players,
            "average_score": average_score,
            "highest_score": highest_score,
            "top10_chart": top10_chart,
            "time_chart": time_chart,
        })

    except Exception as e:
        return render(request, "dashboard.html", {
            "top_ten": [],
            "error": str(e)
        })