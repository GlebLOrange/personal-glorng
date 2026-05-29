<script setup lang="ts">
import { ref } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import { api } from "@/composables/useApi";
import { useNotify } from "@/composables/useNotify";

const display = ref("0");
const expression = ref("");
const loading = ref(false);
const { toast } = useNotify();

const buttons = ["7", "8", "9", "/", "4", "5", "6", "*", "1", "2", "3", "-", "0", ".", "=", "+"];

const EXPR_RE = /^(-?\d+\.?\d*)\s*([+\-*/])\s*(-?\d+\.?\d*)$/;

function isOperator(val: string): boolean {
  return ["+", "-", "*", "/"].includes(val);
}

async function evaluate(expr: string): Promise<number | null> {
  const match = expr.match(EXPR_RE);
  if (!match) {
    const num = Number(expr);
    return Number.isFinite(num) ? num : null;
  }

  const a = Number(match[1]);
  const op = match[2];
  const b = Number(match[3]);
  if (!Number.isFinite(a) || !Number.isFinite(b)) return null;

  const { data } = await api.post("/tools/calculator", null, {
    params: { a, b, op },
  });
  return data.result;
}

async function handleInput(val: string): Promise<void> {
  if (val === "=") {
    loading.value = true;
    try {
      const result = await evaluate(expression.value);
      if (result === null || !Number.isFinite(result)) {
        toast("Invalid expression", "error");
        display.value = "Error";
        expression.value = "";
      } else {
        display.value = String(result);
        expression.value = String(result);
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Calculation failed";
      toast(msg, "error");
      display.value = "Error";
      expression.value = "";
    } finally {
      loading.value = false;
    }
    return;
  }

  if (
    val === "." &&
    expression.value
      .split(/[+\-*/]/)
      .pop()
      ?.includes(".")
  ) {
    return;
  }

  if (expression.value === "0" && !isOperator(val) && val !== ".") {
    expression.value = val;
  } else {
    expression.value += val;
  }
  display.value = expression.value;
}

function clear(): void {
  display.value = "0";
  expression.value = "";
}
</script>

<template>
  <AdminPageLayout title="calculator" max-width="sm">
    <BaseCard>
      <div class="bg-surface-dark rounded-lg p-4 mb-4 text-right">
        <div class="text-xs text-surface-mid h-5">{{ expression || "&nbsp;" }}</div>
        <div class="text-2xl font-bold text-surface-light">{{ loading ? "..." : display }}</div>
      </div>

      <div class="grid grid-cols-4 gap-2">
        <BaseButton variant="ghost" size="sm" class="col-span-2" @click="clear"> AC </BaseButton>
        <div class="col-span-2" />

        <BaseButton
          v-for="btn in buttons"
          :key="btn"
          :variant="isOperator(btn) || btn === '=' ? 'primary' : 'secondary'"
          size="lg"
          :disabled="loading"
          @click="handleInput(btn)"
        >
          {{ btn }}
        </BaseButton>
      </div>
    </BaseCard>
  </AdminPageLayout>
</template>
