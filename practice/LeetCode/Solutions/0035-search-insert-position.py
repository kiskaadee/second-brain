from typing import List

class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        if not nums:
            return 0

        left = 0
        right = len(nums) - 1

        while left <= right:
            mid = left + (right - left) // 2
            if nums[mid] == target:
                return mid
            elif target > nums[mid]:
                left = mid + 1

            else:
                right = mid - 1
        
        return left



if __name__ == "__main__":

    sol = Solution()

    test_cases = [
	    ([1, 2, 3, 4, 5], 5, 4),
        ([1, 3, 5, 6], 5, 2),
        ([1, 3, 5, 6], 2, 1),
        ([1, 3, 5, 6], 7, 4),
        ([1, 2, 3, 5, 6], 4, 3),
        ([], 1, 0)
    ]

    for i, (nums, target, expected_output) in enumerate(test_cases, start=1):
        res = sol.searchInsert(nums, target)
        if res == expected_output:
            print(f"Test {i} PASSED")
        else:
            print(f"Test {i} FAILED:")
            print(f"    Expected output: {expected_output}, got {res}")
