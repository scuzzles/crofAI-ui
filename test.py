from flask import Flask, request, jsonify, render_template, url_for, redirect, abort, send_file, Response, stream_with_context # I don't need all of these for this test but I was lazy
from datetime import datetime, date, timedelta
import secrets
import string
import statistics
from math import floor

app = Flask(__name__)

number = 1712028000000 # got lazy, forgot I did this. there's a reason newer models don't use this

session = {"login": "test", "plan": "hobby"} # feel free to play with these values

# this can be set to "main" or "test".
CURRENT_VERSION = "main"

seen_speeds = {'deepseek-r1-0528': [18.38, 66.89, 313.87, 33.2, 30.18, 19.39, 30.59, 222.88, 31.91, 37.06], 'deepseek-r1-0528-turbo': [37.86, 32.89, 53.83, 35.9, 43.32, 59.16, 16.9, 44.77, 29.16, 43.31], 'deepseek-r1-distill-llama-70b': [89.08, 90.72, 80.95, 95.92, 151.95, 107.41, 90.42, 4.44, 4.72, 4.64], 'deepseek-r1-distill-qwen-32b': [152.56, 94.14, 64.28, 97.84, 162.84, 110.69, 101.88, 2.17, 3.64, 4.87], 'deepseek-v3-0324': [32.99, 60.93, 76.32, 86.74, 76.81, 71.94, 26.92, 42.83, 48.85, 72.29], 'deepseek-v3-0324-turbo': [863.67, 106.01, 96.11, 101.74, 14.54, 50.67, 96.89, 116.27, 219.03, 183.73], 'deepseek-v3.1': [0.96, 0.73, 1.93, 0.0, 8.26, 1.21, 0.91, 0.0, 0.7, 0.91], 'deepseek-v3.1-reasoner': [1118.98, 1059.44, 209.4, 13.55, 1223.42, 1239.33, 1414.29, 1272.03, 1348.65, 10.72], 'deepseek-v3.1-terminus': [0.0, 0.0, 0.0, 13.9, 15.21, 0.0, 0.0, 0.0, 0.0, 22.19], 'deepseek-v3.1-terminus-reasoner': [783.98, 1247.93, 1762.81, 3.5, 7.9, 7.8, 1033.16, 1471.0, 14.11, 288.92], 'deepseek-v3.1:free': [2.07, 0.81, 0.97, 1.0, 2.78, 0.62, 1.65, 1.95, 0.5, 1.12], 'deepseek-v3.2': [23.01, 3.17, 7.31, 6.68, 7.14, 10.1, 2.33, 6.38, 1.73, 6.37], 'deepseek-v3.2-chat': [35.51, 32.82, 32.09, 34.47, 23.16, 35.75, 25.7, 22.1, 22.71, 21.41], 'deepseek-v3.2-exp': [185.23, 207.01, 127.62, 106.62, 108.84, 138.79, 117.32, 264.27, 278.55, 183.38], 'deepseek-v3.2-precision': [69.56, 69.49, 66.15, 61.19, 52.37, 63.01, 68.31, 47.01, 46.23, 39.52], 'deepseek-v3.2-speciale': [107.22, 110.62, 115.24, 113.07, 99.24, 69.63, 43.45, 26.87, 59.1, 30.16], 'devstral-2': [283.75, 235.07, 176.37, 67.23, 101.67, 13.34, 76.46, 144.12, 166.84, 65.41], 'gemma-3-27b-it': [77.51, 108.77, 72.33, 98.38, 96.41, 90.18, 106.64, 101.08, 110.51, 104.67], 'glm-4.5': [198.21, 195.79, 209.58, 209.46, 171.91, 247.33, 267.29, 264.69, 182.24, 270.56], 'glm-4.6': [136.39, 114.77, 111.82, 108.39, 125.16, 111.0, 100.26, 51.33, 103.39, 94.95], 'glm-4.6-turbo': [145.42, 112.17, 121.12, 118.92, 111.65, 111.55, 9.92, 86.36, 118.52, 62.53], 'glm-4.7': [92.21, 68.22, 65.25, 13.78, 51.56, 47.49, 13.98, 55.23, 66.39, 41.02], 'glm-4.7-precision': [144.61, 25.03, 17.17, 88.34, 307.53, 151.0, 276.2], 'gpt-oss-120b': [75.3, 55.28, 71.99, 69.24, 80.61, 64.81, 62.07, 187.22, 609.55, 179.79], 'gpt-oss-safeguard-120b': [0.0, 0.0, 166.07, 482.25, 743.18, 734.43, 588.27, 600.64, 712.73, 405.58], 'intellect-3': [58.25, 58.83, 57.18, 114.32, 68.39, 155.95, 76.92, 24.11, 235.98, 483.57], 'kimi-k2-0905': [15.23, 136.58, 62.17, 34.25, 78.27, 81.59, 70.45, 19.99, 34.18, 54.49], 'kimi-k2-0905-turbo': [940.36, 1010.68, 919.3, 934.33, 1019.37, 967.57, 995.85, 947.5, 484.51, 944.87], 'kimi-k2-eco': [0.0, 0.0, 0.0, 22.73, 40.78, 49.2, 7.47, 26.81, 0.0, 0.0], 'kimi-k2-thinking': [71.29, 34.47, 9.69, 41.63, 70.8, 67.84, 68.73, 32.49, 72.54, 49.69], 'kimi-k2-thinking-turbo': [58.67, 8.17, 1.12, 4.2, 5.79, 3.45, 2.28, 3.14, 2.65, 1.81], 'llama-4-scout': [47.53, 42.97, 39.49, 47.45, 10.52, 34.58, 184.14, 70.01, 44.76, 53.52], 'llama3.3-70b': [0.7, 1358.99, 1508.38, 1510.92, 1480.87, 1178.95, 0.0, 0.0, 0.0, 52.98], 'minimax-m2': [90.47, 110.54, 87.44, 47.75, 113.84, 139.68, 150.27, 67.75, 961.63, 138.86], 'minimax-m2.1': [63.84, 58.25, 53.09, 152.3, 48.35, 15.66, 10.22, 51.61, 16.42, 82.61], 'minimax-m2.1-precision': [47.17, 56.41, 18.27, 146.61, 35.55, 44.73, 254.27, 215.24, 158.44, 201.76], 'qwen3-235b-a22b-2507-instruct': [1058.81, 94.03, 75.57, 1261.07, 75.23, 55.16, 43.66, 46.16, 59.45, 68.04], 'qwen3-235b-a22b-2507-thinking': [59.2, 71.82, 64.69, 66.14, 69.32, 70.99, 58.73, 84.11, 165.43, 272.41], 'qwen3-coder': [12.21, 16.76, 27.92, 30.79, 20.49, 28.75, 27.78, 71.12, 68.7, 76.57], 'qwen3-coder-turbo': [1664.63, 359.08, 770.7, 51.74, 437.79, 977.77, 662.4, 1073.35, 531.35, 178.77], 'qwen3-coder:free': [129.0, 121.36, 34.2, 70.0, 69.33, 69.55, 67.95, 72.6, 77.26, 737.01], 'qwen3-next-80b-a3b-instruct': [3.05, 164.75, 31.84, 34.69, 23.01, 1772.24, 7.48, 2990.95, 1393.61, 11.44], 'ring-1t': [0.67, 45.29, 254.07, 283.02, 191.84, 272.44, 207.56, 20.89, 0.0, 0.0], 'stok-0.4.1': [6474.44, 3138.59, 6852.15, 3640.11, 5731.88, 5614.15, 972.18, 6636.07, 3512.36, 3608.52]}
# seen_speeds is usually pulled from a mem cache every time it's needed but I figured this would be easier for simple testing

