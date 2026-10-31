<script setup lang="ts">
import { ref } from "vue";

import KeyGlyphIcon from "@/components/icons/KeyGlyphIcon.vue";
import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import { useNotify } from "@/composables/useNotify";

const display = ref("0");
const expression = ref("");
const { run: runEval, loading } = useApiAction();
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
    const result = await runEval(() => evaluate(expression.value), {
      errorMessage: "Calculation failed",
    });
    if (result === undefined) {
      display.value = "Error";
      expression.value = "";
      return;
    }
    if (result === null || !Number.isFinite(result)) {
      toast("Invalid expression", "error");
      display.value = "Error";
      expression.value = "";
    } else {
      display.value = String(result);
      expression.value = String(result);
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
  "/": "divide",
  "*": "multiply",
  "-": "subtract",
  "+": "add",
  "=": "equals",
  ".": "decimal point",
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
    max-width="5xl"
    :narrow="false"
    tool
  >
    <div class="page-tool-actions">
      <Card class="w-auto max-w-full">
        <div
          class="mb-4 rounded-lg bg-surface-dark p-4 text-right"
          role="status"
          aria-live="polite"
          aria-atomic="true"
        >
          <div class="h-5 text-xs text-surface-mid" aria-hidden="true">
            {{ expression || "\u00a0" }}
          </div>
          <div class="text-2xl font-bold text-surface-light">
            <span class="sr-only">Result: </span>
            {{ loading ? "…" : display }}
          </div>
        </div>

        <div class="tool-grid">
          <BaseButton
            variant="ghost"
            size="sm"
            class="col-span-2 gap-1.5"
            aria-label="all clear"
            :icon="false"
            @click="clear"
          >
            <KeyGlyphIcon glyph="AC" class-name="size-4" />
            <span class="sr-only">AC</span>
          </BaseButton>
          <div class="col-span-2" aria-hidden="true" />

          <BaseButton
            v-for="btn in buttons"
            :key="btn"
            :variant="isOperator(btn) || btn === '=' ? 'primary' : 'secondary'"
            size="lg"
            :disabled="loading"
            :aria-label="buttonAriaLabel(btn)"
            :icon="false"
            @click="handleInput(btn)"
          >
            <KeyGlyphIcon :glyph="btn" class-name="size-5" />
            <span class="sr-only">{{ buttonAriaLabel(btn) ?? btn }}</span>
          </BaseButton>
        </div>
      </Card>
    </div>
  </PageShell>
</template>
