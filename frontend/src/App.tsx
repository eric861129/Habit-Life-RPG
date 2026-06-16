import { AppHeader } from "./components/AppHeader";
import { BottomNav } from "./components/BottomNav";
import { HeroStatus } from "./components/HeroStatus";
import { LevelPanel } from "./components/LevelPanel";
import { NoticeToast } from "./components/NoticeToast";
import { QuestLog } from "./components/QuestLog";
import { demoHabits, demoNotice, demoProfile } from "./data/demoState";

export default function App() {
  const handleStaticCheckIn = () => {
    // API integration is added in Chapter 7.3.
  };

  return (
    <main className="page font-mono">
      <div className="app-shell">
        <AppHeader />
        <div className="content">
          <HeroStatus profile={demoProfile} />
          <QuestLog habits={demoHabits} onCheckIn={handleStaticCheckIn} />
          <LevelPanel exp={demoProfile.exp} level={demoProfile.level} />
        </div>
        <BottomNav />
        <NoticeToast notice={demoNotice} />
      </div>
    </main>
  );
}
