"use client";

import { useState, useTransition, type ReactNode } from "react";

interface ConfirmButtonProps {
  action: (formData: FormData) => void | Promise<void>;
  id?: string;
  extraFields?: Record<string, string>;
  label?: string;
  confirmLabel?: string;
  children?: ReactNode;
  className?: string;
}

/**
 * Inline two-step confirmation — no window.confirm (per DESIGN.md).
 * First click reveals a "Confirm" button; a second click performs the action.
 */
export function ConfirmButton({
  action,
  id,
  extraFields,
  label = "this record",
  confirmLabel = "Confirm",
  children,
  className = "btn-danger btn-sm",
}: ConfirmButtonProps) {
  const [armed, setArmed] = useState(false);
  const [pending, startTransition] = useTransition();

  if (armed) {
    return (
      <span className="confirm-inline" role="group" aria-label={`Confirm delete ${label}`}>
        <button
          type="button"
          className="btn-ghost btn-sm"
          disabled={pending}
          onClick={() => setArmed(false)}
        >
          Cancel
        </button>
        <form
          action={(formData) =>
            startTransition(async () => {
              await action(formData);
            })
          }
        >
          {id ? <input type="hidden" name="id" value={id} /> : null}
          {extraFields
            ? Object.entries(extraFields).map(([k, v]) => (
                <input key={k} type="hidden" name={k} value={v} />
              ))
            : null}
          <button type="submit" className={className} disabled={pending}>
            {pending ? "Deleting…" : confirmLabel}
          </button>
        </form>
      </span>
    );
  }

  return (
    <button
      type="button"
      className={className}
      onClick={() => setArmed(true)}
    >
      {children ?? "Delete"}
    </button>
  );
}