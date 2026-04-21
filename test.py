from flask import Flask, request, jsonify, render_template, redirect, abort
from datetime import datetime
import secrets
import string
import statistics
from math import floor

app = Flask(__name__)

number = 1712028000000

session = {"login": "test", "plan": "hobby"}

CURRENT_VERSION = "main"

seen_speeds = {
    "deepseek-r1-0528": [
        18.38,
        66.89,
        313.87,
        33.2,
        30.18,
        19.39,
        30.59,
        222.88,
        31.91,
        37.06,
    ],
    "deepseek-r1-0528-turbo": [
        37.86,
        32.89,
        53.83,
        35.9,
        43.32,
        59.16,
        16.9,
        44.77,
        29.16,
        43.31,
    ],
    "deepseek-v3-0324": [
        32.99,
        60.93,
        76.32,
        86.74,
        76.81,
        71.94,
        26.92,
        42.83,
        48.85,
        72.29,
    ],
    "deepseek-v3-0324-turbo": [
        863.67,
        106.01,
        96.11,
        101.74,
        14.54,
        50.67,
        96.89,
        116.27,
        219.03,
        183.73,
    ],
    "kimi-k2-0905": [
        15.23,
        136.58,
        62.17,
        34.25,
        78.27,
        81.59,
        70.45,
        19.99,
        34.18,
        54.49,
    ],
    "kimi-k2-0905-turbo": [
        940.36,
        1010.68,
        919.3,
        934.33,
        1019.37,
        967.57,
        995.85,
        947.5,
        484.51,
        944.87,
    ],
    "kimi-k2-thinking": [
        71.29,
        34.47,
        9.69,
        41.63,
        70.8,
        67.84,
        68.73,
        32.49,
        72.54,
        49.69,
    ],
    "kimi-k2-thinking-turbo": [
        58.67,
        8.17,
        1.12,
        4.2,
        5.79,
        3.45,
        2.28,
        3.14,
        2.65,
        1.81,
    ],
    "deepseek-v3.2": [23.01, 3.17, 7.31, 6.68, 7.14, 10.1, 2.33, 6.38, 1.73, 6.37],
    "deepseek-v3.2-chat": [
        35.51,
        32.82,
        32.09,
        34.47,
        23.16,
        35.75,
        25.7,
        22.1,
        22.71,
        21.41,
    ],
    "deepseek-v3.2-precision": [
        69.56,
        69.49,
        66.15,
        61.19,
        52.37,
        63.01,
        68.31,
        47.01,
        46.23,
        39.52,
    ],
    "glm-4.7": [92.21, 68.22, 65.25, 13.78, 51.56, 47.49, 13.98, 55.23, 66.39, 41.02],
    "glm-4.6": [
        136.39,
        114.77,
        111.82,
        108.39,
        125.16,
        111.0,
        100.26,
        51.33,
        103.39,
        94.95,
    ],
    "glm-4.6-turbo": [
        145.42,
        112.17,
        121.12,
        118.92,
        111.65,
        111.55,
        9.92,
        86.36,
        118.52,
        62.53,
    ],
    "glm-4.5": [
        198.21,
        195.79,
        209.58,
        209.46,
        171.91,
        247.33,
        267.29,
        264.69,
        182.24,
        270.56,
    ],
    "qwen3-coder": [
        12.21,
        16.76,
        27.92,
        30.79,
        20.49,
        28.75,
        27.78,
        71.12,
        68.7,
        76.57,
    ],
    "qwen3-coder-turbo": [
        1664.63,
        359.08,
        770.7,
        51.74,
        437.79,
        977.77,
        662.4,
        1073.35,
        531.35,
        178.77,
    ],
    "gemma-3-27b-it": [
        77.51,
        108.77,
        72.33,
        98.38,
        96.41,
        90.18,
        106.64,
        101.08,
        110.51,
        104.67,
    ],
    "llama-4-scout": [
        47.53,
        42.97,
        39.49,
        47.45,
        10.52,
        34.58,
        184.14,
        70.01,
        44.76,
        53.52,
    ],
    "llama3.3-70b": [
        0.7,
        1358.99,
        1508.38,
        1510.92,
        1480.87,
        1178.95,
        0.0,
        0.0,
        0.0,
        52.98,
    ],
    "minimax-m2.1": [
        63.84,
        58.25,
        53.09,
        152.3,
        48.35,
        15.66,
        10.22,
        51.61,
        16.42,
        82.61,
    ],
    "intellect-3": [
        58.25,
        58.83,
        57.18,
        114.32,
        68.39,
        155.95,
        76.92,
        24.11,
        235.98,
        483.57,
    ],
    "devstral-2": [
        283.75,
        235.07,
        176.37,
        67.23,
        101.67,
        13.34,
        76.46,
        144.12,
        166.84,
        65.41,
    ],
    "stok-0.4.1": [
        6474.44,
        3138.59,
        6852.15,
        3640.11,
        5731.88,
        5614.15,
        972.18,
        6636.07,
        3512.36,
        3608.52,
    ],
}


