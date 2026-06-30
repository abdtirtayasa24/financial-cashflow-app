import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <h1>Financial Cashflow</h1>
      <p>
        Cashflow recording and BI reporting application. The dashboard, transactions,
        approvals, reports, and admin pages arrive in later milestones.
      </p>
      <p>
        <Link href="/login">Sign in</Link>
      </p>
    </main>
  );
}