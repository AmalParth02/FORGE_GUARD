import os
import cv2
import numpy as np
from preprocessing.services import ImagePreprocessor

class OCRService:
    """
    Optimized PaddleOCR Engine wrapper service for high-performance text recognition.
    Features:
    - Persistent singleton OCR instance (loaded once, reused across all requests)
    - Optimal detection limits and batched recognition for fast CPU throughput
    - Automatic CPU/GPU hardware detection
    - Smart in-memory image scaling to prevent CPU latency explosion on high-res camera photos
    - Fully supports PaddleOCR 3.x (PaddleX pipeline) and legacy formats
    """
    _ocr_instance = None
    _device_info = None

    @classmethod
    def get_device_info(cls):
        """
        Detects and caches runtime execution hardware (GPU CUDA vs multi-threaded CPU).
        """
        if cls._device_info is None:
            try:
                import paddle
                has_cuda = paddle.device.is_compiled_with_cuda()
                device_str = paddle.device.get_device()
                if has_cuda and 'gpu' in device_str:
                    cls._device_info = f"GPU (CUDA: {device_str})"
                else:
                    cpu_count = os.cpu_count() or 4
                    cls._device_info = f"CPU (Multi-threaded, {cpu_count} logical cores)"
            except Exception:
                cpu_count = os.cpu_count() or 4
                cls._device_info = f"CPU (Multi-threaded, {cpu_count} logical cores)"
        return cls._device_info

    @classmethod
    def get_ocr_engine(cls):
        """
        Retrieves or initializes the shared PaddleOCR singleton instance.
        Configured with tuned detection limits, batched recognition, and disabled heavy distortion filters.
        """
        if cls._ocr_instance is None:
            from paddleocr import PaddleOCR
            cls._ocr_instance = PaddleOCR(
                ocr_version='PP-OCRv3',
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                text_det_limit_side_len=736,
                text_det_limit_type='max',
                text_det_thresh=0.3,
                text_det_box_thresh=0.6,
                text_det_unclip_ratio=1.6,
                text_recognition_batch_size=16,
                enable_mkldnn=False,
                lang='en'
            )
        return cls._ocr_instance

    @classmethod
    def warmup(cls):
        """
        Pre-warms the OCR engine with a small synthetic image during server startup
        to eliminate first-request cold-start latency.
        """
        try:
            engine = cls.get_ocr_engine()
            dummy = np.ones((100, 100, 3), dtype=np.uint8) * 255
            engine.ocr(dummy)
            print(f"[OCR Engine Ready] Initialized and warmed on {cls.get_device_info()}", flush=True)
        except Exception as e:
            print(f"[OCR Warmup Notice] {e}", flush=True)

    @classmethod
    def extract_text(cls, image_input, apply_preprocessing=True):
        """
        Performs in-memory preprocessing (optional) and fast PaddleOCR recognition.
        Accepts:
        - numpy.ndarray (BGR image)
        - bytes (image file binary)
        - str (file path)

        Returns standardized full text, line items, and confidence scores.
        """
        # 1. Load image into memory as numpy BGR array
        if isinstance(image_input, np.ndarray):
            image = image_input
        elif isinstance(image_input, bytes):
            image = cv2.imdecode(np.frombuffer(image_input, np.uint8), cv2.IMREAD_COLOR)
        elif isinstance(image_input, str):
            if not os.path.exists(image_input):
                raise ValueError(f"Image not found at path: {image_input}")
            image = cv2.imread(image_input)
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        if image is None:
            raise ValueError("Could not decode image for OCR processing.")

        # 2. Optional In-Memory Preprocessing
        if apply_preprocessing:
            image = ImagePreprocessor.preprocess(image)

        # 3. Smart Image Normalization (Optimal resolution for PP-OCRv3 on CPU)
        max_dim = 736
        h, w = image.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            ocr_image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            ocr_image = image

        lines = []
        full_text_parts = []

        try:
            ocr_engine = cls.get_ocr_engine()
            result = ocr_engine.ocr(ocr_image)

            if result and len(result) > 0:
                first_item = result[0]

                # Case A: PaddleOCR 3.x / PaddleX OCRResult or Dictionary structure
                if isinstance(first_item, dict) or hasattr(first_item, 'keys'):
                    rec_texts = first_item.get('rec_texts', []) if hasattr(first_item, 'get') else first_item['rec_texts']
                    rec_scores = first_item.get('rec_scores', []) if hasattr(first_item, 'get') else first_item['rec_scores']
                    rec_polys = first_item.get('rec_polys', None) if hasattr(first_item, 'get') else None
                    if rec_polys is None and hasattr(first_item, 'get'):
                        rec_polys = first_item.get('dt_polys', [])

                    for i, text in enumerate(rec_texts):
                        clean_text = str(text).strip()
                        if not clean_text:
                            continue

                        score = float(rec_scores[i]) if i < len(rec_scores) else 1.0
                        if score < 0.2:  # Filter low-confidence noise
                            continue

                        bbox = []
                        if rec_polys is not None and i < len(rec_polys):
                            poly = rec_polys[i]
                            if hasattr(poly, 'tolist'):
                                bbox = poly.tolist()
                            elif isinstance(poly, (list, tuple)):
                                bbox = list(poly)

                        lines.append({
                            "text": clean_text,
                            "confidence": round(score, 4),
                            "bbox": bbox
                        })
                        full_text_parts.append(clean_text)

                # Case B: Legacy PaddleOCR 2.x structure [[[bbox, (text, score)], ...]]
                elif isinstance(first_item, list):
                    for line in first_item:
                        if isinstance(line, list) and len(line) >= 2:
                            bbox_raw, (text, confidence) = line[0], line[1]
                            clean_text = str(text).strip()
                            if clean_text:
                                bbox = bbox_raw.tolist() if hasattr(bbox_raw, 'tolist') else bbox_raw
                                lines.append({
                                    "text": clean_text,
                                    "confidence": round(float(confidence), 4),
                                    "bbox": bbox
                                })
                                full_text_parts.append(clean_text)

            full_text = "\n".join(full_text_parts)

        except Exception as ocr_err:
            full_text = ""
            lines = []
            print(f"PaddleOCR Engine Error: {ocr_err}")

        return {
            "text": full_text,
            "lines": lines,
            "line_count": len(lines),
            "preprocessed": True
        }
