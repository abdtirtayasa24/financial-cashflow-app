"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { apiSend, apiUpload } from "@/lib/api";
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

// --- Transactions ---
function opt(formData: FormData, key: string): string | null {
  const v = str(formData, key);
  return v === "" ? null : v;
}

export async function createTransaction(
  _prev: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  let created: { id: string };
  try {
    created = await apiSend<{ id: string }>("/api/transactions", "POST", {
      transaction_date: str(formData, "transaction_date"),
      direction: str(formData, "direction"),
      amount: Number(str(formData, "amount")),
      cash_account_id: str(formData, "cash_account_id"),
      department_id: str(formData, "department_id"),
      category_id: str(formData, "category_id"),
      payment_method_id: str(formData, "payment_method_id"),
      counterparty_name: opt(formData, "counterparty_name"),
      reference_no: opt(formData, "reference_no"),
      description: opt(formData, "description"),
    });
  } catch (e) {
    return { error: e instanceof Error ? e.message : "Failed to create transaction" };
  }
  redirect(`/transactions/${created.id}`);
}

export async function updateTransaction(
  _prev: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  const id = str(formData, "id");
  try {
    await apiSend(`/api/transactions/${id}`, "PATCH", {
      transaction_date: str(formData, "transaction_date") || undefined,
      direction: str(formData, "direction") || undefined,
      amount: str(formData, "amount")
        ? Number(str(formData, "amount"))
        : undefined,
      cash_account_id: str(formData, "cash_account_id") || undefined,
      department_id: str(formData, "department_id") || undefined,
      category_id: str(formData, "category_id") || undefined,
      payment_method_id: str(formData, "payment_method_id") || undefined,
      counterparty_name: opt(formData, "counterparty_name"),
      reference_no: opt(formData, "reference_no"),
      description: opt(formData, "description"),
    });
  } catch (e) {
    return { error: e instanceof Error ? e.message : "Failed to update transaction" };
  }
  redirect(`/transactions/${id}`);
}

export async function submitTransaction(
  _prev: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  const id = str(formData, "id");
  try {
    await apiSend(`/api/transactions/${id}/submit`, "POST");
  } catch (e) {
    return { error: e instanceof Error ? e.message : "Failed to submit transaction" };
  }
  revalidatePath(`/transactions/${id}`);
  revalidatePath("/transactions");
  return { error: null };
}

export async function deleteTransaction(formData: FormData): Promise<void> {
  await apiSend(`/api/transactions/${str(formData, "id")}`, "DELETE");
  revalidatePath("/transactions");
  redirect("/transactions");
}

// --- Attachments ---
export async function uploadAttachment(
  _prev: ActionResult | null,
  formData: FormData
): Promise<ActionResult> {
  const id = str(formData, "id");
  const file = formData.get("file");
  if (!(file instanceof File)) {
    return { error: "No file selected" };
  }
  const payload = new FormData();
  payload.set("file", file);
  try {
    await apiUpload(`/api/transactions/${id}/attachments`, payload);
  } catch (e) {
    return { error: e instanceof Error ? e.message : "Failed to upload file" };
  }
  revalidatePath(`/transactions/${id}`);
  return { error: null };
}

export async function deleteAttachment(formData: FormData): Promise<void> {
  const id = str(formData, "id");
  const attachmentId = str(formData, "attachmentId");
  await apiSend(
    `/api/transactions/${id}/attachments/${attachmentId}`,
    "DELETE"
  );
  revalidatePath(`/transactions/${id}`);
}