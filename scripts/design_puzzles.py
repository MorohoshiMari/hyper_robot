#!/usr/bin/env python3
"""
ハイパーロボット パズル設計・BFS検証スクリプト

壁フォーマット（requirements.md より）:
  S_i[j] (j=0..14, 1-indexed=1..15): S_i[j-1]=='1' → マス(i,j-1)とマス(i,j)の間に縦壁
    ≡ 列方向の壁（左右を区切る壁）
  T_j[i] (i=0..14, 1-indexed=1..15): T_j[i-1]=='1' → マス(i-1,j)とマス(i,j)の間に横壁
    ≡ 行方向の壁（上下を区切る壁）

walls_h[i][j] = True → 行iの、列j-1と列jの間に壁（left/rightの移動をブロック）
walls_v[i][j] = True → 列jの、行i-1と行iの間に壁（up/downの移動をブロック）
"""

from collections import deque

BOARD = 16
CENTER = {(7,7),(7,8),(8,7),(8,8)}
COLORS = ['red','blue','yellow','green']

def is_center(i,j):
    return (i,j) in CENTER

def can_move_wall(i, j, di, dj, walls_h, walls_v):
    """壁チェックのみ（ロボット/センターは別途）"""
    if di == -1:  # up: マス(i-1,j)とマス(i,j)の間
        if i == 0: return False
        return not walls_v[i][j]
    elif di == 1:  # down: マス(i,j)とマス(i+1,j)の間
        if i == BOARD-1: return False
        return not walls_v[i+1][j]
    elif dj == -1:  # left: マス(i,j-1)とマス(i,j)の間
        if j == 0: return False
        return not walls_h[i][j]
    elif dj == 1:  # right: マス(i,j)とマス(i,j+1)の間
        if j == BOARD-1: return False
        return not walls_h[i][j+1]
    return False

def compute_dest(ri, rj, color, robots, walls_h, walls_v, di, dj):
    i, j = ri, rj
    while True:
        if not can_move_wall(i, j, di, dj, walls_h, walls_v):
            break
        ni, nj = i+di, j+dj
        if is_center(ni, nj):
            break
        occupied = any(robots[c] == (ni,nj) for c in COLORS if c != color)
        if occupied:
            break
        i, j = ni, nj
    return (i, j)

DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1)]

def bfs(target_color, robots_init, chips, walls_h, walls_v, max_depth=10):
    goal = chips[target_color]

    def to_state(r):
        return tuple(r[c] for c in COLORS)

    if robots_init[target_color] == goal:
        return 0, []

    init_state = to_state(robots_init)
    queue = deque()
    queue.append((init_state, 0, []))
    visited = {init_state}

    while queue:
        state, depth, path = queue.popleft()
        if depth >= max_depth:
            continue

        robots = {c: state[i] for i,c in enumerate(COLORS)}

        for color in COLORS:
            ri, rj = robots[color]
            for di, dj in DIRECTIONS:
                dest = compute_dest(ri, rj, color, robots, walls_h, walls_v, di, dj)
                if dest == robots[color]:
                    continue

                new_robots = dict(robots)
                new_robots[color] = dest
                new_state = to_state(new_robots)

                if new_state in visited:
                    continue
                visited.add(new_state)

                new_path = path + [(color, di, dj, dest)]
                if new_robots[target_color] == goal:
                    return depth+1, new_path

                queue.append((new_state, depth+1, new_path))

    return None, None

def dir_name(di, dj):
    return {(-1,0):"上",(1,0):"下",(0,-1):"左",(0,1):"右"}[(di,dj)]

def make_walls():
    """16x16のFalse配列を作成"""
    return [[False]*16 for _ in range(16)]

def set_wall_h(walls_h, i, j):
    """マス(i,j-1)とマス(i,j)の間に縦壁を設置 (j=1..15)"""
    assert 1 <= j <= 15
    walls_h[i][j] = True

def set_wall_v(walls_v, i, j):
    """マス(i-1,j)とマス(i,j)の間に横壁を設置 (i=1..15)"""
    assert 1 <= i <= 15
    walls_v[i][j] = True

def encode_walls(walls_h, walls_v):
    """壁をテキスト形式にエンコード"""
    s_lines = []
    for i in range(16):
        row = ""
        for j in range(1, 16):
            row += "1" if walls_h[i][j] else "0"
        s_lines.append(row)

    t_lines = []
    for j in range(16):
        col = ""
        for i in range(1, 16):
            col += "1" if walls_v[i][j] else "0"
        t_lines.append(col)

    return s_lines, t_lines

def build_problem_text(robots, chips, walls_h, walls_v):
    s_lines, t_lines = encode_walls(walls_h, walls_v)
    lines = []
    for c in COLORS:
        ri,rj = robots[c]
        ci,cj = chips[c]
        lines.append(f"{ri} {rj} {ci} {cj}")
    lines.extend(s_lines)
    lines.extend(t_lines)
    return "\n".join(lines) + "\n"

