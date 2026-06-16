import type { UserProfile } from "../types";

type HeroStatusProps = {
  profile: UserProfile;
};

export function HeroStatus({ profile }: HeroStatusProps) {
  const expGoal = profile.level * 200;
  const expPercent = Math.min(100, Math.round((profile.exp / expGoal) * 100));

  return (
    <section className="pixel-card hero-card" aria-labelledby="hero-status-title">
      <div className="hero-main">
        <div className="avatar" aria-hidden="true">
          LV
        </div>
        <div className="hero-name">
          <h2 id="hero-status-title">{profile.username}</h2>
          <span>Apprentice Habit Knight</span>
        </div>
      </div>

      <div className="rank-grid" aria-label="Hero summary">
        <StatusChip label="Level" value={String(profile.level)} />
        <StatusChip label="Guild" value="Rank D" />
        <StatusChip label="Streak" value="3 days" />
      </div>

      <div className="stat-row">
        <Stat label="HP" value={`${profile.hp}/100`} />
        <Stat label="Gold" value={`${profile.gold} G`} />
      </div>

      <div className="progress-block">
        <div className="progress-label">
          <span>EXP</span>
          <strong>
            {profile.exp} / {expGoal}
          </strong>
        </div>
        <div className="progress" aria-label={`EXP ${profile.exp} of ${expGoal}`}>
          <span style={{ width: `${expPercent}%` }} />
        </div>
      </div>
    </section>
  );
}

function StatusChip({ label, value }: { label: string; value: string }) {
  return (
    <div className="rank-chip">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