def comma_number(number: int):
    number = int(number)
    ordered_num = list(str(number))
    ordered_num.reverse()
    if len(ordered_num) > 3:
        splits = len(ordered_num)/3
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

def money_format(value: float) -> str: # I got lazy
    return f"{round(value, 3):.3f}"

def openrouter_models(): # This is just a model list, it's called openrouter_models because I changed the format when I started working with openrouter
    models_list = {
      "data": [

        #{
        #    "speed": 10,
        #    "id": "crof-tester",
        #    "name": "CrofAI: Crof Tester",
        #    "created": number,
        #    "context_length": 32000,
        #    "max_completion_tokens": 30000,
        #    "quantization": "fp2",
        #    "pricing": {
        #        "prompt": "0.0000002",
        #        "completion": "0.00000025",
        #    }
        #},

        #{
        #  "speed": 70,
        #  "id": "kimi-k2-thinking",
        #  "name": "MoonshotAI: Kimi K2 Thinking",
        #  "created": 1762447430,
        #  "context_length": 131072,
        #  "max_completion_tokens": 131072,
        #  "quantization": "fp4",
        #  "pricing": {
        #    "prompt": "0.00000040",
        #    "completion": "0.00000080",
        #  }
        #},

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
          }
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
          }
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
          }
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
          }
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
          }
        },

        {
          "speed": 50,
          "id": "deepseek-v3.2-speciale",
          "name": "DeepSeek: DeepSeek V3.2 Speciale",
          "created": 1765220964,
          "context_length": 163840,
          "max_completion_tokens": 163840,
          "quantization": "fp8",
          "pricing": {
            "prompt": "0.00000035",
            "completion": "0.00000045",
          }
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
          }
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
          }
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
          }
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
          }
        },

        {
          "speed": 50,
          "id": "glm-4.7-precision",
          "name": "Z.AI: GLM 4.7",
          "created": 1766957785,
          "context_length": 202752,
          "max_completion_tokens": 202752,
          "quantization": "fp8",
          "pricing": {
            "prompt": "0.00000050",
            "completion": "0.00000210",
          }
        },

        {
          "speed": 100,
          "id": "glm-4.6-turbo",
          "name": "Z.AI: GLM 4.6",
          "created": 1762575030,
          "context_length": 202752,
          "max_completion_tokens": 202752,
          "quantization": "fp8",
          "pricing": {
            "prompt": "0.0000005",
            "completion": "0.00000225",
          }
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
          }
        },

        {
          "speed": 50,
          "id": "minimax-m2.1-precision",
          "name": "MiniMax: MiniMax M2.1",
          "created": 1766957785,
          "context_length": 196608,
          "max_completion_tokens": 196608,
          "quantization": "fp8",
          "pricing": {
            "prompt": "0.00000035",
            "completion": "0.00000127",
          }
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
          }
        },

        {
          "speed": 20,
          "id": "kimi-k2-eco",
          "name": "MoonshotAI: Kimi K2",
          "created": number,
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q2_k",
          "pricing": {
            "prompt": "0.00000005",
            "completion": "0.0000001",
          }
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
          }
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
          }
        },

        {
          "speed": 30,
          "id": "ring-1t",
          "name": "inclusionAI: Ring-1T",
          "created": 1757083316,
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q4_0",
          "pricing": {
            "prompt": "0.0000004",
            "completion": "0.000001",
          }
        },

        {
          "speed": 15,
          "id": "deepseek-v3.2-exp",
          "name": "DeepSeek: DeepSeek V3.2 Exp",
          "created": 1755799640,
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q4_0",
          "pricing": {
            "prompt": "0.00000015",
            "completion": "0.0000003"
          }
        },

        {
          "speed": 18,
          "id": "deepseek-v3.1-terminus",
          "name": "DeepSeek: DeepSeek V3.1 Terminus",
          "created": 1755799640,
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q4_0",
          "pricing": {
            "prompt": "0.0000002",
            "completion": "0.0000005",
          }
        },

        {
          "speed": 18,
          "id": "deepseek-v3.1-terminus-reasoner",
          "name": "DeepSeek: DeepSeek V3.1 Terminus",
          "created": 1755799640,
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q4_0",
          "pricing": {
            "prompt": "0.0000002",
            "completion": "0.0000005",
          }
        },

        {
          "speed": 18,
          "id": "deepseek-v3.1",
          "name": "DeepSeek: DeepSeek V3.1",
          "created": 1755799640,
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q4_0",
          "pricing": {
            "prompt": "0.00000015",
            "completion": "0.0000005",
          }
        },

        {
          "speed": 32,
          "id": "deepseek-v3.1-reasoner",
          "name": "DeepSeek: DeepSeek V3.1",
          "created": 1755799640,
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q4_0",
          "pricing": {
            "prompt": "0.00000015",
            "completion": "0.0000005",
          }
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
            }
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
            }
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
          }
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
          }
        },

        {
          "speed": 322,
          "id": "qwen3-next-80b-a3b-instruct",
          "name": "Qwen: Qwen3 Next 80B A3B Instruct",
          "created": 1757651484.888002, # replace with appropriate number
          "context_length": 262144,
          "max_completion_tokens": 262144,
          "quantization": "Q8_0",
          "pricing": {
            "prompt": "0.00000008",
            "completion": "0.00000038",
          }
        },

        {
          "speed": 50,
          "id": "qwen3-235b-a22b-2507-instruct",
          "name": "Qwen: Qwen3 235B A22B 2507",
          "created": 1753149982.621645, # replace with appropriate number
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q8_0",
          "pricing": {
            "prompt": "0.0000001",
            "completion": "0.00000025",
          }
        },

        {
          "speed": 27,
          "id": "qwen3-235b-a22b-2507-thinking",
          "name": "Qwen: Qwen3 235B A22B Thinking 2507",
          "created": 1753493357.191588, # replace with appropriate number
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q8_0",
          "pricing": {
            "prompt": "0.0000001",
            "completion": "0.0000003",
          }
        },

        {
          "speed": 200,
          "id": "qwen3-coder",
          "name": "Qwen: Qwen3 Coder",
          "created": 1753219761.509367, # replace with appropriate number
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "fp8",
          "pricing": {
            "prompt": "0.00000015",
            "completion": "0.00000035",
          }
        },

        {
          "speed": 250,
          "id": "qwen3-coder-turbo",
          "name": "Qwen: Qwen3 Coder",
          "created": 1753292189.809791, # replace with appropriate number
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "fp8",
          "pricing": {
            "prompt": "0.0000002",
            "completion": "0.0000005",
          }
        },

        {
          "speed": 150,
          "id": "gpt-oss-120b",
          "name": "OpenAI: GPT OSS 120B",
          "created": "1754447935.370325",
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q4_0",
          "pricing": {
            "prompt": "0.00000007",
            "completion": "0.00000027",
          }
        },

        {
          "speed": 30,
          "id": "gpt-oss-safeguard-120b",
          "name": "OpenAI: gpt-oss-safeguard-120b",
          "created": "1754447935.370325",
          "context_length": 131072,
          "max_completion_tokens": 131072,
          "quantization": "Q8_0",
          "pricing": {
            "prompt": "0.00000007",
            "completion": "0.00000027",
          }
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
          }
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
          }
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
          }
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
          }
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
          }
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
          }
        },

      ]
    }
    return models_list

