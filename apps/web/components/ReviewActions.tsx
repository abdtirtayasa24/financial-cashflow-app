"use client";

import { useActionState, useState } from "react";
import { AlertCircle, Ban, CheckCircle2, XCircle } from "lucide-react";

import {
  approveTransaction,
  rejectTransaction,
  voidTransaction,
} from "@/app/actions";

export function ApproveForm({ id }: { id: string }) {
  const [state, formAction, pending] = useActionState(approveTransaction, null);

  return (
    <form action={formAction} className="action-inline">
      <input type="hidden" name="id" value={id} />
      <button type="submit" className="btn-primary btn-sm" disabled={pending}>
        <CheckCircle2 size={16} />
        {pending ? "Approving…" : "Approve"}
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

export function RejectForm({ id }: { id: string }) {
  const [open, setOpen] = useState(false);
  const [state, formAction, pending] = useActionState(rejectTransaction, null);

  if (!open) {
    return (
      <button type="button" className="btn-danger btn-sm" onClick={() => setOpen(true)}>
        <XCircle size={16} />
        Reject
      </button>
    );
  }

  return (
    <form action={formAction} className="review-form">
      <input type="hidden" name="id" value={id} />
      <label className="sr-only" htmlFor={`reject-reason-${id}`}>
        Rejection reason
      </label>
      <textarea
        id={`reject-reason-${id}`}
        name="reason"
        required
        minLength={1}
        rows={2}
        placeholder="Reason for rejection"
        disabled={pending}
      />
      <div className="review-form__actions">
        <button
          type="button"
          className="btn-ghost btn-sm"
          disabled={pending}
          onClick={() => setOpen(false)}
        >
          Cancel
        </button>
        <button type="submit" className="btn-danger btn-sm" disabled={pending}>
          {pending ? "Rejecting…" : "Reject"}
        </button>
      </div>
      {state?.error ? (
        <p className="error" role="alert">
          <AlertCircle size={16} />
          {state.error}
        </p>
      ) : null}
    </form>
  );
}

export function VoidForm({ id }: { id: string }) {
  const [open, setOpen] = useState(false);
  const [state, formAction, pending] = useActionState(voidTransaction, null);

  if (!open) {
    return (
      <button type="button" className="btn-danger btn-sm" onClick={() => setOpen(true)}>
        <Ban size={16} />
        Void
      </button>
    );
  }

  return (
    <form action={formAction} className="review-form">
      <input type="hidden" name="id" value={id} />
      <label className="sr-only" htmlFor={`void-reason-${id}`}>
        Void reason
      </label>
      <textarea
        id={`void-reason-${id}`}
        name="reason"
        required
        minLength={1}
        rows={2}
        placeholder="Reason for voiding"
        disabled={pending}
      />
      <div className="review-form__actions">
        <button
          type="button"
          className="btn-ghost btn-sm"
          disabled={pending}
          onClick={() => setOpen(false)}
        >
          Cancel
        </button>
        <button type="submit" className="btn-danger btn-sm" disabled={pending}>
          {pending ? "Voiding…" : "Void transaction"}
        </button>
      </div>
      {state?.error ? (
        <p className="error" role="alert">
          <AlertCircle size={16} />
          {state.error}
        </p>
      ) : null}
    </form>
  );
}
