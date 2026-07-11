import {useState} from "react";

import {session} from "./auth/session";
import {AuthScreen} from "./components/AuthScreen";
import {Dashboard} from "./components/Dashboard";


export default function App() {
  const [token, setToken] = useState<string | null>(() => session.getToken());
  const [expired, setExpired] = useState(false);

  const authenticate = (nextToken: string) => {
    session.setToken(nextToken);
    setToken(nextToken);
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
