"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { apiSend } from "@/lib/api";
import { createClient } from "@/lib/supabase-server";

function str(formData: FormData, key: string): string {
  return String(formData.get(key) ?? "");
}

export interface ActionResult {
  error: string | null;
}

export async function signIn(
  _prev: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword({
    email: str(formData, "email"),
    password: str(formData, "password"),
  });
  if (error) {
    return { error: error.message };
  }
  redirect("/dashboard");
}

export async function signOut(): Promise<void> {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/login");
}

// --- Departments ---
export async function createDepartment(formData: FormData): Promise<void> {
  await apiSend("/api/departments", "POST", {
    name: str(formData, "name"),
    code: str(formData, "code"),
    is_active: true,
  });
  revalidatePath("/admin/departments");
}

export async function deleteDepartment(formData: FormData): Promise<void> {
  await apiSend(`/api/departments/${str(formData, "id")}`, "DELETE");
  revalidatePath("/admin/departments");
}

export async function toggleDepartmentActive(formData: FormData): Promise<void> {
  await apiSend(`/api/departments/${str(formData, "id")}`, "PATCH", {
    is_active: str(formData, "active") !== "true",
  });
  revalidatePath("/admin/departments");
}

// --- Cashflow categories ---
export async function createCategory(formData: FormData): Promise<void> {
  await apiSend("/api/categories", "POST", {
    name: str(formData, "name"),
    direction: str(formData, "direction"),
    is_active: true,
  });
  revalidatePath("/admin/categories");
}

export async function deleteCategory(formData: FormData): Promise<void> {
  await apiSend(`/api/categories/${str(formData, "id")}`, "DELETE");
  revalidatePath("/admin/categories");
}

export async function toggleCategoryActive(formData: FormData): Promise<void> {
  await apiSend(`/api/categories/${str(formData, "id")}`, "PATCH", {
    is_active: str(formData, "active") !== "true",
  });
  revalidatePath("/admin/categories");
}

// --- Payment methods ---
export async function createPaymentMethod(formData: FormData): Promise<void> {
  await apiSend("/api/payment-methods", "POST", {
    name: str(formData, "name"),
    is_active: true,
  });
  revalidatePath("/admin/payment-methods");
}

export async function deletePaymentMethod(formData: FormData): Promise<void> {
  await apiSend(`/api/payment-methods/${str(formData, "id")}`, "DELETE");
  revalidatePath("/admin/payment-methods");
}

export async function togglePaymentMethodActive(
  formData: FormData
): Promise<void> {
  await apiSend(`/api/payment-methods/${str(formData, "id")}`, "PATCH", {
    is_active: str(formData, "active") !== "true",
  });
  revalidatePath("/admin/payment-methods");
}

// --- Cash accounts ---
export async function createCashAccount(formData: FormData): Promise<void> {
  await apiSend("/api/cash-accounts", "POST", {
    name: str(formData, "name"),
    account_type: str(formData, "account_type"),
    opening_balance: Number(str(formData, "opening_balance") || 0),
    opening_balance_date: str(formData, "opening_balance_date"),
    is_active: true,
  });
  revalidatePath("/admin/cash-accounts");
}

export async function deleteCashAccount(formData: FormData): Promise<void> {
  await apiSend(`/api/cash-accounts/${str(formData, "id")}`, "DELETE");
  revalidatePath("/admin/cash-accounts");
}

// --- App settings (key/value, upsert) ---
export async function upsertAppSetting(formData: FormData): Promise<void> {
  await apiSend("/api/settings", "PUT", {
    key: str(formData, "key"),
    value: str(formData, "value"),
  });
  revalidatePath("/admin/settings");
}

// --- Users ---
export async function createUser(formData: FormData): Promise<void> {
  await apiSend("/api/users", "POST", {
    email: str(formData, "email"),
    password: str(formData, "password"),
    full_name: str(formData, "full_name"),
    role: str(formData, "role"),
    department_id: str(formData, "department_id") || null,
  });
  revalidatePath("/admin/users");
}

export async function updateUser(formData: FormData): Promise<void> {
  await apiSend(`/api/users/${str(formData, "id")}`, "PATCH", {
    full_name: str(formData, "full_name") || undefined,
    role: str(formData, "role") || undefined,
    department_id: str(formData, "department_id") || null,
    status: str(formData, "status") || undefined,
  });
  revalidatePath("/admin/users");
}