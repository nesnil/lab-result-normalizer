"""核心 OCR 逻辑（与传输层无关，可单测、可换壳）。"""

from .loader import ImageLoadError, LoadedPage, load_pages
from .ocr import ENGINE_NAME, OcrResult, PageResult, run_ocr

__all__ = [
    "ImageLoadError",
    "LoadedPage",
    "load_pages",
    "ENGINE_NAME",
    "OcrResult",
    "PageResult",
    "run_ocr",
]
