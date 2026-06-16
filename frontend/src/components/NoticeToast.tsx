import type { Notice } from "../types";

type NoticeToastProps = {
  notice: Notice | null;
};

export function NoticeToast({ notice }: NoticeToastProps) {
  if (notice === null) {
    return null;
  }

  const isError = notice.kind === "error";

  return (
    <aside className={`notice-toast ${notice.kind}`} role={isError ? "alert" : "status"} aria-live={isError ? "assertive" : "polite"}>
      <strong>{notice.title}</strong>
      <span>{notice.message}</span>
    </aside>
  );
}