data_for_pricing = openrouter_models() # this is JUST pricing, speed gets changed separately
# I also do not remember why I did this, if it helps this is normally in a different file?

def current_month() -> int:
    return datetime.now().month

def get_month_name(month_num):
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    if 1 <= month_num <= 12:
        return months[month_num - 1]
    else:
        raise ValueError("Month number must be between 1 and 12")

@app.route("/home")
def home_page(): # home_page is the landing page, home() is playground, this is also weird but oh well
    return render_template("home.html", version=CURRENT_VERSION)

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
    userdata = { # normally pulled from db
        "usable_requests": 250, # this is the amount of requests the user has left for the day
        "requests_plan": 250, # this is the amount of requests the user is granted each day before using any
        "free_requests": 12345, # confusing but this is the total number of user all time requests
    }

    usable_requests = userdata.get("usable_requests")
    requests_plan = userdata.get("requests_plan")

    month = get_month_name(current_month()) # there is a better way to do this, but I don't feel like changing it

    free_requests = userdata["free_requests"]
    return render_template("dashboard.html", free_requests=userdata["free_requests"], month=month, usable_requests=usable_requests, requests_plan=requests_plan)

@app.route("/pricing")
def pricing():
    vision_models = ["llama-4-scout"] # sets which models get the "vision" flag/icon
    models = eval(str(data_for_pricing["data"])) # weird, I know

    model_index = -1
    for model in models:
        model_index += 1
        mid = model['id'] # just in case this wasn't obvious, "mid" is model id
        if mid in seen_speeds:
            models[model_index]["speed"] = round(statistics.mean(seen_speeds[mid]))


    print("updated model speeds")
    new_data = list(models)
    for model in new_data:
        # update prices
        prompt_price = str(round(float(model['pricing']['prompt'])*1000000, 2))
        if len(prompt_price) == 3:
            prompt_price = f"{prompt_price}0"

        completion_price = str(round(float(model['pricing']['completion'])*1000000, 2))
        if len(completion_price) == 3:
            completion_price = f"{completion_price}0"

        model["pricing"]["prompt"] = prompt_price
        model["pricing"]["completion"] = completion_price

        # update context_data
        model['context_length'] = comma_number(model['context_length'])
        model['max_completion_tokens'] = comma_number(model['max_completion_tokens'])

    if "login" in session:
        if "plan" not in session:
            requests_plan = 250
            if requests_plan == None:
                session["plan"] = "free"
            if requests_plan == 250:
                session["plan"] = "hobby"
            if requests_plan == 1000:
                session["plan"] = "pro"
        return render_template("pricing.html", loggedin=True, models=models, float=float, round=round, plan=session['plan'], vision_models=vision_models)
    else:
        return render_template("pricing.html", loggedin=False, models=models, float=float, round=round, plan="free", vision_models=vision_models)

