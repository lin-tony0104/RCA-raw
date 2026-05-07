import json
from pathlib import Path

# ==================== 需要改的部分 =================
exp = "005_wiki_RCA2_aging" #資料夾前綴

#Json內容
def get_json_content(seg):
    return{
  "basic_config":{
    "policy":"RCA2_aging",
    "trace":f"seg_wiki/wiki_seg{seg}"
  },
  
  "policy_config":{
      "cache_size":3811783475,
      "region_size":1000,
      "alpha":0.9
  },
  
  "evaluator_config":{
      "region":100,
      "warmup":1000000,
      "verbose":True
  }
}
# ========== 需要改的部分 =================




# 3. 執行生成邏輯
for i in range(10):
    # 建立目錄物件
    exp_path = Path(f"{exp}_seg{i}")
    result_path = Path(f"{exp}_seg{i}/result")

    # 建立目錄 (exist_ok=True 表示如果資料夾已存在，不會報錯)
    exp_path.mkdir(parents=True, exist_ok=True)
    result_path.mkdir(parents=True, exist_ok=True)

    # 定義 JSON 檔案路徑
    json_path = exp_path / "config.json"
    
    # 將資料寫入 JSON 檔案
    with open(json_path, "w", encoding="utf-8") as f:
        # indent=4 讓產出的 JSON 檔案易於閱讀
        json.dump(get_json_content(i), f, indent=4, ensure_ascii=False)

    
print(f"{exp} JSON files generated successfully.")
