
# [1927. Sum Game](https://leetcode.com/problems/sum-game/)

**Difficulty**: Medium
## Problem Statement

Alice and Bob take turns playing a game, with **Alice** **starting first**.

You are given a string `num` of **even length** consisting of digits and `'?'` characters. On each turn, a player will do the following if there is still at least one `'?'` in `num`:

1. Choose an index `i` where `num[i] == '?'`.
2. Replace `num[i]` with any digit between `'0'` and `'9'`.

The game ends when there are no more `'?'` characters in `num`.

For Bob to win, the sum of the digits in the first half of `num` must be **equal** to the sum of the digits in the second half. For Alice to win, the sums must **not be equal**.

- For example, if the game ended with `num = "243801"`, then Bob wins because `2+4+3 = 8+0+1`. If the game ended with `num = "243803"`, then Alice wins because `2+4+3 != 8+0+3`.

Assuming Alice and Bob play **optimally**, return `true` _if Alice will win and_ `false` if Bob will win.

**Example 1:**

**Input:** num = "5023"
**Output:** false
**Explanation:** There are no moves to be made.
The sum of the first half is equal to the sum of the second half: 5 + 0 = 2 + 3.

**Example 2:**

**Input:** num = "25??"
**Output:** true
**Explanation:** Alice can replace one of the '?'s with '9' and it will be impossible for Bob to make the sums equal.

**Example 3:**

**Input:** num = "?3295???"
**Output:** false
**Explanation:** It can be proven that Bob will always win. One possible outcome is:
- Alice replaces the first '?' with '9'. num = "93295???".
- Bob replaces one of the '?' in the right half with '9'. num = "932959??".
- Alice replaces one of the '?' in the right half with '2'. num = "9329592?".
- Bob replaces the last '?' in the right half with '7'. num = "93295927".
Bob wins because 9 + 3 + 2 + 9 = 5 + 9 + 2 + 7.

**Constraints:**

- `2 <= num.length <= 105`
- `num.length` is **even**.
- `num` consists of only digits and `'?'`.

### Hint 1
Bob can always make the total sum of both sides equal in mod 9.

### Hint 2

Why does the difference between the number of question marks on the left and right side matter?

---

## Intuition

The game is determined by the difference between the digit sums of the two halves. Alice starts the game, so the parity of the number of `'?'` characters determines which player makes the final move. However, the total number of `'?'` characters alone does not appear to determine the outcome. Hint 2 suggests that the relevant quantity is the difference between the number of `'?'` characters in the left and right halves. For example:


```python 
num = "234???" 
# Left half: 2 + 3 + 4 = 9
# Right half: 0
#
# All three unknown digits are in the right half.
# Alice makes the first move, followed by Bob and then Alice.
#
# The optimal strategy is not yet clear.
```

- Alice always goes first
- All strings can be halved in two symmetrically 
- **the distribution of `?`s between the two halves matters.** 
## Algorithm


## Testing

Initial test cases:

- `"5023"` → `False`
- `"25??"` → `True`
- `"?3295???"` → `False`


```python
if __name__ == "__main__":
    sol = Solution()

    test_cases = [("5023", False), ("25??", True), ("25??", False)]

    for i, (num, exp) in enumerate(test_cases, start=1):
        out = sol.sumGame(num)

        print("TEST PASSED" if out == exp else f"TEST {i} FAILED")


```
## Implementation

```python

class Solution:
    def sumGame(self, sum: str) -> bool:
        # to-do
        return False

```
## Complexity


## Takeaways

