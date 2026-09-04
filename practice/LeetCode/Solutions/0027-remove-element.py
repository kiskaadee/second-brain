from typing import List


class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        w = 0

        for i in range(len(nums)):
            if nums[i] != val:
                nums[w] = nums[i]
                w += 1

        return w


if __name__ == "__main__":
    sol = Solution()

    test_cases = [
            ([3, 2, 2, 3], 3, 2, [2, 2]),
            ([0, 1, 2, 2, 3, 0, 4, 2], 2, 5, [0, 1, 3, 0, 4]),
            ([1], 1, 0, []),
            ([1], 2, 1, [1]),
            ([], 1, 0, []),
        ]
    for i, (nums, val, expected_k, expected_prefix) in enumerate(test_cases):
        original_nums = nums[:]
        nums_copy = nums[:]
        k = sol.removeElement(nums_copy, val)

        prefix = sorted(nums_copy[:k])
        expected_sorted = sorted(expected_prefix)

        passed = k == expected_k and prefix == expected_sorted

        if passed:
            print(f"Test {i+1} PASSED")
        else:
            print(
                f"Test {i+1} FAILED: input={original_nums}, val={val}, expected_k={expected_k}, got_k={k}, expected_prefix={expected_prefix}, got_prefix={nums_copy[:k]}"
            )
