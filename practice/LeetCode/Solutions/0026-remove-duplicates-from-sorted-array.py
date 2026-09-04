from typing import List


class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        if not nums:
            return 0

        w = 1

        for i in range(1, len(nums)):
            if nums[i] != nums[i-1]:
                nums[w] = nums[i]
                w+=1

        return w

if __name__ == "__main__":
    sol = Solution()

    test_cases = [
        # input, expected_k, expected_prefix
        ([1, 1, 2], 2, [1, 2]),
        ([0, 0, 1, 1, 1, 2, 2, 3, 3, 4], 5, [0, 1, 2, 3, 4]),
        ([1, 2, 3, 4, 5], 5, [1, 2, 3, 4, 5]),
        ([2, 2, 2, 2], 1, [2]),
        ([], 0, []),
        ([1], 1, [1]),
    ]

    for i, (nums, expected_k, expected_prefix) in enumerate(test_cases, start=1):
        nums = nums[:]
        k = sol.removeDuplicates(nums)

        passed = (
            k == expected_k and nums[:k] == expected_prefix
        )

        if passed:
            print(f"Test {i} PASSED")
        else:
            print(f"Test {i} FAILED")
            print(f"    expected k: {expected_k}, got k={k} ")
            print(f"    expected prefix: {expected_prefix}, got {nums[:k]}")
            print(f"    array state: {nums}")
