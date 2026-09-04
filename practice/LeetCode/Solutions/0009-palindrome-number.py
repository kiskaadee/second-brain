class Solution:
    def isPalindrome(self, x: int) -> bool:
        if x < 0:
            return False
        if x < 10:
            return True
        if x % 10 == 0:
            return False
        return self.two_pointers(x)

    def two_pointers(self, x: int) -> bool:
        s: str = str(x)
        i, j = 0, len(s) - 1

        while i < j:
            if s[i] != s[j]:
                return False
            i += 1
            j -= 1
        return True

    def reverse_string(self, x: int) -> bool:
        chars: str = str(x)
        # rev_chars = "".join(chars[i] for i in range(len(chars) - 1, -1, -1))
        rev_chars = chars[::-1]
        return chars == rev_chars

    def reverse_half(self, x: int) -> bool:
        r: int = 0
        while x > r:
            r = 10 * r + x % 10
            x //= 10
        return x == r or x == r // 10
