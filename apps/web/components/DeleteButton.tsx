"use client";

import { type ReactNode } from "react";

import { ConfirmButton } from "@/components/ConfirmButton";

interface DeleteButtonProps {
  action: (formData: FormData) => void | Promise<void>;
  id: string;
  label?: string;
  children?: ReactNode;
}

/**
 * Inline two-step confirmation for destructive admin actions.
 * Delegates to {@link ConfirmButton} so no `window.confirm` is used (DESIGN.md).
 * Kept as its own export so the existing admin pages need no changes.
 */
export function DeleteButton({ action, id, label, children }: DeleteButtonProps) {
  return (
    <ConfirmButton
      action={action}
      id={id}
      label={label}
      confirmLabel="Confirm"
      className="btn-danger btn-sm"
    >
      {children ?? "Delete"}
    </ConfirmButton>
  );
}