def verify(robots, chips, walls_h, walls_v, name):
    print(f"\n=== {name} ===")
    all_ok = True
    for color in COLORS:
        depth, path = bfs(color, robots, chips, walls_h, walls_v, max_depth=10)
        if depth is None:
            print(f"  [{color:6s}] 解なし (10手以内)")
            all_ok = False
        else:
            steps = " -> ".join(f"{p[0]} {dir_name(p[1],p[2])}" for p in path)
            status = "OK" if 3 <= depth <= 8 else f"範囲外({depth}手)"
            print(f"  [{color:6s}] {depth}手 [{status}]: {steps}")
            if depth < 3 or depth > 8:
                all_ok = False
    return all_ok

# ================================================================
# パズル設計
# ================================================================

# ----------------------------------------------------------------
# sample3: 壁で通路が区切られ、ロボットを踏み台にするパズル
# ----------------------------------------------------------------
# 設計方針:
#   赤チップ: (11, 11) — 右下エリア
#   赤ロボット: (2, 2) — 左上スタート
#   壁で右側・下側の通路を区切り、他のロボットを踏み台にする
#
# 解答例(赤):
#   赤 右 → (2,14) 右端まで
#   赤 下 → (11,14) 下まで
#   赤 左 → (11,11) チップへ（緑ロボットが(11,12)にいてストッパー）
#   → 3手

def make_sample3():
    robots = {
        'red':    (2,  2),
        'blue':   (2, 14),
        'yellow': (11, 2),
        'green':  (11,12),
    }
    chips = {
        'red':    (11, 11),
        'blue':   ( 5,  5),
        'yellow': (14,  1),
        'green':  ( 1, 14),
    }
    walls_h = make_walls()
    walls_v = make_walls()

    # 壁を追加して解をコントロール
    # 赤の経路: (2,2)→右→(2,14)、(2,14)→下→(11,14)、(11,14)→左→(11,11) [green(11,12)でストップ]
    # これを成立させるために(11,14)から下への移動をブロックする壁は不要（greenが(11,12)でストッパー）
    # 赤が(11,14)で止まるために: 青が(2,14)にいるので赤は青の手前(2,13)で止まる
    # → 青の初期位置を変更: blue=(2,14)→ 赤が右移動すると(2,14)まで行けない
    # 再設計: blue を右端ではなく別の場所に移す

    robots = {
        'red':    ( 2,  2),
        'blue':   ( 5,  9),
        'yellow': (11,  2),
        'green':  (11, 12),
    }
    chips = {
        'red':    (11, 11),
        'blue':   ( 1,  5),
        'yellow': (14,  1),
        'green':  ( 1, 14),
    }

    # 赤の経路:
    #   (2,2) → 右 → (2,15) [右端]
    #   (2,15) → 下 → (11,15) [黄が(11,2)にいる行の右端 ... 壁なければ15まで]
    #   壁: (12,15)と(11,15)の間に横壁 → walls_v[12][15]=True でストップ
    #   (11,15) → 左 → (11,11) [green(11,12)がストッパー → (11,13)で止まる]
    #   green が(11,12)だと赤は(11,13)で止まる。チップは(11,11)
    #   → greenをストッパーにするにはgreen=(11,12)ではなくchipの右隣に置く
    #   → green = (11,12) → 赤(11,15)→左→(11,13) ✗
    #   → green = (11,12): 赤 (11,15)→左→(11,13) ✗ チップ(11,11)に届かない

    # 再設計: 壁を使ってストップさせる
    # 赤: (2,2)→右→(2,15)→下→(11,15)→左→(11,11)
    #   (11,15)→左→(11,11) に止まるために walls_h[11][11]=True を設置
    #   これにより(11,10)と(11,11)の間に壁ができ、(11,11)でストップ

    # green をどかす
    robots = {
        'red':    ( 2,  2),
        'blue':   ( 5,  9),
        'yellow': (14,  2),
        'green':  ( 9,  5),
    }
    chips = {
        'red':    (11, 11),
        'blue':   ( 0,  5),
        'yellow': ( 0, 14),
        'green':  (14, 10),
    }

    # 赤の解: (2,2)→右→(2,15)→下→(11,15)→左→(11,11) [壁で止まる]
    # walls_h[11][12]: マス(11,11)とマス(11,12)の間に壁 → 右から来るとここで止まる
    set_wall_h(walls_h, 11, 12)

    # 縦移動で(2,15)→下→止まる位置を(11,15)にする
    # 行12以降に壁: walls_v[12][15]=True → マス(11,15)とマス(12,15)の間
    set_wall_v(walls_v, 12, 15)

    # 青の解を考える: blue(5,9) → chip(0,5)
    # (5,9)→上→(0,9)→左→(0,5) [右側に壁か端でストップ]
    # (0,5)でストップするために walls_h[0][6]=True
    set_wall_h(walls_h, 0, 6)

    # 黄の解: yellow(14,2) → chip(0,14)
    # (14,2)→右→(14,15)→上→(0,15)→左→(0,14) [walls_h[0][15]がないと(0,0)まで行く]
    # walls_h[0][15]: マス(0,14)とマス(0,15)の間
    set_wall_h(walls_h, 0, 15)

    # 緑の解: green(9,5) → chip(14,10)
    # (9,5)→下→(15,5)→右→(15,15)→上→(14,15)→左→(14,10)
    # walls_h[14][11]: マス(14,10)とマス(14,11)の間
    set_wall_h(walls_h, 14, 11)

    return robots, chips, walls_h, walls_v

