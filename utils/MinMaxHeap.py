class MinMaxHeap:
    """
    0-indexed 
    0th level is min level

    支援操作 insert, pop_min, pop_max
    """
    
    def __init__(self):
        self.heap = []
        self.index_dict = {}  # 物件 -> index

    
    def insert(self,val):
        self.heap.append(val)
        self.index_dict[val]=len(self.heap)-1
        self._bubble_up(len(self.heap) - 1)


    def pop_min(self):
        if not self.heap:
            raise IndexError("Heap is empty")

        m=self.heap[0]
        self._swap(0,-1)
        self.heap.pop()
        del self.index_dict[m]
        self._trickle_down_min(0)
        return m

    def pop_max(self):
        if not self.heap:
            raise IndexError("Heap is empty")
        if len(self.heap)==1:
            return self.heap.pop()
        layer1_indexes =self._get_children_indices(0)
        max_index=max(layer1_indexes , key=lambda x: self.heap[x])
        m=self.heap[max_index]
        self._swap(max_index,-1)
        self.heap.pop()
        del self.index_dict[m]
        self._trickle_down_max(max_index)
        return m




    def _bubble_up(self, i):
        parent=self._get_parent_index(i)
        if parent is None:
            return
        
        if self._is_min_level(i):
            if self.heap[i]>self.heap[parent]:
                self._swap(i,parent)
                self._bubble_up_max(parent)
            else:
                self._bubble_up_min(i)

        else:
            if self.heap[i]<self.heap[parent]:
                self._swap(i,parent)
                self._bubble_up_min(parent)
            else:
                self._bubble_up_max(i)


    def _bubble_up_min(self, i):
        grandparent=self._get_grandparent_index(i)
        if grandparent is None:
            return
        if self.heap[i]<self.heap[grandparent]:
            self._swap(i,grandparent)
            self._bubble_up_min(grandparent)

    def _bubble_up_max(self, i):
        grandparent=self._get_grandparent_index(i)
        if grandparent is None:
            return
        if self.heap[i]>self.heap[grandparent]:
            self._swap(i,grandparent)
            self._bubble_up_max(grandparent)

    def _trickle_down_min(self,i):
        children=self._get_children_indices(i)
        grandchildren=self._get_grandchildren_indices(i)

        if len(grandchildren)==0:
            if len(children)==0:
                return
        
            min_index=min(children, key=lambda x: self.heap[x])
            if self.heap[min_index]<self.heap[i]:
                self._swap(i, min_index)
            return
        else:
            min_index=min(grandchildren, key=lambda x: self.heap[x])
            if self.heap[min_index]<self.heap[i]:
                self._swap(i, min_index)
                
                #交換後檢查父子關係
                curr_parrent=self._get_parent_index(min_index)
                if self.heap[min_index]>self.heap[curr_parrent]:
                    self._swap(curr_parrent, min_index)
                self._trickle_down_min(min_index)

    def _trickle_down_max(self,i):
        children=self._get_children_indices(i)
        grandchildren=self._get_grandchildren_indices(i)

        if len(grandchildren)==0:
            if len(children)==0:
                return
            
            max_index=max(children, key=lambda x: self.heap[x])
            if self.heap[max_index]>self.heap[i]:
                self._swap(i, max_index)
            return 
        else:
            max_index=max(grandchildren, key=lambda x: self.heap[x])
            if self.heap[max_index] > self.heap[i]:
                self._swap(i, max_index)
                
                #交換後檢查父子關係
                curr_parrent=self._get_parent_index(max_index)
                if self.heap[max_index] < self.heap[curr_parrent]:
                    self._swap(curr_parrent,max_index)
                self._trickle_down_max(max_index)


    def _swap(self, i, j):
        self.heap[i] , self.heap[j] = self.heap[j] , self.heap[i]
        self.index_dict[self.heap[i]]=i
        self.index_dict[self.heap[j]]=j

    def _is_min_level(self, i):
        depth= (i+1).bit_length() - 1
        return depth % 2==0
    def _get_parent_index(self, i):
        return None if i<1 else (i-1)//2
    def _get_grandparent_index(self, i):
        parent=self._get_parent_index(i)
        if parent is not None:
            return self._get_parent_index(parent)
        return None
    def _get_children_indices(self, i):
        indices=[]
        for j in [i*2+1,i*2+2]:
            if j<len(self.heap):
                indices.append(j)
        return indices
    
    def _get_grandchildren_indices(self, i):
        indices=[]
        for j in [i*4+3,i*4+4,i*4+5,i*4+6]:
            if j<len(self.heap):
                indices.append(j)
        return indices







##test
if __name__ == "__main__":
    h = MinMaxHeap()

    h.insert(10)
    h.insert(5)
    h.insert(20)
    h.insert(1)
    h.insert(15)
    h.insert(30)

    #測試pop_min, pop_max
    assert h.pop_min() == 1
    assert h.pop_max() == 30

    # 剩下應該是 5, 10, 15, 20
    remaining = sorted(h.heap)
    assert remaining == [5, 10, 15, 20]

    h.insert(2)
    h.insert(50)
    h.insert(3)
    #測試pop_min, pop_max
    assert h.pop_min() == 2
    assert h.pop_max() == 50

    #測試index_dict[val]
    for val in h.heap:
        assert h.index_dict[val]==h.heap.index(val) #可能隱含相同val卻有兩個index的問題 ，但cache暫時應該是不會碰上 (問題具體是:某些重複的val 可能會因為相同val被pop而找不到index)

    h=MinMaxHeap()
    #測試pop_min是否會報空堆
    try:
        h.pop_min()
    except IndexError as e:
        assert str(e) == "Heap is empty"
    #測試pop_max是否會報空堆
    try:
        h.pop_max()
    except IndexError as e:
        assert str(e) == "Heap is empty"    

    print("pass all")