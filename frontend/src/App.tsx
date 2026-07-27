import {useState} from "react";

import type {TokenResponse} from "./api/client";
import {session} from "./auth/session";
import {AuthScreen} from "./components/AuthScreen";
import {Dashboard} from "./components/Dashboard";


export default function App() {
  const [initialSession] = useState(() => session.restore());
  const [token, setToken] = useState<string | null>(initialSession.token);
  const [expired, setExpired] = useState(initialSession.expired);

  const authenticate = (response: TokenResponse) => {
    session.set(response.access_token, response.expires_in);
    setToken(response.access_token);
    setExpired(false);
  };

  const logout = () => {
    session.clear();
    setToken(null);
    setExpired(false);
  };

  const unauthorized = () => {
    session.clear();
    setToken(null);
    setExpired(true);
  };

  return token ? (
    <Dashboard token={token} onLogout={logout} onUnauthorized={unauthorized} />
  ) : (
    <AuthScreen expired={expired} onAuthenticated={authenticate} />
  );
}