@app.route("/", methods=["GET", "POST"])
def home():
    models = openrouter_models()["data"]
    if "login" in session:
        return render_template("playground.html", models=models, admin=False)
    else:
        return redirect("/home")

@app.route("/user_api_create-token")
def create_token_api(): # normally does more stuff but for testing it just needs to return a token
    if "login" in session:
        username = session["login"]
        userdata = {}
        newtoken = f"nahcrof_{''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase)for i in range(20))}"
        userdata["token"] = newtoken
        return jsonify({"message": "success", "token": newtoken})
    else: # state of the art security against anyone who'd try to make a token without being signed in
        return jsonify({"message": "no."}), 401

@app.route("/privacy")
def privacy_page():
    return render_template("privacy.html")

@app.route("/privacy/")
def privacy_page2():
    return render_template("privacy.html")

@app.route("/startups", methods=["GET", "POST"])
def startups():
    if request.method == "POST":
        data = request.form
        startup_name = data.get("startup_name")
        website = data.get("website")
        email = data.get("contact_email")
        description = data.get("description")
        use_case = data.get("use_case")
        print(f"\nSTARTUP REQUEST\ncompany name: {startup_name}\nwebsite: {website}\nemail: {email}\ndescription: ```{description}```\nuse for crofAI: ```{use_case}```")
        # normally the form is sent to me but I'll just print it for now
        return render_template("startups.html", success_message="Form sumbitted!")
    else:
        return render_template("startups.html")

