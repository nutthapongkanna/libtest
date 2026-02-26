# TLNK Library

Python library สำหรับ Web Scraping และ Data Transformation

## คุณสมบัติ

- รองรับ Python 3.8 ขึ้นไป
- **Web Scraping** — HTTP client และ HTML/JSON parser
- **Data Transformation** — ทำความสะอาดและแปลงข้อมูล
- **Utilities** — Retry mechanism, logging, date/text helpers

## โครงสร้างโปรเจกต์

```
tlnk/
├── scraper/          # HTTP client และ parsers
├── transform/        # Data cleaner และ converter
└── utils/            # Utilities (logger, retry, headers, etc.)
```

---

## การติดตั้ง (Development)

```bash
git clone https://github.com/your-username/tlnk.git
cd tlnk
pip3 install -e .
```


---

## การติดตั้งจาก Private GitHub Repository

> **หมายเหตุ:** `tokengithub` คือ Personal Access Token ที่สร้างขึ้นเพื่อใช้ติดตั้ง library จาก private repository

### ติดตั้งใน Jupyter Notebook

```bash
# ไม่ระบุเวอร์ชัน (ใช้ล่าสุด)
!pip3 install git+https://tokengithub@github.com/travellink-data-platform/tlnk-de-lib.git

# ระบุเวอร์ชัน
!pip3 install git+https://tokengithub@github.com/travellink-data-platform/tlnk-de-lib.git@1.0.1

# อัปเดตเป็นเวอร์ชันล่าสุด (force upgrade)
!pip3 install -U git+https://tokengithub@github.com/travellink-data-platform/tlnk-de-lib.git
```

### ติดตั้งผ่าน Terminal

```bash
# ไม่ระบุเวอร์ชัน (ใช้ล่าสุด)
pip3 install git+https://tokengithub@github.com/travellink-data-platform/tlnk-de-lib.git

# ระบุเวอร์ชัน
pip3 install git+https://tokengithub@github.com/travellink-data-platform/tlnk-de-lib.git@1.0.1

# อัปเดตเป็นเวอร์ชันล่าสุด (force upgrade)
pip3 install -U git+https://tokengithub@github.com/travellink-data-platform/tlnk-de-lib.git
```

---

## การใช้งาน

### HTML Parser

```python
from tlnk import HtmlParser

html = """
<table>
    <tr><th>ชื่อ</th><th>ราคา</th></tr>
    <tr><td>สินค้า A</td><td>100</td></tr>
</table>
"""

parser = HtmlParser(html)
products = parser.find_table("table")
# [{'ชื่อ': 'สินค้า A', 'ราคา': '100'}]
```

### JSON Parser

```python
from tlnk import JsonParser

data = {"user": {"name": "สมชาย", "age": 25}}
parser = JsonParser(data)

name = parser.get("user", "name")  # "สมชาย"
flat = parser.flatten()            # {'user.name': 'สมชาย', 'user.age': 25}
```

### Data Cleaner & Converter

```python
from tlnk import DataCleaner, DataConverter

# Cleaner
cleaner = DataCleaner()
text = cleaner.strip_whitespace("  สวัสดี  ")  # "สวัสดี"

# Converter
converter = DataConverter()
num = converter.to_int("123")       # 123
price = converter.to_float("99.99") # 99.99
```

---

## การทดสอบ

```bash
# ใช้ unittest
python -m unittest discover -s tests -v

# หรือใช้ pytest
pytest tests/
```

---

## การ Push Code พร้อม Tag

### Checklist ก่อน Release

- [ ] อัปเดต version ใน `pyproject.toml`
- [ ] รัน tests ให้ผ่านทั้งหมด
- [ ] Commit และ push code
- [ ] สร้างและ push tag
- [ ] ตรวจสอบ GitHub Actions ว่ารันสำเร็จ

### ขั้นตอน

**1. อัปเดต version ใน `pyproject.toml`**

```toml
[project]
name = "tlnk"
version = "1.0.1"  # เปลี่ยนเป็น version ใหม่
```

**2. Commit และสร้าง Tag**

```bash
git add .
git commit -m "Bump version to 1.0.1"
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin main --tags

```