def comma_number(number: int):
    number = int(number)
    ordered_num = list(str(number))
    ordered_num.reverse()
    if len(ordered_num) > 3:
        splits = len(ordered_num) / 3
        splits = floor(splits)
        start = 0
        for x in range(0, splits):
            if start == 0:
                start += 3
            else:
                start += 4
            ordered_num.insert(start, ",")
    ordered_num.reverse()
    if ordered_num[0] == ",":
        ordered_num.pop(0)
    return "".join(ordered_num)


def money_format(value: float) -> str:
    return f"{round(value, 3):.3f}"


def openrouter_models():
    models_list = {
        "data": [
            {
                "speed": 100,
                "id": "kimi-k2-thinking",
                "name": "MoonshotAI: Kimi K2 Thinking",
                "created": 1762447430,
                "context_length": 262144,
                "max_completion_tokens": 262144,
                "quantization": "Q4_0",
                "pricing": {
                    "prompt": "0.0000004",
                    "completion": "0.0000015",
                },
            },
            {
                "speed": 150,
                "id": "kimi-k2-thinking-turbo",
                "name": "MoonshotAI: Kimi K2 Thinking",
                "created": 1762447430,
                "context_length": 262144,
                "max_completion_tokens": 262144,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.000001",
                    "completion": "0.000003",
                },
            },
            {
                "speed": 50,
                "id": "deepseek-v3.2",
                "name": "DeepSeek: DeepSeek V3.2",
                "created": 1755799640,
                "context_length": 163840,
                "max_completion_tokens": 163840,
                "quantization": "Q4_0",
                "pricing": {
                    "prompt": "0.00000028",
                    "completion": "0.00000038",
                },
            },
            {
                "speed": 50,
                "id": "deepseek-v3.2-chat",
                "name": "DeepSeek: DeepSeek V3.2",
                "created": 1755799640,
                "context_length": 163840,
                "max_completion_tokens": 163840,
                "quantization": "Q4_0",
                "pricing": {
                    "prompt": "0.00000028",
                    "completion": "0.00000038",
                },
            },
            {
                "speed": 50,
                "id": "deepseek-v3.2-precision",
                "name": "DeepSeek: DeepSeek V3.2",
                "created": 1755799640,
                "context_length": 163840,
                "max_completion_tokens": 163840,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.00000035",
                    "completion": "0.00000045",
                },
            },
            {
                "speed": 50,
                "id": "devstral-2",
                "name": "Mistral: Devstral 2 2512",
                "created": 1765688214,
                "context_length": 262144,
                "max_completion_tokens": 262144,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.00000007",
                    "completion": "0.00000031",
                },
            },
            {
                "speed": 70,
                "id": "kimi-k2-0905",
                "name": "MoonshotAI: Kimi K2 0905",
                "created": 1757083316,
                "context_length": 131072,
                "max_completion_tokens": 131072,
                "quantization": "Q8_0",
                "pricing": {
                    "prompt": "0.00000015",
                    "completion": "0.00000055",
                },
            },
            {
                "speed": 500,
                "id": "kimi-k2-0905-turbo",
                "name": "MoonshotAI: Kimi K2 0905",
                "created": 1757083316,
                "context_length": 131072,
                "max_completion_tokens": 8192,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.00000035",
                    "completion": "0.000001",
                },
            },
            {
                "speed": 50,
                "id": "glm-4.7",
                "name": "Z.AI: GLM 4.7",
                "created": 1766445494,
                "context_length": 202752,
                "max_completion_tokens": 202752,
                "quantization": "fp4",
                "pricing": {
                    "prompt": "0.00000040",
                    "completion": "0.00000140",
                },
            },
            {
                "speed": 50,
                "id": "glm-4.6-turbo",
                "name": "Z.AI: GLM 4.6",
                "created": 1762575030,
                "context_length": 202752,
                "max_completion_tokens": 202752,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.0000005",
                    "completion": "0.00000225",
                },
            },
            {
                "speed": 50,
                "id": "minimax-m2.1",
                "name": "MiniMax: MiniMax M2.1",
                "created": 1766794658,
                "context_length": 131072,
                "max_completion_tokens": 131072,
                "quantization": "awq",
                "pricing": {
                    "prompt": "0.00000028",
                    "completion": "0.0000009",
                },
            },
            {
                "speed": 50,
                "id": "intellect-3",
                "name": "Prime Intellect: INTELLECT-3",
                "created": 1764358004,
                "context_length": 128000,
                "max_completion_tokens": 128000,
                "quantization": "Q8_0",
                "pricing": {
                    "prompt": "0.00000015",
                    "completion": "0.000001",
                },
            },
            {
                "speed": 30,
                "id": "glm-4.6",
                "name": "Z.AI: GLM 4.6",
                "created": number,
                "context_length": 131072,
                "max_completion_tokens": 131072,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.0000003",
                    "completion": "0.0000006",
                },
            },
            {
                "speed": 30,
                "id": "glm-4.5",
                "name": "Z.AI: GLM 4.5",
                "created": number,
                "context_length": 131072,
                "max_completion_tokens": 131072,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.0000002",
                    "completion": "0.0000004",
                },
            },
            {
                "speed": 10,
                "id": "deepseek-v3-0324",
                "name": "DeepSeek: DeepSeek V3 0324",
                "created": number,
                "context_length": 131072,
                "max_completion_tokens": 8192,
                "quantization": "Q4_0",
                "pricing": {
                    "prompt": "0.0000002",
                    "completion": "0.00000025",
                },
            },
            {
                "speed": 500,
                "id": "deepseek-v3-0324-turbo",
                "name": "DeepSeek: DeepSeek V3 0324",
                "created": number,
                "context_length": 131072,
                "max_completion_tokens": 8192,
                "quantization": "Q4_0",
                "pricing": {
                    "prompt": "0.0000005",
                    "completion": "0.000001",
                },
            },
            {
                "speed": 120,
                "id": "deepseek-r1-0528",
                "name": "DeepSeek: R1 0528",
                "created": number,
                "context_length": 131072,
                "max_completion_tokens": 131072,
                "quantization": "Q4_0",
                "pricing": {
                    "prompt": "0.00000025",
                    "completion": "0.00000025",
                },
            },
            {
                "speed": 150,
                "id": "deepseek-r1-0528-turbo",
                "name": "DeepSeek: R1 0528",
                "created": number,
                "context_length": 131072,
                "max_completion_tokens": 131072,
                "quantization": "Q4_0",
                "pricing": {
                    "prompt": "0.000001",
                    "completion": "0.000002",
                },
            },
            {
                "speed": 200,
                "id": "qwen3-coder",
                "name": "Qwen: Qwen3 Coder",
                "created": 1753219761.509367,
                "context_length": 131072,
                "max_completion_tokens": 131072,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.00000015",
                    "completion": "0.00000035",
                },
            },
            {
                "speed": 250,
                "id": "qwen3-coder-turbo",
                "name": "Qwen: Qwen3 Coder",
                "created": 1753292189.809791,
                "context_length": 131072,
                "max_completion_tokens": 131072,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.0000002",
                    "completion": "0.0000005",
                },
            },
            {
                "speed": 80,
                "id": "gemma-3-27b-it",
                "name": "Google: Gemma 3 27B",
                "created": number,
                "context_length": 131072,
                "max_completion_tokens": 131072,
                "quantization": "Q8_0",
                "pricing": {
                    "prompt": "0.00000004",
                    "completion": "0.00000010",
                },
            },
            {
                "speed": 65,
                "id": "llama-4-scout",
                "name": "Meta: Llama 4 Scout",
                "created": number,
                "context_length": 262144,
                "max_completion_tokens": 16384,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.00000008",
                    "completion": "0.0000004",
                },
            },
            {
                "speed": 40,
                "id": "llama3.3-70b",
                "name": "Meta: Llama 3.3 70B Instruct",
                "created": number,
                "context_length": 131072,
                "max_completion_tokens": 8192,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.00000012",
                    "completion": "0.0000002",
                },
            },
            {
                "speed": 50,
                "id": "deepseek-r1-distill-llama-70b",
                "name": "DeepSeek: R1 Distill Llama 70B",
                "created": number,
                "context_length": 65536,
                "max_completion_tokens": 65536,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.0000001",
                    "completion": "0.0000001",
                },
            },
            {
                "speed": 50,
                "id": "deepseek-r1-distill-qwen-32b",
                "name": "DeepSeek: R1 Distill Qwen 32B",
                "created": number,
                "context_length": 65536,
                "max_completion_tokens": 65536,
                "quantization": "fp8",
                "pricing": {
                    "prompt": "0.0000001",
                    "completion": "0.0000001",
                },
            },
            {
                "speed": 3500,
                "id": "stok-0.4.1",
                "name": "CrofAI: Stok 0.4.1",
                "created": number,
                "context_length": 2048,
                "max_completion_tokens": 2048,
                "quantization": "stok",
                "pricing": {
                    "prompt": "0.0",
                    "completion": "0.0",
                },
            },
        ]
    }
    return models_list


