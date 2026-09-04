class Solution:
    def lengthOfLastWord(self, s: str) -> int:
        if not s:
            return 0
        return self.traverse_backwards(s)

    def split_words(self, s: str) -> int:
        words = s.split()
        return len(words[-1]) if words else 0

    def traverse_backwards(self, s: str) -> int:
        start = None
        for i, char in enumerate(reversed(s)):
            if start is None and char != " ":
                # found start
                start = i
            if start is not None:
                if char == " ":
                    # found end
                    return i - start
        return len(s) - start if start is not None else 0


if __name__ == "__main__":
    sol = Solution()

    test_cases = [
        ("Hello World", 5),
        ("   fly me   to   the moon  ", 4),
        ("luffy is still joyboy", 6),
        ("", 0),
        ("H     ", 1),
    ]

    for i, (s, expected_output) in enumerate(test_cases, start=1):
        res = sol.lengthOfLastWord(s)
        if res == expected_output:
            print("TEST PASSED")
        else:
            print(f"Test {i} FAILED:")
            print(f"    Expected output: {expected_output}, got: {res}")