# ----------------------------------------------------------------
# sample4: ロボット同士の連携が必要なパズル
# ----------------------------------------------------------------
def make_sample4():
    robots = {
        'red':    ( 0, 13),
        'blue':   (13,  0),
        'yellow': ( 3, 10),
        'green':  (10,  3),
    }
    chips = {
        'red':    ( 6,  6),
        'blue':   ( 6,  9),
        'yellow': ( 9,  6),
        'green':  ( 9,  9),
    }
    walls_h = make_walls()
    walls_v = make_walls()

    # 赤(0,13)→chip(6,6)
    # (0,13)→左→(0,0)→下→(6,0)→右→(6,6) [壁で止まる]
    # walls_h[6][7]: マス(6,6)とマス(6,7)の間
    set_wall_h(walls_h, 6, 7)

    # 青(13,0)→chip(6,9)
    # (13,0)→右→(13,15)→上→(6,15)→左→(6,9) [壁で止まる]
    # walls_h[6][10]: マス(6,9)とマス(6,10)の間
    set_wall_h(walls_h, 6, 10)

    # 黄(3,10)→chip(9,6)
    # (3,10)→下→(9,10)→左→(9,6) [壁で止まる]
    # まず(9,10)で止まるために walls_v[10][10]=True
    set_wall_v(walls_v, 10, 10)
    # (9,10)→左→(9,6) で止まるために walls_h[9][7]=True
    set_wall_h(walls_h, 9, 7)

    # 緑(10,3)→chip(9,9)
    # (10,3)→上→(9,3)→右→(9,9) [壁で止まる]
    # まず(9,3)で止まるために walls_v[10][3]=True
    set_wall_v(walls_v, 10, 3)
    # (9,3)→右→(9,9) で止まるために walls_h[9][10]=True
    set_wall_h(walls_h, 9, 10)

    return robots, chips, walls_h, walls_v

# ----------------------------------------------------------------
# sample5: より複雑な壁配置のパズル
# ----------------------------------------------------------------
def make_sample5():
    robots = {
        'red':    ( 1, 14),
        'blue':   (14,  1),
        'yellow': ( 1,  1),
        'green':  (14, 14),
    }
    chips = {
        'red':    ( 5,  5),
        'blue':   (10, 10),
        'yellow': ( 5, 10),
        'green':  (10,  5),
    }
    walls_h = make_walls()
    walls_v = make_walls()

    # 赤(1,14)→chip(5,5)
    # (1,14)→左→(1,0)→下→(5,0)→右→(5,5) [壁で止まる]
    # walls_h[5][6]: マス(5,5)とマス(5,6)の間
    set_wall_h(walls_h, 5, 6)

    # 青(14,1)→chip(10,10)
    # (14,1)→右→(14,15)→上→(10,15)→左→(10,10) [壁で止まる]
    # walls_h[10][11]: マス(10,10)とマス(10,11)の間
    set_wall_h(walls_h, 10, 11)

    # 黄(1,1)→chip(5,10)
    # (1,1)→下→(6,1)→右→(6,10)→上→(5,10) [壁で止まる]
    # まず(6,1)で止まるために walls_v[7][1]=True
    set_wall_v(walls_v, 7, 1)
    # (6,1)→右→(6,10) で止まるために walls_h[6][11]=True
    set_wall_h(walls_h, 6, 11)
    # (6,10)→上→(5,10) で止まるために walls_v[6][10]=True
    set_wall_v(walls_v, 6, 10)

    # 緑(14,14)→chip(10,5)
    # (14,14)→左→(14,0)→上→(10,0)→右→(10,5) [壁で止まる]
    # walls_v[9][0] は左端なのでBOARD外。walls_h[10][6]でストップ
    set_wall_h(walls_h, 10, 6)

    return robots, chips, walls_h, walls_v

# ================================================================
# メイン処理
# ================================================================

problems = {
    'sample3': make_sample3(),
    'sample4': make_sample4(),
    'sample5': make_sample5(),
}

print("=" * 60)
print("パズル検証開始")
print("=" * 60)

results = {}
for name, (robots, chips, walls_h, walls_v) in problems.items():
    ok = verify(robots, chips, walls_h, walls_v, name)
    results[name] = (robots, chips, walls_h, walls_v, ok)

print("\n" + "=" * 60)
print("テキスト出力")
print("=" * 60)

for name, (robots, chips, walls_h, walls_v, ok) in results.items():
    text = build_problem_text(robots, chips, walls_h, walls_v)
    print(f"\n--- {name}.txt ---")
    print(text)
