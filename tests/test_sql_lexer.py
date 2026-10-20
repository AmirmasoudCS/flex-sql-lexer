
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEXER_SOURCE = PROJECT_ROOT / "sql.l"
REPORT_PATH = PROJECT_ROOT / "test_report.json"


def find_executable(name, fallback_paths):
    executable = shutil.which(name)

    if executable:
        return executable

    for path in fallback_paths:
        if Path(path).is_file():
            return path

    raise FileNotFoundError(
        f"Could not find {name}. Add it to PATH or update the fallback paths."
    )


FLEX = find_executable(
    "flex",
    [r"C:\msys64\usr\bin\flex.exe"],
)

GCC = find_executable(
    "gcc",
    [r"C:\msys64\usr\bin\gcc.exe"],
)


class SQLLexerTests(unittest.TestCase):
    results = []
    temp_dir = None
    executable = None

    @classmethod
    def setUpClass(cls):
        if not LEXER_SOURCE.exists():
            raise FileNotFoundError(
                f"Could not find sql.l at {LEXER_SOURCE}"
            )

        cls.temp_dir = tempfile.TemporaryDirectory()
        build_dir = Path(cls.temp_dir.name)

        generated_c = build_dir / "lex.yy.c"
        cls.executable = build_dir / "sql.exe"

        flex_result = subprocess.run(
            [FLEX, "-o", str(generated_c), str(LEXER_SOURCE)],
            capture_output=True,
            text=True,
        )

        if flex_result.returncode != 0:
            raise RuntimeError(
                "Flex compilation failed:\n"
                + flex_result.stdout
                + flex_result.stderr
            )

        gcc_result = subprocess.run(
            [GCC, str(generated_c), "-o", str(cls.executable)],
            capture_output=True,
            text=True,
        )

        if gcc_result.returncode != 0:
            raise RuntimeError(
                "GCC compilation failed:\n"
                + gcc_result.stdout
                + gcc_result.stderr
            )

    @classmethod
    def tearDownClass(cls):
        report = {
            "project": "SQL Lexical Analyzer",
            "test_count": len(cls.results),
            "passed": sum(
                result["status"] == "PASS"
                for result in cls.results
            ),
            "failed": sum(
                result["status"] == "FAIL"
                for result in cls.results
            ),
            "tests": cls.results,
        }

        REPORT_PATH.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        if cls.temp_dir:
            cls.temp_dir.cleanup()

    def run_lexer_test(self, sql_input, expected_fragments):
        process = subprocess.run(
            [str(self.executable)],
            input=sql_input,
            capture_output=True,
            text=True,
        )

        output = process.stdout

        missing = [
            fragment
            for fragment in expected_fragments
            if fragment not in output
        ]

        errors = []

        if process.returncode != 0:
            errors.append(
                f"Exit code: {process.returncode}"
            )

        if process.stderr.strip():
            errors.append(
                f"Unexpected stderr: {process.stderr.strip()}"
            )

        if missing:
            errors.append(
                f"Missing expected output: {missing}"
            )

        status = "PASS" if not errors else "FAIL"

        self.__class__.results.append({
            "test": self.id().split(".")[-1],
            "status": status,
            "input": sql_input,
            "expected_fragments": expected_fragments,
            "stdout": output,
            "stderr": process.stderr,
            "errors": errors,
        })

        self.assertEqual(process.returncode, 0, "\n".join(errors))
        self.assertEqual(process.stderr.strip(), "", "\n".join(errors))
        self.assertFalse(missing, "\n".join(errors))

    def test_assignment_example(self):
        self.run_lexer_test(
            "SELECT name, age FROM Students WHERE age >= 18;",
            [
                "KEYWORD: SELECT",
                "IDENTIFIER: name",
                "PUNCT: ,",
                "IDENTIFIER: age",
                "KEYWORD: FROM",
                "IDENTIFIER: Students",
                "KEYWORD: WHERE",
                "COMPARISON OPERATOR: >=",
                "NUMBER: 18",
                "PUNCT: ;",
            ],
        )

    def test_keywords_and_identifiers(self):
        self.run_lexer_test(
            "SELECT first_name FROM Students;",
            [
                "KEYWORD: SELECT",
                "IDENTIFIER: first_name",
                "KEYWORD: FROM",
                "IDENTIFIER: Students",
            ],
        )

    def test_integer_and_float(self):
        self.run_lexer_test(
            "SELECT 123, 45.67;",
            [
                "NUMBER: 123",
                "NUMBER: 45.67",
                "PUNCT: ,",
                "PUNCT: ;",
            ],
        )

    def test_quoted_strings(self):
        self.run_lexer_test(
            """SELECT 'Ali', "test";""",
            [
                "STRING LITERAL: 'Ali'",
                'STRING LITERAL: "test"',
                "PUNCT: ,",
                "PUNCT: ;",
            ],
        )

    def test_comparison_operators(self):
        self.run_lexer_test(
            "a = b AND c <> d AND e != f AND g < h AND i > j AND k <= l AND m >= n",
            [
                "COMPARISON OPERATOR: =",
                "COMPARISON OPERATOR: <>",
                "COMPARISON OPERATOR: !=",
                "COMPARISON OPERATOR: <",
                "COMPARISON OPERATOR: >",
                "COMPARISON OPERATOR: <=",
                "COMPARISON OPERATOR: >=",
            ],
        )

    def test_arithmetic_operators(self):
        self.run_lexer_test(
            "a + b - c * d / e % f",
            [
                "ARITHMETIC OPERATOR: +",
                "ARITHMETIC OPERATOR: -",
                "ARITHMETIC OPERATOR: *",
                "ARITHMETIC OPERATOR: /",
                "ARITHMETIC OPERATOR: %",
            ],
        )

    def test_punctuation(self):
        self.run_lexer_test(
            "SELECT t.name, (t.age);",
            [
                "PUNCT: .",
                "PUNCT: ,",
                "PUNCT: (",
                "PUNCT: )",
                "PUNCT: ;",
            ],
        )

    def test_single_line_comment(self):
        self.run_lexer_test(
            "SELECT name -- comment\nFROM Students;",
            [
                "KEYWORD: SELECT",
                "SINGLE LINE COMMENT",
                "KEYWORD: FROM",
                "IDENTIFIER: Students",
            ],
        )

    def test_multiline_comment(self):
        self.run_lexer_test(
            "SELECT name; /* first line\nsecond line */ SELECT age;",
            [
                "KEYWORD: SELECT",
                "MULTI LINE COMMENT",
                "IDENTIFIER: age",
            ],
        )

    def test_whitespace_is_ignored(self):
        self.run_lexer_test(
            "SELECT\tname\r\nFROM   Students ;",
            [
                "KEYWORD: SELECT",
                "IDENTIFIER: name",
                "KEYWORD: FROM",
                "IDENTIFIER: Students",
                "PUNCT: ;",
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
