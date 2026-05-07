import torch
from emb_init_random import rand_embedding
from emb_init_sobol import sobal_embedding





def check_orthogonality_2(embeddings):
    # 確保輸入在正確的設備上 (例如 GPU)
    device = embeddings.device 
    num_pairs=1000000
    # 獲取嵌入向量的數量 N 和維度 D
    num_embeddings, emb_dim = embeddings.shape

    i = torch.randint(0, num_embeddings, (num_pairs,))
    j = torch.randint(0, num_embeddings, (num_pairs,))
    mask = i != j
    i, j = i[mask], j[mask]

    inner_products_list = torch.sum(embeddings[i] * embeddings[j], dim=1)

    avg_Inner_prod = round((inner_products_list.abs().mean().item()), 2)
    max_Inner_prod = round((inner_products_list.abs().max().item()), 2)

    return inner_products_list, avg_Inner_prod, max_Inner_prod





def check_orthogonality(embeddings):
    # 確保輸入在正確的設備上 (例如 GPU)
    device = embeddings.device 
    
    # 獲取嵌入向量的數量 N 和維度 D
    num_embeddings, emb_dim = embeddings.shape

    # 1. 計算所有向量對的內積矩陣 (N x N 的矩陣)
    # 大部分運算都在 GPU 上平行執行
    inner_products_matrix = torch.matmul(embeddings, embeddings.t())
    
    # 2. 提取對角線以下的內積值（排除自己與自己的乘積）
    # 使用 torch.tril_indices 獲取索引
    # offset=-1 表示排除主對角線
    # 將索引創建在與 embeddings 相同的 device 上
    lower_triangle_indices = torch.tril_indices(
        row=num_embeddings, 
        col=num_embeddings, 
        offset=-1, 
        device=device
    )
    
    # 使用索引從矩陣中選取所有內積值
    inner_products_list = inner_products_matrix[
        lower_triangle_indices[0], 
        lower_triangle_indices[1]
    ]
    
    # 3. 計算平均值和最大值
    # 此處使用 .item() 將結果移回 CPU 進行最終報告
    avg_Inner_prod = round((inner_products_list.abs().mean().item()), 2)
    max_Inner_prod = round((inner_products_list.abs().max().item()), 2)

    return inner_products_list, avg_Inner_prod, max_Inner_prod



if __name__=="__main__":
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("GPU is available. Using CUDA device.")
    else:
        device = torch.device("cpu")
        print("GPU not available. Using CPU device.")
    
    # 100000
    num_id, emb_dim = 1000, 128
    # num_id, emb_dim = 1000000, 128

    rand = rand_embedding(num_id,emb_dim)
    sobal = sobal_embedding(num_id,emb_dim)

    nums=torch.arange(0,num_id, dtype= torch.int)

    rand_emb_num = rand(nums)
    sobal_emb_num = sobal(nums)

    # rand_list, rand_avg, rand_max= check_orthogonality(rand_emb_num)
    # sobal_list, sobal_avg, sobal_max= check_orthogonality(sobal_emb_num)
    rand_list, rand_avg, rand_max= check_orthogonality_2(rand_emb_num)
    sobal_list, sobal_avg, sobal_max= check_orthogonality_2(sobal_emb_num)



    print(f"rand_emb:")
    print(f"avg_abs_Inner_prodr: {rand_avg} max_abs_Inner_prodr: {rand_max}")
    print(f"sobal_emb:")
    print(f"avg_abs_Inner_prodr: {sobal_avg} max_abs_Inner_prodr: {sobal_max}")