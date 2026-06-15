"""冒烟测试：不依赖外部图片，合成一张化验单表格图，跑通 loader → ocr 全链路。

运行：在已装好依赖的环境（建议 Python 3.11 + requirements.txt）下
    pytest -q tests/test_smoke.py
或直接：
    python tests/test_smoke.py
"""

from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# 让测试能 import src.*
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core import load_pages, run_ocr  # noqa: E402

# 一张极简的"血常规"表格，列：项目 / 结果 / 单位 / 参考区间
ROWS = [
    ["项目", "结果", "单位", "参考区间"],
    ["白细胞", "6.2", "10^9/L", "3.5-9.5"],
    ["血红蛋白", "145", "g/L", "130-175"],
    ["血小板", "210", "10^9/L", "125-350"],
]
COL_X = [40, 280, 460, 640]


# 跨平台中文字体候选；找不到任何一个就没法画中文，测试应跳过而非失败
_CJK_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux fonts-noto-cjk
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",  # macOS
    "C:\\Windows\\Fonts\\msyh.ttc",  # Windows
]


def _load_cjk_font(size: int):
    for path in _CJK_FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return None


def _make_lab_image() -> bytes:
    img = Image.new("RGB", (900, 260), "white")
    draw = ImageDraw.Draw(img)
    font = _load_cjk_font(28)
    if font is None:
        import pytest

        pytest.skip("无可用中文字体，无法合成中文化验单图（非代码问题）。")
    for r, row in enumerate(ROWS):
        y = 30 + r * 55
        for c, cell in enumerate(row):
            draw.text((COL_X[c], y), cell, fill="black", font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_base64_roundtrip_to_markdown():
    raw = _make_lab_image()
    b64 = base64.b64encode(raw).decode()

    pages = load_pages(image_base64=b64)
    assert len(pages) == 1

    result = run_ocr(pages)

    # 至少识别到部分关键字（OCR 不保证 100%，放宽断言）
    text = result.plain_text
    assert any(kw in text for kw in ("白细胞", "血红蛋白", "血小板")), text
    # 表格还原后应包含 Markdown 表格分隔行
    assert "---" in result.markdown, result.markdown
    assert result.mean_confidence > 0.0
    print("\n=== Markdown ===\n" + result.markdown)
    print("\n=== plain_text ===\n" + result.plain_text)
    print(f"\nmean_confidence={result.mean_confidence} warnings={result.warnings}")


def test_rejects_no_input():
    import pytest

    from src.core import ImageLoadError

    with pytest.raises(ImageLoadError):
        load_pages()


if __name__ == "__main__":
    test_base64_roundtrip_to_markdown()
    print("\nOK")
