class Solution:
    def strStr(self, haystack: str, needle: str) -> int:
        if not needle:
            return 0

        L = len(haystack)
        N = len(needle)

        for i in range(L - N + 1):
            if haystack[i] == needle[0]:
                if haystack[i:i+N] == needle:
                    return i

        return -1

if __name__ == "__main__":
    sol = Solution()
    test_cases = [
        ("sadbutsad", "sad", 0),
        ("leetcode", "leeto", -1),
        ("shakespeare", "pea", 6),
        ("", "", 0),           # empty in empty
        ("abc", "", 0),        # empty needle
        ("", "a", -1),         # empty haystack
        ("aaaaa", "aa", 0),    # overlapping matches
        ("abc", "c", 2),       # match at end
    ]

    for i, (haystack, needle, expected_index) in enumerate(test_cases, start=1):
        index = sol.strStr(haystack, needle)

        if index == expected_index:
            print(f"Test {i} PASSED")
        else:
            print(f"Test {i} FAILED")
            print(f"haystack: '{haystack}', needle: '{needle}'")
            print(f"Expected return: {expected_index}, got: {index}")
