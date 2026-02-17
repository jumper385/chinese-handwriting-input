import time
import argparse
from src.ocr_inference import OCRModel

parser = argparse.ArgumentParser(description="A simple script using argparse.")
parser.add_argument("filepath", help="filepath of file")

args = parser.parse_args()

RUN_BYPASS=False

def now():
    return time.perf_counter()

def ms(t):
    return 1000.0 * t

t0 = now()
ocr = OCRModel()
t1 = now()
print(f"Init (load model): {ms(t1 - t0):.1f} ms")

REPEAT_COUNT = 30
if not RUN_BYPASS:
    for idx in range(REPEAT_COUNT):

        output = []

        t0 = now()
        result = ocr.predict(args.filepath)
        t1 = now()

        delta = t1 - t0
        print(f"Init (Predict Round {idx + 1}): {ms(delta):.1f} ms; Result = {result}")

result = ocr.predict(args.filepath)
print(result)
