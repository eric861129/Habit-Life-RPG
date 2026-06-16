import { useEffect, useState } from "react";

import { ApiError, checkInHabit, getHabits, getUserProfile } from "./api/client";
import { AppHeader } from "./components/AppHeader";
import { BottomNav } from "./components/BottomNav";
import { HeroStatus } from "./components/HeroStatus";
import { LevelPanel } from "./components/LevelPanel";
import { NoticeToast } from "./components/NoticeToast";
import { QuestLog } from "./components/QuestLog";
import type { Habit, Notice, UserProfile } from "./types";

export default function App() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadGameState() {
      try {
        const [nextProfile, nextHabits] = await Promise.all([getUserProfile(), getHabits()]);
        if (!isMounted) {
          return;
        }
        setProfile(nextProfile);
        setHabits(nextHabits);
        setNotice(null);
      } catch (error) {
        if (!isMounted) {
          return;
        }
        setNotice(toErrorNotice(error));
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadGameState();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleCheckIn = async (habitId: number) => {
    try {
      const result = await checkInHabit(habitId);
      setProfile((currentProfile) =>
        currentProfile === null
          ? currentProfile
          : {
              ...currentProfile,
              exp: result.current_exp,
              gold: result.current_gold,
              level: result.current_level,
            },
      );
      setHabits((currentHabits) =>
        currentHabits.map((habit) =>
          habit.id === result.habit_id
            ? { ...habit, checked_in_today: result.checked_in, last_check_in: new Date().toISOString() }
            : habit,
        ),
      );
      setNotice({
        kind: result.leveled_up ? "level" : "success",
        title: result.leveled_up ? "Level gate unlocked" : "Quest reward claimed",
        message: result.leveled_up
          ? "Guild rank updated. The next quest board awaits."
          : "+40 EXP / +8 gold. Keep the guild ledger shining.",
      });
    } catch (error) {
      setNotice(toErrorNotice(error));
    }
  };

  return (
    <main className="page font-mono">
      <div className="app-shell">
        <AppHeader />
        <div className="content">
          {isLoading ? (
            <section className="pixel-card empty-state" aria-live="polite">
              Connecting to guild server...
            </section>
          ) : profile === null ? (
            <section className="pixel-card empty-state" aria-live="polite">
              Start FastAPI on port 8000 to open today&apos;s quest board.
            </section>
          ) : (
            <>
              <HeroStatus profile={profile} />
              <QuestLog habits={habits} onCheckIn={handleCheckIn} />
              <LevelPanel exp={profile.exp} level={profile.level} />
            </>
          )}
        </div>
        <BottomNav />
        <NoticeToast notice={notice} />
      </div>
    </main>
  );
}

function toErrorNotice(error: unknown): Notice {
  if (error instanceof ApiError) {
    return {
      kind: "error",
      title: `Guild error ${error.status}`,
      message: error.message,
    };
  }

  return {
    kind: "error",
    title: "Guild server offline",
    message: "Start FastAPI on port 8000 before opening the React frontend.",
  };
}
