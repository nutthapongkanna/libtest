"""
Unit tests for tlnk package.
"""
import unittest
from tlnk.utils.text import clean_whitespace, to_snake_case, truncate, is_empty
from tlnk.utils.date import parse_date, to_iso, is_valid_date
from tlnk.utils.dtype import to_int, to_float, to_bool, to_str
from tlnk.utils.retry import retry
from tlnk.utils.headers import get_default_headers, get_random_user_agent
from tlnk.scraper.parser import HtmlParser, JsonParser, ParserError
from tlnk.scraper.http import HttpClient
from tlnk.transform.cleaner import DataCleaner, DataCleanerError
from tlnk.transform.converter import DataConverter, DataConverterError


# ── Utils ────────────────────────────────────────────────────────

class TestTextUtils(unittest.TestCase):
    def test_clean_whitespace(self):
        self.assertEqual(clean_whitespace("  hello   world  "), "hello world")

    def test_to_snake_case(self):
        self.assertEqual(to_snake_case("Hello World"), "hello_world")

    def test_truncate(self):
        self.assertEqual(truncate("Hello World", 8), "Hello...")
        self.assertEqual(truncate("Hi", 10), "Hi")

    def test_is_empty(self):
        self.assertTrue(is_empty(None))
        self.assertTrue(is_empty("   "))
        self.assertFalse(is_empty("hello"))


class TestDateUtils(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(parse_date("2024-01-15").year, 2024)

    def test_to_iso(self):
        self.assertEqual(to_iso("15/01/2024"), "2024-01-15")
        self.assertIsNone(to_iso("invalid"))

    def test_is_valid_date(self):
        self.assertTrue(is_valid_date("2024-01-15"))
        self.assertFalse(is_valid_date("hello"))


class TestDtypeUtils(unittest.TestCase):
    def test_to_int(self):
        self.assertEqual(to_int("1,000"), 1000)
        self.assertEqual(to_int("abc", default=0), 0)

    def test_to_float(self):
        self.assertEqual(to_float("1,234.56"), 1234.56)

    def test_to_bool(self):
        self.assertTrue(to_bool("yes"))
        self.assertFalse(to_bool("no"))
        self.assertIsNone(to_bool("maybe"))

    def test_to_str(self):
        self.assertEqual(to_str(None), "")
        self.assertEqual(to_str(42), "42")


class TestHeaders(unittest.TestCase):
    def test_get_random_user_agent(self):
        self.assertIn("Mozilla", get_random_user_agent())

    def test_get_default_headers(self):
        headers = get_default_headers()
        self.assertIn("User-Agent", headers)

    def test_headers_with_referer(self):
        headers = get_default_headers(referer="https://example.com")
        self.assertEqual(headers["Referer"], "https://example.com")


class TestRetry(unittest.TestCase):
    def test_success(self):
        @retry(max_attempts=3)
        def ok(): return "ok"
        self.assertEqual(ok(), "ok")

    def test_retry_then_succeed(self):
        count = [0]

        @retry(max_attempts=3, delay=0)
        def fail_twice():
            count[0] += 1
            if count[0] < 3:
                raise ValueError("fail")
            return "ok"

        self.assertEqual(fail_twice(), "ok")
        self.assertEqual(count[0], 3)

    def test_raise_after_max(self):
        @retry(max_attempts=2, delay=0)
        def always_fail(): raise ValueError("fail")
        with self.assertRaises(ValueError):
            always_fail()


# ── Scraper ──────────────────────────────────────────────────────

class TestHttpClient(unittest.TestCase):
    def test_repr(self):
        client = HttpClient(base_url="https://example.com")
        self.assertIn("HttpClient", repr(client))

    def test_build_url_with_base(self):
        client = HttpClient(base_url="https://api.example.com")
        self.assertEqual(client._build_url("/users"), "https://api.example.com/users")

    def test_build_url_absolute(self):
        client = HttpClient()
        self.assertEqual(client._build_url("https://other.com"), "https://other.com")

    def test_context_manager(self):
        with HttpClient() as client:
            self.assertIsInstance(client, HttpClient)


class TestHtmlParser(unittest.TestCase):
    def setUp(self):
        self.html = """
        <html><head><title>Test</title></head>
        <body>
          <h1 class="title">Hello</h1>
          <a href="https://example.com">Click</a>
          <ul><li>A</li><li>B</li></ul>
          <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
          </table>
        </body></html>"""
        try:
            self.parser = HtmlParser(self.html)
            self.bs4 = True
        except ImportError:
            self.bs4 = False

    def test_empty_raises(self):
        with self.assertRaises(ParserError):
            HtmlParser("")

    def test_find_text(self):
        if not self.bs4: self.skipTest("bs4 not installed")
        self.assertEqual(self.parser.find_text("h1.title"), "Hello")

    def test_find_all_text(self):
        if not self.bs4: self.skipTest("bs4 not installed")
        self.assertEqual(self.parser.find_all_text("li"), ["A", "B"])

    def test_find_attr(self):
        if not self.bs4: self.skipTest("bs4 not installed")
        self.assertEqual(self.parser.find_attr("a", "href"), "https://example.com")

    def test_find_table(self):
        if not self.bs4: self.skipTest("bs4 not installed")
        rows = self.parser.find_table()
        self.assertEqual(rows[0]["Name"], "Alice")

    def test_repr(self):
        if not self.bs4: self.skipTest("bs4 not installed")
        self.assertIn("HtmlParser", repr(self.parser))


class TestJsonParser(unittest.TestCase):
    def setUp(self):
        self.parser = JsonParser({"user": {"name": "Alice", "city": "Bangkok"}, "items": [1, 2]})

    def test_none_raises(self):
        with self.assertRaises(ParserError):
            JsonParser(None)

    def test_get_nested(self):
        self.assertEqual(self.parser.get("user", "name"), "Alice")

    def test_get_default(self):
        self.assertEqual(self.parser.get("missing", default="N/A"), "N/A")

    def test_get_list(self):
        self.assertEqual(self.parser.get("items", 0), 1)

    def test_flatten(self):
        flat = self.parser.flatten()
        self.assertEqual(flat["user.name"], "Alice")

    def test_keys(self):
        self.assertIn("user", self.parser.keys())

    def test_repr(self):
        self.assertIn("JsonParser", repr(self.parser))


# ── Transform ────────────────────────────────────────────────────

class TestDataCleaner(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"name": "Alice",   "age": "30", "city": "Bangkok"},
            {"name": "",        "age": "25", "city": "Chiang Mai"},
            {"name": "Alice",   "age": "30", "city": "Bangkok"},
            {"name": "  Bob  ", "age": "28", "city": "  Phuket  "},
        ]

    def test_invalid_raises(self):
        with self.assertRaises(DataCleanerError):
            DataCleaner("not a list")

    def test_count(self):
        self.assertEqual(DataCleaner(self.data).count, 4)

    def test_drop_nulls(self):
        result = DataCleaner(self.data).drop_nulls(["name"]).to_list()
        self.assertEqual(len(result), 3)

    def test_drop_duplicates(self):
        result = DataCleaner(self.data).drop_duplicates(["name", "age"]).to_list()
        self.assertEqual([r["name"] for r in result].count("Alice"), 1)

    def test_strip_whitespace(self):
        result = DataCleaner(self.data).strip_whitespace().to_list()
        bob = next(r for r in result if "Bob" in r["name"])
        self.assertEqual(bob["name"], "Bob")

    def test_rename_columns(self):
        result = DataCleaner(self.data).rename_columns({"name": "full_name"}).to_list()
        self.assertIn("full_name", result[0])

    def test_fill_null(self):
        result = DataCleaner(self.data).fill_null("N/A", ["name"]).to_list()
        self.assertTrue(any(r["name"] == "N/A" for r in result))

    def test_no_mutate(self):
        original = [{"name": "Alice"}]
        DataCleaner(original).drop_nulls().to_list()
        self.assertEqual(original[0]["name"], "Alice")

    def test_summary(self):
        s = DataCleaner(self.data).drop_nulls(["name"]).summary()
        self.assertEqual(s["original_count"], 4)
        self.assertEqual(s["dropped"], 1)

    def test_repr(self):
        self.assertIn("DataCleaner", repr(DataCleaner(self.data)))


