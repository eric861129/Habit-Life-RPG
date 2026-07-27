import {Coins, LogOut, RefreshCw, Sparkles, Swords} from "lucide-react";
import {useCallback, useEffect, useState} from "react";

import {
  ApiError,
  archiveHabit,
  checkInHabit,
  createHabit,
  getProfile,
  listHabits,
  updateHabit,
} from "../api/client";
import type {Habit, HabitInput, Notice, UserProfile} from "../types";
import {HabitForm} from "./HabitForm";
import {HabitList} from "./HabitList";

const PRIORITY_RANK = {high: 0, medium: 1, low: 2} as const;

function sortHabits(habits: Habit[]): Habit[] {
  return [...habits].sort(
    (left, right) => PRIORITY_RANK[left.priority] - PRIORITY_RANK[right.priority]
      || left.id - right.id,
  );
}


type DashboardProps = {
  token: string;
  onLogout: () => void;
  onUnauthorized: () => void;
};

export function Dashboard({token, onLogout, onUnauthorized}: DashboardProps) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [editingHabit, setEditingHabit] = useState<Habit | null | undefined>(undefined);
  const [isSaving, setIsSaving] = useState(false);
  const [checkingId, setCheckingId] = useState<number | null>(null);

  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const [nextProfile, nextHabits] = await Promise.all([getProfile(token), listHabits(token)]);
      setProfile(nextProfile);
      setHabits(sortHabits(nextHabits));
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 401) {
        onUnauthorized();
        return;
      }
      setLoadError(caught instanceof Error ? caught.message : "無法載入資料。");
    } finally {
      setIsLoading(false);
    }
  }, [onUnauthorized, token]);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const saveHabit = async (input: HabitInput) => {
    setIsSaving(true);
    try {
      if (editingHabit) {
        const updated = await updateHabit(token, editingHabit.id, input);
        setHabits((current) => sortHabits(
          current.map((habit) => habit.id === updated.id ? updated : habit),
        ));
        setNotice({kind: "success", title: "習慣已更新", message: updated.title});
      } else {
        const created = await createHabit(token, input);
        setHabits((current) => sortHabits([...current, created]));
        setNotice({kind: "success", title: "習慣已建立", message: created.title});
      }
      setEditingHabit(undefined);
    } catch (caught) {
      handleActionError(caught);
    } finally {
      setIsSaving(false);
    }
  };

  const handleArchive = async (habit: Habit) => {
    try {
      await archiveHabit(token, habit.id);
      setHabits((current) => current.filter((item) => item.id !== habit.id));
      setNotice({kind: "success", title: "習慣已封存", message: habit.title});
    } catch (caught) {
      handleActionError(caught);
    }
  };

  const handleCheckIn = async (habit: Habit) => {
    setCheckingId(habit.id);
    try {
      const result = await checkInHabit(token, habit.id);
      setProfile((current) => current ? {
        ...current,
        exp: result.current_exp,
        gold: result.current_gold,
        level: result.current_level,
      } : current);
      setHabits((current) => current.map((item) => item.id === habit.id ? {
        ...item,
        checked_in_today: true,
        last_checkin_date: result.checkin_date,
        streak_count: result.streak_count,
      } : item));
      setNotice({
        kind: result.leveled_up ? "level" : "success",
        title: result.leveled_up ? "等級提升" : "今天的努力已記錄",
        message: `+${result.exp_earned} EXP · +${result.gold_earned} gold`,
      });
    } catch (caught) {
      handleActionError(caught);
    } finally {
      setCheckingId(null);
    }
  };

  const handleActionError = (caught: unknown) => {
    if (caught instanceof ApiError && caught.status === 401) {
      onUnauthorized();
      return;
    }
    setNotice({
      kind: "error",
      title: "操作未完成",
      message: caught instanceof Error ? caught.message : "請稍後再試。",
    });
  };

  if (isLoading) {
    return <main className="app-page"><div className="dashboard-shell loading-shell" aria-live="polite">正在整理今天的冒險日誌...</div></main>;
  }

  if (loadError || !profile) {
    return (
      <main className="app-page">
        <section className="dashboard-shell load-error" role="alert">
          <h1>暫時無法載入日誌</h1>
          <p>{loadError ?? "請重新載入。"}</p>
          <button className="primary-button" type="button" onClick={() => void loadDashboard()}>
            <RefreshCw aria-hidden="true" /><span>重新載入</span>
          </button>
        </section>
      </main>
    );
  }

  const completed = habits.filter((habit) => habit.checked_in_today).length;
  const threshold = profile.level * 200;
  const progress = Math.min(100, (profile.exp / threshold) * 100);

  return (
    <main className="app-page">
      <header className="app-header">
        <a className="brand-lockup" href="#main-content" aria-label="Habit Life RPG 首頁">
          <Swords aria-hidden="true" />
          <span>Habit Life <strong>RPG</strong></span>
        </a>
        <div className="header-account">
          <span>{profile.username}</span>
          <button type="button" className="icon-button" onClick={onLogout} aria-label="登出" title="登出">
            <LogOut aria-hidden="true" />
          </button>
        </div>
      </header>

      <div className="dashboard-shell" id="main-content">
        {notice ? (
          <div className={`notice notice-${notice.kind}`} role={notice.kind === "error" ? "alert" : "status"}>
            {notice.kind === "level" ? <Sparkles aria-hidden="true" /> : <span className="notice-mark">{notice.kind === "error" ? "!" : "✓"}</span>}
            <div><strong>{notice.title}</strong><span>{notice.message}</span></div>
            <button type="button" className="icon-button" onClick={() => setNotice(null)} aria-label="關閉通知">×</button>
          </div>
        ) : null}

        <section className="summary-grid" aria-label="角色與今日摘要">
          <div className="profile-panel">
            <img src="/hero-avatar.png" alt="目前冒險者" />
            <div className="profile-main">
              <p className="section-label">Hero profile</p>
              <h1>{profile.username}</h1>
              <div className="level-line"><span>Level</span><strong>{profile.level}</strong></div>
              <div className="progress-track" aria-label={`${profile.exp} / ${threshold} EXP`}>
                <span style={{width: `${progress}%`}} />
              </div>
              <p className="progress-copy"><strong>{profile.exp} EXP</strong><span>下一級 {threshold} EXP</span></p>
            </div>
            <div className="gold-stat"><Coins aria-hidden="true" /><strong>{profile.gold} gold</strong></div>
          </div>

          <div className="today-panel">
            <p className="section-label">Today</p>
            <h2>今日進度</h2>
            <div className="today-count"><strong>{completed}/{habits.length}</strong><span>habits done</span></div>
            <div className="today-rail"><span style={{width: habits.length ? `${(completed / habits.length) * 100}%` : "0%"}} /></div>
            <p>{completed === habits.length && habits.length > 0 ? "今日清單已完成。" : `${habits.length - completed} 個習慣等待完成。`}</p>
          </div>
        </section>

        {editingHabit !== undefined ? (
          <HabitForm
            habit={editingHabit}
            isSaving={isSaving}
            onCancel={() => setEditingHabit(undefined)}
            onSave={saveHabit}
          />
        ) : null}

        <HabitList
          habits={habits}
          checkingId={checkingId}
          onAdd={() => setEditingHabit(null)}
          onArchive={(habit) => void handleArchive(habit)}
          onCheckIn={(habit) => void handleCheckIn(habit)}
          onEdit={setEditingHabit}
        />
      </div>
    </main>
  );
}
