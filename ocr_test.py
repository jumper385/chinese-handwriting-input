import time
import argparse
from paddleocr import PaddleOCR

parser = argparse.ArgumentParser(description="A simple script using argparse.")
parser.add_argument("filepath", help="filepath of file")

args = parser.parse_args()

RUN_BYPASS=False

def now():
    return time.perf_counter()

def ms(t):
    return 1000.0 * t

t0 = now()
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False, 
    text_det_thresh=0.5,
    lang="ch")
t1 = now()
print(f"Init (load model): {ms(t1 - t0):.1f} ms")

REPEAT_COUNT = 30
if not RUN_BYPASS:
    for idx in range(REPEAT_COUNT):

        output = []

        t0 = now()
        result = ocr.predict(
            input=args.filepath)
        for res in result:
            output = res.get("rec_texts", [])
        t1 = now()

        delta = t1 - t0
        print(f"Init (Predict Round {idx + 1}): {ms(delta):.1f} ms; Result = {output}")

result = ocr.predict(
        input = args.filepath)

for res in result:
    output = res.get("rec_texts", [])
    print(output)
