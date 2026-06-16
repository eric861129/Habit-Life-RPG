const navItems = ["Home", "Quests", "Hero"];

export function BottomNav() {
  return (
    <nav className="bottom-nav" aria-label="Main navigation">
      {navItems.map((item) => (
        <button key={item} type="button" className={item === "Home" ? "is-active" : ""}>
          {item}
        </button>
      ))}
    </nav>
  );
}
