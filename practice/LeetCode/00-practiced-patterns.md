# Practiced Patterns

This document tracks the algorithmic patterns encountered while solving LeetCode problems.

The goal is not to measure mastery, but to record exposure. A pattern is added once it has been implemented in at least one problem. As more exercises are solved, the lists grow, making it easier to identify which techniques have been practiced repeatedly and which still need focused work.

The tables below provide two complementary views:

- **Practiced patterns:** groups problems by the primary algorithmic technique they exercise.
- **Patterns by problem:** records the main pattern(s) used to solve each individual problem.

## Patterns

| Pattern               | Notes                                                                                | **Problems**                                                                                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Array / Linear Scan   | The "default" pattern. Many Easy problems are just one pass over an array or string. | [#01](01-two-sum.md)<br>[#13](13-roman-to-integer.md)<br>[#14](14-longest-common-prefix.md)<br>[#28](28-find-the-index-of-the-first-occurrence-in-a-string.md)<br> |
| In-place Edit         | Modify the existing container while maintaining a write index                        | [#26](26-remove-duplicates-from-sorted-array.md)<br>[#27](27-remove-element.md)                                                                                 |
| String                | String-specific manipulation/search.                                                 | [#14](14-longest-common-prefix.md)                                                                                                                              |
| String Search         | Find the first occurrence of a pattern within a larger string.                       | [#28](28-find-the-index-of-the-first-occurrence-in-a-string.md)                                                                                                    |
| Linked List           | Separate from Two Pointers because the mechanics differ.                             | [#21](21-merge-two-sorted-lists.md)                                                                                                                             |
| Hash Table            | Dictionaries, sets, counting, lookups.                                               | [#01](01-two-sum.md)<br>[#13](13-roman-to-integer.md)<br>[#20](20-valid-parentheses.md)                                                                            |
| Stack                 | LIFO problems.                                                                       | [#20](20-valid-parentheses.md)                                                                                                                                     |
| Queue                 | FIFO problems.                                                                       |                                                                                                                                                                 |
| Two Pointers          | Left/right, fast/slow, read/write.                                                   | [#09](09-palindrome-number.md)<br>[#21](21-merge-two-sorted-lists.md)<br>[#26](26-remove-duplicates-from-sorted-array.md)<br>[#27](27-remove-element.md)<br>    |
| Sliding Window        | Dynamic intervals.                                                                   |                                                                                                                                                                 |
| Binary Search         | Search over ordered space.                                                           | [#14](14-longest-common-prefix.md)<br>[#35](35-search-insert-position.md)                                                                                       |
| Tree DFS/BFS          | Tree traversals.                                                                     | #                                                                                                                                                               |
| Graph DFS/BFS         | Graph traversals.                                                                    |                                                                                                                                                                 |
| Heap / Priority Queue | Top-K, scheduling, streaming.                                                        |                                                                                                                                                                 |
| Backtracking          | Search with undo.                                                                    |                                                                                                                                                                 |
| Dynamic Programming   | Memoization/state transitions.                                                       |                                                                                                                                                                 |
| Greedy                | Locally optimal choices.                                                             |                                                                                                                                                                 |
## Problems

| Problem                                                                               | Primary Pattern                 | Secondary Pattern        |
| ------------------------------------------------------------------------------------- | ------------------------------- | ------------------------ |
| [#1 Two Sum](01-two-sum.md)                                                           | HashMap                         | Array                    |
| [#9 Palindrome Number](09-palindrome-number.md)                                       | Two pointers (or half-reversal) | Math                     |
| [#13 Roman to Integer](13-roman-to-integer.md)                                        | HashMap                         | Linear scan              |
| [#14 Longest Common Prefix](14-longest-common-prefix.md)                              | String                          | Linear scan              |
| [#20 Valid Parentheses](20-valid-parentheses.md)                                         | Stack                           | HashMap (matching pairs) |
| [#21 Merge Two Sorted Lists](21-merge-two-sorted-lists.md)                            | Two pointers                    | Linked List              |
| [#26 Remove Duplicates from Sorted Array](26-remove-duplicates-from-sorted-array.md)  | Two pointers                    | In-place array           |
| [#27 Remove Element](27-remove-element.md)                                            | Two pointers                    | In-place filtering       |
| [#28 Find First Occurrence](28-find-the-index-of-the-first-occurrence-in-a-string.md) | String  Search                  | Linear scan              |
| [#35 Search Insert Position](35-search-insert-position.md)                            |                                 |                          |
