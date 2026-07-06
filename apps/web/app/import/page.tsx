import { ImportTransactionsForm } from "@/components/ImportTransactionsForm";
import { getCurrentUser } from "@/lib/current-user";

export default async function ImportPage() {
  const user = await getCurrentUser();
  if (!user || user.role !== "FINANCE_ADMIN") {
    return (
      <div className="container">
        <div className="empty">
          <div className="empty__title">Not available</div>
          <p className="empty__desc">Only Finance Admin users can import transactions.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <div>
          <h1>Import transactions</h1>
          <p className="page-header__subtitle">Upload CSV or Excel rows. Valid rows are imported as draft transactions.</p>
        </div>
      </div>
      <div className="section">
        <ImportTransactionsForm />
      </div>
    </div>
  );
}
