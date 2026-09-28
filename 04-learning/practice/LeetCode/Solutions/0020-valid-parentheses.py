class Solution:
    def isValid(self, string: str) -> bool:
        pairs = {"(": ")", "{": "}", "[": "]"}

        stack = []

        for char in string:
            if char in pairs:
                stack.append(pairs[char])
            elif not stack or stack.pop() != char:
                return False

        return not stack
