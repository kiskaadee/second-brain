from typing import Optional, Any
# Definition for singly-linked list (expanded).
class ListNode:
    def __init__(self, val: Any = 0, next=None):
        if next is not None and not isinstance(next, ListNode):
            raise TypeError("`next` must be a linked list or None")
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        next_id = hex(id(self.next)) if self.next else None
        return f"ListNode(id={hex(id(self))}, val={self.val}: {type(self.val)}, next={next_id})"

    def inspect(self):
        current = self
        while current:
            print(current)
            current = current.next


class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode()
        current = dummy

        while list1 and list2:
            if list1.val <= list2.val:
                current.next = list1
                list1 = list1.next
            else:
                current.next = list2
                list2 = list2.next
            current = current.next
        current.next = list1 or list2
        return dummy.next
