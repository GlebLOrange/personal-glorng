import type { Component } from "vue";

import CheckIcon from "@/components/icons/CheckIcon.vue";
import CloseIcon from "@/components/icons/CloseIcon.vue";
import PencilIcon from "@/components/icons/PencilIcon.vue";
import PlusIcon from "@/components/icons/PlusIcon.vue";
import TrashIcon from "@/components/icons/TrashIcon.vue";
import type { BaseButtonVariant } from "@/constants/actionButtonVariants";

/**
 * Default leading SVG for BaseButton / ToolbarPillButton by variant or semantic action.
 * Callers with custom meaning should pass an explicit icon in the slot instead of relying on this.
 */
export const ACTION_BUTTON_ICON: Partial<Record<BaseButtonVariant, Component>> = {
  create: PlusIcon,
  add: PlusIcon,
  save: CheckIcon,
  edit: PencilIcon,
  remove: TrashIcon,
  delete: TrashIcon,
  cancel: CloseIcon,
  primary: CheckIcon,
  success: CheckIcon,
};