data_for_pricing = openrouter_models()


def current_month() -> int:
    return datetime.now().month


def get_month_name(month_num):
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    if 1 <= month_num <= 12:
        return months[month_num - 1]
    else:
        raise ValueError("Month number must be between 1 and 12")


@app.route("/home")
def home_page():
    return render_template("ui3/home.html", version=CURRENT_VERSION)


@app.route("/user-api/credits")
def user_credits_api():
    if "login" in session:
        username = session["login"]
        userdata = {}
        userdata["credits"] = 5
        return jsonify(money_format(userdata["credits"]))
    return "no"


@app.route("/dashboard")
def dashboard():
    username = session["login"]
    userdata = {
        "usable_requests": 250,
        "requests_plan": 250,
        "free_requests": 12345,
    }

    usable_requests = userdata.get("usable_requests")
    requests_plan = userdata.get("requests_plan")

    month = get_month_name(current_month())

    free_requests = userdata["free_requests"]
    return render_template(
        "ui3/dashboard.html",
        free_requests=userdata["free_requests"],
        month=month,
        usable_requests=usable_requests,
        requests_plan=requests_plan,
    )


@app.route("/pricing")
def pricing():
    vision_models = ["llama-4-scout"]
    models = eval(str(data_for_pricing["data"]))

    model_index = -1
    for model in models:
        model_index += 1
        mid = model["id"]
        if mid in seen_speeds:
            models[model_index]["speed"] = round(statistics.mean(seen_speeds[mid]))

    print("updated model speeds")
    new_data = list(models)
    for model in new_data:
        prompt_price = str(round(float(model["pricing"]["prompt"]) * 1000000, 2))
        if len(prompt_price) == 3:
            prompt_price = f"{prompt_price}0"

        completion_price = str(
            round(float(model["pricing"]["completion"]) * 1000000, 2)
        )
        if len(completion_price) == 3:
            completion_price = f"{completion_price}0"

        model["pricing"]["prompt"] = prompt_price
        model["pricing"]["completion"] = completion_price

        model["context_length"] = comma_number(model["context_length"])
        model["max_completion_tokens"] = comma_number(model["max_completion_tokens"])

    if "login" in session:
        if "plan" not in session:
            requests_plan = 250
            if requests_plan == None:
                session["plan"] = "free"
            if requests_plan == 250:
                session["plan"] = "hobby"
            if requests_plan == 1000:
                session["plan"] = "pro"
        return render_template(
            "ui3/pricing.html",
            loggedin=True,
            models=models,
            float=float,
            round=round,
            plan=session["plan"],
            vision_models=vision_models,
        )
    else:
        return render_template(
            "ui3/pricing.html",
            loggedin=False,
            models=models,
            float=float,
            round=round,
            plan="free",
            vision_models=vision_models,
        )


