#!/usr/bin/env python3
"""
グループベースの総当たり最適化で真の最適解を発見
"""

import json
import math
from itertools import permutations
import time

# データ読み込み
with open('static/full_graph_data.json', 'r') as f:
    data = json.load(f)

# 素材アイテムを抽出
basic_items = [n for n in data['nodes'] if n['category'] == 'basic']
basic_ids = {n['id'] for n in basic_items}

print(f'素材アイテム数: {len(basic_items)}')

# グループ分け
groups = {
    'AP': ['1026', '1052', '1058', '1027', '1004', '3070'],  # 6個
    'AD': ['1036', '1037', '1038', '1042', '1018'],          # 5個
    'Tank': ['1028', '1029', '1033', '1006'],                # 4個
    'Other': ['2022']                                         # 1個（固定）
}

print("\nグループ分け:")
for group_name, item_ids in groups.items():
    print(f"{group_name}グループ ({len(item_ids)}個):")
    for item_id in item_ids:
        item_name = next(n['label'] for n in basic_items if n['id'] == item_id)
        print(f"  {item_name} (ID: {item_id})")

# 接続関係の構築
connections = {}
for item in basic_items:
    connections[item['id']] = set()

for edge in data['edges']:
    if edge['source'] in basic_ids:
        target_id = edge['target']
        for edge2 in data['edges']:
            if edge2['target'] == target_id and edge2['source'] != edge['source'] and edge2['source'] in basic_ids:
                connections[edge['source']].add(edge2['source'])
                connections[edge2['source']].add(edge['source'])

def calculate_polygon_distance(pos1, pos2, n):
    """正n角形上の2点間の最短距離を計算"""
    diff = abs(pos1 - pos2)
    return min(diff, n - diff)

def calculate_total_edge_length(arrangement, connections):
    """配置における辺の長さの総和を計算"""
    n = len(arrangement)
    total_length = 0
    
    position = {item_id: i for i, item_id in enumerate(arrangement)}
    
    for item_id, connected_items in connections.items():
        if item_id in position:
            pos1 = position[item_id]
            for connected_id in connected_items:
                if connected_id in position:
                    pos2 = position[connected_id]
                    distance = calculate_polygon_distance(pos1, pos2, n)
                    total_length += distance
    
    return total_length // 2

def generate_all_arrangements(groups):
    """グループベースの全配置を生成（グループ順序固定で計算量削減）"""
    ap_perms = list(permutations(groups['AP']))
    ad_perms = list(permutations(groups['AD']))
    tank_perms = list(permutations(groups['Tank']))
    other_items = groups['Other']
    
    print(f"\n計算量:")
    print(f"AP: {len(ap_perms)}通り")
    print(f"AD: {len(ad_perms)}通り")
    print(f"Tank: {len(tank_perms)}通り")
    print(f"Other: {len(other_items)}通り")
    print(f"総計: {len(ap_perms) * len(ad_perms) * len(tank_perms) * len(other_items):,}通り")
    
    arrangements = []
    
    # グループ順序を固定（AP → AD → Tank → Other）
    for ap_perm in ap_perms:
        for ad_perm in ad_perms:
            for tank_perm in tank_perms:
                arrangement = []
                arrangement.extend(ap_perm)
                arrangement.extend(ad_perm)
                arrangement.extend(tank_perm)
                arrangement.extend(other_items)
                arrangements.append(arrangement)
    
    return arrangements

def find_optimal_arrangement():
    """総当たりで最適配置を発見"""
    print("\n=== 総当たり最適化開始 ===")
    start_time = time.time()
    
    arrangements = generate_all_arrangements(groups)
    total_arrangements = len(arrangements)
    
    print(f"総配置数: {total_arrangements:,}")
    
    best_arrangement = None
    best_score = float('inf')
    
    for i, arrangement in enumerate(arrangements):
        score = calculate_total_edge_length(arrangement, connections)
        
        if score < best_score:
            best_score = score
            best_arrangement = arrangement
        
        # 進捗表示
        if (i + 1) % 100000 == 0:
            elapsed = time.time() - start_time
            progress = (i + 1) / total_arrangements * 100
            print(f"進捗: {progress:.1f}% ({i+1:,}/{total_arrangements:,}) - "
                  f"現在のベスト: {best_score} - 経過時間: {elapsed:.1f}秒")
    
    end_time = time.time()
    print(f"\n=== 最適化完了 ===")
    print(f"実行時間: {end_time - start_time:.1f}秒")
    print(f"検索した配置数: {total_arrangements:,}")
    
    return best_arrangement, best_score

# 現在の配置を評価
current_order = [
    "1037", "1026", "1004", "1052", "2022", "1027", "1028",
    "1029", "1033", "1006", "1058", "1036", "1042", "3070",
    "1018", "4638", "1038"
]

# ウォッチフルワードストーンを除外
current_order_filtered = [item_id for item_id in current_order if item_id != '4638']

current_score = calculate_total_edge_length(current_order_filtered, connections)
print(f"\n現在の配置の辺長総和: {current_score}")

# 最適化実行
optimal_arrangement, optimal_score = find_optimal_arrangement()

print(f"\n=== 最適化結果 ===")
print(f"現在の配置: {current_score}")
print(f"最適配置: {optimal_score}")
print(f"改善率: {(current_score - optimal_score) / current_score * 100:.1f}%")

print(f"\n最適配置順（正16角形の頂点順）:")
item_map = {item['id']: item['label'] for item in basic_items}
for i, item_id in enumerate(optimal_arrangement):
    print(f'{i+1}. {item_map[item_id]} (ID: {item_id})')

# JavaScript用の配列を出力
print(f'\n=== JavaScript用配列 ===')
js_array = str(optimal_arrangement).replace("'", '"')
print(f'const optimalBasicOrder = {js_array};')

# グループごとの配置を確認
print(f'\n=== グループごとの配置確認 ===')
for i, item_id in enumerate(optimal_arrangement):
    item_name = item_map[item_id]
    group = None
    for group_name, item_ids in groups.items():
        if item_id in item_ids:
            group = group_name
            break
    print(f'{i+1}. {item_name} ({group}グループ)')