class TestDataConverter(unittest.TestCase):
    def setUp(self):
        self.data = [
            {"age": "30", "price": "1,500.00", "active": "yes", "date": "15/01/2024"},
            {"age": "25", "price": "800.00",   "active": "no",  "date": "2024-02-20"},
        ]

    def test_invalid_raises(self):
        with self.assertRaises(DataConverterError):
            DataConverter("not a list")

    def test_to_int(self):
        result = DataConverter(self.data).to_int(["age"]).to_list()
        self.assertIsInstance(result[0]["age"], int)

    def test_to_float(self):
        result = DataConverter(self.data).to_float(["price"]).to_list()
        self.assertIsInstance(result[0]["price"], float)

    def test_to_bool(self):
        result = DataConverter(self.data).to_bool(["active"]).to_list()
        self.assertTrue(result[0]["active"])
        self.assertFalse(result[1]["active"])

    def test_to_date_iso(self):
        result = DataConverter(self.data).to_date_iso(["date"]).to_list()
        self.assertEqual(result[0]["date"], "2024-01-15")

    def test_cast(self):
        result = DataConverter(self.data).cast({
            "age": "int", "price": "float", "active": "bool", "date": "date"
        }).to_list()
        self.assertIsInstance(result[0]["age"], int)
        self.assertIsInstance(result[0]["price"], float)
        self.assertIsInstance(result[0]["active"], bool)

    def test_cast_invalid_raises(self):
        with self.assertRaises(DataConverterError):
            DataConverter(self.data).cast({"age": "unknown"}).to_list()

    def test_no_mutate(self):
        original = [{"age": "30"}]
        DataConverter(original).to_int(["age"]).to_list()
        self.assertEqual(original[0]["age"], "30")

    def test_repr(self):
        self.assertIn("DataConverter", repr(DataConverter(self.data)))


if __name__ == "__main__":
    unittest.main()