@app.route("/", methods=["GET", "POST"])
def home():
    models = openrouter_models()["data"]
    if "login" in session:
        return render_template("ui3/playground.html", models=models, admin=False)
    else:
        return redirect("/home")


@app.route("/user_api_create-token")
def create_token_api():
    if "login" in session:
        username = session["login"]
        userdata = {}
        newtoken = f"nahcrof_{''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(20))}"
        userdata["token"] = newtoken
        return jsonify({"message": "success", "token": newtoken})
    else:
        return jsonify({"message": "no."}), 401


@app.route("/privacy")
def privacy_page():
    return render_template("ui3/privacy.html")


@app.route("/privacy/")
def privacy_page2():
    return render_template("ui3/privacy.html")


@app.route("/startups", methods=["GET", "POST"])
def startups():
    if request.method == "POST":
        data = request.form
        startup_name = data.get("startup_name")
        website = data.get("website")
        email = data.get("contact_email")
        description = data.get("description")
        use_case = data.get("use_case")
        print(
            f"\nSTARTUP REQUEST\ncompany name: {startup_name}\nwebsite: {website}\nemail: {email}\ndescription: ```{description}```\nuse for crofAI: ```{use_case}```"
        )
        return render_template("ui3/startups.html", success_message="Form sumbitted!")
    else:
        return render_template("ui3/startups.html")


