import {beforeEach, describe, expect, it} from "vitest";

import {session} from "./session";


beforeEach(() => {
  window.localStorage.clear();
  window.sessionStorage.clear();
});


describe("browser session", () => {
  it("stores the token and absolute expiry in sessionStorage", () => {
    session.set("reader-token", 3600, 1_000);

    expect(JSON.parse(window.sessionStorage.getItem("hlr.session.v2") ?? "null")).toEqual({
      token: "reader-token",
      expiresAt: 3_601_000,
    });
    expect(window.localStorage.getItem("hlr.session.v1")).toBeNull();
  });

  it("restores a session that has not expired", () => {
    session.set("reader-token", 3600, 1_000);

    expect(session.restore(3_600_999)).toEqual({token: "reader-token", expired: false});
  });

  it("clears a session at its expiry boundary", () => {
    session.set("reader-token", 3600, 1_000);

    expect(session.restore(3_601_000)).toEqual({token: null, expired: true});
    expect(window.sessionStorage.getItem("hlr.session.v2")).toBeNull();
  });
});
