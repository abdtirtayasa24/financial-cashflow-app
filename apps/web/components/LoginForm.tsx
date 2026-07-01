"use client";

import { useActionState } from "react";
import { AlertCircle } from "lucide-react";

import { signIn } from "@/app/actions";

export function LoginForm() {
  const [state, formAction] = useActionState(signIn, null);

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-card__brand">
          <span className="login-card__brand-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </span>
          <span className="login-card__brand-name">Financial Cashflow</span>
        </div>

        <h1>Welcome back</h1>
        <p className="login-card__subtitle">Sign in to your account to continue.</p>

        <form action={formAction} aria-labelledby="login-title">
          <span id="login-title" className="sr-only">Sign in</span>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              placeholder="you@company.com"
            />
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
          <div className="form-actions">
            <button type="submit" className="btn-primary">
              Sign in
            </button>
          </div>
          {state?.error ? (
            <p className="error" role="alert">
              <AlertCircle size={16} />
              {state.error}
            </p>
          ) : null}
        </form>
      </div>
    </div>
  );
}