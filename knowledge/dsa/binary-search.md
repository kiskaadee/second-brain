# Binary Search: The Geometry of Uncertainty

## Key Insights

- **The Information Theory Insight** — Binary search is not an array trick, but a systematic method for reducing uncertainty.
- **Boundary Management** — `left` and `right` are not merely indices; they are boundaries that define what is still possible.
- **The Loop Invariant as a Contract** — Correct binary search implementations follow explicit logical guarantees rather than memorized pointer manipulations.
- **Monotonicity** — Binary search applies whenever the search space has a predictable ordering that allows us to eliminate one half after evaluating a candidate.
- **Escaping the Array** — The search space does not need to be stored in memory. We can binary-search a range of possible answers.

---

## Introduction

Binary search is an algorithm for locating a target or boundary within an **ordered search space** by repeatedly eliminating approximately half of the remaining possibilities.

For a collection of $N$ elements, this produces a time complexity of $O(\log N)$.

The important idea, however, is not the array, the index, or even the midpoint. The fundamental idea is **reducing uncertainty as quickly as possible**.

---

## The Cost of Scale

Imagine you are given a digital safe with a 4-digit combination ranging from `0000` to `9999`. There are 10,000 possible combinations, and you have no idea which one opens the safe.

If you test the combinations sequentially:

```text
0000
0001
0002
0003
...
9999
```

