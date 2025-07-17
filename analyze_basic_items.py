#!/usr/bin/env python3
"""
素材アイテムの最適配置を分析
"""

import json
import numpy as np
from itertools import permutations

# データ読み込み
with open('static/full_graph_data.json', 'r') as f:
    data = json.load(f)

# 素材アイテムを抽出
basic_items = [n for n in data['nodes'] if n['category'] == 'basic']
basic_ids = {n['id'] for n in basic_items}

print(f'素材アイテム数: {len(basic_items)}')
print('\n素材アイテム一覧:')
for item in basic_items:
    print(f'  {item["label"]} (ID: {item["id"]})')

# 素材アイテム間の接続を分析
basic_connections = {}
for item in basic_items:
    basic_connections[item['id']] = set()

# 各素材アイテムが使われる先を記録
for edge in data['edges']:
    if edge['source'] in basic_ids:
        # この素材が使われる先の他の素材を見つける
        target_id = edge['target']
        # targetアイテムの他の素材を探す
        for edge2 in data['edges']:
            if edge2['target'] == target_id and edge2['source'] != edge['source'] and edge2['source'] in basic_ids:
                basic_connections[edge['source']].add(edge2['source'])
                basic_connections[edge2['source']].add(edge['source'])

# 接続数でソート
connection_counts = [(item['id'], item['label'], len(basic_connections[item['id']])) for item in basic_items]
connection_counts.sort(key=lambda x: x[2], reverse=True)

print('\n素材アイテムの接続度（他の素材との共通合成先数）:')
for item_id, item_name, count in connection_counts:
    print(f'  {item_name}: {count}個の他の素材と関連')

# 隣接行列を作成
n = len(basic_items)
item_to_idx = {item['id']: i for i, item in enumerate(basic_items)}
adjacency_matrix = np.zeros((n, n))

for item_id, connections in basic_connections.items():
    i = item_to_idx[item_id]
    for connected_id in connections:
        j = item_to_idx[connected_id]
        adjacency_matrix[i][j] = 1

print(f'\n隣接行列の密度: {np.sum(adjacency_matrix) / (n * n):.3f}')

# 最適配置の提案
print('\n=== 最適配置の提案 ===')
print('正多角形配置での最適化戦略:')
print('1. 最も接続の多い素材を隣接させる')
print('2. グリーディアルゴリズムで配置順を決定')

# グリーディアルゴリズムで配置順を決定
placed = []
remaining = list(basic_items)

# 最も接続の多い素材から開始
start_item = max(remaining, key=lambda x: len(basic_connections[x['id']]))
placed.append(start_item)
remaining.remove(start_item)

# 残りを配置
while remaining:
    # 現在配置済みの最後のアイテムと最も関連の強いものを選ぶ
    last_item = placed[-1]
    last_connections = basic_connections[last_item['id']]
    
    # 残りの中で最も関連の強いものを探す
    best_item = None
    best_score = -1
    
    for item in remaining:
        # このアイテムと配置済みアイテムとの総接続数を計算
        score = 0
        if item['id'] in last_connections:
            score += 10  # 直前のアイテムとの接続を重視
        
        for placed_item in placed:
            if item['id'] in basic_connections[placed_item['id']]:
                score += 1
        
        if score > best_score:
            best_score = score
            best_item = item
    
    if best_item is None:
        best_item = remaining[0]
    
    placed.append(best_item)
    remaining.remove(best_item)

print('\n推奨配置順（正多角形の頂点順）:')
for i, item in enumerate(placed):
    connections_count = len(basic_connections[item['id']])
    print(f'{i+1}. {item["label"]} (接続数: {connections_count})')

# 配置による総エッジ長の推定
print('\n配置効果の推定:')
total_connections = 0
adjacent_connections = 0

for i, item1 in enumerate(placed):
    for j, item2 in enumerate(placed):
        if i < j and item2['id'] in basic_connections[item1['id']]:
            total_connections += 1
            # 隣接チェック（円形配置での隣）
            if abs(i - j) == 1 or (i == 0 and j == len(placed) - 1):
                adjacent_connections += 1

print(f'総接続数: {total_connections}')
print(f'隣接配置できた接続: {adjacent_connections} ({adjacent_connections/max(total_connections,1)*100:.1f}%)')