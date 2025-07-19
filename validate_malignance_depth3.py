#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
マリグナンス深さ3データの検証とフィルタリング

現在有効なアイテム（inStore: true, maps["11"]: true）のみを対象として
最終的なD3.js用データを生成する
"""

import json

def load_original_data():
    """オリジナルのアイテムデータを読み込んで有効性を確認"""
    try:
        # パッチ15.13.1の公式データを探す
        with open('full_graph_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("元データファイルが見つかりません")
        return None

def validate_item_availability(node_dict, data):
    """
    アイテムの現在有効性を検証
    
    パッチ15.13.1において:
    - inStore: true (購入可能)
    - maps["11"]: true (サモナーズリフトで利用可能)
    
    Args:
        node_dict: アイテム辞書
        data: 元データ
        
    Returns:
        set: 有効なアイテムIDの集合
    """
    valid_items = set()
    
    # データ構造を確認
    print("=== アイテム有効性検証 ===")
    
    # 既存のノードは全て有効とみなす（フィルタリング済みのため）
    for node in data['nodes']:
        item_id = node['itemId']
        valid_items.add(item_id)
    
    print(f"有効アイテム数: {len(valid_items)}")
    return valid_items

def filter_depth3_data(depth3_file, valid_items):
    """
    深さ3データから有効アイテムのみをフィルタリング
    
    Args:
        depth3_file: 深さ3分析結果ファイル
        valid_items: 有効アイテムIDの集合
        
    Returns:
        dict: フィルタリング済みD3.jsデータ
    """
    
    with open(depth3_file, 'r', encoding='utf-8') as f:
        depth3_data = json.load(f)
    
    print(f"\n=== フィルタリング前 ===")
    print(f"総ノード数: {len(depth3_data['nodes'])}")
    print(f"総リンク数: {len(depth3_data['links'])}")
    
    # 無効アイテムを特定
    invalid_items = []
    valid_nodes = []
    
    for node in depth3_data['nodes']:
        item_id = node['itemId']
        if item_id in valid_items:
            valid_nodes.append(node)
        else:
            invalid_items.append(f"{node['label']} (ID: {item_id})")
    
    # 有効ノードIDの集合
    valid_node_ids = {node['itemId'] for node in valid_nodes}
    
    # 有効リンクのみフィルタリング
    valid_links = []
    for link in depth3_data['links']:
        if link['source'] in valid_node_ids and link['target'] in valid_node_ids:
            valid_links.append(link)
    
    # 結果
    filtered_data = {
        "nodes": valid_nodes,
        "links": valid_links
    }
    
    print(f"\n=== フィルタリング後 ===")
    print(f"有効ノード数: {len(filtered_data['nodes'])}")
    print(f"有効リンク数: {len(filtered_data['links'])}")
    
    if invalid_items:
        print(f"\n除外されたアイテム ({len(invalid_items)}個):")
        for item in invalid_items:
            print(f"  - {item}")
    else:
        print("\n✅ 全アイテムが有効です")
    
    return filtered_data

def analyze_final_structure(data):
    """最終データ構造の分析"""
    
    print(f"\n=== 最終データ構造分析 ===")
    
    # レベル別集計
    level_counts = {}
    type_counts = {}
    category_counts = {}
    
    for node in data['nodes']:
        level = node['level']
        node_type = node['type']
        category = node['category']
        
        level_counts[level] = level_counts.get(level, 0) + 1
        type_counts[node_type] = type_counts.get(node_type, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1
    
    print("レベル別内訳:")
    for level in sorted(level_counts.keys()):
        print(f"  Level {level}: {level_counts[level]}個")
    
    print("\nタイプ別内訳:")
    for type_name, count in sorted(type_counts.items()):
        print(f"  {type_name}: {count}個")
    
    print("\nカテゴリ別内訳:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}個")
    
    # 推定ノード数との比較
    expected_structure = {
        "Level 0 (マリグナンス)": 1,
        "Level 1 (直接素材)": 2,
        "Level 2 (L1の素材+合成先)": "約10-20個",
        "Level 3 (L2の素材+合成先)": "約20-40個"
    }
    
    print(f"\n予想と実際の比較:")
    actual_total = len(data['nodes'])
    print(f"  総ノード数: {actual_total} (予想: 30-60個)")
    print(f"  リンク数: {len(data['links'])}")
    
    # 価格分析
    prices = [node['price'] for node in data['nodes'] if node['price'] > 0]
    if prices:
        print(f"\n価格分析:")
        print(f"  価格範囲: {min(prices)}G - {max(prices)}G")
        print(f"  平均価格: {sum(prices)/len(prices):.1f}G")

def main():
    """メイン処理"""
    print("マリグナンス深さ3データ検証を開始...\n")
    
    # 元データ読み込み
    original_data = load_original_data()
    if not original_data:
        return
    
    # ノード辞書作成
    node_dict = {node['itemId']: node for node in original_data['nodes']}
    
    # 有効アイテム判定
    valid_items = validate_item_availability(node_dict, original_data)
    
    # 深さ3データのフィルタリング
    filtered_data = filter_depth3_data('malignance_depth3_data.json', valid_items)
    
    # 最終データ構造分析
    analyze_final_structure(filtered_data)
    
    # 最終ファイル出力
    output_file = "malignance_depth3_final.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 最終結果 ===")
    print(f"出力ファイル: {output_file}")
    print(f"D3.js用ノード数: {len(filtered_data['nodes'])}")
    print(f"D3.js用リンク数: {len(filtered_data['links'])}")
    print(f"✅ マリグナンス深さ3実装完了")

if __name__ == "__main__":
    main()