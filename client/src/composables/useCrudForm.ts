import { computed, ref } from "vue";

export interface CrudFormOptions<TForm, TItem> {
  emptyForm: () => TForm;
  toForm: (item: TItem) => TForm;
  formTitleCreate?: string;
  formTitleEdit?: string;
}

/** Shared create/edit modal form state for admin CRUD pages. */
export function useCrudForm<TForm, TItem extends { id: number }>(
  options: CrudFormOptions<TForm, TItem>,
) {
  const showForm = ref(false);
  const editingId = ref<number | null>(null);
  const form = ref(options.emptyForm()) as { value: TForm };

  const formTitle = computed(() =>
    editingId.value !== null
      ? (options.formTitleEdit ?? "Edit")
      : (options.formTitleCreate ?? "Create"),
  );

  function resetForm(): void {
    form.value = options.emptyForm();
    editingId.value = null;
  }

  function openCreate(): void {
    resetForm();
    showForm.value = true;
  }

  function openEdit(item: TItem): void {
    editingId.value = item.id;
    form.value = options.toForm(item);
    showForm.value = true;
  }

  function closeForm(): void {
    showForm.value = false;
    resetForm();
  }

  return {
    showForm,
    editingId,
    form,
    formTitle,
    resetForm,
    openCreate,
    openEdit,
    closeForm,
  };
}
