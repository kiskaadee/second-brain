# Python String Methods Reference
## Core Mental Model

Python strings are **immutable sequences of Unicode characters**.

This means that once a string exists, its contents cannot be changed in place:

```python
s = "hello"

s[0] = "H"  # TypeError
```

Operations that appear to modify a string instead **return a new string**:

```python
s = "hello"

upper = s.upper()
replaced = s.replace("h", "H")

# s itself is unchanged
```

This distinction matters for both correctness and performance.

> **Mental model:** treat a string as a fixed sequence. If you need to construct a different string, either create the result through a single string operation or accumulate mutable pieces and join them afterward.

---

## 1. Inspection and Validation

These methods return boolean values and are useful for validating input or checking character properties.

```python
s = "Python311"

s.isalnum()       # True: all characters are letters or digits
s.isalpha()       # False: contains digits
s.isdigit()       # False: not all characters are digits

"12345".isdigit() # True

s.startswith("Py")  # True
s.endswith("311")   # True

"thon" in s         # True
```

Common character-classification methods include:

|Method|True when...|
|---|---|
|`.isalnum()`|all characters are alphanumeric|
|`.isalpha()`|all characters are alphabetic|
|`.isdigit()`|all characters are digits|
|`.isspace()`|all characters are whitespace|
|`.islower()`|all cased characters are lowercase|
|`.isupper()`|all cased characters are uppercase|

---

## 2. Transformation and Cleaning

String transformation methods return new strings; they do not modify the original.

### Whitespace

```python
s = "   Hello, World!   "

s.strip()   # "Hello, World!"
s.lstrip()  # "Hello, World!   "
s.rstrip()  # "   Hello, World!"
```

### Case conversion

```python
s = "hello, world"

s.lower()       # "hello, world"
s.upper()       # "HELLO, WORLD"
s.capitalize()  # "Hello, world"
s.title()       # "Hello, World"
```

### Replacement

```python
"banana".replace("a", "o")
# "bonono"
```

The original string remains unchanged:

```python
s = "banana"

s.replace("a", "o")

s  # "banana"
```

---

## 3. Splitting and Joining

Splitting and joining are especially important in algorithm problems because they provide an efficient way to move between a string and a collection of string fragments.

### Splitting

`.split()` converts a string into a list of substrings.

```python
sentence = "apple,banana,cherry"

sentence.split(",")
# ['apple', 'banana', 'cherry']
```

Without an argument, `.split()` uses runs of whitespace as the separator:

```python
"hello   world\npython".split()
# ['hello', 'world', 'python']
```

You can limit the number of splits:

```python
"a-b-c-d".split("-", 2)
# ['a', 'b', 'c-d']
```

### Joining

`.join()` takes an iterable of strings and constructs one string, placing the caller string between the elements.

```python
words = ["Backend", "Engineer", "Roadmap"]

" ".join(words)
# "Backend Engineer Roadmap"

"".join(words)
# "BackendEngineerRoadmap"

"-".join(["a", "b", "c"])
# "a-b-c"
```

A useful mental model is:

```text
split:  string → list[str]
join:   iterable[str] → string
```

---

## 4. Searching and Indexing

### Substring search

```python
s = "leetcode"

"code" in s       # True
"xyz" in s        # False
```

### Finding positions

`.find()` returns the first matching index, or `-1` if the substring is absent.

```python
s.find("t")   # 3
s.find("z")   # -1
```

`.index()` behaves similarly, but raises `ValueError` when the substring is absent.

```python
s.index("t")  # 3

s.index("z")  # ValueError
```

### Counting

```python
s.count("e")  # 3
```

---

## 5. Indexing and Slicing

Strings support random access through indexing:

```python
s = "abcdefg"

s[0]   # "a"
s[3]   # "d"
s[-1]  # "g"
```

Indexing is constant time:

$$
T_{\text{index}} = O(1)
$$

However, strings do **not** support item assignment:

```python
s[0] = "A"
# TypeError
```

### Slicing

Slicing creates a new string containing the selected characters.

```python
s = "abcdefg"

s[1:4]   # "bcd"
s[:3]    # "abc"
s[3:]    # "defg"
s[::2]   # "aceg"
s[::-1]  # "gfedcba"
```

A slice of length $K$ requires $O(K)$ time and space because the resulting string has to be constructed.

Therefore:

```python
s[i]
```

is:

$$
O(1)
$$

while:

```python
s[i:j]
```

is:

$$
O(j-i)
$$

This distinction matters when slices appear inside loops.

---

## 6. Mutability and Character-by-Character Modification

