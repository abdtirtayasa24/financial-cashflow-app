import Link from "next/link";

export default function HomePage() {
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
        <h1>Cashflow recording &amp; BI reporting</h1>
        <p className="login-card__subtitle">
          A centralized system for recording, classifying, reviewing, and analyzing cash inflows and outflows.
        </p>
        <div className="form-actions">
          <Link href="/login" className="btn-primary" style={{ textDecoration: "none" }}>
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}