@app.route("/settings")
def settings():
    if "login" in session:
        user = {
            "credits": 5,
            "user_type": "normal",
            "auto_top_up": "off",
            "email": "email@example.com",
        }
        top_up = True if user["auto_top_up"] == "on" else False
        user_credits = (
            money_format(user["credits"]) if user["user_type"] != "free" else "∞"
        )
        try:
            email = user["email"]
        except KeyError:
            email = None
        return render_template(
            "ui3/settings.html",
            username=session["login"],
            user_credits=user_credits,
            email=email,
            top_up=top_up,
        )
    else:
        return redirect("/login")


@app.route("/settings-api/add-credits")
def add_credits_page():
    if "login" in session:
        username = session["login"]
        return redirect("https://buy.stripe.com/test")
    else:
        return redirect("/login")


@app.route("/settings-api/auto-top-up", methods=["POST"])
def auto_top_up_api():
    if "login" in session:
        username = session["login"]
        userdata = {}
        data = request.json
        userdata["auto_top_up"] = data["toggle"]
        userdata = str(userdata)
        return jsonify("success")
    else:
        return abort(401)


@app.route("/settings-api/delete-user")
def delete_user():
    return redirect("/logout")


@app.route("/settings-api/update-password", methods=["POST"])
def update_user_password():
    username = session["login"]
    data = request.json
    current_password_input = data.get("currentPassword", None)
    new_password_input = data.get("newPassword", None)
    return jsonify({"error": False})


@app.route("/settings-api/update-email/<email>")
def update_user_email(email):
    if "login" in session:
        return redirect("/settings")
    else:
        return "you're not logged in silly goose"


@app.route("/login", methods=["GET", "POST"])
@app.route("/signin", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return redirect("/")
    else:
        return render_template("ui3/signin.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return redirect("/")
    else:
        return render_template("ui3/signup.html")


@app.route("/ui/crofui.css")
def crofuicss():
    return redirect("https://ai.nahcrof.com/ui/crofui.css")


@app.route("/ui/crofui.js")
def crofuijs():
    return redirect("https://ai.nahcrof.com/ui/crofui.js")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)