Strings cannot be modified in place.

If an algorithm needs to change individual characters, a common approach is:

```python
chars = list("hello")

chars[0] = "H"
chars[4] = "!"

result = "".join(chars)

result
# "Hell!"
```

The general pattern is:

```text
immutable string
      ↓
mutable list
      ↓
modify in place
      ↓
join once
      ↓
new string
```

This is particularly useful when an algorithm performs many character modifications.

---

# Performance Patterns

## 7. Repeated String Construction

The important performance question is not simply:

> "Are strings immutable?"

It is:

> **How many characters does each operation have to copy or construct?**

Consider the conceptual pattern:

```python
result = ""

for char in chars:
    result += char
```

With immutable strings, repeatedly extending the result can require repeatedly constructing larger strings:

```text
""       → "a"
"a"      → "ab"
"ab"     → "abc"
"abc"    → "abcd"
...
```

Under the straightforward immutable-string model, the amount of data copied is approximately:

$$
0 + 1 + 2 + \dots + (N-1)
$$

which is:

$$
\frac{N(N-1)}{2} = O(N^2)
$$

The more important lesson is therefore:

> **Repeatedly rebuilding an immutable aggregate can turn an apparently linear loop into a quadratic algorithm.**

### Preferred accumulation pattern

When constructing many string fragments, accumulate them in a mutable collection and construct the final string once:

```python
result = []

for char in chars:
    result.append(char)

result = "".join(result)
```

The work is approximately:

```text
append N elements  → O(N)
join N elements    → O(N)
---------------------------
total              → O(N)
```

This gives:

$$
O(N) + O(N) = O(N)
$$

### Why `.join()` is the right abstraction

The advantage of `.join()` is not merely that it is a "faster version of `+`."

It lets the runtime construct the final string **as one operation**, rather than requiring the algorithm to repeatedly grow an immutable result.

A useful general pattern is:

```text
BAD CONCEPTUALLY:

partial result
      ↓
rebuild
      ↓
larger result
      ↓
rebuild
      ↓
larger result
      ↓
...


GOOD:

individual pieces
      ↓
mutable collection
      ↓
construct once
      ↓
final result
```

> **General DSA pattern:** when an immutable result must be built incrementally, accumulate pieces first and materialize the final immutable object once.

### Python implementation nuance

For algorithm analysis, it is useful to understand the quadratic model above. However, avoid treating the statement "`+=` is always $O(N^2)$ in Python" as an absolute rule.

CPython has an optimization that can make some repeated `str += ...` operations substantially more efficient when the string can be resized in place.

Nevertheless:

```python
"".join(parts)
```

remains the clearest and idiomatic approach when you already have multiple string fragments to combine.

The broader lesson—**repeatedly rebuilding immutable data can be expensive**—is more important than memorizing a rule about one Python implementation.

---

## 8. A Critical Complexity Distinction

The fact that a piece of code contains one loop does **not** automatically make it $O(N)$.

Always analyze the work performed by each iteration.

For example:

```python
for i in range(n):
    result.append(s[i])
```

If `append()` is amortized $O(1)$:

$$
N \times O(1) = O(N)
$$

But consider an operation whose cost grows with the amount of data accumulated so far:

```text
iteration 1 → work proportional to 1
iteration 2 → work proportional to 2
iteration 3 → work proportional to 3
...
iteration N → work proportional to N
```

Then:

$$
1 + 2 + 3 + \dots + N = O(N^2)
$$

This is why, when analyzing string algorithms, ask:

> **How much existing data does this operation have to touch?**

---

## 9. Quick Complexity Reference

|Operation|Typical complexity|
|---|--:|
|`s[i]`|$O(1)$|
|`s[i:j]`|$O(K)$|
|`s[::-1]`|$O(N)$|
|`"x" in s`|$O(N)$ worst case|
|`s.find(x)`|$O(N)$ typical upper-bound model|
|`s.count(x)`|$O(N)$|
|`s.lower()`|$O(N)$|
|`s.replace(...)`|$O(N)$ typical|
|`s.split(...)`|$O(N)$ total output construction|
|`"".join(parts)`|$O(N)$ in total output size|
|`list(s)`|$O(N)$|
|`s + t`|$O(len(s) + len(t))$|
|repeated immutable concatenation|potentially $O(N^2)$|
|`list.append()`|$O(1)$ amortized|

The exact implementation complexity of some string operations depends on the operation, input, and Python implementation. For DSA analysis, the important distinction is usually between operations that touch a constant amount of data and operations that must process the existing string or produce a new string proportional to its size.
