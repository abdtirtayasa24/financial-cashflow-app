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