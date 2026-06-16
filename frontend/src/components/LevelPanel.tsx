type LevelPanelProps = {
  exp: number;
  level: number;
};

export function LevelPanel({ exp, level }: LevelPanelProps) {
  const expGoal = level * 200;
  const expPercent = Math.min(100, Math.round((exp / expGoal) * 100));

  return (
    <section className="pixel-card level-panel" aria-labelledby="level-panel-title">
      <div>
        <h2 id="level-panel-title">Level gate unlocked</h2>
        <p className="muted">Rewards are written into the guild ledger by the backend.</p>
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
