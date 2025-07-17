#!/usr/bin/env python3
"""
アイテムの関係性（親子関係）に基づく分類を分析
"""

import requests

patch_version = "15.13.1"

def analyze_item_relationships():
    url = f'https://ddragon.leagueoflegends.com/cdn/{patch_version}/data/en_US/item.json'
    response = requests.get(url)
    data = response.json()
    
    print('=== アイテム関係性分析 ===\n')
    
    # 現在のグラフに含まれるアイテムIDリスト
    graph_items = {
        '1011': 'Giant\'s Belt',
        '1028': 'Ruby Crystal', 
        '3083': 'Warmog\'s Armor',
        '3143': 'Randuin\'s Omen',
        '3116': 'Rylai\'s Crystal Scepter',
        '3084': 'Heartsteel',
        '3067': 'Kindlegem',
        '3066': 'Winged Moonplate',
        '3044': 'Phage',
        '3801': 'Crystalline Bracer',
        '3082': 'Warden\'s Mail',
        '1026': 'Blasting Wand',
        '1052': 'Amplifying Tome',
        '2022': 'Glowing Mote',
        '1006': 'Rejuvenation Bead',
        '1036': 'Long Sword',
        '1029': 'Cloth Armor'
    }
    
    # 各アイテムを分類
    basic_items = []      # 素材アイテム（子がいない）
    intermediate_items = [] # 中間アイテム（親も子もいる）
    legendary_items = []   # レジェンダリー（親がいない）
    
    # intoマップの構築（どのアイテムの素材になるか）
    into_map = {}
    for item_id, item in data['data'].items():
        if 'from' in item:
            for material_id in item['from']:
                if material_id not in into_map:
                    into_map[material_id] = []
                into_map[material_id].append(item_id)
    
    for item_id, name in graph_items.items():
        if item_id in data['data']:
            item = data['data'][item_id]
            has_from = 'from' in item
            has_into = item_id in into_map
            price = item['gold']['total']
            
            if not has_from and has_into:
                # 子がいない、親がいる = 素材アイテム
                basic_items.append((item_id, name, price))
            elif has_from and has_into:
                # 親も子もいる = 中間アイテム
                intermediate_items.append((item_id, name, price))
            elif has_from and not has_into:
                # 子がいる、親がいない = レジェンダリー
                legendary_items.append((item_id, name, price))
            else:
                # どちらもない（理論上は存在しないはず）
                print(f"⚠️ 特殊なアイテム: {name} (ID: {item_id})")
    
    print('🟢 素材アイテム（子がいない）:')
    for item_id, name, price in sorted(basic_items, key=lambda x: x[2]):
        print(f'  {name} (ID: {item_id}, {price}G)')
    
    print(f'\n🔵 中間アイテム（親も子もいる）:')
    for item_id, name, price in sorted(intermediate_items, key=lambda x: x[2]):
        print(f'  {name} (ID: {item_id}, {price}G)')
        # 詳細表示
        if item_id in data['data']:
            item = data['data'][item_id]
            if 'from' in item:
                print(f'    子: {[graph_items.get(mid, mid) for mid in item["from"]]}')
            if item_id in into_map:
                parents = [graph_items.get(pid, pid) for pid in into_map[item_id] if pid in graph_items]
                if parents:
                    print(f'    親: {parents}')
    
    print(f'\n🟡 レジェンダリーアイテム（親がいない）:')
    for item_id, name, price in sorted(legendary_items, key=lambda x: x[2]):
        print(f'  {name} (ID: {item_id}, {price}G)')
    
    # 価格ベースと関係性ベースの比較
    print(f'\n📊 分類方法の比較:')
    print(f'\n価格ベース（1600G基準）vs 関係性ベース:')
    
    mismatches = []
    
    for item_id, name in graph_items.items():
        if item_id in data['data']:
            item = data['data'][item_id]
            price = item['gold']['total']
            
            # 価格ベース分類
            if price <= 799:
                price_category = '素材'
            elif price <= 1600:
                price_category = '中間'
            else:
                price_category = 'レジェンダリー'
            
            # 関係性ベース分類
            has_from = 'from' in item
            has_into = item_id in into_map
            
            if not has_from and has_into:
                relation_category = '素材'
            elif has_from and has_into:
                relation_category = '中間'
            elif has_from and not has_into:
                relation_category = 'レジェンダリー'
            else:
                relation_category = '特殊'
            
            # デバッグ出力
            print(f'{name} (ID: {item_id}):')
            print(f'  価格: {price}G → {price_category}')
            print(f'  has_from: {has_from}, has_into: {has_into} → {relation_category}')
            
            if price_category != relation_category:
                mismatches.append((name, item_id, price, price_category, relation_category))
                print(f'  ⚠️ 不一致！')
            print()
    
    print(f'\n⚠️ 不一致のアイテム一覧:')
    for name, item_id, price, price_cat, rel_cat in mismatches:
        print(f'  {name} (ID: {item_id}, {price}G): 価格={price_cat}, 関係性={rel_cat}')

if __name__ == "__main__":
    analyze_item_relationships()