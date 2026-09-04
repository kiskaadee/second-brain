from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}

        for i, x in enumerate(nums):
            y = target - x
            if y in seen:
                return [i, seen[y]]
            seen[x] = i
        return []

    def brute_force(self, nums: List[int], target: int) -> List[int]:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []
