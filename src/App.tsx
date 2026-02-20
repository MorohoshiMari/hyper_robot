import { useState, useEffect, useCallback } from "react";
import "./App.css";
import type { Color, Direction, Problem, GameState } from "./types";
import { parseProblem } from "./parser";
import { computeDestination, moveRobot, checkCleared } from "./game";

const COLORS: Color[] = ["red", "blue", "yellow", "green"];
const DIRECTIONS: Direction[] = ["up", "down", "left", "right"];
const CELL_SIZE = 50;
const BOARD_BORDER = 3;

function isCenterBlock(i: number, j: number): boolean {
  return (i === 7 || i === 8) && (j === 7 || j === 8);
}

function App() {
  const [problemList, setProblemList] = useState<string[]>([]);
  const [problemIndex, setProblemIndex] = useState(0);
  const [problem, setProblem] = useState<Problem | null>(null);
  const [targetColor, setTargetColor] = useState<Color>("red");
  const [game, setGame] = useState<GameState | null>(null);

  // 問題一覧を読み込み
  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}problems/index.json`)
      .then((r) => r.json())
      .then((list: string[]) => setProblemList(list))
      .catch(() => setProblemList([]));
  }, []);

  // 問題を読み込み
  useEffect(() => {
    if (problemList.length === 0) return;
    const name = problemList[problemIndex];
    fetch(`${import.meta.env.BASE_URL}problems/${name}.txt`)
      .then((r) => r.text())
      .then((text) => {
        const p = parseProblem(name, text);
        setProblem(p);
        setTargetColor("red");
        setGame({
          robots: { ...p.robots },
          history: [],
          moveCount: 0,
          selectedRobot: null,
          cleared: false,
        });
      });
  }, [problemList, problemIndex]);

  const handleSelectRobot = useCallback(
    (color: Color) => {
      if (!game || game.cleared) return;
      setGame((g) =>
        g
          ? { ...g, selectedRobot: g.selectedRobot === color ? null : color }
          : g
      );
    },
    [game]
  );

  const handleMove = useCallback(
    (direction: Direction) => {
      if (!game || !game.selectedRobot || !problem || game.cleared) return;
      const newRobots = moveRobot(
        game.selectedRobot,
        direction,
        game.robots,
        problem.walls
      );
      // 移動しなかった場合は無視
      const old = game.robots[game.selectedRobot];
      const dest = newRobots[game.selectedRobot];
      if (old.i === dest.i && old.j === dest.j) return;

      const cleared = checkCleared(targetColor, newRobots, problem.chips);
      setGame({
        robots: newRobots,
        history: [...game.history, game.robots],
        moveCount: game.moveCount + 1,
        selectedRobot: game.selectedRobot,
        cleared,
      });
    },
    [game, problem, targetColor]
  );

  const handleClickDestination = useCallback(
    (i: number, j: number) => {
      if (!game || !game.selectedRobot || !problem || game.cleared) return;
      // どの方向に移動するとこのマスに到達するか探す
      for (const dir of DIRECTIONS) {
        const dest = computeDestination(
          game.selectedRobot,
          dir,
          game.robots,
          problem.walls
        );
        if (dest.i === i && dest.j === j) {
          handleMove(dir);
          return;
        }
      }
    },
    [game, problem, handleMove]
  );

  const handleUndo = useCallback(() => {
    if (!game || game.history.length === 0) return;
    const prev = game.history[game.history.length - 1];
    setGame({
      robots: prev,
      history: game.history.slice(0, -1),
      moveCount: game.moveCount - 1,
      selectedRobot: game.selectedRobot,
      cleared: false,
    });
  }, [game]);

  const handleReset = useCallback(() => {
    if (!problem) return;
    setGame({
      robots: { ...problem.robots },
      history: [],
      moveCount: 0,
      selectedRobot: null,
      cleared: false,
    });
  }, [problem]);

  const switchProblem = useCallback(
    (delta: number) => {
      if (problemList.length === 0) return;
      setProblemIndex(
        (idx) => (idx + delta + problemList.length) % problemList.length
      );
    },
    [problemList]
  );

  if (!problem || !game) {
    return <div style={{ padding: 40 }}>読み込み中...</div>;
  }

  // 選択中のロボットの移動先を計算
  const destinations: { dir: Direction; i: number; j: number }[] = [];
  if (game.selectedRobot && !game.cleared) {
    for (const dir of DIRECTIONS) {
      const dest = computeDestination(
        game.selectedRobot,
        dir,
        game.robots,
        problem.walls
      );
      const cur = game.robots[game.selectedRobot];
      if (dest.i !== cur.i || dest.j !== cur.j) {
        destinations.push({ dir, i: dest.i, j: dest.j });
      }
    }
  }

  // セルの壁クラスを計算
  function getWallClasses(i: number, j: number): string {
    if (!problem) return "";
    const classes: string[] = [];
    // 上壁: vertical[i][j] (i>0) or ボード上端
    if (i > 0 && problem.walls.vertical[i][j]) classes.push("wall-top");
    if (i < 15 && problem.walls.vertical[i + 1][j]) classes.push("wall-bottom");
    if (j > 0 && problem.walls.horizontal[i][j]) classes.push("wall-left");
    if (j < 15 && problem.walls.horizontal[i][j + 1]) classes.push("wall-right");
    return classes.join(" ");
  }

  return (
    <>
      {/* ボード */}
      <div className="board-container">
        <div className="board">
          {Array.from({ length: 16 }, (_, i) =>
            Array.from({ length: 16 }, (_, j) => {
              const isCenter = isCenterBlock(i, j);
              const destInfo = destinations.find(
                (d) => d.i === i && d.j === j
              );
              const isDestination = !!destInfo;

              // このマスにチップがあるか
              const chipColor = COLORS.find(
                (c) => problem.chips[c].i === i && problem.chips[c].j === j
              );

              // このセルに表示すべき矢印を判定（ロボットの隣接セルに矢印を置く）
              const arrowDir = game.selectedRobot && !game.cleared
                ? (() => {
                    const cur = game.robots[game.selectedRobot];
                    for (const d of destinations) {
                      if (d.dir === "up" && i === cur.i - 1 && j === cur.j) return d.dir;
                      if (d.dir === "down" && i === cur.i + 1 && j === cur.j) return d.dir;
                      if (d.dir === "left" && i === cur.i && j === cur.j - 1) return d.dir;
                      if (d.dir === "right" && i === cur.i && j === cur.j + 1) return d.dir;
                    }
                    return null;
                  })()
                : null;

              return (
                <div
                  key={`${i}-${j}`}
                  className={`cell ${isCenter ? `center-block center-${targetColor}${i === 7 ? " center-top" : ""}${i === 8 ? " center-bottom" : ""}${j === 7 ? " center-left" : ""}${j === 8 ? " center-right" : ""}` : ""} ${isDestination ? "destination" : ""} ${getWallClasses(i, j)}`}
                  onClick={() => {
                    if (arrowDir) {
                      handleMove(arrowDir);
                    } else if (isDestination) {
                      handleClickDestination(i, j);
                    } else if (game.selectedRobot) {
                      setGame((g) => g ? { ...g, selectedRobot: null } : g);
                    }
                  }}
                >
                  {chipColor && (
                    <div className={`chip ${chipColor}`} />
                  )}
                  {arrowDir && (
                    <div
                      className={`arrow ${arrowDir}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMove(arrowDir);
                      }}
                    />
                  )}
                </div>
              );
            })
          )}
        </div>
        {/* ロボット（ボード上に絶対配置） */}
        {COLORS.map((color) => (
          <div
            key={color}
            className={`robot ${color} ${game.selectedRobot === color ? "selected" : ""}`}
            style={{
              top: BOARD_BORDER + game.robots[color].i * CELL_SIZE + CELL_SIZE / 2,
              left: BOARD_BORDER + game.robots[color].j * CELL_SIZE + CELL_SIZE / 2,
            }}
            onClick={() => handleSelectRobot(color)}
          />
        ))}
      </div>

      {/* 右パネル */}
      <div className="panel">
        <div className="target-color">
          <span>ターゲット:</span>
          <div className={`target-indicator ${targetColor}`} />
        </div>

        <h2>手数</h2>
        <div className={`move-count ${game.cleared ? `cleared-${targetColor}` : ""}`}>{game.moveCount}</div>

        {game.cleared && (
          <div className="cleared-message">CLEAR!</div>
        )}

        <button onClick={handleUndo} disabled={game.history.length === 0}>
          UNDO
        </button>
        <button onClick={handleReset}>RESET</button>

        <div className="problem-nav">
          <button onClick={() => switchProblem(-1)}>&lt;</button>
          <span className="problem-name">{problem.name}</span>
          <button onClick={() => switchProblem(1)}>&gt;</button>
        </div>

        <div>
          <span style={{ fontSize: "0.8rem", color: "#888" }}>
            ターゲット色変更:
          </span>
          <div style={{ display: "flex", gap: 6, marginTop: 4 }}>
            {COLORS.map((c) => (
              <div
                key={c}
                className={`target-indicator ${c}`}
                style={{
                  cursor: "pointer",
                  border: c === targetColor ? "2px solid #fff" : "none",
                }}
                onClick={() => setTargetColor(c)}
              />
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
