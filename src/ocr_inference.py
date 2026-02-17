from paddleocr import PaddleOCR

class OCRModel:
    def __init__(self):
        self.model = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False, 
                text_det_thresh=0.3,
                lang="ch")

    def _ranked_items_from_result(self, result_item):
        texts = result_item.get("rec_texts", []) or []
        scores = result_item.get("rec_scores", []) or []

        ranked = []
        for index, text in enumerate(texts):
            if text is None:
                continue
            score = float(scores[index]) if index < len(scores) else 0.0
            ranked.append({"text": str(text), "score": score})

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked
        
    def predict(self, filepath):
        result_list = self.model.predict(
                input = filepath
                )
        detections = []

        for result_item in result_list:
            ranked = self._ranked_items_from_result(result_item)
            if ranked:
                detections.append(ranked[0]["text"])

        return detections

    def predict_ranked(self, filepath, limit=5):
        result_list = self.model.predict(input=filepath)
        candidates = []

        for result_item in result_list:
            candidates.extend(self._ranked_items_from_result(result_item))

        unique_candidates = []
        seen = set()
        for item in candidates:
            text = item["text"]
            if text in seen:
                continue
            seen.add(text)
            unique_candidates.append(item)

        unique_candidates.sort(key=lambda item: item["score"], reverse=True)
        return unique_candidates[:limit]
