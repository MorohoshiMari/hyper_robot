#!/usr/bin/env python3
"""
ハイパーロボット パズル生成・BFS検証スクリプト

壁フォーマット:
  S_i (i=0..15): 各行15文字。S_i[j-1]=='1' → マス(i,j-1)とマス(i,j)の間に縦壁
  T_j (j=0..15): 各列15文字。T_j[i-1]=='1' → マス(i-1,j)とマス(i,j)の間に横壁

walls_h[i][j]: マス(i,j-1)とマス(i,j)の間に壁あり (j=1..15)
walls_v[i][j]: マス(i-1,j)とマス(i,j)の間に壁あり (i=1..15)
"""

from collections import deque
from copy import deepcopy

BOARD = 16
CENTER = {(7,7),(7,8),(8,7),(8,8)}
COLORS = ['red','blue','yellow','green']

def is_center(i,j):
    return (i,j) in CENTER

def parse_problem(text):
    lines = text.strip().split('\n')
    robots = {}
    chips = {}
    color_names = ['red','blue','yellow','green']
    for idx, c in enumerate(color_names):
        parts = lines[idx].split()
        robots[c] = (int(parts[0]), int(parts[1]))
        chips[c]  = (int(parts[2]), int(parts[3]))

    # S lines (walls_h): lines[4..19]
    walls_h = [[False]*16 for _ in range(16)]
    for i in range(16):
        s = lines[4+i]
        for j in range(1, 16):
            if s[j-1] == '1':
                walls_h[i][j] = True

    # T lines (walls_v): lines[20..35]
    walls_v = [[False]*16 for _ in range(16)]
    for j in range(16):
        t = lines[20+j]
        for i in range(1, 16):
            if t[i-1] == '1':
                walls_v[i][j] = True

    return robots, chips, walls_h, walls_v

def can_move(i, j, di, dj, walls_h, walls_v):
    """(i,j)からdi,dj方向に1マス進めるか（壁チェックのみ）"""
    if di == -1:  # up
        if i == 0: return False
        return not walls_v[i][j]
    elif di == 1:  # down
        if i == BOARD-1: return False
        return not walls_v[i+1][j]
    elif dj == -1:  # left
        if j == 0: return False
        return not walls_h[i][j]
    elif dj == 1:  # right
        if j == BOARD-1: return False
        return not walls_h[i][j+1]
    return False

def compute_dest(color, robots, walls_h, walls_v, di, dj):
    i, j = robots[color]
    while True:
        if not can_move(i, j, di, dj, walls_h, walls_v):
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
    """BFSで最小手数を返す。見つからない場合はNone"""
    goal = chips[target_color]

    # state: tuple of ((ri,rj),(bi,bj),(yi,yj),(gi,gj))
    def robots_to_state(r):
        return tuple(r[c] for c in COLORS)

    init_state = robots_to_state(robots_init)

    if robots_init[target_color] == goal:
        return 0, []

    queue = deque()
    queue.append((init_state, 0, []))
    visited = {init_state}

    while queue:
        state, depth, path = queue.popleft()
        if depth >= max_depth:
            continue

        robots = {c: state[i] for i,c in enumerate(COLORS)}

        for ci, color in enumerate(COLORS):
            for di, dj in DIRECTIONS:
                dest = compute_dest(color, robots, walls_h, walls_v, di, dj)
                if dest == robots[color]:
                    continue  # 動かない

                new_robots = dict(robots)
                new_robots[color] = dest
                new_state = robots_to_state(new_robots)

                if new_state in visited:
                    continue
                visited.add(new_state)

                new_path = path + [(color, di, dj, dest)]

                if new_robots[target_color] == goal:
                    return depth+1, new_path

                queue.append((new_state, depth+1, new_path))

    return None, None

def dir_name(di, dj):
    if di==-1: return "up"
    if di==1: return "down"
    if dj==-1: return "left"
    return "right"

def verify_all_colors(problem_text, name=""):
    robots, chips, walls_h, walls_v = parse_problem(problem_text)
    print(f"\n=== {name} ===")
    print(f"Robots: {robots}")
    print(f"Chips:  {chips}")
    results = {}
    for color in COLORS:
        depth, path = bfs(color, robots, chips, walls_h, walls_v)
        if depth is None:
            print(f"  [{color}] 解なし (10手以内)")
            results[color] = None
        else:
            steps = " -> ".join(f"{p[0]} {dir_name(p[1],p[2])}" for p in path)
            print(f"  [{color}] {depth}手: {steps}")
            results[color] = depth
    return results

# ===== パズル定義 =====
# フォーマット:
#   行1-4: "ri rj Ri Rj" (ロボット位置 チップ位置)
#   行5-20: S_0..S_15 (各15文字, 縦壁)
#   行21-36: T_0..T_15 (各15文字, 横壁)

# -------------------------------------------------------
# sample3: 赤ロボットが右→下でチップへ向かう中難易度パズル
# -------------------------------------------------------
SAMPLE3 = """\
2 2 10 10
13 1 6 14
0 14 3 5
12 7 15 12
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000001000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
"""

# -------------------------------------------------------
# sample4: 壁を使ったリフレクション系パズル
# -------------------------------------------------------
SAMPLE4 = """\
0 0 11 11
15 15 4 4
0 15 12 3
15 0 3 12
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000100000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
"""

# -------------------------------------------------------
# sample5: 別配置のパズル
# -------------------------------------------------------
SAMPLE5 = """\
3 3 12 12
12 3 3 12
3 12 12 3
12 12 3 3
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
000000000000000
"""

if __name__ == "__main__":
    verify_all_colors(SAMPLE3, "sample3")
    verify_all_colors(SAMPLE4, "sample4")
    verify_all_colors(SAMPLE5, "sample5")
