class Solution:
    SYMBOLS = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000,
    }

    def romanToInt(self, s: str) -> int:
        result = 0
        values = self.SYMBOLS
        current = values[s[0]]

        for i in range(len(s) - 1):
            following = values[s[i + 1]]
            result += current * (-1 if following > current else 1)
            current = following

        return result + current
