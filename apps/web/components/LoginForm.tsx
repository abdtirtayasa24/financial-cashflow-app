"use client";

import { useActionState } from "react";

import { signIn } from "@/app/actions";

export function LoginForm() {
  const [state, formAction] = useActionState(signIn, null);

  return (
    <form action={formAction} className="login card" aria-labelledby="login-title">
      <h1 id="login-title">Sign in</h1>
      <div className="field">
        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" autoComplete="email" required />
      </div>
      <div className="field">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="current-password"
          required
        />
      </div>
      <button type="submit" className="btn-primary">
        Sign in
      </button>
      {state?.error ? (
        <p className="error" role="alert">
          {state.error}
        </p>
      ) : null}
    </form>
  );
}