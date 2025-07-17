#!/usr/bin/env python3
"""
5層グラフの接続関係を検証
"""

def verify_graph_connections():
    print('=== 5層グラフ接続関係検証 ===')
    
    # 現在のノード
    nodes = {
        'giants-belt': {'name': 'Giant\'s Belt', 'type': 'center'},
        'ruby-crystal': {'name': 'Ruby Crystal', 'type': 'center_child'},
        'parent-3083': {'name': 'Warmog\'s Armor', 'type': 'center_parent'},
        'parent-3143': {'name': 'Randuin\'s Omen', 'type': 'center_parent'},
        'parent-3116': {'name': 'Rylai\'s Crystal Scepter', 'type': 'center_parent'},
        'parent-3084': {'name': 'Heartsteel', 'type': 'center_parent'},
        'child-parent-3067': {'name': 'Kindlegem', 'type': 'child_other_parent'},
        'child-parent-3801': {'name': 'Crystalline Bracer', 'type': 'child_other_parent'},
        'child-parent-3044': {'name': 'Phage', 'type': 'child_other_parent'},
        'material-3801': {'name': 'Crystalline Bracer', 'type': 'parent_other_child'},
        'material-3082': {'name': 'Warden\'s Mail', 'type': 'parent_other_child'},
        'material-1026': {'name': 'Blasting Wand', 'type': 'parent_other_child'},
        'material-1052': {'name': 'Amplifying Tome', 'type': 'parent_other_child'}
    }
    
    # 現在のエッジ
    edges = [
        {'source': 'ruby-crystal', 'target': 'giants-belt', 'type': 'child-parent'},
        {'source': 'giants-belt', 'target': 'parent-3083', 'type': 'parent-child'},
        {'source': 'giants-belt', 'target': 'parent-3143', 'type': 'parent-child'},
        {'source': 'giants-belt', 'target': 'parent-3116', 'type': 'parent-child'},
        {'source': 'giants-belt', 'target': 'parent-3084', 'type': 'parent-child'},
        {'source': 'ruby-crystal', 'target': 'child-parent-3067', 'type': 'child-parent'},
        {'source': 'ruby-crystal', 'target': 'child-parent-3801', 'type': 'child-parent'},
        {'source': 'ruby-crystal', 'target': 'child-parent-3044', 'type': 'child-parent'},
        {'source': 'material-3801', 'target': 'parent-3083', 'type': 'child-parent'},
        {'source': 'material-3082', 'target': 'parent-3143', 'type': 'child-parent'},
        {'source': 'material-1026', 'target': 'parent-3116', 'type': 'child-parent'},
        {'source': 'material-1052', 'target': 'parent-3116', 'type': 'child-parent'}
    ]
    
    print(f'\\n📊 ノード総数: {len(nodes)}個')
    print(f'📊 エッジ総数: {len(edges)}個')
    
    # 層別ノード数確認
    layers = {}
    for node_id, node_data in nodes.items():
        layer_type = node_data['type']
        if layer_type not in layers:
            layers[layer_type] = []
        layers[layer_type].append((node_id, node_data['name']))
    
    print(f'\\n🔍 層別ノード分布:')
    for layer_type, layer_nodes in layers.items():
        print(f'  {layer_type}: {len(layer_nodes)}個')
        for node_id, node_name in layer_nodes:
            print(f'    - {node_name} ({node_id})')
    
    # 各ノードの接続関係チェック
    print(f'\\n🔗 各ノードの接続関係:')
    
    connection_count = {}
    for node_id in nodes.keys():
        connection_count[node_id] = {'incoming': 0, 'outgoing': 0}
    
    for edge in edges:
        source = edge['source']
        target = edge['target']
        connection_count[source]['outgoing'] += 1
        connection_count[target]['incoming'] += 1
    
    for node_id, node_data in nodes.items():
        incoming = connection_count[node_id]['incoming']
        outgoing = connection_count[node_id]['outgoing']
        total = incoming + outgoing
        print(f'  {node_data["name"]} ({node_id}):')
        print(f'    入力: {incoming}, 出力: {outgoing}, 合計: {total}')
    
    # 孤立ノードチェック
    isolated_nodes = []
    for node_id, counts in connection_count.items():
        if counts['incoming'] == 0 and counts['outgoing'] == 0:
            isolated_nodes.append(node_id)
    
    if isolated_nodes:
        print(f'\\n🚨 孤立ノード（接続なし）: {len(isolated_nodes)}個')
        for node_id in isolated_nodes:
            print(f'  - {nodes[node_id]["name"]} ({node_id})')
    else:
        print(f'\\n✅ 孤立ノードなし: 全ノードが接続されています')
    
    # 期待される接続パターンチェック
    print(f'\\n🎯 期待される接続パターン検証:')
    
    # 1. 中心から各親への接続
    center_to_parents = [e for e in edges if e['source'] == 'giants-belt' and e['target'].startswith('parent-')]
    print(f'  中心 → 親: {len(center_to_parents)}/4 (期待: 4)')
    
    # 2. 子から中心への接続
    child_to_center = [e for e in edges if e['source'] == 'ruby-crystal' and e['target'] == 'giants-belt']
    print(f'  子 → 中心: {len(child_to_center)}/1 (期待: 1)')
    
    # 3. 子から子の別親への接続
    child_to_other_parents = [e for e in edges if e['source'] == 'ruby-crystal' and e['target'].startswith('child-parent-')]
    print(f'  子 → 子の別親: {len(child_to_other_parents)}/3 (期待: 3)')
    
    # 4. 親の別子から親への接続
    materials_to_parents = [e for e in edges if e['source'].startswith('material-') and e['target'].startswith('parent-')]
    print(f'  親の別子 → 親: {len(materials_to_parents)}/4 (期待: 4)')
    
    # 問題点の特定
    print(f'\\n🔍 問題点の特定:')
    
    # 重複名チェック
    name_counts = {}
    for node_data in nodes.values():
        name = node_data['name']
        name_counts[name] = name_counts.get(name, 0) + 1
    
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    if duplicates:
        print(f'  🚨 重複名: {duplicates}')
        print(f'    → Crystalline Bracerが2つ存在（child-parent-3801 と material-3801）')
        print(f'    → これにより接続の混乱が生じている可能性')
    
    # 推奨修正案
    print(f'\\n💡 推奨修正案:')
    print(f'  1. 重複アイテム名の解決')
    print(f'     - child-parent-3801 (Crystalline Bracer) → 削除または名前変更')
    print(f'     - より多様な "子の別親" アイテムを使用')
    print(f'  2. 不足している接続の追加')
    print(f'  3. エッジの方向と色の統一')
    
    # 修正後の推奨アイテム
    print(f'\\n📋 修正後の推奨アイテム構成:')
    print(f'  子の別親: Kindlegem, Winged Moonplate, Phage (重複排除)')
    print(f'  親の別子: Crystalline Bracer, Warden\'s Mail, Blasting Wand, Amplifying Tome')

if __name__ == "__main__":
    verify_graph_connections()