you are performing a **[linear search](https://en.wikipedia.org/wiki/Linear_search)**.

In the worst case, you must test all 10,000 possibilities. The number of attempts grows directly with the size of the search space:

$$  
O(N)  
$$

Now imagine the safe provides an additional piece of information after every incorrect attempt:

> **Too high**.

or:

> **Too low**.

That changes everything.

Instead of starting at `0000`, you try:

```text
5000
```

Suppose the safe responds:

> **Too high**.

You have immediately eliminated every possibility from `5001` through `9999`.

You did not test those combinations individually. You eliminated them through a single comparison.

The remaining search space is:

```text
0000 ───────────────── 4999
```

You then try the midpoint again:

```text
2500
```

Suppose the response now is:

> **Too low**.

Now everything from `0000` through `2500` can be discarded:

```text
2501 ──────────────── 4999
```

After only two comparisons, the original 10,000 possibilities have been reduced to 2,499.

The important part is not the particular numbers. It is the strategy:

> **Each comparison should eliminate as much uncertainty as possible.**

After every step, the search space is approximately halved:

$$  
N \rightarrow \frac{N}{2}  
\rightarrow \frac{N}{4}  
\rightarrow \frac{N}{8}  
\rightarrow \cdots  
$$

After $k$ steps, the possible keys left are approximately:
$$
\frac{N}{2^k}
$$ The search ends when:
$$  
\frac{N}{2^k} \leq 1  
$$

which gives:
$$  
k \approx \log_2 N  
$$

This is the source of binary search's $O(\log N)$ time complexity.

---

## The Mental Model: Halving Uncertainty

The same reasoning appears in something as ordinary as looking up a word in a dictionary.

Suppose you want to find a word beginning with the letter **'S'**. You do not start at the first page and scan forward one page at a time. Instead, you open the dictionary somewhere around the middle.

Suppose the words on that page begin with **M**. You immediately know that your target cannot appear before that point. 

You discard the entire first portion of the dictionary and continue searching only the remaining portion.

Then, you repeat the process:

1. Identify the remaining search space.
2. Inspect its midpoint.
3. Use the result to determine which half can be discarded.
4. Repeat.

Eventually, the search space contains either the target or nothing.

This is the essence of binary search.

> **Binary search maximizes the information gained from each comparison by using that comparison to eliminate an entire region of the search space.**

---

## From Intuition to Code: Managing Boundaries

To translate this reasoning into code, we need a way to represent the part of the search space that remains possible.

We do not need to keep track of every candidate individually.

We only need two boundaries:
```text
left                                                     right
  │                                                        │
  ▼                                                        ▼
  ┌────────────────────────────────────────────────────────┐
  │                     remaining space                    │
  └────────────────────────────────────────────────────────┘

```

For an array, these boundaries are usually indices:

```python
left = 0 # index of the first element
right = len(arr) - 1 # index of the last element 
```

Together, they define the current search window:

```text
[left, right]
```

For the standard implementation, this window is **inclusive**.

That means:

- `left` is a possible candidate.
- `right` is a possible candidate.
- Everything outside `[left, right]` has already been proven impossible.

The algorithm's job is therefore not simply to "move pointers."

Its job is to repeatedly **prove that portions of the search space can no longer contain the answer**.

---

## The Loop Invariant as a Contract

Before writing the `while` loop, establish a logical guarantee—a **loop invariant**:

> **If the target exists in the array, it is guaranteed to lie somewhere within the inclusive range `[left, right]`.**

Initially:

```python
left = 0
right = len(arr) - 1
```

so the entire array is considered possible.

Every comparison must preserve the invariant.

Suppose:

```python
arr[mid] < target
```

Because the array is sorted, everything at or before `mid` is also less than the target.

Therefore, none of those elements can be the answer.

We can safely discard them:

```python
left = mid + 1
```

Then our search space is narrowed down to only those elements after the mid point:

```text
						      left                       right
                                │                          │
								▼                          ▼
  ┌────────────────────────────────────────────────────────┐
  │     ---- discarted ----    │      remaining space      │
  └────────────────────────────────────────────────────────┘
```

Likewise, if:

```python
arr[mid] > target
```

then everything at or after `mid` is too large, so we discard that region:

```python
right = mid - 1
```

Norrowing the search space to only the elements before `mid`:

```text
left                       right
  │                          │
  ▼                          ▼
  ┌────────────────────────────────────────────────────────┐
  │      remaining space      │     ---- discarted ----    │
  └────────────────────────────────────────────────────────┘
```

The invariant remains true after every update.

Thinking in terms of the invariant is much more reliable than memorizing:

> "If smaller, move left. If larger, move right."

The pointer updates are consequences of the logical guarantee.

---

## Calculating the Pivot

Once the boundaries are known, we inspect the middle of the remaining search space.

The midpoint can be calculated as:

$$  
mid = left + \frac{right-left}{2}  
$$

In Python:

```python
mid = left + (right - left) // 2
```

You will often see the simpler expression:

```python
mid = (left + right) // 2
```

For Python, both produce the same result for ordinary non-negative array indices because Python integers have arbitrary precision.

The first formulation is nevertheless worth learning because in languages using fixed-width integers, such as C++ or Java, `left + right` can overflow before the division takes place.

The overflow-safe form:

```python
left + (right - left) // 2
```

avoids that intermediate addition.

---

## Why `mid + 1` and `mid - 1`?

Consider the case where:

```python
arr[mid] < target
```

We know that `mid` itself cannot be the answer: we just checked it, and it is not equal to the target.

Therefore, keeping `mid` inside the next search window is unnecessary.

We can move directly past it:

```python
left = mid + 1
```

Likewise:

```python
right = mid - 1
```

when `arr[mid] > target`.

This is important for **termination**.

Suppose:

```python
left == right == mid
```

and we decide that the target must be to the right.

If we wrote:

```python
left = mid
```

the boundaries would remain unchanged:

```python
left == right
```

The loop could repeat forever.

By using:

```python
left = mid + 1
```

or:

```python
right = mid - 1
```

we guarantee that the current midpoint is removed from consideration and that the search window strictly shrinks.

---

## Prerequisites for Efficient Binary Search

Binary search depends on structure in the search space.

### Ordered or Monotonic Search Space

For the classic binary search problem, the elements must be ordered:

```text
1  4  7  10  15  21  30
```

This ordering lets us infer information about an entire region from a single comparison.

For generalized binary search, the search space does not necessarily contain sorted values. Instead, it must have some **[monotonic property](https://www.baeldung.com/cs/monotonic-functions-applications)** that allows one half to be discarded after evaluating a candidate.

### Efficient Access to the Search Space

For the standard array implementation to achieve $O(\log N)$ time, accessing the midpoint should be efficient—typically $O(1)$ random access.

Arrays provide this property:

```python
arr[mid]
```

can be evaluated directly.

A linked list does not.

Although a linked list can be sorted, reaching its midpoint requires traversing its nodes. Repeatedly performing those traversals introduces additional work and destroys the usual $O(\log N)$ time advantage.

Therefore, binary search is naturally suited to arrays and other data structures that provide efficient access to arbitrary positions.

---

## Practical Implementation

The standard iterative implementation is:

```python
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    # Invariant:
    # If target exists, it is within [left, right].
    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid

        if arr[mid] < target:
            # Everything through mid is too small.
            left = mid + 1
        else:
            # Everything through mid is too large.
            right = mid - 1

    # The search space is exhausted.
    return -1
```

The control flow follows directly from the invariant:

```python
arr[mid] == target
        │
        └── found → return mid

arr[mid] < target
        │
        └── target must be to the right
            left = mid + 1

arr[mid] > target
        │
        └── target must be to the left
            right = mid - 1
```

When the loop terminates:

```python
left > right
```

there are no candidates remaining.

Therefore, the target does not exist in the search space.

Returning `-1` is a common convention for representing "not found," although different APIs may choose different conventions.

---

## Why the Loop Condition Is `left <= right`

The search window is inclusive:

```python
[left, right]
```

Therefore, when:

```python
left == right
```

there is still **one possible element** to examine.

For example:

```text
left
 │
 ▼
[42]
 ▲
 │
right
```

The loop must still execute so that `42` can be checked.

Only when:

```python
left > right
```

is the search space genuinely empty.

Therefore:

```python
while left <= right:
```

matches the definition of the search window.

This relationship is worth remembering:

```python
left <= right   # →   at least one candidate remains
left > right    # →   no candidates remain
```

---

## Why Not Use Recursion in Python?

Binary search can also be expressed recursively:

```python
def binary_search_recursive(arr, target, left, right):
    if left > right:
        return -1

    mid = left + (right - left) // 2

    if arr[mid] == target:
        return mid

    if arr[mid] < target:
        return binary_search_recursive(
            arr, target, mid + 1, right
        )

    return binary_search_recursive(
        arr, target, left, mid - 1
    )
```

The recursive and iterative versions have the same time complexity:

$$  
O(\log N)  
$$

However, they differ in space usage.

Every recursive call creates a new stack frame. Because Python does not perform **[tail-call optimization](https://inventwithpython.com/recursion/chapter8.html)**, those frames remain on the call stack until the recursion unwinds.

Therefore:
- Iterative version: $O(1)$ extra space.
- Recursive version: $O(\log N)$ extra space.

Binary search does not benefit from recursive structure, so the iterative implementation is generally preferable in Python.

The important point is not that binary search recursion becomes deep for ordinary arrays—it does not. A search over one million elements requires only about 20 iterations. The issue is that recursion introduces stack usage and Python's recursion-depth limitation without providing a compensating benefit.

---

## Escaping the Array: Monotonicity

A common misconception is that binary search requires a physical array of sorted numbers.

It does not.

The deeper requirement is a **[monotonic search space](https://paths.grasp.study/courses/47d07de9-ab78-4fd8-80fb-843bd335361c/modules/3b44a9fb-ed8c-4f29-98eb-39fa66a25fb7/lessons/fd88f7b5-b3ca-421c-98d9-f8d90dea02e0)**.

Consider a predicate that tells us whether a candidate answer is valid:

```text
candidate:  1  2  3  4  5  6  7  8
valid?:     F  F  F  F  T  T  T  T
                         ^
                    first valid
```

Once the predicate becomes `True`, it never becomes `False` again.

This gives us a boundary:

```text
False | True
      ^
   answer
```

Binary search can locate that boundary without any array containing the values.

The general pattern is:

> **Find a boundary in a monotonic search space where a condition changes from one state to another.**

At each step, evaluate the midpoint. 

If the midpoint is invalid, everything on one side can also be eliminated.

If the midpoint is valid, everything on the other side can be eliminated.

The same halving principle applies.

---
## Binary Search on the Answer

This is sometimes called ***binary search on the answer***.

Instead of asking:

> "Where is this value in the array?"

we ask:

> "What is the smallest value for which this condition becomes true?"

For example, suppose a problem asks for the [minimum eating speed ](https://www.geeksforgeeks.org/dsa/koko-eating-bananas/)that allows someone to consume all banana piles within a given number of hours.

We could search the possible speeds:

```text
1  2  3  4  5  6  7  ...  max(pile)
```

We don't need an array containing every possible speed.

We only need to evaluate whether a particular speed is sufficient.

The resulting predicate might look like:

```text
speed:     1  2  3  4  5  6  7
sufficient F  F  F  F  T  T  T
                     ^
               minimum valid
```

Binary search can locate the first `True`.

The same pattern appears in problems involving:

- Minimum eating speed.
- Minimum shipping capacity.
- Minimum time required to complete a task.
- Maximum feasible value.
- Integer square roots.
- Finding the first or last occurrence of a value.
- Finding insertion positions and boundaries.

The physical representation of the search space changes, but the reasoning remains the same.

---

## The General Binary Search Pattern

At its most abstract, binary search can be understood as:

1. Define the search space.
2. Define what it means for a candidate to be valid.
3. Establish the monotonic property.
4. Choose the midpoint.
5. Evaluate the midpoint.
6. Determine which half cannot contain the answer.
7. Discard that half.
8. Repeat until the boundary is found.

The crucial step is **not** calculating the midpoint.

The crucial step is proving that one side can be discarded.

Without that proof, choosing a midpoint does not constitute binary search.

---

## Complexity Analysis

Each iteration reduces the search space by approximately half:

$$  
N \rightarrow \frac{N}{2}  
\rightarrow \frac{N}{4}  
\rightarrow \frac{N}{8}  
\rightarrow \cdots  
$$

Therefore, the number of iterations grows logarithmically:

|Aspect|Iterative|Recursive|
|---|--:|--:|
|Time|$O(\log N)$|$O(\log N)$|
|Extra space|$O(1)$|$O(\log N)$|

The $O(\log N)$ time complexity assumes that evaluating the midpoint or predicate itself takes $O(1)$ time.

This distinction matters.

For example, binary search over an array provides $O(1)$ access to `arr[mid]`, so the overall algorithm is $O(\log N)$.

If evaluating a candidate requires substantial additional work, the total complexity becomes:

$$  
O(\log N \times C)  
$$

where $C$ is the cost of evaluating one candidate.

---

## Summary Checklist

Before implementing binary search, verify:

-  Is the search space **sorted or monotonic**?
-  Can evaluating a candidate tell me which half can be discarded?
-  Have I clearly defined what the search boundaries represent?
-  Is my search window inclusive or exclusive?
-  Does my loop condition match that boundary convention?
-  Does the target, if present, remain inside my search window?
-  After checking `mid`, can I safely exclude it?
-  Do my updates guarantee that the search space strictly shrinks?
-  Am I returning the appropriate result when the search space becomes empty?
-  If I am searching for a boundary rather than an exact value, have I defined which boundary I need?
-  Does evaluating the midpoint actually take constant or otherwise acceptable time?

The most important question is:

> **What information does evaluating the midpoint give me that allows me to eliminate an entire region of the search space?**

If that question has a precise answer, you are probably looking at a binary search problem.