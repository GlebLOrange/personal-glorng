<script setup lang="ts">
import { ref } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
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

  const { data } = await api.post("/tools/calculator", { a, b, op });
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

const OPERATOR_LABELS: Record<string, string> = {
  "/": "Divide",
  "*": "Multiply",
  "-": "Subtract",
  "+": "Add",
  "=": "Equals",
  ".": "Decimal point",
};

function buttonAriaLabel(val: string): string | undefined {
  return OPERATOR_LABELS[val];
}
</script>

<template>
  <PageShell
    title="calculator"
    :breadcrumbs="[{ label: 'tools', to: '/tools' }, { label: 'calculator' }]"
    back-to="/tools"
    max-width="sm"
    :narrow="false"
  >
    <Card>
      <div
        class="bg-surface-dark rounded-lg p-4 mb-4 text-right"
        role="status"
        aria-live="polite"
        aria-atomic="true"
      >
        <div class="text-xs text-surface-mid h-5" aria-hidden="true">
          {{ expression || "\u00a0" }}
        </div>
        <div class="text-2xl font-bold text-surface-light">
          <span class="sr-only">Result: </span>
          {{ loading ? "..." : display }}
        </div>
      </div>

      <div class="tool-grid">
        <BaseButton
          variant="ghost"
          size="sm"
          class="col-span-2"
          aria-label="All clear"
          @click="clear"
        >
          AC
        </BaseButton>
        <div class="col-span-2" aria-hidden="true" />

        <BaseButton
          v-for="btn in buttons"
          :key="btn"
          :variant="isOperator(btn) || btn === '=' ? 'primary' : 'secondary'"
          size="lg"
          :disabled="loading"
          :aria-label="buttonAriaLabel(btn)"
          @click="handleInput(btn)"
        >
          {{ btn }}
        </BaseButton>
      </div>
    </Card>
  </PageShell>
</template>
