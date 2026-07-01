export type Role =
  | "EMPLOYEE"
  | "DEPARTMENT_MANAGER"
  | "FINANCE_ADMIN"
  | "MANAGEMENT"
  | "SYSTEM_ADMIN";

export interface CurrentUser {
  id: string;
  role: Role;
  department_id: string | null;
  full_name: string;
  status: "ACTIVE" | "INACTIVE";
  email: string | null;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  parent_department_id: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Category {
  id: string;
  parent_category_id: string | null;
  name: string;
  direction: string;
  is_active: boolean;
  created_at: string;
}

export interface PaymentMethod {
  id: string;
  name: string;
  is_active: boolean;
}

export interface CashAccount {
  id: string;
  name: string;
  account_type: string;
  opening_balance: number;
  opening_balance_date: string;
  currency: string;
  is_active: boolean;
  created_at: string;
}

export interface AppSetting {
  id: string;
  key: string;
  value: string;
  updated_by: string | null;
  updated_at: string;
  created_at: string;
}

export interface User {
  id: string;
  email: string | null;
  full_name: string;
  role: Role;
  department_id: string | null;
  status: "ACTIVE" | "INACTIVE";
  created_at: string;
}

export const ROLES: Role[] = [
  "EMPLOYEE",
  "DEPARTMENT_MANAGER",
  "FINANCE_ADMIN",
  "MANAGEMENT",
  "SYSTEM_ADMIN",
];

export type TransactionDirection = "INFLOW" | "OUTFLOW";

export type TransactionStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "APPROVED"
  | "REJECTED"
  | "VOIDED";

export const TRANSACTION_STATUSES: TransactionStatus[] = [
  "DRAFT",
  "SUBMITTED",
  "APPROVED",
  "REJECTED",
  "VOIDED",
];

export const DIRECTIONS: TransactionDirection[] = ["INFLOW", "OUTFLOW"];

export interface Transaction {
  id: string;
  transaction_no: string;
  transaction_date: string;
  direction: TransactionDirection;
  amount: number;
  currency: string;
  exchange_rate: number;
  base_amount: number;
  cash_account_id: string;
  department_id: string;
  category_id: string;
  payment_method_id: string | null;
  counterparty_name: string | null;
  reference_no: string | null;
  description: string | null;
  status: TransactionStatus;
  created_by: string;
  submitted_at: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  rejection_reason: string | null;
  void_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface Attachment {
  id: string;
  transaction_id: string;
  original_file_name: string;
  stored_file_name: string;
  relative_path: string;
  mime_type: string;
  file_size_bytes: number;
  checksum_sha256: string | null;
  uploaded_by: string;
  uploaded_at: string;
}

export interface AuditLog {
  id: string;
  transaction_id: string;
  actor_user_id: string;
  actor_name: string | null;
  action: string;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  reason: string | null;
  created_at: string;
}

export const STATUS_LABELS: Record<TransactionStatus, string> = {
  DRAFT: "Draft",
  SUBMITTED: "Submitted",
  APPROVED: "Approved",
  REJECTED: "Rejected",
  VOIDED: "Voided",
};

export const STATUS_BADGE_CLASS: Record<TransactionStatus, string> = {
  DRAFT: "badge--draft",
  SUBMITTED: "badge--pending",
  APPROVED: "badge--approved",
  REJECTED: "badge--rejected",
  VOIDED: "badge--voided",
};