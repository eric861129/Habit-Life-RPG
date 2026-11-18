import {ArrowUpRight} from "lucide-react";


export function OfficialSiteLink() {
  return (
    <aside className="official-site" aria-label="Habit Life RPG 正式版">
      <img src="/habit-life-rpg-qr.png" alt="Habit Life RPG 正式版 QR Code" width="132" height="132" />
      <div>
        <a href="https://habitliferpg.com/">
          前往 Habit Life RPG 正式版 <ArrowUpRight aria-hidden="true" size={18} />
        </a>
        <p>habitliferpg.com</p>
      </div>
    </aside>
  );
}
