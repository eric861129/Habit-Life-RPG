import type { Habit } from "../types";

type QuestLogProps = {
  habits: Habit[];
  checkingHabitId: number | null;
  onCheckIn: (habitId: number) => void | Promise<void>;
};

export function QuestLog({ habits, checkingHabitId, onCheckIn }: QuestLogProps) {
  return (
    <section className="quest-section" aria-labelledby="quest-log-title">
      <div className="section-heading">
        <div>
          <h2 id="quest-log-title">Quest Log</h2>
          <p className="muted">Complete one scroll, claim one reward.</p>
        </div>
        <span className="meta">{habits.length} scrolls</span>
      </div>

      <div className="quest-list">
        {habits.map((habit, index) => (
          <QuestScroll
            key={habit.id}
            habit={habit}
            index={index}
            isChecking={checkingHabitId === habit.id}
            onCheckIn={onCheckIn}
          />
        ))}
      </div>
    </section>
  );
}

type QuestScrollProps = {
  habit: Habit;
  index: number;
  isChecking: boolean;
  onCheckIn: (habitId: number) => void | Promise<void>;
};

function QuestScroll({ habit, index, isChecking, onCheckIn }: QuestScrollProps) {
  const isDone = habit.checked_in_today;
  const category = habit.category ?? "Guild";
  const status = isDone ? "Done" : isChecking ? "Claiming" : "Ready";
  const buttonLabel = isDone ? "已完成" : isChecking ? "結算中..." : "打卡領獎";

  return (
    <article className={`quest-scroll ${isDone ? "is-done" : ""} ${isChecking ? "is-checking" : ""}`}>
      <div className="scroll-caps" aria-hidden="true" />
      <div className="scroll-body">
        <div className="habit-meta">
          <span>Quest {String(index + 1).padStart(2, "0")}</span>
          <strong>{status}</strong>
        </div>
        <h3>{habit.title}</h3>
        <p>{category} quest · Guild reward posted</p>
        <div className="reward-row">
          <span>+40 EXP</span>
          <span>+8 gold</span>
          <button
            type="button"
            className="checkin-button"
            disabled={isDone || isChecking}
            onClick={() => onCheckIn(habit.id)}
          >
            {buttonLabel}
          </button>
        </div>
      </div>
      <div className="scroll-caps" aria-hidden="true" />
    </article>
  );
}
