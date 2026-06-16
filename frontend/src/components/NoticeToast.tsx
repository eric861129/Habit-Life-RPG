import type { Notice } from "../types";

type NoticeToastProps = {
  notice: Notice | null;
};

export function NoticeToast({ notice }: NoticeToastProps) {
  if (notice === null) {
    return null;
  }

  return (
    <aside className={`notice-toast ${notice.kind}`} role="status" aria-live="polite">
      <strong>{notice.title}</strong>
      <span>{notice.message}</span>
    </aside>
  );
}
