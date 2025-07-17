#!/usr/bin/env python3
"""
正多角形上での辺の長さ総和を最小化する最適配置を計算
"""

import json
import math
from itertools import permutations
import random

# データ読み込み
with open('static/full_graph_data.json', 'r') as f:
    data = json.load(f)

# 素材アイテムを抽出
basic_items = [n for n in data['nodes'] if n['category'] == 'basic']
basic_ids = {n['id'] for n in basic_items}

print(f'素材アイテム数: {len(basic_items)}')

# 素材アイテム間の接続関係を構築
connections = {}
for item in basic_items:
    connections[item['id']] = set()

# 各素材アイテムが使われる先を記録
for edge in data['edges']:
    if edge['source'] in basic_ids:
        target_id = edge['target']
        # targetアイテムの他の素材を探す
        for edge2 in data['edges']:
            if edge2['target'] == target_id and edge2['source'] != edge['source'] and edge2['source'] in basic_ids:
                connections[edge['source']].add(edge2['source'])
                connections[edge2['source']].add(edge['source'])

print(f'接続関係を構築完了')

def calculate_polygon_distance(pos1, pos2, n):
    """正n角形上の2点間の最短距離を計算"""
    diff = abs(pos1 - pos2)
    return min(diff, n - diff)

def calculate_total_edge_length(arrangement, connections):
    """配置における辺の長さの総和を計算"""
    n = len(arrangement)
    total_length = 0
    
    # 各アイテムの位置を記録
    position = {item_id: i for i, item_id in enumerate(arrangement)}
    
    # 全ての接続について距離を計算
    for item_id, connected_items in connections.items():
        if item_id in position:
            pos1 = position[item_id]
            for connected_id in connected_items:
                if connected_id in position:
                    pos2 = position[connected_id]
                    distance = calculate_polygon_distance(pos1, pos2, n)
                    total_length += distance
    
    return total_length // 2  # 重複を除去

def greedy_optimization(basic_items, connections):
    """グリーディアルゴリズムで最適配置を探索"""
    n = len(basic_items)
    best_arrangement = None
    best_score = float('inf')
    
    # 複数の開始点で試行
    for start_item in basic_items:
        arrangement = [start_item['id']]
        remaining = [item for item in basic_items if item['id'] != start_item['id']]
        
        while remaining:
            best_next = None
            best_next_score = float('inf')
            
            for candidate in remaining:
                # 試行配置でのスコアを計算
                temp_arrangement = arrangement + [candidate['id']]
                score = calculate_total_edge_length(temp_arrangement, connections)
                
                if score < best_next_score:
                    best_next_score = score
                    best_next = candidate
            
            arrangement.append(best_next['id'])
            remaining.remove(best_next)
        
        final_score = calculate_total_edge_length(arrangement, connections)
        if final_score < best_score:
            best_score = final_score
            best_arrangement = arrangement
    
    return best_arrangement, best_score

def simulated_annealing(basic_items, connections, iterations=1000):
    """シミュレーテッドアニーリングで最適化"""
    current = [item['id'] for item in basic_items]
    random.shuffle(current)
    current_score = calculate_total_edge_length(current, connections)
    
    best = current.copy()
    best_score = current_score
    
    temperature = 100.0
    cooling_rate = 0.995
    
    for iteration in range(iterations):
        # 隣接する2つの要素を交換
        new_arrangement = current.copy()
        i, j = random.sample(range(len(new_arrangement)), 2)
        new_arrangement[i], new_arrangement[j] = new_arrangement[j], new_arrangement[i]
        
        new_score = calculate_total_edge_length(new_arrangement, connections)
        
        # 受け入れ判定
        if new_score < current_score or random.random() < math.exp((current_score - new_score) / temperature):
            current = new_arrangement
            current_score = new_score
            
            if new_score < best_score:
                best = new_arrangement.copy()
                best_score = new_score
        
        temperature *= cooling_rate
        
        if iteration % 100 == 0:
            print(f'Iteration {iteration}: Best score = {best_score}')
    
    return best, best_score

# 現在の配置を評価
current_order = [
    '1036', '1018', '1037', '1038', '1028', '2022', '1052',
    '1027', '1029', '1033', '1004', '1042', '1006', '1026',
    '3070', '1058', '4638'
]

current_score = calculate_total_edge_length(current_order, connections)
print(f'\n現在の配置の辺長総和: {current_score}')

# グリーディ最適化
print('\n=== グリーディ最適化 ===')
greedy_arrangement, greedy_score = greedy_optimization(basic_items, connections)
print(f'グリーディ最適化後の辺長総和: {greedy_score}')

# シミュレーテッドアニーリング
print('\n=== シミュレーテッドアニーリング ===')
sa_arrangement, sa_score = simulated_annealing(basic_items, connections)
print(f'シミュレーテッドアニーリング後の辺長総和: {sa_score}')

# 最適な配置を選択
best_arrangement = sa_arrangement if sa_score < greedy_score else greedy_arrangement
best_score = min(sa_score, greedy_score)

print(f'\n=== 最適配置結果 ===')
print(f'改善前: {current_score}')
print(f'改善後: {best_score}')
print(f'改善率: {(current_score - best_score) / current_score * 100:.1f}%')

print(f'\n最適配置順（正多角形の頂点順）:')
item_map = {item['id']: item['label'] for item in basic_items}
for i, item_id in enumerate(best_arrangement):
    print(f'{i+1}. {item_map[item_id]} (ID: {item_id})')

# JavaScript用の配列を出力
print(f'\n=== JavaScript用配列 ===')
js_array = str(best_arrangement).replace("'", '"')
print(f'const optimalBasicOrder = {js_array};')