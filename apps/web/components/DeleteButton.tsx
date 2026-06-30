"use client";

import { type ReactNode, useTransition } from "react";

interface DeleteButtonProps {
  action: (formData: FormData) => void | Promise<void>;
  id: string;
  label?: string;
  children?: ReactNode;
}

export function DeleteButton({ action, id, label, children }: DeleteButtonProps) {
  const [pending, startTransition] = useTransition();
  return (
    <form
      action={(formData) => {
        if (window.confirm(`Delete ${label ?? "this record"}?`)) {
          startTransition(() => action(formData));
        }
      }}
    >
      <input type="hidden" name="id" value={id} />
      <button type="submit" className="btn-danger btn-sm" disabled={pending}>
        {children ?? "Delete"}
      </button>
    </form>
  );
}