@app.route("/settings")
def settings():
    if "login" in session:
        user = {"credits": 5, "user_type": "normal", "auto_top_up": "off", "email": "email@example.com"} # once again, usually pulled from a database
        top_up = True if user["auto_top_up"] == "on" else False
        user_credits = money_format(user["credits"]) if user["user_type"] != "free" else "∞"
        try:
            email = user["email"]
        except KeyError:
            email = None
        return render_template("settings.html", username=session['login'], user_credits=user_credits, email=email, top_up=top_up)
    else:
        return redirect("/login")

@app.route("/settings-api/add-credits") # This redirects to the actual link so that I can track most likely person associated with the purchase
def add_credits_page():
    if "login" in session:
        username = session["login"]
        return redirect("https://buy.stripe.com/8wM01ggBicK5doIbII")
    else:
        return redirect("/login")

@app.route("/settings-api/auto-top-up", methods=["POST"])
def auto_top_up_api():
    if "login" in session:
        username = session["login"]
        userdata = {} # you'll never guess what this usually is
        data = request.json
        userdata["auto_top_up"] = data['toggle']
        userdata = str(userdata) # user data must be stored as a string because me from 2 years ago was especially ignorant
        return jsonify("success")
    else:
        return abort(401)

@app.route("/settings-api/delete-user")
def delete_user(): # normally deletes the user first
    return redirect("/logout")

@app.route("/settings-api/update-password", methods=["POST"])
def update_user_password():
    # obviously would usually do more, but this is all the info that is needed in the request
    username = session["login"]
    data = request.json
    current_password_input = data.get("currentPassword", None)
    new_password_input = data.get("newPassword", None)
    return jsonify({"error": False})


@app.route("/settings-api/update-email/<email>")
def update_user_email(email):
    if "login" in session:
        # normally all you have to do is include <email>. The API figures the rest through session data
        return redirect("/settings")
    else:
        return "you're not logged in silly goose"


@app.route("/login", methods=["GET", "POST"])
@app.route("/signin", methods=["GET", "POST"])
def login():
    # this will usually check your password and username, then return errors where necessary. I set it up like this so it is a bit easier and has all the things that you need to supply the backend with.
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return redirect("/")
    else:
        return render_template("signin.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # same situation as /signin here
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return redirect("/")
    else:
        return render_template("signup.html")

@app.route("/ui/crofui.css")
def crofuicss():
    return redirect("https://ai.nahcrof.com/ui/crofui.css")


@app.route("/ui/crofui.js")
def crofuijs():
    return redirect("https://ai.nahcrof.com/ui/crofui.js")


app.run(host="0.0.0.0", port=8008) # haha, nice
