import {Archive, Check, Flame, Pencil, Plus} from "lucide-react";

import type {Habit} from "../types";

const PRIORITY_LABELS = {
  high: "高優先",
  medium: "中優先",
  low: "低優先",
} as const;


type HabitListProps = {
  habits: Habit[];
  checkingId: number | null;
  onAdd: () => void;
  onArchive: (habit: Habit) => void;
  onCheckIn: (habit: Habit) => void;
  onEdit: (habit: Habit) => void;
};

export function HabitList({habits, checkingId, onAdd, onArchive, onCheckIn, onEdit}: HabitListProps) {
  return (
    <section className="habit-workspace" aria-labelledby="habit-list-title">
      <div className="habit-toolbar">
        <div>
          <p className="section-label">Daily ledger</p>
          <h2 id="habit-list-title">今日習慣</h2>
        </div>
        <button type="button" className="primary-button" onClick={onAdd}>
          <Plus aria-hidden="true" />
          <span>新增習慣</span>
        </button>
      </div>

      {habits.length === 0 ? (
        <div className="empty-state">
          <img src="/hero-avatar.png" alt="等待第一個習慣的冒險者" />
          <p>建立第一個習慣，開始累積今天的進度。</p>
        </div>
      ) : (
        <div className="habit-table" role="list">
          <div className="habit-table-head" aria-hidden="true">
            <span>Habit</span><span>Streak</span><span>Today</span><span>Actions</span>
          </div>
          {habits.map((habit) => (
            <article className="habit-row" role="listitem" key={habit.id}>
              <div className="habit-copy">
                <div className="habit-title-line">
                  <h3>{habit.title}</h3>
                  <span className={`priority-badge priority-${habit.priority}`}>
                    {PRIORITY_LABELS[habit.priority]}
                  </span>
                </div>
                <p>{habit.category ?? "未分類"}{habit.description ? ` · ${habit.description}` : ""}</p>
              </div>
              <div className="streak-cell" aria-label={`連續 ${habit.streak_count} 天`}>
                <Flame aria-hidden="true" />
                <strong>{habit.streak_count}</strong>
                <span>days</span>
              </div>
              <button
                type="button"
                className={`checkin-button ${habit.checked_in_today ? "is-done" : ""}`}
                disabled={habit.checked_in_today || checkingId !== null}
                aria-label={habit.checked_in_today ? `${habit.title}已完成` : `完成${habit.title}`}
                onClick={() => onCheckIn(habit)}
              >
                <Check aria-hidden="true" />
                <span>{habit.checked_in_today ? "已完成" : checkingId === habit.id ? "記錄中..." : "完成"}</span>
              </button>
              <div className="row-actions">
                <button type="button" className="icon-button" onClick={() => onEdit(habit)} aria-label={`編輯${habit.title}`} title="編輯">
                  <Pencil aria-hidden="true" />
                </button>
                <button type="button" className="icon-button danger-tool" onClick={() => onArchive(habit)} aria-label={`封存${habit.title}`} title="封存">
                  <Archive aria-hidden="true" />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
