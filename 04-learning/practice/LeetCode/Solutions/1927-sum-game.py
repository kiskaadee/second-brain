class Solution:
    def sumGame(self, sum: str) -> bool:
        return False


if __name__ == "__main__":
    sol = Solution()

    test_cases = [("5023", False), ("25??", True), ("25??", False)]

    for i, (num, exp) in enumerate(test_cases, start=1):
        out = sol.sumGame(num)

        print("TEST PASSED" if out == exp else f"TEST {i} FAILED")
