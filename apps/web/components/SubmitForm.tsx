"use client";

import { useActionState } from "react";
import { AlertCircle, Send } from "lucide-react";

import { submitTransaction } from "@/app/actions";

export function SubmitForm({ id }: { id: string }) {
  const [state, formAction] = useActionState(submitTransaction, null);

  return (
    <form action={formAction} className="action-inline">
      <input type="hidden" name="id" value={id} />
      <button type="submit" className="btn-primary">
        <Send size={16} />
        Submit for approval
      </button>
      {state?.error ? (
        <p className="error" role="alert">
          <AlertCircle size={16} />
          {state.error}
        </p>
      ) : null}
    </form>
  );
}