#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
マリグナンス（ID: 3118）を起点とした深さ3ルールの完全網羅的実装

厳密な深さ3ルール:
- Level 0: マリグナンス(3118) 
- Level 1: マリグナンスの直接素材(3802, 1026)
- Level 2: Level 1アイテムの素材 + Level 1アイテムの合成先
- Level 3: Level 2アイテムの素材 + Level 2アイテムの合成先

パッチ15.13.1の公式データを使用し、網羅性を最優先とする。
"""

import json
from collections import defaultdict, deque

def load_data():
    """アイテムデータを読み込む"""
    with open('full_graph_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def build_relationships(data):
    """
    アイテム関係性の双方向グラフを構築
    
    Returns:
        materials_graph: item_id -> [material_ids] (何から作られるか)
        crafts_graph: item_id -> [craft_ids] (何を作るか)
        node_dict: item_id -> node_data
    """
    materials_graph = defaultdict(list)  # target -> [sources] (素材リスト)
    crafts_graph = defaultdict(list)     # source -> [targets] (合成先リスト)
    node_dict = {}
    
    # ノードの辞書化
    for node in data['nodes']:
        node_dict[node['itemId']] = node
    
    # エッジの処理
    for edge in data['edges']:
        source = edge['source']
        target = edge['target']
        
        # source は target の素材
        materials_graph[target].append(source)
        # source から target が作れる  
        crafts_graph[source].append(target)
    
    return materials_graph, crafts_graph, node_dict

def get_depth3_items(start_item, materials_graph, crafts_graph, node_dict):
    """
    深さ3ルールに基づく完全網羅的アイテム収集
    
    Args:
        start_item: 起点アイテムID (3118)
        materials_graph: 素材関係グラフ  
        crafts_graph: 合成関係グラフ
        node_dict: アイテムデータ辞書
        
    Returns:
        dict: レベル別アイテムリスト
    """
    
    # 結果格納
    levels = {
        0: set([start_item]),  # Level 0: マリグナンス
        1: set(),              # Level 1: 直接素材
        2: set(),              # Level 2: Level1の素材・合成先
        3: set()               # Level 3: Level2の素材・合成先
    }
    
    print(f"=== 深さ3分析開始: {node_dict[start_item]['label']} (ID: {start_item}) ===\n")
    
    # Level 1: マリグナンスの直接素材
    level1_materials = materials_graph[start_item]
    levels[1].update(level1_materials)
    
    print(f"Level 1 (マリグナンスの直接素材): {len(level1_materials)}個")
    for item_id in level1_materials:
        item = node_dict[item_id]
        print(f"  - {item['label']} (ID: {item_id}, {item['category']})")
    print()
    
    # Level 2: Level 1の素材・合成先を収集
    print("Level 2 分析:")
    for level1_item in levels[1]:
        item_name = node_dict[level1_item]['label']
        
        # Level 1アイテムの素材
        materials = materials_graph[level1_item]
        levels[2].update(materials)
        print(f"  {item_name}の素材: {len(materials)}個 - {[node_dict[m]['label'] for m in materials]}")
        
        # Level 1アイテムの合成先
        crafts = crafts_graph[level1_item]
        levels[2].update(crafts)
        print(f"  {item_name}の合成先: {len(crafts)}個 - {[node_dict[c]['label'] for c in crafts]}")
    
    print(f"\nLevel 2 合計: {len(levels[2])}個")
    for item_id in sorted(levels[2]):
        item = node_dict[item_id]
        print(f"  - {item['label']} (ID: {item_id}, {item['category']})")
    print()
    
    # Level 3: Level 2の素材・合成先を収集
    print("Level 3 分析:")
    for level2_item in levels[2]:
        item_name = node_dict[level2_item]['label']
        
        # Level 2アイテムの素材
        materials = materials_graph[level2_item]
        levels[3].update(materials)
        print(f"  {item_name}の素材: {len(materials)}個 - {[node_dict[m]['label'] for m in materials]}")
        
        # Level 2アイテムの合成先
        crafts = crafts_graph[level2_item]
        levels[3].update(crafts)
        print(f"  {item_name}の合成先: {len(crafts)}個 - {[node_dict[c]['label'] for c in crafts]}")
    
    print(f"\nLevel 3 合計: {len(levels[3])}個")
    for item_id in sorted(levels[3]):
        item = node_dict[item_id]
        print(f"  - {item['label']} (ID: {item_id}, {item['category']})")
    print()
    
    return levels

def create_d3_data(levels, node_dict, materials_graph, crafts_graph):
    """
    D3.js用のノードとリンクを生成
    
    Args:
        levels: レベル別アイテム辞書
        node_dict: アイテムデータ辞書 
        materials_graph: 素材関係グラフ
        crafts_graph: 合成関係グラフ
        
    Returns:
        dict: D3.js用データ (nodes, links)
    """
    
    # 全アイテムの集合
    all_items = set()
    for level_items in levels.values():
        all_items.update(level_items)
    
    # ノード生成
    nodes = []
    for level, items in levels.items():
        for item_id in sorted(items):
            item = node_dict[item_id]
            
            # レベル別のタイプ設定
            if level == 0:
                node_type = "target"
            elif level == 1:
                node_type = "direct_material"
            elif level == 2:
                node_type = "level2"
            else:  # level == 3
                node_type = "level3"
            
            node = {
                "itemId": item_id,
                "label": item['label'],
                "level": level,
                "type": node_type,
                "category": item['category'],
                "price": item.get('price', 0),
                "stats": item.get('stats', {}),
                "description": item.get('description', '')
            }
            nodes.append(node)
    
    # リンク生成（包含されるアイテム間のみ）
    links = []
    for item_id in all_items:
        # 素材リンク
        for material_id in materials_graph[item_id]:
            if material_id in all_items:
                links.append({
                    "source": material_id,
                    "target": item_id,
                    "type": "crafts-into"
                })
    
    return {
        "nodes": nodes,
        "links": links
    }

def analyze_statistics(levels, node_dict):
    """統計分析とサマリー出力"""
    
    print("=== 統計分析 ===")
    
    total_nodes = sum(len(items) for items in levels.values())
    print(f"総ノード数: {total_nodes}")
    
    for level, items in levels.items():
        print(f"Level {level}: {len(items)}個")
    
    # カテゴリ別集計
    category_counts = defaultdict(int)
    for level_items in levels.values():
        for item_id in level_items:
            category = node_dict[item_id]['category']
            category_counts[category] += 1
    
    print(f"\nカテゴリ別内訳:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}個")
    
    # 価格帯分析
    all_items = set()
    for level_items in levels.values():
        all_items.update(level_items)
    
    prices = [node_dict[item_id].get('price', 0) for item_id in all_items]
    prices = [p for p in prices if p > 0]
    
    if prices:
        print(f"\n価格統計:")
        print(f"  最低価格: {min(prices)}G")
        print(f"  最高価格: {max(prices)}G")
        print(f"  平均価格: {sum(prices)/len(prices):.1f}G")

def main():
    """メイン処理"""
    print("マリグナンス深さ3分析を開始します...\n")
    
    # データ読み込み
    data = load_data()
    materials_graph, crafts_graph, node_dict = build_relationships(data)
    
    # マリグナンスの存在確認
    start_item = "3118"
    if start_item not in node_dict:
        print(f"エラー: マリグナンス (ID: {start_item}) がデータに存在しません")
        return
    
    # 深さ3分析実行
    levels = get_depth3_items(start_item, materials_graph, crafts_graph, node_dict)
    
    # D3.js用データ生成
    d3_data = create_d3_data(levels, node_dict, materials_graph, crafts_graph)
    
    # 結果出力
    output_file = "malignance_depth3_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(d3_data, f, ensure_ascii=False, indent=2)
    
    print(f"=== 結果出力 ===")
    print(f"ファイル出力: {output_file}")
    print(f"総ノード数: {len(d3_data['nodes'])}")
    print(f"総リンク数: {len(d3_data['links'])}")
    
    # 統計分析
    analyze_statistics(levels, node_dict)
    
    print(f"\n=== 深さ3分析完了 ===")

if __name__ == "__main__":
    main()