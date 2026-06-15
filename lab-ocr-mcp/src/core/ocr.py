"""核心 OCR 逻辑：图像 → 文本 + 还原后的 Markdown 表格。

设计边界（与 acits-xskills/AGENTS.md 第 4 节一致）：
- 本模块只做"图 → 文"，**绝不做任何标准化**（项目归一 / LOINC / 单位换算 / 异常判定
  全部在 skill 的阶段 1–5 完成）。
- 输出对 skill「阶段 1 解析拆分」友好：把检验报告的表格还原成 Markdown 表格，
  使阶段 1 能逐行抽取 raw_name / raw_value / raw_unit / raw_ref_range 四元组。

表格还原是纯几何启发式（按行列聚类文本框），不依赖深度表格模型，零额外权重，
对绝大多数规整的化验单表格足够；复杂版面退化为带换行的纯文本，仍可被阶段 1 处理。
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from statistics import median

import numpy as np
from PIL import Image

from .loader import LoadedPage


@dataclass
class Word:
    """一个识别出的文本框：文字 + 几何中心 + 行高，用于版面重建。"""

    text: str
    x_left: float
    x_right: float
    y_center: float
    height: float
    confidence: float


@dataclass
class PageResult:
    """单页 OCR 结果。"""

    page_index: int
    source_kind: str
    markdown: str  # 还原后的 Markdown（表格或带换行的纯文本）
    plain_text: str  # 纯文本（按阅读顺序，换行保留行结构）
    word_count: int
    mean_confidence: float
    warnings: list[str] = field(default_factory=list)


@dataclass
class OcrResult:
    """整份输入（可能多页）的聚合结果，供 server 层包装成 MCP 工具返回值。"""

    markdown: str
    plain_text: str
    pages: list[PageResult]
    engine: str
    warnings: list[str] = field(default_factory=list)

    @property
    def mean_confidence(self) -> float:
        confs = [p.mean_confidence for p in self.pages if p.word_count]
        return round(sum(confs) / len(confs), 4) if confs else 0.0


class _EngineHolder:
    """惰性、线程安全地持有一个 RapidOCR 实例（模型加载较重，全局复用一份）。"""

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    try:
                        from rapidocr_onnxruntime import RapidOCR
                    except ImportError as exc:  # pragma: no cover
                        raise RuntimeError(
                            "未安装 rapidocr-onnxruntime；请 pip install "
                            "rapidocr-onnxruntime。"
                        ) from exc
                    cls._instance = RapidOCR()
        return cls._instance


ENGINE_NAME = "rapidocr-onnxruntime"


def run_ocr(pages: list[LoadedPage]) -> OcrResult:
    """对一批已加载的页面执行 OCR，并合并为一份结果。"""
    engine = _EngineHolder.get()
    page_results: list[PageResult] = []

    for page in pages:
        words = _recognize(engine, page.image)
        if not words:
            page_results.append(
                PageResult(
                    page_index=page.page_index,
                    source_kind=page.source_kind,
                    markdown="",
                    plain_text="",
                    word_count=0,
                    mean_confidence=0.0,
                    warnings=["本页未识别到任何文字。"],
                )
            )
            continue

        rows = _cluster_rows(words)
        markdown = _rows_to_markdown(rows)
        plain_text = _rows_to_plain(rows)
        confs = [w.confidence for w in words]
        page_results.append(
            PageResult(
                page_index=page.page_index,
                source_kind=page.source_kind,
                markdown=markdown,
                plain_text=plain_text,
                word_count=len(words),
                mean_confidence=round(sum(confs) / len(confs), 4),
            )
        )

    return _merge_pages(page_results)


def _recognize(engine, image: Image.Image) -> list[Word]:
    """调 RapidOCR，把原始返回规整成 Word 列表。"""
    arr = np.asarray(image)
    result, _elapsed = engine(arr)
    if not result:
        return []

    words: list[Word] = []
    for box, text, score in result:
        text = (text or "").strip()
        if not text:
            continue
        # box 是四点坐标 [[x,y],...]，顺时针。取外接范围。
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        words.append(
            Word(
                text=text,
                x_left=min(xs),
                x_right=max(xs),
                y_center=sum(ys) / len(ys),
                height=max(ys) - min(ys),
                confidence=float(score),
            )
        )
    return words


def _cluster_rows(words: list[Word]) -> list[list[Word]]:
    """按 y 中心把文本框聚成行；行内按 x 从左到右排序。

    阈值取所有词高度中位数的一半：同一行的词 y 中心相近，不同行间距更大。
    """
    if not words:
        return []
    line_tol = max(median(w.height for w in words) * 0.6, 6.0)

    ordered = sorted(words, key=lambda w: w.y_center)
    rows: list[list[Word]] = []
    current: list[Word] = [ordered[0]]
    current_y = ordered[0].y_center

    for w in ordered[1:]:
        if abs(w.y_center - current_y) <= line_tol:
            current.append(w)
            # 用运行均值更新基准 y，缓解逐渐漂移
            current_y = sum(x.y_center for x in current) / len(current)
        else:
            rows.append(sorted(current, key=lambda x: x.x_left))
            current = [w]
            current_y = w.y_center
    rows.append(sorted(current, key=lambda x: x.x_left))
    return rows


def _looks_tabular(rows: list[list[Word]]) -> bool:
    """多数行有 ≥2 个单元，才当作表格还原；否则退化为纯文本。"""
    if len(rows) < 2:
        return False
    multi = sum(1 for r in rows if len(r) >= 2)
    return multi >= max(2, len(rows) // 2)


def _rows_to_markdown(rows: list[list[Word]]) -> str:
    """把行聚类渲染成 Markdown。规整表格 → Markdown 表格；否则 → 段落文本。"""
    if not rows:
        return ""
    if not _looks_tabular(rows):
        return _rows_to_plain(rows)

    columns = _infer_columns(rows)
    table_rows: list[list[str]] = []
    for row in rows:
        cells = ["" for _ in columns]
        for w in row:
            idx = _assign_column(w, columns)
            cells[idx] = (cells[idx] + " " + w.text).strip() if cells[idx] else w.text
        table_rows.append(cells)

    header = table_rows[0]
    body = table_rows[1:]
    lines = [
        "| " + " | ".join(_escape(c) for c in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for r in body:
        lines.append("| " + " | ".join(_escape(c) for c in r) + " |")
    return "\n".join(lines)


def _infer_columns(rows: list[list[Word]]) -> list[tuple[float, float]]:
    """从所有词的 x 区间估计列边界：把 x_left 一维聚类成若干列。"""
    lefts = sorted(w.x_left for row in rows for w in row)
    if not lefts:
        return [(0.0, float("inf"))]
    widths = [w.x_right - w.x_left for row in rows for w in row]
    gap = max(median(widths) * 0.8, 20.0) if widths else 40.0

    centers: list[float] = [lefts[0]]
    for x in lefts[1:]:
        if x - centers[-1] > gap:
            centers.append(x)
    # 把列中心转成 [start, next_start) 边界
    bounds: list[tuple[float, float]] = []
    for i, c in enumerate(centers):
        hi = centers[i + 1] if i + 1 < len(centers) else float("inf")
        bounds.append((c, hi))
    return bounds


def _assign_column(w: Word, columns: list[tuple[float, float]]) -> int:
    for i, (lo, hi) in enumerate(columns):
        if lo <= w.x_left < hi:
            return i
    return len(columns) - 1


def _rows_to_plain(rows: list[list[Word]]) -> str:
    return "\n".join(" ".join(w.text for w in row) for row in rows)


def _escape(cell: str) -> str:
    return cell.replace("|", "\\|").replace("\n", " ").strip()


def _merge_pages(page_results: list[PageResult]) -> OcrResult:
    md_parts: list[str] = []
    txt_parts: list[str] = []
    multi = len(page_results) > 1
    for p in page_results:
        if multi:
            md_parts.append(f"### 第 {p.page_index + 1} 页\n\n{p.markdown}")
            txt_parts.append(f"--- 第 {p.page_index + 1} 页 ---\n{p.plain_text}")
        else:
            md_parts.append(p.markdown)
            txt_parts.append(p.plain_text)

    warnings: list[str] = []
    for p in page_results:
        warnings.extend(p.warnings)

    return OcrResult(
        markdown="\n\n".join(md_parts).strip(),
        plain_text="\n\n".join(txt_parts).strip(),
        pages=page_results,
        engine=ENGINE_NAME,
        warnings=warnings,
    )
