"""publication_check.py 의 규칙이 잡을 것을 잡고 잡지 말 것을 놓아 주는지 댄다.

사용: python3 -m unittest discover -s scripts -p 'test_*.py'
시험용 비밀 값은 진짜가 아니다 — 모양만 맞춘 가짜이고, 일부러 이어 붙여 이 파일이 검사에 걸리지 않게 한다.
"""
import os
import unittest

import publication_check as pc


def hits(text, env=None):
    old = os.environ.get("PUBLICATION_DENYLIST")
    if env is not None:
        os.environ["PUBLICATION_DENYLIST"] = env
    try:
        return pc.scan("t", text, pc.org_rules())
    finally:
        if env is not None:
            if old is None:
                del os.environ["PUBLICATION_DENYLIST"]
            else:
                os.environ["PUBLICATION_DENYLIST"] = old


class Catches(unittest.TestCase):
    def test_secrets(self):
        for s in [
            "gh" + "p_" + "a1B2" * 9,
            "AK" + "IA" + "ABCDEFGHIJKLMNOP",
            "-----BEGIN " + "RSA PRIVATE KEY-----",
            "xo" + "xb-" + "1234567890-abc",
            "s" + "k-ant-" + "x" * 24,
            "password" + " = " + "hunter2hunter2",
        ]:
            self.assertTrue(hits(s), s)

    def test_local_paths(self):
        self.assertTrue(hits("C:" + "/Users/" + "kim/Desktop/repo"))
        self.assertTrue(hits("C:" + "\\Users\\" + "kim\\repo"))
        self.assertTrue(hits("/ho" + "me/kim/work"))
        self.assertTrue(hits("x/App" + "Data/Local/Temp"))

    def test_tool_traces_and_network(self):
        self.assertTrue(hits("lo" + "cal_1a2b3c4d-1a2b-1a2b-1a2b-1a2b3c4d5e6f"))
        self.assertTrue(hits("db at 192." + "168.0.12"))
        self.assertTrue(hits("build." + "corp"))

    def test_personal_email(self):
        self.assertTrue(hits("contact " + "someone" + "@" + "gmail.com"))

    def test_org_denylist_from_env(self):
        self.assertTrue(hits("Shipped to ACME line 3", env=r"(?i)\bacme\b"))
        self.assertFalse(hits("Shipped to line 3", env=r"(?i)\bacme\b"))


class Passes(unittest.TestCase):
    def test_allowed(self):
        for s in [
            "Co-Authored-By: Claude <noreply" + "@anthropic.com>",
            "123+someone@users." + "noreply.github.com",
            "see user@example.com",
            "C:/Users/<이름>/repo",
            "/home/<user>/repo",
            "picasso/src/main/kotlin/dev/picasso/middleware/Model.kt",
            "PR #19, commit 2ef6871, §15.313",
            "password: <비밀번호>",
            "public IP 8.8.8.8",
        ]:
            self.assertEqual([], hits(s), s)

    def test_mask_hides_value(self):
        line = hits("gh" + "p_" + "a1B2" * 9)[0]
        self.assertNotIn("a1B2a1B2", line)


if __name__ == "__main__":
    unittest.main()
