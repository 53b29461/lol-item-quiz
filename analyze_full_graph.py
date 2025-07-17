#!/usr/bin/env python3
"""
出題範囲の全アイテムでグラフ構築データを分析
"""

import requests
import json

patch_version = "15.13.1"

def filter_items(all_items):
    """app.pyと同じフィルタリング処理 + アリーナ版除外"""
    map_filtered_items = {item_id: item for item_id, item in all_items.items() if item.get('maps', {}).get('11', False) and not all(item.get('maps', {}).get(map_id, False) for map_id in ['11', '12', '21', '30'])}
    
    target_tags = ['Consumable', 'Trinket', 'Boots', 'Jungle', 'Lane']
    exclude_item_names = ['ロング ソード']
    tag_filtered_items = {item_id: item for item_id, item in all_items.items() if any(tag in item.get('tags', []) for tag in target_tags) and item['name'] not in exclude_item_names}
    
    final_filtered_items = {item_id: item for item_id, item in map_filtered_items.items() if item_id not in tag_filtered_items}
    
    exclude_ids = ['6693', '6673', '4641', '4637', '1516', '1517', '1518', '1519']
    last_final_filtered_items = {item_id: item for item_id, item in final_filtered_items.items() if item_id not in exclude_ids}
    
    # アリーナ版アイテム（IDが32で始まる）を除外
    arena_filtered_items = {item_id: item for item_id, item in last_final_filtered_items.items() if not item_id.startswith('32')}
    
    return arena_filtered_items

def analyze_full_graph():
    # データ取得
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/ja_JP/item.json'
    response = requests.get(url)
    data = response.json()
    
    # フィルタリング
    all_items = {item_id: item for item_id, item in data['data'].items() if item.get('requiredAlly') != 'Ornn'}
    filtered_items = filter_items(all_items)
    
    print(f'=== 出題範囲全アイテム分析 ===')
    print(f'総アイテム数: {len(filtered_items)}')
    
    # 関係性ベース分類
    into_map = {}
    for item_id, item in filtered_items.items():
        if 'from' in item:
            for material_id in item['from']:
                if material_id not in into_map:
                    into_map[material_id] = []
                into_map[material_id].append(item_id)
    
    basic_items = []      # 素材アイテム（子がいない）
    intermediate_items = [] # 中間アイテム（親も子もいる）
    legendary_items = []   # レジェンダリー（親がいない）
    
    nodes = []
    edges = []
    
    for item_id, item in filtered_items.items():
        has_from = 'from' in item
        has_into = item_id in into_map
        price = item['gold']['total']
        name = item['name']
        
        # 分類
        if not has_from and has_into:
            category = 'basic'
            basic_items.append((item_id, name, price))
        elif has_from and has_into:
            category = 'intermediate'
            intermediate_items.append((item_id, name, price))
        elif has_from and not has_into:
            category = 'legendary'
            legendary_items.append((item_id, name, price))
        else:
            category = 'isolated'
        
        # ステータス情報を抽出
        stats = item.get('stats', {})
        description = item.get('plaintext', '')
        
        # ノードデータ
        nodes.append({
            'id': item_id,
            'label': name,
            'category': category,
            'price': price,
            'itemId': item_id,
            'stats': stats,
            'description': description
        })
        
        # エッジデータ（親子関係）
        if 'from' in item:
            for material_id in item['from']:
                if material_id in filtered_items:
                    edges.append({
                        'source': material_id,
                        'target': item_id,
                        'type': 'crafts-into'
                    })
    
    print(f'\\n📊 分類結果:')
    print(f'🟢 素材アイテム: {len(basic_items)}個')
    print(f'🔵 中間アイテム: {len(intermediate_items)}個')
    print(f'🟡 レジェンダリーアイテム: {len(legendary_items)}個')
    print(f'\\n🔗 関係性:')
    print(f'エッジ数: {len(edges)}個')
    
    # JSONファイルとして出力
    graph_data = {
        'nodes': nodes,
        'edges': edges,
        'stats': {
            'total_items': len(filtered_items),
            'basic_items': len(basic_items),
            'intermediate_items': len(intermediate_items),
            'legendary_items': len(legendary_items),
            'edges': len(edges)
        }
    }
    
    with open('full_graph_data.json', 'w', encoding='utf-8') as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=2)
    
    print(f'\\n✅ full_graph_data.json に出力完了')
    
    # 大きなコンポーネントの分析
    print(f'\\n📈 主要アイテムの関係性:')
    
    # 最も多くの子を持つアイテム（素材として使われる）
    material_usage = {}
    for edge in edges:
        material_id = edge['source']
        if material_id not in material_usage:
            material_usage[material_id] = 0
        material_usage[material_id] += 1
    
    top_materials = sorted(material_usage.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f'\\n🔧 最も使われる素材アイテム（Top 10）:')
    for item_id, count in top_materials:
        item_name = filtered_items[item_id]['name']
        print(f'  {item_name} (ID: {item_id}): {count}個のアイテムに使用')
    
    # 最も多くの親を持つアイテム（複雑な合成）
    parent_count = {}
    for edge in edges:
        target_id = edge['target']
        if target_id not in parent_count:
            parent_count[target_id] = 0
        parent_count[target_id] += 1
    
    complex_items = sorted(parent_count.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f'\\n🔧 最も複雑な合成アイテム（Top 10）:')
    for item_id, count in complex_items:
        item_name = filtered_items[item_id]['name']
        print(f'  {item_name} (ID: {item_id}): {count}個の素材が必要')

if __name__ == "__main__":
    analyze_full_graph()