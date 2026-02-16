import type { Problem, Robots, Chips, Walls } from "./types";

export function parseProblem(name: string, text: string): Problem {
  const lines = text.trim().split("\n");

  const parseRobotLine = (line: string) => {
    const [ri, rj, Ri, Rj] = line.trim().split(/\s+/).map(Number);
    return { robot: { i: ri, j: rj }, chip: { i: Ri, j: Rj } };
  };

  const red = parseRobotLine(lines[0]);
  const blue = parseRobotLine(lines[1]);
  const yellow = parseRobotLine(lines[2]);
  const green = parseRobotLine(lines[3]);

  const robots: Robots = {
    red: red.robot,
    blue: blue.robot,
    yellow: yellow.robot,
    green: green.robot,
  };

  const chips: Chips = {
    red: red.chip,
    blue: blue.chip,
    yellow: yellow.chip,
    green: green.chip,
  };

  // S_0〜S_15: 縦壁 (マス(i,j-1)とマス(i,j)の間)
  const horizontal: boolean[][] = [];
  for (let i = 0; i < 16; i++) {
    const s = lines[4 + i].trim();
    const row: boolean[] = [false]; // j=0 には左壁なし（ボード外枠は別管理）
    for (let j = 0; j < 15; j++) {
      row.push(s[j] === "1");
    }
    horizontal.push(row);
  }

  // T_0〜T_15: 横壁 (マス(i-1,j)とマス(i,j)の間)
  const vertical: boolean[][] = [];
  for (let j = 0; j < 16; j++) {
    const t = lines[20 + j].trim();
    const col: boolean[] = [false]; // i=0 には上壁なし（ボード外枠は別管理）
    for (let i = 0; i < 15; i++) {
      col.push(t[i] === "1");
    }
    vertical.push(col);
  }

  // vertical[j][i] → マス(i-1,j)とマス(i,j)の間に壁
  // walls.vertical[i][j] に変換
  const verticalByRow: boolean[][] = [];
  for (let i = 0; i < 16; i++) {
    const row: boolean[] = [];
    for (let j = 0; j < 16; j++) {
      row.push(vertical[j][i]);
    }
    verticalByRow.push(row);
  }

  const walls: Walls = {
    horizontal,
    vertical: verticalByRow,
  };

  return { name, robots, chips, walls };
}
