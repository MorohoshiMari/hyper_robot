import type { Color, Direction, Position, Robots, Walls } from "./types";

const BOARD_SIZE = 16;

// 中央4マスは進入不可
function isCenterBlock(i: number, j: number): boolean {
  return (i === 7 || i === 8) && (j === 7 || j === 8);
}

function isOccupied(pos: Position, robots: Robots, exclude?: Color): boolean {
  for (const color of ["red", "blue", "yellow", "green"] as Color[]) {
    if (color === exclude) continue;
    if (robots[color].i === pos.i && robots[color].j === pos.j) return true;
  }
  return false;
}

// 壁チェック: (i,j) から direction 方向に1マス進めるか
function hasWallBetween(
  i: number,
  j: number,
  direction: Direction,
  walls: Walls
): boolean {
  switch (direction) {
    case "up":
      if (i === 0) return true; // ボード上端
      // vertical[i][j] → マス(i-1,j)とマス(i,j)の間に壁
      return walls.vertical[i][j];
    case "down":
      if (i === BOARD_SIZE - 1) return true;
      return walls.vertical[i + 1][j];
    case "left":
      if (j === 0) return true;
      // horizontal[i][j] → マス(i,j-1)とマス(i,j)の間に壁
      return walls.horizontal[i][j];
    case "right":
      if (j === BOARD_SIZE - 1) return true;
      return walls.horizontal[i][j + 1];
  }
}

const DELTA: Record<Direction, { di: number; dj: number }> = {
  up: { di: -1, dj: 0 },
  down: { di: 1, dj: 0 },
  left: { di: 0, dj: -1 },
  right: { di: 0, dj: 1 },
};

export function computeDestination(
  color: Color,
  direction: Direction,
  robots: Robots,
  walls: Walls
): Position {
  const { di, dj } = DELTA[direction];
  let { i, j } = robots[color];

  while (true) {
    if (hasWallBetween(i, j, direction, walls)) break;
    const ni = i + di;
    const nj = j + dj;
    if (isCenterBlock(ni, nj)) break;
    if (isOccupied({ i: ni, j: nj }, robots, color)) break;
    i = ni;
    j = nj;
  }

  return { i, j };
}

export function moveRobot(
  color: Color,
  direction: Direction,
  robots: Robots,
  walls: Walls
): Robots {
  const dest = computeDestination(color, direction, robots, walls);
  return { ...robots, [color]: dest };
}

export function checkCleared(
  targetColor: Color,
  robots: Robots,
  chips: { red: Position; blue: Position; yellow: Position; green: Position }
): boolean {
  const robot = robots[targetColor];
  const chip = chips[targetColor];
  return robot.i === chip.i && robot.j === chip.j;
}
