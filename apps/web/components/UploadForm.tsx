"use client";

import { useActionState } from "react";
import { AlertCircle, Upload } from "lucide-react";

import { uploadAttachment } from "@/app/actions";

const ACCEPT = ".pdf,.png,.jpg,.jpeg";

export function UploadForm({ id }: { id: string }) {
  const [state, formAction] = useActionState(uploadAttachment, null);

  return (
    <form action={formAction} className="upload-form" aria-label="Upload attachment">
      <input type="hidden" name="id" value={id} />
      <div className="upload-form__row">
        <input
          id={`file-${id}`}
          name="file"
          type="file"
          accept={ACCEPT}
          required
          aria-label="Choose file"
        />
        <button type="submit" className="btn-ghost">
          <Upload size={16} />
          Upload
        </button>
      </div>
      <p className="field__hint">
        PDF, PNG, or JPG up to 10 MB.
      </p>
      {state?.error ? (
        <p className="error" role="alert">
          <AlertCircle size={16} />
          {state.error}
        </p>
      ) : null}
    </form>
  );
}