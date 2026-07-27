import {Eye, EyeOff, LogIn, ShieldPlus, UserRound} from "lucide-react";
import {useState, type FormEvent} from "react";

import {ApiError, login, register, type TokenResponse} from "../api/client";


type AuthScreenProps = {
  expired: boolean;
  onAuthenticated: (response: TokenResponse) => void;
};

export function AuthScreen({expired, onAuthenticated}: AuthScreenProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const response =
        mode === "register" ? await register(username, password) : await login(username, password);
      onAuthenticated(response);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "暫時無法連線，請稍後再試。");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-layout" aria-labelledby="auth-title">
        <div className="auth-identity">
          <img src="/hero-avatar.png" alt="Habit Life RPG 冒險者" className="auth-avatar" />
          <div>
            <p className="brand-name">Habit Life RPG</p>
            <h1 id="auth-title">{expired ? "重新登入" : "開啟今天的冒險日誌"}</h1>
            <p className="auth-copy">把今天完成的行動，留成看得見的成長紀錄。</p>
          </div>
        </div>

        <form className="auth-form" onSubmit={submit}>
          <div className="segmented" role="tablist" aria-label="帳號模式">
            <button
              type="button"
              role="tab"
              aria-selected={mode === "login"}
              className={mode === "login" ? "is-selected" : ""}
              onClick={() => {
                setMode("login");
                setError(null);
              }}
            >
              登入
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === "register"}
              className={mode === "register" ? "is-selected" : ""}
              onClick={() => {
                setMode("register");
                setError(null);
              }}
            >
              註冊
            </button>
          </div>

          <label className="field">
            <span>使用者名稱</span>
            <span className="input-shell">
              <UserRound aria-hidden="true" />
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
                minLength={3}
                maxLength={32}
                required
              />
            </span>
          </label>

          <label className="field">
            <span>密碼</span>
            <span className="input-shell">
              <input
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                type={showPassword ? "text" : "password"}
                autoComplete={mode === "register" ? "new-password" : "current-password"}
                minLength={10}
                maxLength={128}
                required
              />
              <button
                type="button"
                className="icon-button"
                aria-label={showPassword ? "隱藏密碼" : "顯示密碼"}
                title={showPassword ? "隱藏密碼" : "顯示密碼"}
                onClick={() => setShowPassword((current) => !current)}
              >
                {showPassword ? <EyeOff aria-hidden="true" /> : <Eye aria-hidden="true" />}
              </button>
            </span>
          </label>

          {error ? <p className="form-error" role="alert">{error}</p> : null}

          <button className="primary-button auth-submit" type="submit" disabled={isSubmitting}>
            {mode === "register" ? <ShieldPlus aria-hidden="true" /> : <LogIn aria-hidden="true" />}
            <span>
              {isSubmitting ? "連線中..." : mode === "register" ? "建立冒險者" : "登入"}
            </span>
          </button>
        </form>
      </section>
    </main>
  );
}
