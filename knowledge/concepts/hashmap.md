# What is a HashMap?

Reference: [HashMaps in Python Tutorial - Data Structures for Coding Interviews](https://www.youtube.com/watch?v=RcZsTI5h0kg)

A HashMap is a data structure that stores items in **key-value pairs**. Instead of using numeric indices (like an array), you use their unique identifier (the key) to quickly retrieve, insert, or delete its associated value with an average time complexity of $O(1)$.

Imagine your phone contacts. Instead of remembering that Alice is stored at position 237, you simply ask for `"Alice"` and immediately retrieve her phone number. The contact name is the **key**; the phone number is the **value**.
## Why use a HashMap?

HashMaps are useful because they allow us to:

- Associate meaningful keys with values instead of relying on numeric indices.
- Perform insertions, lookups, and updates in average-case **O(1)** time.
- Express intent more clearly than searching sequentially through a list.

## How it works
Under the hood, a HashMap relies on an array and a "hash function." When you add a key-value pair, the hash function takes the key and translates it into a fixed-size integer (the hash code). This integer determines the memory bucket (or slot) where the entry should be stored.

Without a HashMap, searching by name would require checking contacts one by one until the correct entry is found. A HashMap avoids that sequential search by computing the bucket directly from the key.

With a HashMap, the program just needs to receive the name of the person whose's name is being searched. The program passes the person's name through a hash-function, which returns the right index where the number is located, without needing to go through every element in the list.

A common challenge on most HashMap implementations is what to do when two keys produce the same hash code (a collision). Modern hash tables employ collision-resolution strategies such as chaining or open addressing. Understanding collision-resolution strategies isn't necessary to use Python dictionaries effectively, but it's an interesting implementation detail to study later.
## Python implementation

A HashMap is an abstract data structure. Different programming languages provide different implementations of the same idea. In Python, the built-in [`dict`](https://docs.python.org/3/tutorial/datastructures.html) is implemented using a hash table. 

- storing a value with some key
- extracting the value given the key
- deleting a key:value pair

Let's check at these operations with more detail: 

### Creating dictionaries
An empty dictionary can be created with the `dict()` constructor or by assingment using a pair of curly braces `{}`. 

```python
my_dict = dict()
my_dict = {}
```

Key-value pairs inside a dictionary are read from left to right, separated by colons (`key:value`). A key value pairs can be declared during the dictionary initialization:

```python
## This creates a dictionary my_order with the keys "drink", "main", and "dessert", and their respective values
my_order: dict = {
	"main" : "Tomato Soup",
	"dessert": "Brownie",
	"drink": "Apple's Juice"
}
```

The dict() constructor can build dictionaries from sequences of key-value pairs:

```python
## this is equivalent to the snippet above
my_order = dict([("main", "Tomato Soup"), ("dessert", "Brownie"), ("drink", "Apple's Juice")])
```

It is worth noting that `{}` is evaluated by the Python interpreter as a literal, which is noticeably faster than `dict()`, which requires a function call and name resolution.

### Inserting and updating values
After initialization, key-value pairs further inserted using the assignment operator over a key property, or using the `update()` method. 

```python
# This creates a new key value pair using the assignment operatior
my_order["side"] = "Garlic Bread"

# This uses the `update()` method to create a new key value pair
my_order.update({"utensils": "yes"})
```

Inserting a value to a key that has an assigned value mutates the 'state' of the property, overriding the previous value associated to the same key.

```python
# Inserting a "size property"
my_order.update({"size": "Medium"})

# Updating  the "size" value
my_order["size"] = "Large"
```


### Retrieving values
Values from a dictionary `d` can be extracted by its key with the syntax `d[key]` or through the `get()` method. Extracting a value for a non-existent with `d[key]` raises a [`KeyError`](https://docs.python.org/3/library/exceptions.html#KeyError "KeyError"), while the same instance using `get()` will return `None`. 

```python
print(my_order["drink"])
# Apple's Juice

print(my_order.get("dessert"))
# Brownie

print(my_order.get("appetizer"))
# None

print(my_order["appetizer"])
# KeyError: 'appetizer'
```

### Removing values
To delete a key-value pair from a Python dictionary, you can use the `del` keyword or the `pop()` method. The pop methods allows passing a second optional argument as fallback that will be thrown if the key isn't found.

```python
del my_order["utensils"] # Raises KeyError if key is missing

my_order.pop("dessert", None) # Returns `None` if key is missing 
```

***Additional Methods***:
- **`.popitem()`**: Removes and returns the **last inserted** key-value pair as a tuple `(key, value)`.
- **`.clear()`**: Removes **all** key-value pairs, leaving the dictionary empty.

### Membership tests
Performing `list(d)` returns a list of all available dictionary keys in insertion order. The `sorted(d)` function returns the sorted list.

```python
list(my_order)
# ['main', 'drink', 'side', 'size']

sorted(my_order)
# ['drink', 'main', 'side', 'size']
```

To check whether a single key is in the dictionary, use the `in` keyword. 

```python
if "drink" in my_order:
	print("Cheers!")
# Cheers!
```

### Dictionary Comprehensions

Dictionary comprehensions can be used to create dictionaries from arbitrary key and value expressions:

```python
my_dict = {x: x**2 for x in (2, 4, 6)}
print(my_dict)
# {2: 4, 4: 16, 6: 36}
```

### Looping Techniques
Using the a dictionary as iterator behaves similar to our list examples above, returning a list of keys on every `next()` call. 

```python
inventory = {
    "apple": 10,
    "banana": 5,
    "orange": 8,
}

for fruit in inventory:
	print(fruit)
# apple
# banana
# orange
```

You can also explicitly iterate over the list of keys using the `keys()` method.

```python
for fruit in inventory.keys():
	print(fruit)
```

The `values()` method allow iterating over the values instead:

```python
for quantity in inventory.values():
	print(quantity)
# 10
# 5
# 8
```

Of course, when needed, you can always access through both the value and the keys by using the `items()` method along with tuple unpacking:

```python
for fruit, quantity in inventory.items():
	print(f"Today we have {quantity} {fruit}s.")

# Today we have 10 apples
# Today we have 5 bananas
# Today we have 8 oranges	
```

When looping through a sequence, the position index and corresponding value can be retrieved at the same time using the [`enumerate()`](../python/enumerate.md) function.

```python
for i, (fruit, quantity) in enumerate(inventory.items(), start=1):
	print(f"{i} - {fruit}: {quantity}")
	
# 1 - apple: 10
# 2 - banana: 5
# 3 - orange: 8
```

To loop over two or more sequences at the same time, the entries can be paired with the `zip()` function.

```python
average_weights: list = [150, 120, 150]

for weight, fruit in zip(average_weights, inventory):
	print(f"A {fruit} weights {weight} on average.")
	
# A apple weights 150 on average.
# A banana weights 120 on average.
# A orange weights 150 on average.
```

This example uses `zip()` along with `items()`

```python

for weight, (fruit, quantity) in zip(average_weights, inventory.items()):
	print(f"The {fruit}s weight: {weight * quantity} g.")
	
# The apples weight: 1500g.
# The bananas weight: 600g.
# The oranges weight: 1200g.
```

## When should I use a dictionary(a HashMap)?

Choose a dictionary whenever your problem is naturally expressed as:

- "Given this key, find its value."
- "Have I already seen this value?"
- "Associate an identifier with some information."

Examples include:

- phone contacts
- user IDs
- caches
- counting frequencies
- the Two Sum problem

## The One Principle to Remember

Lists organize data by **position**.

HashMaps organize data by **identity**.

Whenever your question begins with:

> *"Do I already know something about this key?"*

a dictionary is often the right data structure.
