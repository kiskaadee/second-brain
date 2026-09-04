from typing import List


class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if len(strs) == 0:
            return ""
        return self.horizontal_scanning(strs)

    def vertical_scanning(self, strs: List[str]) -> str:
        prefix = []
        ref_string = strs[0]

        for i, char in enumerate(ref_string):
            for string in strs[1:]:
                if i >= len(string) or string[i] != char:
                    return "".join(prefix)
            prefix.append(char)

        return "".join(prefix)

    def horizontal_scanning(self, strs: List[str]) -> str:
        prefix = strs[0]

        for string in strs[1:]:
            while not string.startswith(prefix):
                prefix = prefix[:-1]

        return prefix

    def transpose_matrix(self, strs: List[str]) -> str:
        prefix = []
        transposed = list(zip(*strs))

        for i, row in enumerate(transposed):
            if not len(set(row)) <= 1:
                return "".join(prefix)
            prefix.append(transposed[i][0])

        return "".join(prefix)

    def binary_search(self, strs: List[str]) -> str:
        def is_common_prefix(strs, k):
            prefix = strs[0][:k]
            for string in strs[1:]:
                if string[:k] != prefix:
                    return False
            return True

        left = 0
        right = min(len(string) for string in strs)
        answer = ""
        while left <= right:
            mid = left + (right - left) // 2
            if is_common_prefix(strs, mid):
                answer = strs[0][:mid]
                left = mid + 1
            else:
                right = mid - 1
        return answer
