export type Color = "red" | "blue" | "yellow" | "green";

export interface Position {
  i: number; // 行 (0-15)
  j: number; // 列 (0-15)
}

export interface Robots {
  red: Position;
  blue: Position;
  yellow: Position;
  green: Position;
}

export interface Chips {
  red: Position;
  blue: Position;
  yellow: Position;
  green: Position;
}

// wallsH[i][j] === true → マス(i,j-1)とマス(i,j)の間に壁（縦方向の壁）
// wallsV[i][j] === true → マス(i-1,j)とマス(i,j)の間に壁（横方向の壁）
export interface Walls {
  horizontal: boolean[][]; // S: 16行 × 16列 (index 0 は未使用、1-15が有効)
  vertical: boolean[][];   // T: 16行 × 16列 (index 0 は未使用、1-15が有効)
}

export interface Problem {
  name: string;
  robots: Robots;
  chips: Chips;
  walls: Walls;
}

export type Direction = "up" | "down" | "left" | "right";

export interface GameState {
  robots: Robots;
  history: Robots[];
  moveCount: number;
  selectedRobot: Color | null;
  cleared: boolean;
}
