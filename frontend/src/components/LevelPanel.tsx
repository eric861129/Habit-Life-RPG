type LevelPanelProps = {
  exp: number;
  level: number;
  isLevelUp?: boolean;
};

export function LevelPanel({ exp, level, isLevelUp = false }: LevelPanelProps) {
  const expGoal = level * 200;
  const expPercent = Math.min(100, Math.round((exp / expGoal) * 100));

  return (
    <section className={`pixel-card level-panel ${isLevelUp ? "is-level-up" : ""}`} aria-labelledby="level-panel-title">
      <div>
        <h2 id="level-panel-title">{isLevelUp ? "Level up!" : "Next rank gate"}</h2>
        <p className="muted">
          {isLevelUp ? "The guild ledger promoted this hero after check-in." : "Rewards are written into the guild ledger by the backend."}
        </p>
      </div>
      <div className="progress-label">
        <span>Next rank</span>
        <strong>
          {exp} / {expGoal} EXP
        </strong>
      </div>
      <div className="progress">
        <span style={{ width: `${expPercent}%` }} />
      </div>
    </section>
  );
}
