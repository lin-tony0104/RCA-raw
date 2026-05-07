class Node():
    def __init__(self,val):
        self.val=val
        self.prev=None
        self.nxt=None
"""
head,prev,left ==================== tail,nxt,right
"""
class deque():
    def __init__(self):
        self.head=None
        self.tail=None
    def pop_left(self): #pop head
        if not self.head:
            raise IndexError("pop from empty deque")
        
        val=self.head.val
        self.head=self.head.nxt
        if self.head:
            self.head.prev=None
        else:
            self.tail=None
        return val

    def pop_right(self): #pop tail
        if not self.tail:
            raise IndexError("pop from empty deque")
        
        val=self.tail.val
        self.tail=self.tail.prev
        if self.tail:
            self.tail.nxt=None
        else:
            self.head=None
        return val

    def insert_left(self,val):# insert head
        node=Node(val)
        if not self.head:
            self.head=self.tail=node
        else:
            node.nxt=self.head
            self.head.prev=node
            self.head=node

    def insert_right(self,val):
        node=Node(val)
        if not self.tail:
            self.head=self.tail=node
        else:
            node.prev=self.tail
            self.tail.nxt=node
            self.tail=node
            
if __name__ == "__main__":
    d=deque()

    #left : insert,pop
    d.insert_left(1)
    d.insert_left(2)  # 順序應為 2, 1
    assert d.pop_left() == 2
    assert d.pop_left() == 1

    # right : insert,pop
    d.insert_right(3)
    d.insert_right(4)  # 順序應為 3, 4
    assert d.pop_right() == 4
    assert d.pop_right() == 3
    
    # mix : insert,pop
    d.insert_left(5)
    d.insert_right(6)
    d.insert_left(7)  # 順序應為 7, 5, 6
    assert d.pop_left() == 7
    assert d.pop_right() == 6
    assert d.pop_left() == 5

    #測是否會報錯
    try:
        d.pop_left()
    except IndexError as e:
        assert str(e) == "pop from empty deque"

    try:
        d.pop_right()
    except IndexError as e:
        assert str(e) == "pop from empty deque"

    print("all pass")