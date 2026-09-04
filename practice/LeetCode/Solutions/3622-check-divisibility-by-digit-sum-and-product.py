class Solution:
    def checkDivisibility(self, number: int) -> bool:
        n = number
        dig_pro = 1
        dig_sum = 0

        while n > 0:
            digit = n % 10
            dig_pro *= digit
            dig_sum += digit
            n //= 10

        return number % (dig_pro + dig_sum) == 0


if __name__ == "__main__":
    sol = Solution()

    test_cases = [
        (99, True),
        (23, False),
    ]

    for i, (n, expected) in enumerate(test_cases, start=1):
        res = sol.checkDivisibility(n)

        if res == expected:
            print("TEST PASSED")

        else:
            print(f"TEST {i} FAILED:")
            print(f"    Expected: {expected}, got: {res}")
