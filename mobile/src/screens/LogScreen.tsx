import { useState } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

import type { LogResponse } from "../api/client";

type LogScreenProps = {
  isSubmitting: boolean;
  lastLogResult: LogResponse | null;
  onSubmit: (text: string) => Promise<void>;
};

export function LogScreen({ isSubmitting, lastLogResult, onSubmit }: LogScreenProps) {
  const [text, setText] = useState("bad sleep and small talk");

  const canSubmit = text.trim().length > 0 && !isSubmitting;

  const handleSubmit = async () => {
    if (!canSubmit) {
      return;
    }

    await onSubmit(text.trim());
    setText("");
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={styles.screen}
    >
      <View style={styles.panel}>
        <Text style={styles.title}>Log energy events</Text>
        <TextInput
          multiline
          placeholder="bad sleep, forced socializing, quiet time..."
          placeholderTextColor="#8C8D86"
          style={styles.input}
          value={text}
          onChangeText={setText}
        />
        <TouchableOpacity
          accessibilityRole="button"
          disabled={!canSubmit}
          style={[styles.submitButton, !canSubmit ? styles.disabledButton : null]}
          onPress={handleSubmit}
        >
          <Text style={styles.submitText}>{isSubmitting ? "Submitting" : "Submit log"}</Text>
        </TouchableOpacity>
      </View>

      {lastLogResult ? (
        <View style={styles.panel}>
          <Text style={styles.title}>Submit result</Text>
          <Text style={styles.score}>
            {lastLogResult.battery_before}% to {lastLogResult.battery_after}%
          </Text>
          <View style={styles.taskList}>
            {lastLogResult.parsed_tasks.map((task) => (
              <View key={`${task.label}-${task.direction}`} style={styles.taskPill}>
                <Text style={styles.taskText}>
                  {task.label} {task.direction === "up" ? "+" : "-"}
                </Text>
              </View>
            ))}
          </View>
        </View>
      ) : null}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: {
    gap: 14,
  },
  panel: {
    backgroundColor: "#FFFFFF",
    borderColor: "#DADBD2",
    borderRadius: 8,
    borderWidth: 1,
    padding: 16,
  },
  title: {
    color: "#151515",
    fontSize: 18,
    fontWeight: "800",
  },
  input: {
    backgroundColor: "#FAFAF7",
    borderColor: "#DADBD2",
    borderRadius: 8,
    borderWidth: 1,
    color: "#151515",
    fontSize: 17,
    lineHeight: 24,
    marginTop: 14,
    minHeight: 140,
    padding: 14,
    textAlignVertical: "top",
  },
  submitButton: {
    alignItems: "center",
    backgroundColor: "#151515",
    borderRadius: 8,
    marginTop: 14,
    paddingVertical: 14,
  },
  disabledButton: {
    backgroundColor: "#9B9C95",
  },
  submitText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "800",
  },
  score: {
    color: "#151515",
    fontSize: 30,
    fontWeight: "900",
    marginTop: 8,
  },
  taskList: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 12,
  },
  taskPill: {
    backgroundColor: "#EEF4EA",
    borderColor: "#C9DBC2",
    borderRadius: 8,
    borderWidth: 1,
    paddingHorizontal: 10,
    paddingVertical: 7,
  },
  taskText: {
    color: "#2C5F39",
    fontSize: 13,
    fontWeight: "800",
  },
});
