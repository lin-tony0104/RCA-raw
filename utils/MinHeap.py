class MinHeap:
    def __init__(self):
        self.heap = []
        self.index_dict = {}  # 物件 -> index

    def insert(self, val):
        self.heap.append(val)
        i = len(self.heap) - 1
        self.index_dict[val] = i
        self._bubble_up(i)

    def pop_min(self):
        if not self.heap:
            raise IndexError("Heap is empty")
        if len(self.heap) == 1:
            val = self.heap.pop()
            del self.index_dict[val]
            return val

        min_val = self.heap[0]
        last_val = self.heap.pop()
        self.heap[0] = last_val
        self.index_dict[last_val] = 0
        del self.index_dict[min_val]
        self._trickle_down(0)
        return min_val
    

    # by GPT
    #index_dict直接用val當key時 會錯 但在用o_id當作key時不會   
    def heapify(self):
        """
        arr: list of objects (already in heap array form)
        時間複雜度: O(n)
        """
        #確保 index_dict 正確
        self.index_dict.clear()
        for idx, val in enumerate(self.heap):
            self.index_dict[val] = idx
        # 從最後一個非葉節點開始
        n = len(self.heap)
        for i in range((n // 2) - 1, -1, -1):
            self._trickle_down(i)



    def _bubble_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.heap[i] < self.heap[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _trickle_down(self, i):
        size = len(self.heap)
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            smallest = i
            if left < size and self.heap[left] < self.heap[smallest]:
                smallest = left
            if right < size and self.heap[right] < self.heap[smallest]:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.index_dict[self.heap[i]] = i
        self.index_dict[self.heap[j]] = j


# by GPT
def is_valid_minheap(heap):
    n = len(heap)
    for i in range(n):
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and heap[i] > heap[left]:
            return False
        if right < n and heap[i] > heap[right]:
            return False
    return True


if __name__ == "__main__":
    h = MinHeap()

    #測試 insert
    h.insert(5)
    h.insert(3)
    h.insert(8)
    h.insert(1)
    assert h.heap == [1,3,8,5]

    #測試 index_dict
    assert h.index_dict[1] == 0
    assert h.index_dict[3] == 1
    assert h.index_dict[8] == 2
    assert h.index_dict[5] == 3
   
    #測試 pop_min
    assert h.pop_min() == 1
    assert h.pop_min() == 3
    assert h.heap == [5, 8] or h.heap == [8, 5]  # 根據 swap 結果可能不同順序
    assert set(h.index_dict.keys()) == {5, 8} 

    #測試 空heap報錯
    h=MinHeap()
    try:
        h.pop_min()
    except IndexError as e:
        assert str(e) == "Heap is empty"

    #測試 heapify
    h=MinHeap()    
    h.insert(1)
    h.insert(2)
    h.insert(3)
    h.insert(4)
    print(h.heap)
    print("dict_key: ", 2 , " val:",  h.index_dict[2]) # heapify的dict_index會出錯 ， 但在key是o_id 且修改的是o_val 時不會錯。


    h.heap = [4,3,2,1]
    print(h.heap)
    h.heapify()
    assert is_valid_minheap(h.heap)
    print(h.heap)

    print("dict_key: ", 2, " val:",  h.index_dict[2]) # heapify的dict_index會出錯 ， 但在key是o_id 且修改的是o_val 時不會錯。


    print("all pass")
